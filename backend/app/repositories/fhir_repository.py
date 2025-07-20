"""
FHIR repository for DiagnoAssist Backend
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.fhir_client import get_fhir_client, FHIRClientError
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.models.soap import SOAPModel
from app.models.fhir_models import FHIRSyncStatus, FHIRSyncRequest, FHIRSyncResponse
from app.utils.fhir_mappers import fhir_mapper
from app.core.exceptions import DatabaseException, NotFoundError

logger = logging.getLogger(__name__)


class FHIRRepository:
    """Repository for FHIR operations"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize FHIR client"""
        self.client = get_fhir_client()
        if not self.client:
            logger.warning("FHIR client not available - FHIR operations will be disabled")
    
    def is_available(self) -> bool:
        """Check if FHIR operations are available"""
        return self.client is not None
    
    async def test_connection(self) -> bool:
        """Test FHIR server connection"""
        if not self.client:
            return False
        
        try:
            return await self.client.test_connection()
        except Exception as e:
            logger.error(f"FHIR connection test failed: {e}")
            return False
    
    # Patient operations
    
    async def create_patient(self, patient: PatientModel) -> Optional[str]:
        """Create a patient in FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping patient creation")
            return None
        
        try:
            # Convert to FHIR patient
            fhir_patient = fhir_mapper.patient_to_fhir(patient)
            
            # Create in FHIR server
            fhir_id = self.client.create_patient(fhir_patient)
            
            if fhir_id:
                logger.info(f"Patient {patient.id} created in FHIR with ID: {fhir_id}")
                return fhir_id
            else:
                logger.error(f"Failed to create patient {patient.id} in FHIR")
                return None
                
        except FHIRClientError as e:
            logger.error(f"FHIR client error creating patient {patient.id}: {e}")
            raise DatabaseException(f"FHIR error: {e}", "fhir_create")
        except Exception as e:
            logger.error(f"Unexpected error creating patient {patient.id} in FHIR: {e}")
            return None
    
    async def get_patient(self, fhir_id: str) -> Optional[PatientModel]:
        """Get a patient from FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping patient retrieval")
            return None
        
        try:
            fhir_patient = self.client.get_patient(fhir_id)
            
            if fhir_patient:
                # Convert to internal model
                patient = fhir_mapper.fhir_to_patient(fhir_patient)
                logger.info(f"Retrieved patient from FHIR with ID: {fhir_id}")
                return patient
            else:
                logger.warning(f"Patient {fhir_id} not found in FHIR")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving patient {fhir_id} from FHIR: {e}")
            return None
    
    async def update_patient(self, fhir_id: str, patient: PatientModel) -> bool:
        """Update a patient in FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping patient update")
            return False
        
        try:
            # Convert to FHIR patient
            fhir_patient = fhir_mapper.patient_to_fhir(patient)
            
            # Update in FHIR server
            success = self.client.update_patient(fhir_id, fhir_patient)
            
            if success:
                logger.info(f"Patient {patient.id} updated in FHIR with ID: {fhir_id}")
                return True
            else:
                logger.error(f"Failed to update patient {patient.id} in FHIR")
                return False
                
        except FHIRClientError as e:
            logger.error(f"FHIR client error updating patient {patient.id}: {e}")
            raise DatabaseException(f"FHIR error: {e}", "fhir_update")
        except Exception as e:
            logger.error(f"Unexpected error updating patient {patient.id} in FHIR: {e}")
            return False
    
    async def delete_patient(self, fhir_id: str) -> bool:
        """Delete a patient from FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping patient deletion")
            return False
        
        try:
            success = self.client.delete_patient(fhir_id)
            
            if success:
                logger.info(f"Patient deleted from FHIR with ID: {fhir_id}")
                return True
            else:
                logger.error(f"Failed to delete patient {fhir_id} from FHIR")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting patient {fhir_id} from FHIR: {e}")
            return False
    
    async def search_patients(self, search_params: Dict[str, str]) -> List[PatientModel]:
        """Search for patients in FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping patient search")
            return []
        
        try:
            fhir_patients = self.client.search_patients(search_params)
            
            patients = []
            for fhir_patient_entry in fhir_patients:
                fhir_patient = fhir_patient_entry.resource
                if fhir_patient:
                    patient = fhir_mapper.fhir_to_patient(fhir_patient)
                    patients.append(patient)
            
            logger.info(f"Found {len(patients)} patients in FHIR search")
            return patients
            
        except Exception as e:
            logger.error(f"Error searching patients in FHIR: {e}")
            return []
    
    # Encounter operations
    
    async def create_encounter(
        self, 
        encounter: EncounterModel, 
        patient_fhir_id: str
    ) -> Optional[str]:
        """Create an encounter in FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping encounter creation")
            return None
        
        try:
            # Convert to FHIR encounter
            fhir_encounter = fhir_mapper.encounter_to_fhir(encounter, patient_fhir_id)
            
            # Create in FHIR server
            fhir_id = self.client.create_encounter(fhir_encounter)
            
            if fhir_id:
                logger.info(f"Encounter {encounter.id} created in FHIR with ID: {fhir_id}")
                return fhir_id
            else:
                logger.error(f"Failed to create encounter {encounter.id} in FHIR")
                return None
                
        except FHIRClientError as e:
            logger.error(f"FHIR client error creating encounter {encounter.id}: {e}")
            raise DatabaseException(f"FHIR error: {e}", "fhir_create")
        except Exception as e:
            logger.error(f"Unexpected error creating encounter {encounter.id} in FHIR: {e}")
            return None
    
    async def get_patient_encounters(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        """Get all encounters for a patient from FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping encounter retrieval")
            return []
        
        try:
            fhir_encounters = self.client.get_patient_encounters(patient_fhir_id)
            
            encounters = []
            for fhir_encounter_entry in fhir_encounters:
                fhir_encounter = fhir_encounter_entry.resource
                if fhir_encounter:
                    # Convert to dictionary representation
                    encounter_dict = {
                        "fhir_id": fhir_encounter.id,
                        "status": fhir_encounter.status,
                        "class": fhir_encounter.class_.code if fhir_encounter.class_ else None,
                        "period": fhir_encounter.period,
                        "subject": fhir_encounter.subject.reference if fhir_encounter.subject else None
                    }
                    encounters.append(encounter_dict)
            
            logger.info(f"Retrieved {len(encounters)} encounters for patient {patient_fhir_id}")
            return encounters
            
        except Exception as e:
            logger.error(f"Error retrieving encounters for patient {patient_fhir_id}: {e}")
            return []
    
    # Observation operations
    
    async def create_soap_observations(
        self,
        soap: SOAPModel,
        patient_fhir_id: str,
        encounter_fhir_id: Optional[str] = None
    ) -> List[str]:
        """Create FHIR observations from SOAP data"""
        if not self.client:
            logger.warning("FHIR client not available - skipping observation creation")
            return []
        
        try:
            # Convert SOAP to FHIR observations
            fhir_observations = fhir_mapper.soap_to_fhir_observations(
                soap, patient_fhir_id, encounter_fhir_id
            )
            
            created_ids = []
            for obs in fhir_observations:
                try:
                    fhir_id = self.client.create_observation(obs)
                    if fhir_id:
                        created_ids.append(fhir_id)
                        logger.debug(f"Created observation in FHIR with ID: {fhir_id}")
                except Exception as e:
                    logger.error(f"Failed to create individual observation: {e}")
                    continue
            
            logger.info(f"Created {len(created_ids)} observations in FHIR from SOAP data")
            return created_ids
            
        except Exception as e:
            logger.error(f"Error creating SOAP observations in FHIR: {e}")
            return []
    
    async def get_patient_observations(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        """Get all observations for a patient from FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping observation retrieval")
            return []
        
        try:
            fhir_observations = self.client.get_patient_observations(patient_fhir_id)
            
            observations = []
            for fhir_obs_entry in fhir_observations:
                fhir_obs = fhir_obs_entry.resource
                if fhir_obs:
                    # Convert to dictionary representation
                    obs_dict = {
                        "fhir_id": fhir_obs.id,
                        "status": fhir_obs.status,
                        "code": fhir_obs.code.text if fhir_obs.code else None,
                        "value": self._extract_observation_value(fhir_obs),
                        "category": fhir_obs.category[0].text if fhir_obs.category else None,
                        "effective_date": fhir_obs.effectiveDateTime,
                        "issued": fhir_obs.issued
                    }
                    observations.append(obs_dict)
            
            logger.info(f"Retrieved {len(observations)} observations for patient {patient_fhir_id}")
            return observations
            
        except Exception as e:
            logger.error(f"Error retrieving observations for patient {patient_fhir_id}: {e}")
            return []
    
    def _extract_observation_value(self, fhir_obs) -> Optional[str]:
        """Extract value from FHIR observation"""
        if hasattr(fhir_obs, 'valueString') and fhir_obs.valueString:
            return fhir_obs.valueString
        elif hasattr(fhir_obs, 'valueQuantity') and fhir_obs.valueQuantity:
            return f"{fhir_obs.valueQuantity.value} {fhir_obs.valueQuantity.unit or ''}"
        elif hasattr(fhir_obs, 'valueCodeableConcept') and fhir_obs.valueCodeableConcept:
            return fhir_obs.valueCodeableConcept.text
        elif hasattr(fhir_obs, 'valueBoolean') and fhir_obs.valueBoolean is not None:
            return str(fhir_obs.valueBoolean)
        elif hasattr(fhir_obs, 'valueInteger') and fhir_obs.valueInteger is not None:
            return str(fhir_obs.valueInteger)
        return None
    
    # Condition operations
    
    async def create_assessment_conditions(
        self,
        assessment_data: str,
        patient_fhir_id: str,
        encounter_fhir_id: Optional[str] = None
    ) -> List[str]:
        """Create FHIR conditions from assessment data"""
        if not self.client:
            logger.warning("FHIR client not available - skipping condition creation")
            return []
        
        try:
            # Convert assessment to FHIR conditions
            fhir_conditions = fhir_mapper.assessment_to_fhir_conditions(
                assessment_data, patient_fhir_id, encounter_fhir_id
            )
            
            created_ids = []
            for condition in fhir_conditions:
                try:
                    fhir_id = self.client.create_condition(condition)
                    if fhir_id:
                        created_ids.append(fhir_id)
                        logger.debug(f"Created condition in FHIR with ID: {fhir_id}")
                except Exception as e:
                    logger.error(f"Failed to create individual condition: {e}")
                    continue
            
            logger.info(f"Created {len(created_ids)} conditions in FHIR from assessment")
            return created_ids
            
        except Exception as e:
            logger.error(f"Error creating assessment conditions in FHIR: {e}")
            return []
    
    async def get_patient_conditions(self, patient_fhir_id: str) -> List[Dict[str, Any]]:
        """Get all conditions for a patient from FHIR server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping condition retrieval")
            return []
        
        try:
            fhir_conditions = self.client.get_patient_conditions(patient_fhir_id)
            
            conditions = []
            for fhir_cond_entry in fhir_conditions:
                fhir_cond = fhir_cond_entry.resource
                if fhir_cond:
                    # Convert to dictionary representation
                    cond_dict = {
                        "fhir_id": fhir_cond.id,
                        "clinical_status": fhir_cond.clinicalStatus.text if fhir_cond.clinicalStatus else None,
                        "verification_status": fhir_cond.verificationStatus.text if fhir_cond.verificationStatus else None,
                        "code": fhir_cond.code.text if fhir_cond.code else None,
                        "onset": fhir_cond.onsetDateTime,
                        "recorded_date": fhir_cond.recordedDate
                    }
                    conditions.append(cond_dict)
            
            logger.info(f"Retrieved {len(conditions)} conditions for patient {patient_fhir_id}")
            return conditions
            
        except Exception as e:
            logger.error(f"Error retrieving conditions for patient {patient_fhir_id}: {e}")
            return []
    
    # Synchronization operations
    
    async def sync_patient_data(self, patient: PatientModel) -> FHIRSyncResponse:
        """Synchronize patient data with FHIR server"""
        try:
            # Check if patient already exists in FHIR
            existing_fhir_id = fhir_mapper.get_fhir_patient_id(patient)
            
            if existing_fhir_id:
                # Update existing patient
                success = await self.update_patient(existing_fhir_id, patient)
                return FHIRSyncResponse(
                    success=success,
                    fhir_id=existing_fhir_id if success else None,
                    errors=[] if success else ["Failed to update patient in FHIR"]
                )
            else:
                # Create new patient
                fhir_id = await self.create_patient(patient)
                return FHIRSyncResponse(
                    success=fhir_id is not None,
                    fhir_id=fhir_id,
                    errors=[] if fhir_id else ["Failed to create patient in FHIR"]
                )
                
        except Exception as e:
            logger.error(f"Error syncing patient {patient.id} with FHIR: {e}")
            return FHIRSyncResponse(
                success=False,
                errors=[str(e)]
            )
    
    async def sync_encounter_data(
        self, 
        encounter: EncounterModel, 
        patient_fhir_id: str
    ) -> FHIRSyncResponse:
        """Synchronize encounter data with FHIR server"""
        try:
            # Create encounter in FHIR
            encounter_fhir_id = await self.create_encounter(encounter, patient_fhir_id)
            
            if not encounter_fhir_id:
                return FHIRSyncResponse(
                    success=False,
                    errors=["Failed to create encounter in FHIR"]
                )
            
            # Create observations from SOAP data
            observation_ids = []
            if encounter.soap:
                observation_ids = await self.create_soap_observations(
                    encounter.soap, patient_fhir_id, encounter_fhir_id
                )
            
            # Create conditions from assessment
            condition_ids = []
            if encounter.soap and encounter.soap.assessment.primary_diagnosis:
                condition_ids = await self.create_assessment_conditions(
                    encounter.soap.assessment.primary_diagnosis,
                    patient_fhir_id,
                    encounter_fhir_id
                )
            
            logger.info(
                f"Synced encounter {encounter.id} to FHIR: "
                f"encounter_id={encounter_fhir_id}, "
                f"observations={len(observation_ids)}, "
                f"conditions={len(condition_ids)}"
            )
            
            return FHIRSyncResponse(
                success=True,
                fhir_id=encounter_fhir_id
            )
            
        except Exception as e:
            logger.error(f"Error syncing encounter {encounter.id} with FHIR: {e}")
            return FHIRSyncResponse(
                success=False,
                errors=[str(e)]
            )
    
    async def get_capability_statement(self) -> Optional[Dict[str, Any]]:
        """Get FHIR server capability statement"""
        if not self.client:
            return None
        
        try:
            return self.client.get_capability_statement()
        except Exception as e:
            logger.error(f"Error getting FHIR capability statement: {e}")
            return None
    
    # Advanced FHIR operations for workflows
    
    async def submit_bundle(self, bundle: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit a FHIR Bundle to the server"""
        if not self.client:
            logger.warning("FHIR client not available - skipping bundle submission")
            return None
        
        try:
            # Submit bundle using client
            response = await self.client.submit_bundle(bundle)
            
            if response:
                logger.info(f"Successfully submitted bundle {bundle.get('id')} to FHIR server")
                return response
            else:
                logger.error(f"Failed to submit bundle {bundle.get('id')} to FHIR server")
                return None
                
        except FHIRClientError as e:
            logger.error(f"FHIR client error submitting bundle: {e}")
            raise DatabaseException(f"FHIR error: {e}", "fhir_bundle_submit")
        except Exception as e:
            logger.error(f"Unexpected error submitting bundle to FHIR: {e}")
            return None
    
    async def validate_resource(self, resource: Dict[str, Any], profile: Optional[str] = None) -> Dict[str, Any]:
        """Validate a FHIR resource against a profile"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource validation")
            return {"valid": False, "issues": ["FHIR client not available"]}
        
        try:
            # Use client's validation endpoint
            validation_result = await self.client.validate_resource(resource, profile)
            
            logger.info(f"Validated {resource.get('resourceType')} resource")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating FHIR resource: {e}")
            return {
                "valid": False,
                "issues": [str(e)]
            }
    
    async def search_resources(
        self, 
        resource_type: str, 
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search for FHIR resources of a specific type"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource search")
            return []
        
        try:
            results = await self.client.search_resources(resource_type, search_params)
            
            logger.info(f"Found {len(results)} {resource_type} resources")
            return results
            
        except Exception as e:
            logger.error(f"Error searching {resource_type} resources: {e}")
            return []
    
    async def create_resource(self, resource: Dict[str, Any]) -> Optional[str]:
        """Create a generic FHIR resource"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource creation")
            return None
        
        try:
            resource_id = await self.client.create_resource(resource)
            
            if resource_id:
                logger.info(f"Created {resource.get('resourceType')} resource with ID: {resource_id}")
                return resource_id
            else:
                logger.error(f"Failed to create {resource.get('resourceType')} resource")
                return None
                
        except Exception as e:
            logger.error(f"Error creating FHIR resource: {e}")
            return None
    
    async def update_resource(self, resource_id: str, resource: Dict[str, Any]) -> bool:
        """Update a generic FHIR resource"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource update")
            return False
        
        try:
            success = await self.client.update_resource(resource_id, resource)
            
            if success:
                logger.info(f"Updated {resource.get('resourceType')} resource: {resource_id}")
                return True
            else:
                logger.error(f"Failed to update {resource.get('resourceType')} resource: {resource_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating FHIR resource {resource_id}: {e}")
            return False
    
    async def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific FHIR resource by type and ID"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource retrieval")
            return None
        
        try:
            resource = await self.client.get_resource(resource_type, resource_id)
            
            if resource:
                logger.info(f"Retrieved {resource_type} resource: {resource_id}")
                return resource
            else:
                logger.warning(f"{resource_type} resource not found: {resource_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving {resource_type} resource {resource_id}: {e}")
            return None
    
    async def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """Delete a specific FHIR resource"""
        if not self.client:
            logger.warning("FHIR client not available - skipping resource deletion")
            return False
        
        try:
            success = await self.client.delete_resource(resource_type, resource_id)
            
            if success:
                logger.info(f"Deleted {resource_type} resource: {resource_id}")
                return True
            else:
                logger.error(f"Failed to delete {resource_type} resource: {resource_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting {resource_type} resource {resource_id}: {e}")
            return False
    
    async def execute_batch_operation(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a batch of FHIR operations"""
        if not self.client:
            logger.warning("FHIR client not available - skipping batch operation")
            return {"success": False, "error": "FHIR client not available"}
        
        try:
            # Create batch bundle
            batch_bundle = {
                "resourceType": "Bundle",
                "type": "batch",
                "entry": []
            }
            
            for operation in operations:
                entry = {
                    "request": operation
                }
                
                if "resource" in operation:
                    entry["resource"] = operation["resource"]
                
                batch_bundle["entry"].append(entry)
            
            # Submit batch bundle
            response = await self.submit_bundle(batch_bundle)
            
            if response:
                logger.info(f"Successfully executed batch operation with {len(operations)} operations")
                return {"success": True, "response": response}
            else:
                logger.error("Failed to execute batch operation")
                return {"success": False, "error": "Batch operation failed"}
                
        except Exception as e:
            logger.error(f"Error executing batch operation: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_subscription(self, subscription: Dict[str, Any]) -> Optional[str]:
        """Create a FHIR Subscription resource"""
        if not self.client:
            logger.warning("FHIR client not available - skipping subscription creation")
            return None
        
        try:
            subscription_id = await self.create_resource(subscription)
            
            if subscription_id:
                logger.info(f"Created FHIR subscription: {subscription_id}")
                return subscription_id
            else:
                logger.error("Failed to create FHIR subscription")
                return None
                
        except Exception as e:
            logger.error(f"Error creating FHIR subscription: {e}")
            return None
    
    async def get_operation_outcome(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract operation outcome from FHIR response"""
        try:
            if response.get("resourceType") == "OperationOutcome":
                issues = response.get("issue", [])
                
                outcome = {
                    "success": not any(issue.get("severity") in ["error", "fatal"] for issue in issues),
                    "warnings": [issue for issue in issues if issue.get("severity") == "warning"],
                    "errors": [issue for issue in issues if issue.get("severity") in ["error", "fatal"]],
                    "information": [issue for issue in issues if issue.get("severity") == "information"]
                }
                
                return outcome
            
            # If not an OperationOutcome, assume success
            return {"success": True, "warnings": [], "errors": [], "information": []}
            
        except Exception as e:
            logger.error(f"Error processing operation outcome: {e}")
            return {"success": False, "errors": [{"message": str(e)}], "warnings": [], "information": []}


# Create repository instance
fhir_repository = FHIRRepository()