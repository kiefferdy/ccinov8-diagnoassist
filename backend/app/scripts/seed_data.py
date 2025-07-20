"""
Database seeding script for DiagnoAssist Backend
"""
import asyncio
import logging
from typing import List
from datetime import datetime, timedelta
import random

from app.models.patient import PatientModel, PatientDemographics, MedicalBackground, AllergyInfo, Medication, MedicalCondition
from app.models.episode import EpisodeModel, EpisodeCategoryEnum, EpisodeStatusEnum
from app.models.encounter import EncounterModel, EncounterTypeEnum, EncounterStatusEnum, Provider, WorkflowInfo
from app.models.soap import SOAPModel, SubjectiveSection, ObjectiveSection, AssessmentSection, PlanSection, VitalSigns
from app.models.auth import UserModel, UserProfile, UserRoleEnum, UserStatusEnum
from app.repositories.patient_repository import patient_repository
from app.repositories.episode_repository import episode_repository
from app.repositories.encounter_repository import encounter_repository
from app.repositories.user_repository import user_repository
from app.core.security import get_password_hash
from app.core.database import init_database

logger = logging.getLogger(__name__)


class DataSeeder:
    """Database seeding manager"""
    
    def __init__(self):
        self.patients = []
        self.episodes = []
        self.encounters = []
        self.users = []
    
    async def seed_users(self):
        """Seed sample users"""
        logger.info("Seeding users...")
        
        sample_users = [
            {
                "email": "dr.smith@diagnoassist.com",
                "password": "doctor123",
                "role": UserRoleEnum.DOCTOR,
                "profile": UserProfile(
                    first_name="John",
                    last_name="Smith",
                    specialty="Internal Medicine",
                    license_number="MD123456",
                    department="Internal Medicine",
                    phone="+1-555-0101"
                )
            },
            {
                "email": "dr.johnson@diagnoassist.com", 
                "password": "doctor123",
                "role": UserRoleEnum.DOCTOR,
                "profile": UserProfile(
                    first_name="Sarah",
                    last_name="Johnson",
                    specialty="Emergency Medicine",
                    license_number="MD789012",
                    department="Emergency",
                    phone="+1-555-0102"
                )
            },
            {
                "email": "dr.brown@diagnoassist.com",
                "password": "doctor123", 
                "role": UserRoleEnum.DOCTOR,
                "profile": UserProfile(
                    first_name="Michael",
                    last_name="Brown",
                    specialty="Family Medicine",
                    license_number="MD345678",
                    department="Family Medicine",
                    phone="+1-555-0103"
                )
            },
            {
                "email": "nurse.wilson@diagnoassist.com",
                "password": "nurse123",
                "role": UserRoleEnum.NURSE,
                "profile": UserProfile(
                    first_name="Emily",
                    last_name="Wilson",
                    specialty="Registered Nurse",
                    license_number="RN567890",
                    department="Emergency",
                    phone="+1-555-0201"
                )
            },
            {
                "email": "nurse.davis@diagnoassist.com",
                "password": "nurse123",
                "role": UserRoleEnum.NURSE,
                "profile": UserProfile(
                    first_name="James",
                    last_name="Davis",
                    specialty="Registered Nurse",
                    license_number="RN901234",
                    department="Internal Medicine",
                    phone="+1-555-0202"
                )
            }
        ]
        
        for user_data in sample_users:
            # Check if user already exists
            existing_user = await user_repository.get_by_email(user_data["email"])
            if existing_user:
                logger.info(f"User {user_data['email']} already exists")
                self.users.append(existing_user)
                continue
            
            user = UserModel(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                status=UserStatusEnum.ACTIVE,
                profile=user_data["profile"],
                is_verified=True
            )
            
            created_user = await user_repository.create(user)
            self.users.append(created_user)
            logger.info(f"Created user: {created_user.email}")
        
        logger.info(f"Seeded {len(self.users)} users")
    
    async def seed_patients(self):
        """Seed sample patients"""
        logger.info("Seeding patients...")
        
        sample_patients = [
            {
                "demographics": PatientDemographics(
                    name="Alice Johnson",
                    date_of_birth="1985-03-15",
                    gender="Female",
                    phone="+1-555-1001",
                    email="alice.johnson@email.com",
                    address="123 Main St, Springfield, IL 62701"
                ),
                "medical_background": MedicalBackground(
                    allergies=[
                        AllergyInfo(
                            allergen="Penicillin",
                            reaction="Rash",
                            severity="Moderate"
                        )
                    ],
                    medications=[
                        Medication(
                            name="Lisinopril",
                            dosage="10mg",
                            frequency="Daily",
                            start_date="2023-01-15"
                        )
                    ],
                    medical_conditions=[
                        MedicalCondition(
                            condition="Hypertension",
                            diagnosed_date="2023-01-15",
                            status="Active"
                        )
                    ]
                )
            },
            {
                "demographics": PatientDemographics(
                    name="Robert Smith",
                    date_of_birth="1972-11-22",
                    gender="Male",
                    phone="+1-555-1002",
                    email="robert.smith@email.com",
                    address="456 Oak Ave, Springfield, IL 62702"
                ),
                "medical_background": MedicalBackground(
                    allergies=[
                        AllergyInfo(
                            allergen="Sulfa drugs",
                            reaction="Difficulty breathing",
                            severity="Severe"
                        )
                    ],
                    medications=[
                        Medication(
                            name="Metformin",
                            dosage="500mg",
                            frequency="Twice daily",
                            start_date="2022-06-10"
                        )
                    ],
                    medical_conditions=[
                        MedicalCondition(
                            condition="Type 2 Diabetes",
                            diagnosed_date="2022-06-10",
                            status="Active"
                        )
                    ]
                )
            },
            {
                "demographics": PatientDemographics(
                    name="Maria Garcia",
                    date_of_birth="1990-07-08",
                    gender="Female",
                    phone="+1-555-1003",
                    email="maria.garcia@email.com",
                    address="789 Pine St, Springfield, IL 62703"
                ),
                "medical_background": MedicalBackground(
                    allergies=[],
                    medications=[],
                    medical_conditions=[]
                )
            },
            {
                "demographics": PatientDemographics(
                    name="David Wilson",
                    date_of_birth="1965-09-12",
                    gender="Male",
                    phone="+1-555-1004",
                    email="david.wilson@email.com",
                    address="321 Elm St, Springfield, IL 62704"
                ),
                "medical_background": MedicalBackground(
                    allergies=[
                        AllergyInfo(
                            allergen="Aspirin",
                            reaction="Stomach upset",
                            severity="Mild"
                        )
                    ],
                    medications=[
                        Medication(
                            name="Atorvastatin",
                            dosage="20mg",
                            frequency="Daily",
                            start_date="2023-03-01"
                        )
                    ],
                    medical_conditions=[
                        MedicalCondition(
                            condition="High Cholesterol",
                            diagnosed_date="2023-03-01",
                            status="Active"
                        )
                    ]
                )
            },
            {
                "demographics": PatientDemographics(
                    name="Jennifer Brown",
                    date_of_birth="1995-12-03",
                    gender="Female",
                    phone="+1-555-1005",
                    email="jennifer.brown@email.com",
                    address="654 Maple Ave, Springfield, IL 62705"
                ),
                "medical_background": MedicalBackground(
                    allergies=[],
                    medications=[],
                    medical_conditions=[]
                )
            }
        ]
        
        for patient_data in sample_patients:
            # Check if patient already exists by email
            if patient_data["demographics"].email:
                existing_patient = await patient_repository.get_by_email(patient_data["demographics"].email)
                if existing_patient:
                    logger.info(f"Patient {patient_data['demographics'].email} already exists")
                    self.patients.append(existing_patient)
                    continue
            
            patient = PatientModel(
                demographics=patient_data["demographics"],
                medical_background=patient_data["medical_background"]
            )
            
            created_patient = await patient_repository.create(patient)
            self.patients.append(created_patient)
            logger.info(f"Created patient: {created_patient.demographics.name}")
        
        logger.info(f"Seeded {len(self.patients)} patients")
    
    async def seed_episodes(self):
        """Seed sample episodes"""
        logger.info("Seeding episodes...")
        
        if not self.patients:
            logger.warning("No patients available for episodes")
            return
        
        episode_templates = [
            {
                "chief_complaint": "Routine annual physical examination",
                "category": EpisodeCategoryEnum.ROUTINE_CARE,
                "status": EpisodeStatusEnum.ACTIVE,
                "tags": ["annual", "physical", "routine"]
            },
            {
                "chief_complaint": "Chest pain and shortness of breath",
                "category": EpisodeCategoryEnum.ACUTE_CARE,
                "status": EpisodeStatusEnum.ACTIVE,
                "tags": ["chest-pain", "cardiology", "urgent"]
            },
            {
                "chief_complaint": "Follow-up for diabetes management",
                "category": EpisodeCategoryEnum.FOLLOW_UP,
                "status": EpisodeStatusEnum.ACTIVE,
                "tags": ["diabetes", "follow-up", "endocrine"]
            },
            {
                "chief_complaint": "Headache and dizziness",
                "category": EpisodeCategoryEnum.ACUTE_CARE,
                "status": EpisodeStatusEnum.RESOLVED,
                "tags": ["headache", "neurology"]
            }
        ]
        
        # Create episodes for first 4 patients
        for i, patient in enumerate(self.patients[:4]):
            if i < len(episode_templates):
                template = episode_templates[i]
                
                episode = EpisodeModel(
                    patient_id=patient.id,
                    chief_complaint=template["chief_complaint"],
                    category=template["category"],
                    status=template["status"],
                    tags=template["tags"],
                    notes=f"Episode created for {patient.demographics.name}"
                )
                
                # Set resolved date if episode is resolved
                if template["status"] == EpisodeStatusEnum.RESOLVED:
                    episode.resolved_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                created_episode = await episode_repository.create(episode)
                self.episodes.append(created_episode)
                logger.info(f"Created episode for {patient.demographics.name}: {created_episode.chief_complaint}")
        
        logger.info(f"Seeded {len(self.episodes)} episodes")
    
    async def seed_encounters(self):
        """Seed sample encounters"""
        logger.info("Seeding encounters...")
        
        if not self.episodes or not self.users:
            logger.warning("No episodes or users available for encounters")
            return
        
        # Get doctors for providers
        doctors = [user for user in self.users if user.role == UserRoleEnum.DOCTOR]
        if not doctors:
            logger.warning("No doctors available for encounters")
            return
        
        encounter_templates = [
            {
                "type": EncounterTypeEnum.ROUTINE_VISIT,
                "status": EncounterStatusEnum.SIGNED,
                "soap": {
                    "subjective": {
                        "chief_complaint": "Annual physical examination",
                        "history_of_present_illness": "Patient presents for routine annual physical. No current complaints.",
                        "review_of_systems": "No significant findings on review of systems."
                    },
                    "objective": {
                        "vital_signs": {
                            "blood_pressure": "120/80 mmHg",
                            "heart_rate": "72 bpm",
                            "temperature": "98.6°F",
                            "respiratory_rate": "16/min"
                        },
                        "physical_examination": "General appearance: Well-appearing adult in no acute distress. Heart: Regular rate and rhythm. Lungs: Clear to auscultation bilaterally."
                    },
                    "assessment": {
                        "primary_diagnosis": "Routine health maintenance",
                        "differential_diagnoses": [],
                        "clinical_impression": "Patient is in good health with no acute concerns."
                    },
                    "plan": {
                        "treatment_plan": "Continue current medications. Routine follow-up in 1 year.",
                        "medications": ["Continue Lisinopril 10mg daily"],
                        "follow_up": "Annual physical in 12 months",
                        "patient_education": "Discussed importance of regular exercise and healthy diet."
                    }
                }
            },
            {
                "type": EncounterTypeEnum.EMERGENCY,
                "status": EncounterStatusEnum.SIGNED,
                "soap": {
                    "subjective": {
                        "chief_complaint": "Chest pain and shortness of breath",
                        "history_of_present_illness": "Patient presents with acute onset chest pain and dyspnea that started 2 hours ago.",
                        "review_of_systems": "Positive for chest pain, shortness of breath. Negative for nausea, vomiting, diaphoresis."
                    },
                    "objective": {
                        "vital_signs": {
                            "blood_pressure": "145/95 mmHg",
                            "heart_rate": "95 bpm",
                            "temperature": "98.4°F",
                            "respiratory_rate": "22/min"
                        },
                        "physical_examination": "Anxious-appearing adult. Heart: Tachycardic but regular. Lungs: Mild bilateral rales."
                    },
                    "assessment": {
                        "primary_diagnosis": "Acute coronary syndrome, rule out",
                        "differential_diagnoses": ["Myocardial infarction", "Unstable angina", "Pulmonary embolism"],
                        "clinical_impression": "High suspicion for cardiac etiology of chest pain."
                    },
                    "plan": {
                        "treatment_plan": "Cardiology consultation, cardiac enzymes, ECG, chest X-ray",
                        "medications": ["Aspirin 325mg", "Nitroglycerin PRN"],
                        "follow_up": "Cardiology follow-up in 1 week",
                        "patient_education": "Return to ED immediately if symptoms worsen."
                    }
                }
            }
        ]
        
        # Create encounters for first 2 episodes
        for i, episode in enumerate(self.episodes[:2]):
            if i < len(encounter_templates):
                template = encounter_templates[i]
                doctor = random.choice(doctors)
                
                # Create SOAP model
                soap = SOAPModel(
                    subjective=SubjectiveSection(
                        chief_complaint=template["soap"]["subjective"]["chief_complaint"],
                        history_of_present_illness=template["soap"]["subjective"]["history_of_present_illness"],
                        review_of_systems=template["soap"]["subjective"]["review_of_systems"]
                    ),
                    objective=ObjectiveSection(
                        vital_signs=VitalSigns(
                            blood_pressure=template["soap"]["objective"]["vital_signs"]["blood_pressure"],
                            heart_rate=template["soap"]["objective"]["vital_signs"]["heart_rate"],
                            temperature=template["soap"]["objective"]["vital_signs"]["temperature"],
                            respiratory_rate=template["soap"]["objective"]["vital_signs"]["respiratory_rate"]
                        ),
                        physical_examination=template["soap"]["objective"]["physical_examination"]
                    ),
                    assessment=AssessmentSection(
                        primary_diagnosis=template["soap"]["assessment"]["primary_diagnosis"],
                        differential_diagnoses=template["soap"]["assessment"]["differential_diagnoses"],
                        clinical_impression=template["soap"]["assessment"]["clinical_impression"]
                    ),
                    plan=PlanSection(
                        treatment_plan=template["soap"]["plan"]["treatment_plan"],
                        medications=template["soap"]["plan"]["medications"],
                        follow_up=template["soap"]["plan"]["follow_up"],
                        patient_education=template["soap"]["plan"]["patient_education"]
                    )
                )
                
                # Create encounter
                encounter = EncounterModel(
                    patient_id=episode.patient_id,
                    episode_id=episode.id,
                    type=template["type"],
                    status=template["status"],
                    provider=Provider(
                        id=doctor.id,
                        name=f"Dr. {doctor.profile.first_name} {doctor.profile.last_name}",
                        specialty=doctor.profile.specialty,
                        department=doctor.profile.department
                    ),
                    soap=soap,
                    workflow=WorkflowInfo(
                        version=1,
                        last_saved=datetime.utcnow(),
                        signed_version=1 if template["status"] == EncounterStatusEnum.SIGNED else None
                    )
                )
                
                # Set signed info if encounter is signed
                if template["status"] == EncounterStatusEnum.SIGNED:
                    encounter.signed_at = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                    encounter.signed_by = doctor.id
                
                created_encounter = await encounter_repository.create(encounter)
                self.encounters.append(created_encounter)
                logger.info(f"Created encounter for episode {episode.id}: {template['type']}")
        
        logger.info(f"Seeded {len(self.encounters)} encounters")
    
    async def run_full_seeding(self, force: bool = False):
        """Run complete database seeding"""
        logger.info("Starting database seeding...")
        
        if not force:
            # Check if data already exists
            existing_patients = await patient_repository.get_all(limit=1)
            if existing_patients:
                logger.info("Database already contains data. Use force=True to re-seed.")
                return
        
        try:
            # Seed users first (needed for encounters)
            await self.seed_users()
            
            # Seed patients
            await self.seed_patients()
            
            # Seed episodes (depends on patients)
            await self.seed_episodes()
            
            # Seed encounters (depends on episodes and users)
            await self.seed_encounters()
            
            logger.info("Database seeding completed successfully!")
            logger.info(f"Summary: {len(self.users)} users, {len(self.patients)} patients, {len(self.episodes)} episodes, {len(self.encounters)} encounters")
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            raise


async def seed_database(force: bool = False):
    """Seed database with sample data"""
    seeder = DataSeeder()
    await seeder.run_full_seeding(force)


if __name__ == "__main__":
    import sys
    import os
    import argparse
    
    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Seed DiagnoAssist database with sample data")
    parser.add_argument("--force", action="store_true", help="Force seeding even if data exists")
    args = parser.parse_args()
    
    # Initialize database and run seeding
    async def main():
        await init_database()
        await seed_database(force=args.force)
    
    asyncio.run(main())