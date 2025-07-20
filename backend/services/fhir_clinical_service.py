from typing import List, Optional, Dict, Any
from repositories.fhir_encounter_repository import FHIREncounterRepository
from repositories.fhir_observation_repository import FHIRObservationRepository
from services.ai_service import AIService
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.bundle import Bundle
from fhir.models.observation import ObservationFHIRModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FHIRClinicalService:
    """
    Service for FHIR clinical data management (Encounters, Observations)
    """
    
    def __init__(
        self,
        fhir_encounter_repo: FHIREncounterRepository,
        fhir_observation_repo: FHIRObservationRepository,
        ai_service: AIService
    ):
        self.fhir_encounter_repo = fhir_encounter_repo
        self.fhir_observation_repo = fhir_observation_repo
        self.ai_service = ai_service
    
    async def create_fhir_encounter(self, encounter_data: Dict[str, Any]) -> FHIREncounter:
        """
        Create FHIR Encounter resource
        
        Args:
            encounter_data: Encounter data in FHIR format
            
        Returns:
            Created FHIR Encounter resource
        """
        try:
            # Validate FHIR Encounter data
            fhir_encounter = FHIREncounter(**encounter_data)
            
            # Store FHIR resource
            created_encounter = self.fhir_encounter_repo.create_fhir_encounter(fhir_encounter)
            
            logger.info(f"Created FHIR Encounter: {created_encounter.id}")
            return created_encounter
            
        except Exception as e:
            logger.error(f"Error creating FHIR Encounter: {str(e)}")
            raise
    
    async def create_fhir_observation(self, observation_data: Dict[str, Any]) -> FHIRObservation:
        """
        Create FHIR Observation resource
        
        Args:
            observation_data: Observation data in FHIR format
            
        Returns:
            Created FHIR Observation resource
        """
        try:
            # Validate FHIR Observation data
            fhir_observation = FHIRObservation(**observation_data)
            
            # Store FHIR resource
            created_observation = self.fhir_observation_repo.create_fhir_observation(fhir_observation)
            
            logger.info(f"Created FHIR Observation: {created_observation.id}")
            return created_observation
            
        except Exception as e:
            logger.error(f"Error creating FHIR Observation: {str(e)}")
            raise
    
    async def create_vital_signs_bundle(self, vital_signs_data: Dict[str, Any]) -> Bundle:
        """
        Create multiple vital sign observations as a Bundle
        
        Args:
            vital_signs_data: Vital signs data
            
        Returns:
            FHIR Bundle with vital sign observations
        """
        try:
            patient_id = vital_signs_data["patient_id"]
            encounter_id = vital_signs_data.get("encounter_id")
            vital_signs = vital_signs_data["vital_signs"]
            timestamp = vital_signs_data.get("timestamp")
            
            # Create bundle
            bundle = Bundle()
            bundle.type = "collection"
            bundle.id = f"vital-signs-{patient_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            bundle.entry = []
            
            # Create observations for each vital sign
            for vital_type, vital_data in vital_signs.items():
                if vital_type in ObservationFHIRModel.VITAL_SIGNS_CODES:
                    observation = ObservationFHIRModel.create_vital_sign_observation(
                        patient_id=patient_id,
                        encounter_id=encounter_id,
                        vital_type=vital_type,
                        value=vital_data["value"],
                        unit=vital_data["unit"],
                        timestamp=datetime.fromisoformat(timestamp) if timestamp else None
                    )
                    
                    # Store observation
                    stored_obs = self.fhir_observation_repo.create_fhir_observation(observation)
                    
                    # Add to bundle
                    bundle.entry.append({
                        "resource": stored_obs.dict()
                    })
            
            logger.info(f"Created vital signs bundle with {len(bundle.entry)} observations")
            return bundle
            
        except Exception as e:
            logger.error(f"Error creating vital signs bundle: {str(e)}")
            raise
    
    async def get_fhir_encounter(self, encounter_id: str) -> Optional[FHIREncounter]:
        """
        Get FHIR Encounter resource by ID
        
        Args:
            encounter_id: Encounter resource ID
            
        Returns:
            FHIR Encounter resource or None
        """
        try:
            return self.fhir_encounter_repo.get_fhir_encounter(encounter_id)
        except Exception as e:
            logger.error(f"Error getting FHIR Encounter {encounter_id}: {str(e)}")
            raise
    
    async def get_fhir_observation(self, observation_id: str) -> Optional[FHIRObservation]:
        """
        Get FHIR Observation resource by ID
        
        Args:
            observation_id: Observation resource ID
            
        Returns:
            FHIR Observation resource or None
        """
        try:
            return self.fhir_observation_repo.get_fhir_observation(observation_id)
        except Exception as e:
            logger.error(f"Error getting FHIR Observation {observation_id}: {str(e)}")
            raise
    
    async def search_encounters(self, search_params: Dict[str, Any]) -> Bundle:
        """
        Search FHIR Encounter resources
        
        Args:
            search_params: FHIR search parameters
            
        Returns:
            FHIR Bundle with search results
        """
        try:
            return self.fhir_encounter_repo.search_fhir_encounters(search_params)
        except Exception as e:
            logger.error(f"Error searching FHIR Encounters: {str(e)}")
            raise
    
    async def search_observations(self, search_params: Dict[str, Any]) -> Bundle:
        """
        Search FHIR Observation resources
        
        Args:
            search_params: FHIR search parameters
            
        Returns:
            FHIR Bundle with search results
        """
        try:
            # This would be implemented in the repository
            # For now, return empty bundle
            bundle = Bundle()
            bundle.type = "searchset"
            bundle.total = 0
            bundle.entry = []
            return bundle
        except Exception as e:
            logger.error(f"Error searching FHIR Observations: {str(e)}")
            raise
