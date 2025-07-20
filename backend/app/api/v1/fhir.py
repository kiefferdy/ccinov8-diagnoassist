"""
FHIR API endpoints for DiagnoAssist Backend
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime

from app.models.auth import CurrentUser
from app.models.fhir_models import FHIRSyncRequest, FHIRSyncResponse, FHIRSyncStatus
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.fhir_sync_service import fhir_sync_service, SyncStrategy
from app.repositories.patient_repository import patient_repository
from app.repositories.encounter_repository import encounter_repository
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.get("/status")
async def get_fhir_status(current_user: CurrentUser = Depends(get_current_user)):
    """Get FHIR server status and connectivity"""
    try:
        status_info = await fhir_sync_service.test_fhir_connectivity()
        sync_stats = await fhir_sync_service.get_sync_statistics()
        
        return {
            "success": True,
            "data": {
                "fhir_server": status_info,
                "sync_statistics": sync_stats,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FHIR status: {str(e)}"
        )


@router.get("/sync/statistics")
async def get_sync_statistics(admin_user: CurrentUser = Depends(require_admin)):
    """Get detailed synchronization statistics (admin only)"""
    try:
        stats = await fhir_sync_service.get_sync_statistics()
        failed_syncs = await fhir_sync_service.get_failed_syncs()
        
        return {
            "success": True,
            "data": {
                "statistics": stats,
                "failed_syncs_count": len(failed_syncs),
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync statistics: {str(e)}"
        )


@router.get("/sync/failed")
async def get_failed_syncs(admin_user: CurrentUser = Depends(require_admin)):
    """Get all failed synchronizations (admin only)"""
    try:
        failed_syncs = await fhir_sync_service.get_failed_syncs()
        
        return {
            "success": True,
            "data": {
                "failed_syncs": failed_syncs,
                "total": len(failed_syncs),
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get failed syncs: {str(e)}"
        )


@router.post("/sync/patient/{patient_id}")
async def sync_patient(
    patient_id: str,
    force_sync: bool = Query(False, description="Force synchronization even if recently synced"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Sync a specific patient to FHIR"""
    try:
        # Get patient
        patient = await patient_repository.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        
        # Sync patient
        sync_response = await fhir_sync_service.sync_patient(patient, force_sync)
        
        return {
            "success": True,
            "data": {
                "patient_id": patient_id,
                "sync_result": sync_response,
                "timestamp": datetime.utcnow()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync patient: {str(e)}"
        )


@router.post("/sync/encounter/{encounter_id}")
async def sync_encounter(
    encounter_id: str,
    force_sync: bool = Query(False, description="Force synchronization even if recently synced"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Sync a specific encounter to FHIR"""
    try:
        # Get encounter
        encounter = await encounter_repository.get_by_id(encounter_id)
        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Encounter {encounter_id} not found"
            )
        
        # Sync encounter
        sync_response = await fhir_sync_service.sync_encounter(encounter, force_sync)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "sync_result": sync_response,
                "timestamp": datetime.utcnow()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync encounter: {str(e)}"
        )


@router.post("/sync/bulk/patients")
async def bulk_sync_patients(
    force_sync: bool = Query(False, description="Force synchronization for all patients"),
    max_patients: int = Query(100, ge=1, le=1000, description="Maximum number of patients to sync"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """Bulk sync all patients to FHIR (admin only)"""
    try:
        results = await fhir_sync_service.sync_all_patients(force_sync, max_patients)
        
        return {
            "success": True,
            "data": {
                "bulk_sync_results": results,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk sync patients: {str(e)}"
        )


@router.post("/sync/bulk/encounters")
async def bulk_sync_encounters(
    force_sync: bool = Query(False, description="Force synchronization for all signed encounters"),
    max_encounters: int = Query(100, ge=1, le=1000, description="Maximum number of encounters to sync"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """Bulk sync all signed encounters to FHIR (admin only)"""
    try:
        results = await fhir_sync_service.sync_all_signed_encounters(force_sync, max_encounters)
        
        return {
            "success": True,
            "data": {
                "bulk_sync_results": results,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk sync encounters: {str(e)}"
        )


@router.post("/sync/retry-failed")
async def retry_failed_syncs(admin_user: CurrentUser = Depends(require_admin)):
    """Retry all failed synchronizations (admin only)"""
    try:
        results = await fhir_sync_service.retry_failed_syncs()
        
        return {
            "success": True,
            "data": {
                "retry_results": results,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry failed syncs: {str(e)}"
        )


@router.get("/sync/status/{entity_type}/{entity_id}")
async def get_entity_sync_status(
    entity_type: str,
    entity_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get synchronization status for a specific entity"""
    try:
        # Validate entity type
        if entity_type not in ["patient", "encounter", "episode"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity type: {entity_type}"
            )
        
        sync_status = await fhir_sync_service.get_sync_status(entity_id, entity_type)
        
        return {
            "success": True,
            "data": {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "sync_status": sync_status,
                "timestamp": datetime.utcnow()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )


@router.get("/strategies")
async def get_sync_strategies(admin_user: CurrentUser = Depends(require_admin)):
    """Get current synchronization strategies for all entity types (admin only)"""
    try:
        strategies = {
            "patient": fhir_sync_service.get_sync_strategy("patient"),
            "encounter": fhir_sync_service.get_sync_strategy("encounter"),
            "episode": fhir_sync_service.get_sync_strategy("episode")
        }
        
        available_strategies = [strategy.value for strategy in SyncStrategy]
        
        return {
            "success": True,
            "data": {
                "current_strategies": strategies,
                "available_strategies": available_strategies,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync strategies: {str(e)}"
        )


@router.post("/strategies/{entity_type}")
async def set_sync_strategy(
    entity_type: str,
    strategy: SyncStrategy,
    admin_user: CurrentUser = Depends(require_admin)
):
    """Set synchronization strategy for an entity type (admin only)"""
    try:
        # Validate entity type
        if entity_type not in ["patient", "encounter", "episode"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity type: {entity_type}"
            )
        
        fhir_sync_service.set_sync_strategy(entity_type, strategy)
        
        return {
            "success": True,
            "data": {
                "entity_type": entity_type,
                "strategy": strategy,
                "message": f"Sync strategy for {entity_type} set to {strategy}",
                "timestamp": datetime.utcnow()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set sync strategy: {str(e)}"
        )


@router.post("/test-connection")
async def test_fhir_connection(current_user: CurrentUser = Depends(get_current_user)):
    """Test FHIR server connection"""
    try:
        connection_test = await fhir_sync_service.test_fhir_connectivity()
        
        return {
            "success": True,
            "data": {
                "connection_test": connection_test,
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test FHIR connection: {str(e)}"
        )


@router.get("/capabilities")
async def get_fhir_capabilities(current_user: CurrentUser = Depends(get_current_user)):
    """Get FHIR server capability statement"""
    try:
        from app.repositories.fhir_repository import fhir_repository
        
        capabilities = await fhir_repository.get_capability_statement()
        
        return {
            "success": True,
            "data": {
                "capabilities": capabilities,
                "available": fhir_repository.is_available(),
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FHIR capabilities: {str(e)}"
        )