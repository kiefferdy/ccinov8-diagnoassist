from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.bundle import Bundle
from models.fhir_resource import FHIRResource
from .base import BaseRepository
import json
import logging

logger = logging.getLogger(__name__)

class FHIRPatientRepository:
    """
    Repository for FHIR Patient resource operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fhir_patient(self, fhir_patient: FHIRPatient) -> FHIRPatient:
        """
        Store FHIR Patient resource
        
        Args:
            fhir_patient: FHIR Patient resource
            
        Returns:
            Stored FHIR Patient resource
        """
        try:
            fhir_resource = FHIRResource(
                resource_type="Patient",
                resource_id=fhir_patient.id,
                fhir_data=fhir_patient.dict(),
                version_id="1"
            )
            
            self.db.add(fhir_resource)
            self.db.commit()
            self.db.refresh(fhir_resource)
            
            logger.info(f"Created FHIR Patient resource: {fhir_patient.id}")
            return FHIRPatient(**fhir_resource.fhir_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating FHIR Patient: {str(e)}")
            raise
    
    def get_fhir_patient(self, patient_id: str) -> Optional[FHIRPatient]:
        """
        Get FHIR Patient resource by ID
        
        Args:
            patient_id: Patient resource ID
            
        Returns:
            FHIR Patient resource or None
        """
        try:
            fhir_resource = self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_type == "Patient",
                    FHIRResource.resource_id == patient_id
                )
            ).order_by(desc(FHIRResource.version_id)).first()
            
            if fhir_resource:
                return FHIRPatient(**fhir_resource.fhir_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting FHIR Patient {patient_id}: {str(e)}")
            raise
    
    def update_fhir_patient(self, patient_id: str, fhir_patient: FHIRPatient) -> Optional[FHIRPatient]:
        """
        Update FHIR Patient resource
        
        Args:
            patient_id: Patient resource ID
            fhir_patient: Updated FHIR Patient resource
            
        Returns:
            Updated FHIR Patient resource or None
        """
        try:
            # Get current version
            current_resource = self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_type == "Patient",
                    FHIRResource.resource_id == patient_id
                )
            ).order_by(desc(FHIRResource.version_id)).first()
            
            if not current_resource:
                return None
            
            # Create new version
            new_version_id = str(int(current_resource.version_id) + 1)
            
            new_resource = FHIRResource(
                resource_type="Patient",
                resource_id=patient_id,
                fhir_data=fhir_patient.dict(),
                version_id=new_version_id
            )
            
            self.db.add(new_resource)
            self.db.commit()
            self.db.refresh(new_resource)
            
            logger.info(f"Updated FHIR Patient resource: {patient_id} (version {new_version_id})")
            return FHIRPatient(**new_resource.fhir_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating FHIR Patient {patient_id}: {str(e)}")
            raise
    
    def search_fhir_patients(self, search_params: Dict[str, Any]) -> Bundle:
        """
        Search FHIR Patient resources
        
        Args:
            search_params: FHIR search parameters
            
        Returns:
            FHIR Bundle with search results
        """
        try:
            # Basic implementation - would need to be expanded for full FHIR search
            query = self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == "Patient"
            )
            
            # Apply search parameters
            # This is a simplified implementation
            results = query.limit(search_params.get('_count', 20)).all()
            
            # Create FHIR Bundle
            bundle = Bundle()
            bundle.type = "searchset"
            bundle.total = len(results)
            bundle.entry = []
            
            for result in results:
                entry = {
                    "resource": result.fhir_data,
                    "search": {"mode": "match"}
                }
                bundle.entry.append(entry)
            
            return bundle
            
        except Exception as e:
            logger.error(f"Error searching FHIR Patients: {str(e)}")
            raise
    
    def delete_fhir_patient(self, patient_id: str) -> bool:
        """
        Delete FHIR Patient resource (soft delete by marking as inactive)
        
        Args:
            patient_id: Patient resource ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            fhir_resource = self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_type == "Patient",
                    FHIRResource.resource_id == patient_id
                )
            ).order_by(desc(FHIRResource.version_id)).first()
            
            if not fhir_resource:
                return False
            
            # Mark patient as inactive instead of hard delete
            patient_data = fhir_resource.fhir_data.copy()
            patient_data['active'] = False
            
            # Create new version with inactive status
            new_version_id = str(int(fhir_resource.version_id) + 1)
            
            new_resource = FHIRResource(
                resource_type="Patient",
                resource_id=patient_id,
                fhir_data=patient_data,
                version_id=new_version_id
            )
            
            self.db.add(new_resource)
            self.db.commit()
            
            logger.info(f"Marked FHIR Patient as inactive: {patient_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting FHIR Patient {patient_id}: {str(e)}")
            raise
