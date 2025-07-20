"""
FHIR synchronization service for DiagnoAssist Backend
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.patient import PatientModel
from app.models.encounter import EncounterModel, EncounterStatusEnum
from app.models.episode import EpisodeModel
from app.models.fhir_models import FHIRSyncStatus, FHIRSyncRequest, FHIRSyncResponse
from app.repositories.fhir_repository import fhir_repository
from app.repositories.patient_repository import patient_repository
from app.repositories.encounter_repository import encounter_repository
from app.repositories.episode_repository import episode_repository
from app.core.exceptions import DatabaseException, NotFoundError

logger = logging.getLogger(__name__)


class SyncStrategy(str, Enum):
    """Synchronization strategy enum"""
    MONGODB_ONLY = "mongodb_only"  # Store only in MongoDB
    FHIR_ONLY = "fhir_only"  # Store only in FHIR
    HYBRID_MONGODB_PRIMARY = "hybrid_mongodb_primary"  # MongoDB primary, sync to FHIR
    HYBRID_FHIR_PRIMARY = "hybrid_fhir_primary"  # FHIR primary, sync to MongoDB
    BIDIRECTIONAL = "bidirectional"  # Keep both in sync


class SyncResult(str, Enum):
    """Synchronization result enum"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    SKIPPED = "skipped"


