from typing import List, Optional
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.bundle import Bundle, BundleEntry
from repositories.fhir_patient_repository import FHIRPatientRepository
from fhir.models.patient import PatientFHIRModel
from fhir.transformers.internal_to_fhir import InternalToFHIRTransformer

class FHIRPatientService:
    def __init__(self, fhir_patient_repo: FHIRPatientRepository):
        self.fhir_patient_repo = fhir_patient_repo
        self.transformer = InternalToFHIRTransformer()
    
    async def create_fhir_patient(self, patient_data: dict) -> FHIRPatient:
        """Create a new patient using FHIR format"""
        
        # Validate patient data
        self._validate_patient_data(patient_data)
        
        # Create FHIR Patient resource
        fhir_patient = PatientFHIRModel.create_fhir_patient(**patient_data)
        
        # Validate FHIR resource
        self._validate_fhir_resource(fhir_patient)
        
        # Save to repository
        saved_patient = await self.fhir_patient_repo.create(fhir_patient)
        
        return saved_patient
    
    async def get_patient_bundle(self, patient_id: str) -> Bundle:
        """Get complete patient data as FHIR Bundle"""
        
        # Get patient
        patient = await self.fhir_patient_repo.get(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Create bundle
        bundle = Bundle()
        bundle.type = "collection"
        bundle.entry = []
        
        # Add patient to bundle
        bundle.entry.append(BundleEntry(**{
            "resource": patient
        }))
        
        # Add related encounters
        encounters = await self._get_patient_encounters(patient_id)
        for encounter in encounters:
            bundle.entry.append(BundleEntry(**{
                "resource": encounter
            }))
        
        # Add observations
        observations = await self._get_patient_observations(patient_id)
        for observation in observations:
            bundle.entry.append(BundleEntry(**{
                "resource": observation
            }))
        
        # Set bundle ID and timestamp
        bundle.id = f"patient-bundle-{patient_id}"
        bundle.timestamp = datetime.utcnow().isoformat()
        
        return bundle
    
    def _validate_fhir_resource(self, resource):
        """Validate FHIR resource against schema"""
        try:
            # The fhir.resources library automatically validates
            resource.json()  # This will raise exception if invalid
        except Exception as e:
            raise ValueError(f"Invalid FHIR resource: {str(e)}")