from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.bundle import Bundle
from models.fhir_resource import FHIRResource
import logging

logger = logging.getLogger(__name__)

class FHIREncounterRepository:
    """
    Repository for FHIR Encounter resource operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fhir_encounter(self, fhir_encounter: FHIREncounter) -> FHIREncounter:
        """
        Store FHIR Encounter resource
        
        Args:
            fhir_encounter: FHIR Encounter resource
            
        Returns:
            Stored FHIR Encounter resource
        """
        try:
            fhir_resource = FHIRResource(
                resource_type="Encounter",
                resource_id=fhir_encounter.id,
                fhir_data=fhir_encounter.dict(),
                version_id="1"
            )
            
            self.db.add(fhir_resource)
            self.db.commit()
            self.db.refresh(fhir_resource)
            
            logger.info(f"Created FHIR Encounter resource: {fhir_encounter.id}")
            return FHIREncounter(**fhir_resource.fhir_data)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating FHIR Encounter: {str(e)}")
            raise
    
    def get_fhir_encounter(self, encounter_id: str) -> Optional[FHIREncounter]:
        """
        Get FHIR Encounter resource by ID
        
        Args:
            encounter_id: Encounter resource ID
            
        Returns:
            FHIR Encounter resource or None
        """
        try:
            fhir_resource = self.db.query(FHIRResource).filter(
                and_(
                    FHIRResource.resource_type == "Encounter",
                    FHIRResource.resource_id == encounter_id
                )
            ).order_by(desc(FHIRResource.version_id)).first()
            
            if fhir_resource:
                return FHIREncounter(**fhir_resource.fhir_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting FHIR Encounter {encounter_id}: {str(e)}")
            raise
    
    def search_fhir_encounters(self, search_params: Dict[str, Any]) -> Bundle:
        """
        Search FHIR Encounter resources
        
        Args:
            search_params: FHIR search parameters
            
        Returns:
            FHIR Bundle with search results
        """
        try:
            query = self.db.query(FHIRResource).filter(
                FHIRResource.resource_type == "Encounter"
            )
            
            # Apply basic search filters
            # This is simplified - full FHIR search would be more complex
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
            logger.error(f"Error searching FHIR Encounters: {str(e)}")
            raise