class FHIRSyncService:
    """Service for managing FHIR synchronization"""
    
    def __init__(self):
        # Default sync strategy - can be configured per entity type
        self.default_strategy = SyncStrategy.HYBRID_MONGODB_PRIMARY
        
        # Entity-specific strategies
        self.entity_strategies = {
            "patient": SyncStrategy.HYBRID_MONGODB_PRIMARY,
            "encounter": SyncStrategy.HYBRID_MONGODB_PRIMARY,
            "episode": SyncStrategy.MONGODB_ONLY  # Episodes are internal only
        }
        
        # Store sync status in memory for now (would use database in production)
        self._sync_status: Dict[str, FHIRSyncStatus] = {}
    
    def get_sync_strategy(self, entity_type: str) -> SyncStrategy:
        """Get synchronization strategy for entity type"""
        return self.entity_strategies.get(entity_type, self.default_strategy)
    
    def set_sync_strategy(self, entity_type: str, strategy: SyncStrategy):
        """Set synchronization strategy for entity type"""
        self.entity_strategies[entity_type] = strategy
        logger.info(f"Set sync strategy for {entity_type}: {strategy}")
    
    async def get_sync_status(self, entity_id: str, entity_type: str) -> Optional[FHIRSyncStatus]:
        """Get synchronization status for an entity"""
        key = f"{entity_type}:{entity_id}"
        return self._sync_status.get(key)
    
    async def update_sync_status(
        self, 
        entity_id: str, 
        entity_type: str, 
        fhir_id: Optional[str] = None,
        status: str = "synced",
        errors: Optional[List[str]] = None
    ):
        """Update synchronization status for an entity"""
        key = f"{entity_type}:{entity_id}"
        
        now = datetime.utcnow()
        
        if key in self._sync_status:
            sync_status = self._sync_status[key]
            sync_status.fhir_id = fhir_id or sync_status.fhir_id
            sync_status.sync_status = status
            sync_status.sync_errors = errors
            sync_status.last_sync = now
            sync_status.updated_at = now
        else:
            sync_status = FHIRSyncStatus(
                entity_id=entity_id,
                entity_type=entity_type,
                fhir_id=fhir_id,
                sync_status=status,
                sync_errors=errors,
                last_sync=now
            )
            self._sync_status[key] = sync_status
        
        logger.debug(f"Updated sync status for {entity_type}:{entity_id} - {status}")
    
    # Patient synchronization
    
    async def sync_patient(
        self, 
        patient: PatientModel, 
        force_sync: bool = False
    ) -> FHIRSyncResponse:
        """Synchronize patient with FHIR server"""
        strategy = self.get_sync_strategy("patient")
        
        # Skip if strategy doesn't involve FHIR
        if strategy == SyncStrategy.MONGODB_ONLY:
            logger.debug(f"Skipping FHIR sync for patient {patient.id} - MongoDB only strategy")
            return FHIRSyncResponse(success=True, errors=["Skipped - MongoDB only strategy"])
        
        # Check if FHIR is available
        if not fhir_repository.is_available():
            logger.warning(f"FHIR not available - skipping patient {patient.id} sync")
            await self.update_sync_status(
                patient.id, "patient", status="failed", 
                errors=["FHIR server not available"]
            )
            return FHIRSyncResponse(success=False, errors=["FHIR server not available"])
        
        # Check if already synced recently (unless forced)
        if not force_sync:
            sync_status = await self.get_sync_status(patient.id, "patient")
            if sync_status and sync_status.sync_status == "synced":
                time_since_sync = datetime.utcnow() - sync_status.last_sync
                if time_since_sync.total_seconds() < 300:  # 5 minutes
                    logger.debug(f"Skipping recent sync for patient {patient.id}")
                    return FHIRSyncResponse(success=True, fhir_id=sync_status.fhir_id)
        
        try:
            # Attempt synchronization
            sync_response = await fhir_repository.sync_patient_data(patient)
            
            # Update sync status
            await self.update_sync_status(
                patient.id, 
                "patient",
                fhir_id=sync_response.fhir_id,
                status="synced" if sync_response.success else "failed",
                errors=sync_response.errors
            )
            
            if sync_response.success:
                logger.info(f"Successfully synced patient {patient.id} to FHIR: {sync_response.fhir_id}")
            else:
                logger.error(f"Failed to sync patient {patient.id} to FHIR: {sync_response.errors}")
            
            return sync_response
            
        except Exception as e:
            logger.error(f"Unexpected error syncing patient {patient.id}: {e}")
            await self.update_sync_status(
                patient.id, "patient", status="failed", errors=[str(e)]
            )
            return FHIRSyncResponse(success=False, errors=[str(e)])
    
    async def sync_encounter(
        self, 
        encounter: EncounterModel, 
        force_sync: bool = False
    ) -> FHIRSyncResponse:
        """Synchronize encounter with FHIR server"""
        strategy = self.get_sync_strategy("encounter")
        
        # Skip if strategy doesn't involve FHIR
        if strategy == SyncStrategy.MONGODB_ONLY:
            logger.debug(f"Skipping FHIR sync for encounter {encounter.id} - MongoDB only strategy")
            return FHIRSyncResponse(success=True, errors=["Skipped - MongoDB only strategy"])
        
        # Only sync signed encounters (completed clinical documentation)
        if encounter.status != EncounterStatusEnum.SIGNED and not force_sync:
            logger.debug(f"Skipping FHIR sync for encounter {encounter.id} - not signed")
            return FHIRSyncResponse(success=True, errors=["Skipped - encounter not signed"])
        
        # Check if FHIR is available
        if not fhir_repository.is_available():
            logger.warning(f"FHIR not available - skipping encounter {encounter.id} sync")
            await self.update_sync_status(
                encounter.id, "encounter", status="failed", 
                errors=["FHIR server not available"]
            )
            return FHIRSyncResponse(success=False, errors=["FHIR server not available"])
        
        try:
            # Get patient to find FHIR ID
            patient = await patient_repository.get_by_id(encounter.patient_id)
            if not patient:
                error_msg = f"Patient {encounter.patient_id} not found for encounter {encounter.id}"
                logger.error(error_msg)
                return FHIRSyncResponse(success=False, errors=[error_msg])
            
            # Ensure patient is synced first
            patient_sync = await self.sync_patient(patient, force_sync=False)
            if not patient_sync.success or not patient_sync.fhir_id:
                error_msg = f"Patient {patient.id} not synced to FHIR - cannot sync encounter"
                logger.error(error_msg)
                return FHIRSyncResponse(success=False, errors=[error_msg])
            
            # Check if already synced recently (unless forced)
            if not force_sync:
                sync_status = await self.get_sync_status(encounter.id, "encounter")
                if sync_status and sync_status.sync_status == "synced":
                    time_since_sync = datetime.utcnow() - sync_status.last_sync
                    if time_since_sync.total_seconds() < 300:  # 5 minutes
                        logger.debug(f"Skipping recent sync for encounter {encounter.id}")
                        return FHIRSyncResponse(success=True, fhir_id=sync_status.fhir_id)
            
            # Attempt synchronization
            sync_response = await fhir_repository.sync_encounter_data(encounter, patient_sync.fhir_id)
            
            # Update sync status
            await self.update_sync_status(
                encounter.id, 
                "encounter",
                fhir_id=sync_response.fhir_id,
                status="synced" if sync_response.success else "failed",
                errors=sync_response.errors
            )
            
            if sync_response.success:
                logger.info(f"Successfully synced encounter {encounter.id} to FHIR: {sync_response.fhir_id}")
            else:
                logger.error(f"Failed to sync encounter {encounter.id} to FHIR: {sync_response.errors}")
            
            return sync_response
            
        except Exception as e:
            logger.error(f"Unexpected error syncing encounter {encounter.id}: {e}")
            await self.update_sync_status(
                encounter.id, "encounter", status="failed", errors=[str(e)]
            )
            return FHIRSyncResponse(success=False, errors=[str(e)])
    
    async def auto_sync_on_encounter_sign(self, encounter_id: str) -> FHIRSyncResponse:
        """Automatically sync encounter when it's signed"""
        try:
            encounter = await encounter_repository.get_by_id(encounter_id)
            if not encounter:
                error_msg = f"Encounter {encounter_id} not found"
                logger.error(error_msg)
                return FHIRSyncResponse(success=False, errors=[error_msg])
            
            # Only auto-sync if encounter is signed
            if encounter.status == EncounterStatusEnum.SIGNED:
                logger.info(f"Auto-syncing signed encounter {encounter_id} to FHIR")
                return await self.sync_encounter(encounter, force_sync=True)
            else:
                return FHIRSyncResponse(
                    success=True, 
                    errors=["Skipped - encounter not signed"]
                )
                
        except Exception as e:
            logger.error(f"Error in auto-sync for encounter {encounter_id}: {e}")
            return FHIRSyncResponse(success=False, errors=[str(e)])
    
    # Bulk operations
    
    async def sync_all_patients(
        self, 
        force_sync: bool = False,
        max_patients: int = 100
    ) -> Dict[str, Any]:
        """Sync all patients to FHIR"""
        logger.info(f"Starting bulk patient sync (max: {max_patients}, force: {force_sync})")
        
        try:
            patients = await patient_repository.get_all(limit=max_patients)
            
            results = {
                "total": len(patients),
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "errors": []
            }
            
            for patient in patients:
                try:
                    sync_response = await self.sync_patient(patient, force_sync)
                    if sync_response.success:
                        if sync_response.errors and "Skipped" in str(sync_response.errors):
                            results["skipped"] += 1
                        else:
                            results["success"] += 1
                    else:
                        results["failed"] += 1
                        if sync_response.errors:
                            results["errors"].extend(sync_response.errors)
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Patient {patient.id}: {str(e)}")
                    logger.error(f"Error syncing patient {patient.id}: {e}")
            
            logger.info(f"Bulk patient sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk patient sync: {e}")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "errors": [str(e)]
            }
    
    async def sync_all_signed_encounters(
        self, 
        force_sync: bool = False,
        max_encounters: int = 100
    ) -> Dict[str, Any]:
        """Sync all signed encounters to FHIR"""
        logger.info(f"Starting bulk signed encounter sync (max: {max_encounters}, force: {force_sync})")
        
        try:
            # Get signed encounters
            encounters = await encounter_repository.get_by_status(
                EncounterStatusEnum.SIGNED, 
                limit=max_encounters
            )
            
            results = {
                "total": len(encounters),
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "errors": []
            }
            
            for encounter in encounters:
                try:
                    sync_response = await self.sync_encounter(encounter, force_sync)
                    if sync_response.success:
                        if sync_response.errors and "Skipped" in str(sync_response.errors):
                            results["skipped"] += 1
                        else:
                            results["success"] += 1
                    else:
                        results["failed"] += 1
                        if sync_response.errors:
                            results["errors"].extend(sync_response.errors)
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Encounter {encounter.id}: {str(e)}")
                    logger.error(f"Error syncing encounter {encounter.id}: {e}")
            
            logger.info(f"Bulk encounter sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk encounter sync: {e}")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "errors": [str(e)]
            }
    
    # Status and monitoring
    
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        stats = {
            "total_entities": len(self._sync_status),
            "by_entity_type": {},
            "by_status": {},
            "recent_syncs": 0,
            "failed_syncs": 0
        }
        
        now = datetime.utcnow()
        recent_threshold = 3600  # 1 hour
        
        for sync_status in self._sync_status.values():
            # Count by entity type
            entity_type = sync_status.entity_type
            if entity_type not in stats["by_entity_type"]:
                stats["by_entity_type"][entity_type] = 0
            stats["by_entity_type"][entity_type] += 1
            
            # Count by status
            status = sync_status.sync_status
            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += 1
            
            # Count recent syncs
            if sync_status.last_sync:
                time_since_sync = (now - sync_status.last_sync).total_seconds()
                if time_since_sync < recent_threshold:
                    stats["recent_syncs"] += 1
            
            # Count failed syncs
            if status == "failed":
                stats["failed_syncs"] += 1
        
        return stats
    
    async def get_failed_syncs(self) -> List[FHIRSyncStatus]:
        """Get all failed synchronizations"""
        failed_syncs = []
        for sync_status in self._sync_status.values():
            if sync_status.sync_status == "failed":
                failed_syncs.append(sync_status)
        
        return failed_syncs
    
    async def retry_failed_syncs(self) -> Dict[str, Any]:
        """Retry all failed synchronizations"""
        failed_syncs = await self.get_failed_syncs()
        
        results = {
            "total_retries": len(failed_syncs),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for sync_status in failed_syncs:
            try:
                if sync_status.entity_type == "patient":
                    patient = await patient_repository.get_by_id(sync_status.entity_id)
                    if patient:
                        sync_response = await self.sync_patient(patient, force_sync=True)
                        if sync_response.success:
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                            if sync_response.errors:
                                results["errors"].extend(sync_response.errors)
                
                elif sync_status.entity_type == "encounter":
                    encounter = await encounter_repository.get_by_id(sync_status.entity_id)
                    if encounter:
                        sync_response = await self.sync_encounter(encounter, force_sync=True)
                        if sync_response.success:
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                            if sync_response.errors:
                                results["errors"].extend(sync_response.errors)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{sync_status.entity_type}:{sync_status.entity_id}: {str(e)}")
        
        logger.info(f"Retry failed syncs completed: {results}")
        return results
    
    async def test_fhir_connectivity(self) -> Dict[str, Any]:
        """Test FHIR server connectivity and capabilities"""
        result = {
            "available": False,
            "connection": False,
            "capabilities": None,
            "error": None
        }
        
        try:
            # Check if FHIR repository is available
            result["available"] = fhir_repository.is_available()
            
            if result["available"]:
                # Test connection
                result["connection"] = await fhir_repository.test_connection()
                
                # Get capability statement
                result["capabilities"] = await fhir_repository.get_capability_statement()
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error testing FHIR connectivity: {e}")
        
        return result


# Create service instance
fhir_sync_service = FHIRSyncService()