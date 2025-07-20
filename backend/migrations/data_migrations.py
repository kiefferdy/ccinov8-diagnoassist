"""
Data migration utilities for DiagnoAssist
"""

import asyncio
import json
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.patient import Patient
from models.episode import Episode
from fhir.models.patient import PatientFHIRModel

async def migrate_patients_to_fhir():
    """
    Migrate existing patient data to FHIR format
    """
    db = SessionLocal()
    try:
        patients = db.query(Patient).all()
        print(f"Migrating {len(patients)} patients to FHIR format...")
        
        for patient in patients:
            # Create FHIR Patient resource
            fhir_patient = PatientFHIRModel.create_fhir_patient(
                patient_id=patient.id,
                first_name=patient.first_name,
                last_name=patient.last_name,
                birth_date=patient.date_of_birth,
                gender=patient.gender,
                phone=patient.contact_info.get('phone') if patient.contact_info else None,
                email=patient.contact_info.get('email') if patient.contact_info else None,
                address=patient.contact_info.get('address') if patient.contact_info else None
            )
            
            # Store FHIR data in the fhir_resources table
            from models.fhir_resource import FHIRResource
            fhir_resource = FHIRResource(
                resource_type="Patient",
                resource_id=patient.id,
                fhir_data=fhir_patient.dict(),
                internal_id=patient.id
            )
            db.add(fhir_resource)
        
        db.commit()
        print("Patient FHIR migration completed successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error during patient FHIR migration: {e}")
        raise
    finally:
        db.close()

async def seed_sample_data():
    """
    Seed database with sample data for development
    """
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Patient).first():
            print("Sample data already exists, skipping seed")
            return
        
        # Create sample patients
        sample_patients = [
            {
                "id": "patient-1",
                "first_name": "John",
                "last_name": "Doe", 
                "date_of_birth": "1985-03-15",
                "gender": "male",
                "contact_info": {
                    "phone": "+1234567890",
                    "email": "john.doe@email.com",
                    "address": {
                        "street": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zip": "12345"
                    }
                },
                "medical_history": {
                    "allergies": ["Penicillin"],
                    "chronic_conditions": [],
                    "surgical_history": []
                }
            },
            {
                "id": "patient-2", 
                "first_name": "Jane",
                "last_name": "Smith",
                "date_of_birth": "1990-07-22",
                "gender": "female",
                "contact_info": {
                    "phone": "+1987654321",
                    "email": "jane.smith@email.com"
                },
                "medical_history": {
                    "allergies": [],
                    "chronic_conditions": ["Hypertension"],
                    "surgical_history": ["Appendectomy (2018)"]
                }
            }
        ]
        
        for patient_data in sample_patients:
            patient = Patient(**patient_data)
            db.add(patient)
        
        db.commit()
        print(f"Seeded {len(sample_patients)} sample patients")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding sample data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Run data migrations
    asyncio.run(seed_sample_data())
    asyncio.run(migrate_patients_to_fhir())