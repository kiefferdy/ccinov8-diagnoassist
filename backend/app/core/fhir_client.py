"""
FHIR client for DiagnoAssist Backend
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
from fhirclient import client
from fhirclient.models import patient as fhir_patient
from fhirclient.models import observation as fhir_observation
from fhirclient.models import condition as fhir_condition
from fhirclient.models import encounter as fhir_encounter
from fhirclient.models import fhirreference, fhirdate, humanname, contactpoint, identifier

from app.config import settings
from app.core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class FHIRClientError(Exception):
    """Custom exception for FHIR client errors"""
    pass


class FHIRClient:
    """FHIR client for interacting with HAPI FHIR server"""
    
    def __init__(self):
        self.base_url = settings.fhir_server_url
        self.client_id = settings.fhir_client_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize FHIR client connection"""
        try:
            # Configure FHIR client settings
            client_settings = {
                'app_id': self.client_id or 'diagnoassist-backend',
                'api_base': self.base_url,
            }
            
            # Create FHIR client instance
            self.client = client.FHIRClient(settings=client_settings)
            
            logger.info(f"FHIR client initialized with base URL: {self.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize FHIR client: {e}")
            raise FHIRClientError(f"Failed to initialize FHIR client: {e}")
    
    async def test_connection(self) -> bool:
        """Test connection to FHIR server"""
        try:
            # Test with a simple capability statement request
            response = requests.get(f"{self.base_url}/metadata", timeout=10)
            
            if response.status_code == 200:
                logger.info("FHIR server connection test successful")
                return True
            else:
                logger.error(f"FHIR server connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"FHIR server connection test failed: {e}")
            return False
    
    def get_capability_statement(self) -> Optional[Dict[str, Any]]:
        """Get FHIR server capability statement"""
        try:
            response = requests.get(f"{self.base_url}/metadata")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get capability statement: {e}")
            return None
    
    # Patient CRUD operations
    
    def create_patient(self, patient_data: fhir_patient.Patient) -> Optional[str]:
        """Create a patient in FHIR server"""
        try:
            # Create patient resource
            patient_data.create(self.client.server)
            
            if patient_data.id:
                logger.info(f"Patient created with FHIR ID: {patient_data.id}")
                return patient_data.id
            else:
                logger.error("Patient creation failed - no ID returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create patient in FHIR: {e}")
            raise FHIRClientError(f"Failed to create patient: {e}")
    
    def get_patient(self, fhir_id: str) -> Optional[fhir_patient.Patient]:
        """Get a patient from FHIR server by ID"""
        try:
            patient = fhir_patient.Patient.read(fhir_id, self.client.server)
            return patient
        except Exception as e:
            logger.error(f"Failed to get patient {fhir_id}: {e}")
            return None
    
    def update_patient(self, fhir_id: str, patient_data: fhir_patient.Patient) -> bool:
        """Update a patient in FHIR server"""
        try:
            patient_data.id = fhir_id
            patient_data.update(self.client.server)
            logger.info(f"Patient {fhir_id} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update patient {fhir_id}: {e}")
            return False
    
    def delete_patient(self, fhir_id: str) -> bool:
        """Delete a patient from FHIR server"""
        try:
            patient = fhir_patient.Patient.read(fhir_id, self.client.server)
            if patient:
                patient.delete(self.client.server)
                logger.info(f"Patient {fhir_id} deleted successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete patient {fhir_id}: {e}")
            return False
    
    def search_patients(self, search_params: Dict[str, str]) -> List[fhir_patient.Patient]:
        """Search for patients using FHIR search parameters"""
        try:
            search_result = fhir_patient.Patient.where(search_params)
            patients = search_result.perform(self.client.server)
            return patients.entry if patients.entry else []
        except Exception as e:
            logger.error(f"Failed to search patients: {e}")
            return []
    
    # Observation operations
    
    def create_observation(self, observation_data: fhir_observation.Observation) -> Optional[str]:
        """Create an observation in FHIR server"""
        try:
            observation_data.create(self.client.server)
            
            if observation_data.id:
                logger.info(f"Observation created with FHIR ID: {observation_data.id}")
                return observation_data.id
            else:
                logger.error("Observation creation failed - no ID returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create observation in FHIR: {e}")
            raise FHIRClientError(f"Failed to create observation: {e}")
    
    def get_patient_observations(self, patient_fhir_id: str) -> List[fhir_observation.Observation]:
        """Get all observations for a patient"""
        try:
            search_params = {'patient': patient_fhir_id}
            search_result = fhir_observation.Observation.where(search_params)
            observations = search_result.perform(self.client.server)
            return observations.entry if observations.entry else []
        except Exception as e:
            logger.error(f"Failed to get observations for patient {patient_fhir_id}: {e}")
            return []
    
    # Condition operations
    
    def create_condition(self, condition_data: fhir_condition.Condition) -> Optional[str]:
        """Create a condition in FHIR server"""
        try:
            condition_data.create(self.client.server)
            
            if condition_data.id:
                logger.info(f"Condition created with FHIR ID: {condition_data.id}")
                return condition_data.id
            else:
                logger.error("Condition creation failed - no ID returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create condition in FHIR: {e}")
            raise FHIRClientError(f"Failed to create condition: {e}")
    
    def get_patient_conditions(self, patient_fhir_id: str) -> List[fhir_condition.Condition]:
        """Get all conditions for a patient"""
        try:
            search_params = {'patient': patient_fhir_id}
            search_result = fhir_condition.Condition.where(search_params)
            conditions = search_result.perform(self.client.server)
            return conditions.entry if conditions.entry else []
        except Exception as e:
            logger.error(f"Failed to get conditions for patient {patient_fhir_id}: {e}")
            return []
    
    # Encounter operations
    
    def create_encounter(self, encounter_data: fhir_encounter.Encounter) -> Optional[str]:
        """Create an encounter in FHIR server"""
        try:
            encounter_data.create(self.client.server)
            
            if encounter_data.id:
                logger.info(f"Encounter created with FHIR ID: {encounter_data.id}")
                return encounter_data.id
            else:
                logger.error("Encounter creation failed - no ID returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create encounter in FHIR: {e}")
            raise FHIRClientError(f"Failed to create encounter: {e}")
    
    def get_patient_encounters(self, patient_fhir_id: str) -> List[fhir_encounter.Encounter]:
        """Get all encounters for a patient"""
        try:
            search_params = {'patient': patient_fhir_id}
            search_result = fhir_encounter.Encounter.where(search_params)
            encounters = search_result.perform(self.client.server)
            return encounters.entry if encounters.entry else []
        except Exception as e:
            logger.error(f"Failed to get encounters for patient {patient_fhir_id}: {e}")
            return []


# Global FHIR client instance
fhir_client: Optional[FHIRClient] = None


async def init_fhir_client():
    """Initialize FHIR client"""
    global fhir_client
    
    try:
        fhir_client = FHIRClient()
        
        # Test connection if FHIR server is configured
        if settings.fhir_server_url:
            connection_ok = await fhir_client.test_connection()
            if connection_ok:
                logger.info("FHIR client initialized and connection tested successfully")
            else:
                logger.warning("FHIR client initialized but connection test failed")
        else:
            logger.info("FHIR client initialized (no server URL configured)")
            
    except Exception as e:
        logger.error(f"Failed to initialize FHIR client: {e}")
        # Don't raise exception - allow app to start without FHIR if needed
        fhir_client = None


async def close_fhir_client():
    """Close FHIR client connections"""
    global fhir_client
    
    if fhir_client:
        logger.info("FHIR client closed")
        fhir_client = None


def get_fhir_client() -> Optional[FHIRClient]:
    """Get FHIR client instance"""
    return fhir_client