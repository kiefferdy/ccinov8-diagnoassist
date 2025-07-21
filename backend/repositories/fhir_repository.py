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
            limit: Maximum number of records
            
        Returns:
            List of FHIR resources with matching type
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == resource_type
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources by type {resource_type}: {str(e)}")
            return []
    
    def get_by_fhir_id(self, fhir_id: str, resource_type: Optional[str] = None) -> Optional[FHIRResource]:
        """
        Get FHIR resource by FHIR ID
        
        Args:
            fhir_id: FHIR resource ID
            resource_type: Optional resource type for more specific search
            
        Returns:
            FHIR resource or None if not found
        """
        try:
            query = self.db.query(FHIRResource).filter(FHIRResource.fhir_id == fhir_id)
            
            if resource_type:
                query = query.filter(FHIRResource.resource_type == resource_type)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource by ID {fhir_id}: {str(e)}")
            return None
    
    def get_by_patient_reference(self, patient_id: Union[UUID, str], skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get FHIR resources that reference a specific patient
        
        Args:
            patient_id: Patient ID (can be UUID or FHIR ID)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of FHIR resources referencing the patient
        """
        try:
            # Search in the JSON content for patient references
            # This is a simplified approach - in practice, you might want more sophisticated JSON querying
            patient_ref_patterns = [
                f'"patient": "{patient_id}"',
                f'"subject": "{patient_id}"',
                f'"Patient/{patient_id}"'
            ]
            
            query = self.db.query(FHIRResource)
            
            for pattern in patient_ref_patterns:
                query = query.filter(
                    FHIRResource.content.contains(pattern)
                )
            
            return query.order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_version(self, fhir_id: str, version: int) -> Optional[FHIRResource]:
        """
        Get specific version of a FHIR resource
        
        Args:
            fhir_id: FHIR resource ID
            version: Version number
            
        Returns:
            FHIR resource version or None if not found
        """
        try:
            return self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.fhir_id == fhir_id,
                    FHIRResource.version == version
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource {fhir_id} version {version}: {str(e)}")
            return None
    
    def get_latest_version(self, fhir_id: str) -> Optional[FHIRResource]:
        """
        Get latest version of a FHIR resource
        
        Args:
            fhir_id: FHIR resource ID
            
        Returns:
            Latest version of FHIR resource or None if not found
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.fhir_id == fhir_id
            ).order_by(desc(FHIRResource.version)).first()
            
        except Exception as e:
            logger.error(f"Error getting latest version of FHIR resource {fhir_id}: {str(e)}")
            return None
    
    def get_all_versions(self, fhir_id: str) -> List[FHIRResource]:
        """
        Get all versions of a FHIR resource
        
        Args:
            fhir_id: FHIR resource ID
            
        Returns:
            List of all versions of the FHIR resource
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.fhir_id == fhir_id
            ).order_by(desc(FHIRResource.version)).all()
            
        except Exception as e:
            logger.error(f"Error getting all versions of FHIR resource {fhir_id}: {str(e)}")
            return []
    
    def search_by_content(self, search_term: str, resource_type: Optional[str] = None, 
                         limit: int = 50) -> List[FHIRResource]:
        """
        Search FHIR resources by content
        
        Args:
            search_term: Term to search for in JSON content
            resource_type: Optional resource type filter
            limit: Maximum number of results
            
        Returns:
            List of FHIR resources containing the search term
        """
        try:
            query = self.db.query(FHIRResource).filter(
                FHIRResource.content.contains(search_term)
            )
            
            if resource_type:
                query = query.filter(FHIRResource.resource_type == resource_type)
            
            return query.order_by(desc(FHIRResource.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching FHIR resources by content '{search_term}': {str(e)}")
            return []
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[FHIRResource]:
        """
        Get FHIR resources by status
        
        Args:
            status: Status (active, inactive, deleted)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of FHIR resources with matching status
        """
        try:
            return self.db.query(FHIRResource).filter(
                FHIRResource.status == status
            ).order_by(desc(FHIRResource.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting FHIR resources by status {status}: {str(e)}")
            return []
    
    def create_new_version(self, fhir_id: str, content: Dict[str, Any], 
                          status: str = "active") -> Optional[FHIRResource]:
        """
        Create a new version of an existing FHIR resource
        
        Args:
            fhir_id: FHIR resource ID
            content: New FHIR resource content
            status: Resource status
            
        Returns:
            New version of FHIR resource or None if failed
        """
        try:
            # Get the latest version number
            latest = self.get_latest_version(fhir_id)
            next_version = (latest.version + 1) if latest else 1
            
            # Extract resource type from content
            resource_type = content.get("resourceType", "Unknown")
            
            new_resource_data = {
                "fhir_id": fhir_id,
                "resource_type": resource_type,
                "version": next_version,
                "content": content,
                "status": status
            }
            
            return self.create(new_resource_data)
            
        except Exception as e:
            logger.error(f"Error creating new version of FHIR resource {fhir_id}: {str(e)}")
            return None
    
    def soft_delete(self, fhir_id: str) -> bool:
        """
        Soft delete a FHIR resource (set status to deleted)
        
        Args:
            fhir_id: FHIR resource ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            latest = self.get_latest_version(fhir_id)
            if not latest:
                return False
            
            # Create a new version with deleted status
            deleted_content = latest.content.copy()
            deleted_content["status"] = "deleted"
            
            deleted_resource = self.create_new_version(fhir_id, deleted_content, "deleted")
            return deleted_resource is not None
            
        except Exception as e:
            logger.error(f"Error soft deleting FHIR resource {fhir_id}: {str(e)}")
            return False
    
    def restore(self, fhir_id: str, content: Optional[Dict[str, Any]] = None) -> Optional[FHIRResource]:
        """
        Restore a deleted FHIR resource
        
        Args:
            fhir_id: FHIR resource ID
            content: Optional new content (uses latest active version if not provided)
            
        Returns:
            Restored FHIR resource or None if failed
        """
        try:
            if content is None:
                # Find the latest active version
                active_versions = self.db.query(FHIRResource).filter(
                    and_(
                        FHIRResource.fhir_id == fhir_id,
                        FHIRResource.status == "active"
                    )
                ).order_by(desc(FHIRResource.version)).first()
                
                if not active_versions:
                    logger.error(f"No active version found for FHIR resource {fhir_id}")
                    return None
                
                content = active_versions.content.copy()
            
            # Ensure status is active in content
            content["status"] = "active"
            
            return self.create_new_version(fhir_id, content, "active")
            
        except Exception as e:
            logger.error(f"Error restoring FHIR resource {fhir_id}: {str(e)}")
            return None
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """
        Get FHIR resource statistics
        
        Returns:
            Dictionary with FHIR resource statistics
        """
        try:
            total_resources = self.count()
            
            type_stats = self.db.query(
                FHIRResource.resource_type,
                func.count(FHIRResource.id).label('count')
            ).group_by(FHIRResource.resource_type).all()
            
            status_stats = self.db.query(
                FHIRResource.status,
                func.count(FHIRResource.id).label('count')
            ).group_by(FHIRResource.status).all()
            
            # Count unique FHIR IDs (actual resources vs versions)
            unique_resources = self.db.query(
                func.count(func.distinct(FHIRResource.fhir_id))
            ).scalar()
            
            return {
                "total_resource_versions": total_resources,
                "unique_resources": unique_resources,
                "type_distribution": {stat.resource_type: stat.count for stat in type_stats},
                "status_distribution": {stat.status: stat.count for stat in status_stats},
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting FHIR resource statistics: {str(e)}")
            return {}
    
    def validate_fhir_content(self, content: Dict[str, Any]) -> bool:
        """
        Basic validation of FHIR resource content
        
        Args:
            content: FHIR resource content to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic FHIR validation - in production, use a proper FHIR validator
            required_fields = ["resourceType"]
            
            for field in required_fields:
                if field not in content:
                    logger.error(f"Missing required FHIR field: {field}")
                    return False
            
            # Additional validation can be added here
            return True
            
        except Exception as e:
            logger.error(f"Error validating FHIR content: {str(e)}")
            return False
    
    def search_by_json_path(self, json_path: str, value: Any, 
                           resource_type: Optional[str] = None) -> List[FHIRResource]:
        """
        Search FHIR resources by JSON path
        
        Args:
            json_path: JSON path to search (e.g., "$.patient.reference")
            value: Value to search for
            resource_type: Optional resource type filter
            
        Returns:
            List of matching FHIR resources
        """
        try:
            # This uses PostgreSQL's JSON path functions
            # The exact syntax may vary depending on your PostgreSQL version
            query = self.db.query(FHIRResource).filter(
                text(f"jsonb_extract_path_text(content, '{json_path}') = :value")
            ).params(value=str(value))
            
            if resource_type:
                query = query.filter(FHIRResource.resource_type == resource_type)
            
            return query.order_by(desc(FHIRResource.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error searching by JSON path {json_path}: {str(e)}")
            return []