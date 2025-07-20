from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.bundle import Bundle
from models.fhir_resource import FHIRResource
import logging

logger = logging.getLogger(__name__)

class FHIRObservationRepository:
    """
    Repository for FHIR Observation resource operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fhir_observation(self, fhir_observation: FHIRObservation) -> FHIRObservation:
        """
        Store FHIR Observation resource
        
        Args:
            fhir_observation: FHIR Observation resource
            
        Returns:
            Stored FHIR Observation resource
        """
        try:
            fhir_resource = FHIRResource(
                resource_type="Observation",
                resource_id=fhir_observation.id,
                fhir_data=fhir_observation.dict(),
                version_id="1"
            )
            
            self.db.add(fhir_resource)
            self.db.commit()
            self.db.refresh(fhir_resource)
            
            logger.info(f"Created FHIR Observation resource: {fhir_observation.id}")
            return FHIRObservation(**fhir_resource.fhir_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating FHIR Observation: {str(e)}")
            raise
    
    def get_fhir_observation(self, observation_id: str) -> Optional[FHIRObservation]:
        """
        Get FHIR Observation resource by ID
        
        Args:
            observation_id: Observation resource ID
            
        Returns:
            FHIR Observation resource or None
        """
        try:
            fhir_resource = self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_type == "Observation",
                    FHIRResource.resource_id == observation_id
                )
            ).order_by(desc(FHIRResource.version_id)).first()
            
            if fhir_resource:
                return FHIRObservation(**fhir_resource.fhir_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting FHIR Observation {observation_id}: {str(e)}")
            raise
    
    def get_observations_by_patient(self, patient_id: str) -> List[FHIRObservation]:
        """
        Get all observations for a patient
        
        Args:
            patient_id: Patient resource ID
            
        Returns:
            List of FHIR Observation resources
        """
        try:
            # This would need to query based on the patient reference in the FHIR data
            # Simplified implementation
            fhir_resources = self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == "Observation"
            ).all()
            
            observations = []
            for resource in fhir_resources:
                fhir_data = resource.fhir_data
                if fhir_data.get("subject", {}).get("reference") == f"Patient/{patient_id}":
                    observations.append(FHIRObservation(**fhir_data))
            
            return observations
            
        except Exception as e:
            logger.error(f"Error getting observations for patient {patient_id}: {str(e)}")
            raise
