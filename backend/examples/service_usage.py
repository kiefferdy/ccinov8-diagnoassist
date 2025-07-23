"""
DiagnoAssist Services Layer - Usage Examples
"""

from services.service_manager import ServiceContext
from api.dependencies import get_service_manager
from schemas.patient import PatientCreate
from schemas.episode import EpisodeCreate
from datetime import date

# Example 1: Basic service usage
def example_patient_operations():
    """Example of basic patient operations"""
    
    # Using service context (recommended for complex operations)
    with ServiceContext() as services:
        
        # Create a patient
        patient_data = PatientCreate(
            medical_record_number="MRN001234",
            first_name="John",
            last_name="Doe", 
            date_of_birth=date(1980, 1, 15),
            gender="male",
            email="john.doe@example.com"
        )
        
        patient = services.patient.create_patient(patient_data)
        print(f"Created patient: {patient.id}")
        
        # Create an episode
        episode_data = EpisodeCreate(
            patient_id=patient.id,
            chief_complaint="Chest pain and shortness of breath",
            encounter_type="outpatient",
            symptoms="Chest pain, dyspnea, fatigue"
        )
        
        episode = services.episode.create_episode(episode_data)
        print(f"Created episode: {episode.id}")
        
        # Generate AI differential diagnoses
        symptoms = ["chest pain", "shortness of breath", "fatigue"]
        diagnoses = services.diagnosis.generate_ai_differential_diagnoses(
            episode_id=str(episode.id),
            symptoms=symptoms,
            patient_data=patient.model_dump()
        )
        
        print(f"Generated {len(diagnoses)} differential diagnoses")
        
        return {
            "patient": patient,
            "episode": episode,
            "diagnoses": diagnoses
        }

# Example 2: Clinical workflow
def example_clinical_workflow():
    """Example of complete clinical workflow"""
    
    with ServiceContext() as services:
        
        # Start clinical encounter
        encounter = services.clinical.start_clinical_encounter(
            patient_mrn="MRN001234",
            chief_complaint="Persistent cough and fever",
            encounter_type="outpatient",
            vital_signs={
                "temperature": 38.5,
                "heart_rate": 95,
                "blood_pressure_systolic": 130,
                "blood_pressure_diastolic": 85
            }
        )
        
        episode_id = str(encounter["episode"].id)
        
        # Generate differential diagnoses
        symptoms = ["cough", "fever", "fatigue"]
        diagnoses = services.diagnosis.generate_ai_differential_diagnoses(
            episode_id=episode_id,
            symptoms=symptoms,
            patient_data=encounter["patient"].model_dump()
        )
        
        # Set final diagnosis
        if diagnoses:
            final_diagnosis = services.diagnosis.set_final_diagnosis(
                episode_id=episode_id,
                diagnosis_id=str(diagnoses[0].id)
            )
            
            # Create treatment plan
            from schemas.treatment import TreatmentCreate
            treatment_data = TreatmentCreate(
                episode_id=encounter["episode"].id,
                diagnosis_id=final_diagnosis.id,
                treatment_type="medication",
                name="Amoxicillin",
                dosage="500mg",
                frequency="twice daily",
                duration="7 days",
                instructions="Take with food"
            )
            
            treatment = services.treatment.create_treatment(treatment_data)
            
            return {
                "encounter": encounter,
                "diagnoses": diagnoses,
                "final_diagnosis": final_diagnosis,
                "treatment": treatment
            }

# Example 3: FastAPI integration
"""
from fastapi import APIRouter, Depends
from services.dependencies import ServiceDep, PaginationDep
from services.service_manager import ServiceManager

router = APIRouter()

@router.post("/patients/")
async def create_patient(
    patient_data: PatientCreate,
    services: ServiceManager = ServiceDep
):
    return services.patient.create_patient(patient_data)

@router.get("/patients/")
async def list_patients(
    services: ServiceManager = ServiceDep,
    pagination = PaginationDep
):
    return services.patient.search_patients(
        skip=pagination.skip,
        limit=pagination.limit
    )

@router.post("/clinical/encounter")
async def start_encounter(
    encounter_data: dict,
    services: ServiceManager = ServiceDep
):
    return services.clinical.start_clinical_encounter(**encounter_data)
"""

if __name__ == "__main__":
    # Run examples
    print("Running patient operations example...")
    result1 = example_patient_operations()
    
    print("\nRunning clinical workflow example...")
    result2 = example_clinical_workflow()
    
    print("\nExamples completed successfully!")
