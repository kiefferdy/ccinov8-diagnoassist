"""
FHIR Resource Repository for DiagnoAssist
Specialized CRUD operations for FHIR Resource model
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from datetime import datetime, date, timedelta
from uuid import UUID
import logging
import json

from models.fhir_resource import FHIRResource
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class FHIRResourceRepository(BaseRepository[FHIRResource]):
    """
    Repository for FHIR Resource model with specialized operations
    """
    
    def __init__(self, db: Session):
        super().__init__(FHIRResource, db)
    
    def get_by_resource_type(self, resource_type: str, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get FHIR resources by type
        
        Args:
            resource_type: FHIR resource type (Patient, Observation, DiagnosticReport, etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of FHIR resources of the specified type
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == resource_type
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources by type {resource_type}: {str(e)}")
            return []
    
    def get_by_resource_id(self, resource_id: str) -> Optional[FHIRResource]:
        """
        Get FHIR resource by its resource_id
        
        Args:
            resource_id: FHIR resource identifier
            
        Returns:
            FHIR resource or None if not found
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.resource_id == resource_id
            ).order_by(desc(FHIRResource.last_updated)).first()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource by resource_id {resource_id}: {str(e)}")
            return None
    
    def get_by_patient_reference(self, patient_reference: str, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get FHIR resources by patient reference
        
        Args:
            patient_reference: Patient reference (e.g., "Patient/123")
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of FHIR resources for the patient
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.patient_reference == patient_reference
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources for patient {patient_reference}: {str(e)}")
            return []
    
    def get_by_encounter_reference(self, encounter_reference: str, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get FHIR resources by encounter reference
        
        Args:
            encounter_reference: Encounter reference (e.g., "Encounter/456")
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of FHIR resources for the encounter
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.encounter_reference == encounter_reference
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources for encounter {encounter_reference}: {str(e)}")
            return []
    
    def search_by_fhir_data(self, search_criteria: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Search FHIR resources by JSON content using PostgreSQL JSON operators
        Note: fhir_data is stored as TEXT, so we cast to JSONB for searching
        
        Args:
            search_criteria: Dictionary of search criteria for JSON fields
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching FHIR resources
        """
        try:
            query = self.db.query(FHIRResource)
            
            for key, value in search_criteria.items():
                if isinstance(value, str):
                    # Use PostgreSQL TEXT search with JSONB casting for string values
                    query = query.filter(
                        text(f"(fhir_data::jsonb->>{repr(key)}) ILIKE :pattern_{key}")
                    ).params(**{f"pattern_{key}": f'%{value}%'})
                elif isinstance(value, dict):
                    # Use JSONB containment for nested objects
                    query = query.filter(
                        text("fhir_data::jsonb @> :criteria")
                    ).params(criteria=json.dumps({key: value}))
                else:
                    # Use exact match for other types
                    query = query.filter(
                        text(f"(fhir_data::jsonb->>{repr(key)}) = :value_{key}")
                    ).params(**{f"value_{key}": str(value)})
            
            return query.order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching FHIR resources by data: {str(e)}")
            return []
    
    def get_active_resources(self, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get active FHIR resources
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active FHIR resources
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.status == "active"
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting active FHIR resources: {str(e)}")
            return []
    
    def get_by_version(self, resource_id: str, version_id: str) -> Optional[FHIRResource]:
        """
        Get specific version of a FHIR resource
        
        Args:
            resource_id: FHIR resource ID
            version_id: Version identifier
            
        Returns:
            FHIR resource version or None if not found
        """
        try:
            return self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_id == resource_id,
                    FHIRResource.version_id == version_id
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource {resource_id} version {version_id}: {str(e)}")
            return None
    
    def get_latest_version(self, resource_id: str) -> Optional[FHIRResource]:
        """
        Get latest version of a FHIR resource
        
        Args:
            resource_id: FHIR resource ID
            
        Returns:
            Latest version of FHIR resource or None if not found
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.resource_id == resource_id
            ).order_by(desc(FHIRResource.version_id)).first()
            
        except Exception as e:
            logger.error(f"Error getting latest version of FHIR resource {resource_id}: {str(e)}")
            return None
    
    def get_all_versions(self, resource_id: str) -> List[FHIRResource]:
        """
        Get all versions of a FHIR resource
        
        Args:
            resource_id: FHIR resource ID
            
        Returns:
            List of all versions of the FHIR resource
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.resource_id == resource_id
            ).order_by(desc(FHIRResource.version_id)).all()
            
        except Exception as e:
            logger.error(f"Error getting all versions of FHIR resource {resource_id}: {str(e)}")
            return []
    
    def mark_as_inactive(self, resource_id: str) -> bool:
        """
        Mark a FHIR resource as inactive
        
        Args:
            resource_id: FHIR resource ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fhir_resource = self.get_by_resource_id(resource_id)
            if not fhir_resource:
                return False
            
            fhir_resource.status = "inactive"
            fhir_resource.last_updated = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking FHIR resource {resource_id} as inactive: {str(e)}")
            self.db.rollback()
            return False
    
    def delete_resource(self, resource_id: str) -> bool:
        """
        Soft delete a FHIR resource by marking as deleted
        
        Args:
            resource_id: FHIR resource ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fhir_resource = self.get_by_resource_id(resource_id)
            if not fhir_resource:
                return False
            
            fhir_resource.status = "deleted"
            fhir_resource.last_updated = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting FHIR resource {resource_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def count_by_resource_type(self, resource_type: str) -> int:
        """
        Count FHIR resources by type
        
        Args:
            resource_type: FHIR resource type
            
        Returns:
            Number of resources of the specified type
        """
        try:
            return self.db.query(func.count(FHIRResource.id)).filter(
                FHIRResource.resource_type == resource_type
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting FHIR resources of type {resource_type}: {str(e)}")
            return 0
    
    def count_by_patient(self, patient_reference: str) -> int:
        """
        Count FHIR resources for a specific patient
        
        Args:
            patient_reference: Patient reference (e.g., "Patient/123")
            
        Returns:
            Number of resources for the patient
        """
        try:
            return self.db.query(func.count(FHIRResource.id)).filter(
                FHIRResource.patient_reference == patient_reference
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting FHIR resources for patient {patient_reference}: {str(e)}")
            return 0
    
    def get_resource_types(self) -> List[str]:
        """
        Get all unique resource types in the database
        
        Returns:
            List of unique FHIR resource types
        """
        try:
            result = self.db.query(FHIRResource.resource_type).distinct().all()
            return [row[0] for row in result]
            
        except Exception as e:
            logger.error(f"Error getting resource types: {str(e)}")
            return []
    
    def create_from_fhir_dict(self, fhir_dict: Dict[str, Any], resource_id: Optional[str] = None) -> Optional[FHIRResource]:
        """
        Create FHIR resource from FHIR dictionary
        
        Args:
            fhir_dict: FHIR resource as dictionary
            resource_id: Optional resource ID (will generate if not provided)
            
        Returns:
            Created FHIRResource or None if failed
        """
        try:
            fhir_resource = FHIRResource.create_from_fhir_resource(fhir_dict, resource_id)
            self.db.add(fhir_resource)
            self.db.commit()
            self.db.refresh(fhir_resource)
            return fhir_resource
            
        except Exception as e:
            logger.error(f"Error creating FHIR resource from dict: {str(e)}")
            self.db.rollback()
            return None
    
    def update_fhir_data(self, resource_id: str, fhir_dict: Dict[str, Any]) -> Optional[FHIRResource]:
        """
        Update FHIR resource data and increment version
        
        Args:
            resource_id: FHIR resource ID
            fhir_dict: Updated FHIR resource as dictionary
            
        Returns:
            Updated FHIRResource or None if failed
        """
        try:
            fhir_resource = self.get_by_resource_id(resource_id)
            if not fhir_resource:
                return None
            
            fhir_resource.update_fhir_data(fhir_dict)
            self.db.commit()
            self.db.refresh(fhir_resource)
            return fhir_resource
            
        except Exception as e:
            logger.error(f"Error updating FHIR resource {resource_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def search_by_code(self, code_system: str, code: str, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Search FHIR resources by coding system and code
        
        Args:
            code_system: Coding system URI
            code: Code value
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching FHIR resources
        """
        try:
            # Search for resources containing the specified code in their coding arrays
            # Cast TEXT to JSONB for searching
            query = self.db.query(FHIRResource).filter(
                text("fhir_data::jsonb @> :search_pattern")
            ).params(
                search_pattern=json.dumps({
                    "code": {
                        "coding": [{"system": code_system, "code": code}]
                    }
                })
            )
            
            return query.order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching FHIR resources by code {code_system}#{code}: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get FHIR resource statistics
        
        Returns:
            Dictionary with FHIR resource statistics
        """
        try:
            total_resources = self.db.query(func.count(FHIRResource.id)).scalar()
            active_resources = self.db.query(func.count(FHIRResource.id)).filter(
                FHIRResource.status == "active"
            ).scalar()
            
            # Count by resource type
            type_counts = self.db.query(
                FHIRResource.resource_type,
                func.count(FHIRResource.id)
            ).group_by(FHIRResource.resource_type).all()
            
            type_distribution = {resource_type: count for resource_type, count in type_counts}
            
            return {
                "total_resources": total_resources or 0,
                "active_resources": active_resources or 0,
                "inactive_resources": (total_resources or 0) - (active_resources or 0),
                "resource_type_distribution": type_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource statistics: {str(e)}")
            return {}