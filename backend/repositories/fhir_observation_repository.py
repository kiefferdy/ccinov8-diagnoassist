from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fhir.resources.observation import Observation as FHIRObservation
from models.fhir_resource import FHIRResource
import logging

logger = logging.getLogger(__name__)

class FHIRObservationRepository:
    """Repository for FHIR Observation resource operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fhir_observation(self, fhir_observation: FHIRObservation) -> FHIRObservation:
        """Store FHIR Observation resource"""
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
        """Get FHIR Observation resource by ID"""
        try:
            fhir_resource = self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == "Observation",
                FHIRResource.resource_id == observation_id
            ).order_by(FHIRResource.version_id.desc()).first()
            
            if fhir_resource:
                return FHIRObservation(**fhir_resource.fhir_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting FHIR Observation {observation_id}: {str(e)}")
            raise
    
    def search_observations(self, search_params: Dict[str, Any]) -> List[FHIRObservation]:
        """Search FHIR Observation resources"""
        try:
            query = self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == "Observation"
            )
            
            # Apply search filters
            observations = query.limit(search_params.get('_count', 20)).all()
            
            return [FHIRObservation(**resource.fhir_data) for resource in observations]
            
        except Exception as e:
            logger.error(f"Error searching FHIR Observations: {str(e)}")
            raise