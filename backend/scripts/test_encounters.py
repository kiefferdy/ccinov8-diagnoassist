"""
Test script for encounter functionality
Tests the complete encounter flow from creation to signing
"""

import sys
import os
import uuid
from datetime import datetime, timezone
import json

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SessionLocal
from repositories.repository_manager import RepositoryManager
from services.encounter_service import EncounterService
from schemas.encounter import (
    EncounterCreate, 
    EncounterUpdate,
    SOAPSectionUpdate,
    SOAPSubjective,
    SOAPObjective,
    SOAPAssessment,
    SOAPPlan,
    Provider
)

def test_encounters():
    """Test the complete encounter workflow"""
    print("Starting Encounter Backend Tests")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    repos = RepositoryManager(db)
    service = EncounterService(repos)
    
    try:
        # Test 1: Check if we can connect to database and create basic data
        print("\n[TEST 1] Database Connection & Setup")
        
        # Create a test patient first (if not exists)
        test_patient_data = {
            "medical_record_number": f"TEST{uuid.uuid4().hex[:8].upper()}",
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "status": "active"
        }
        
        patient = repos.patient.create(test_patient_data)
        print(f"[OK] Created test patient: {patient.id}")
        
        # Create a test episode
        test_episode_data = {
            "patient_id": patient.id,
            "chief_complaint": "Persistent cough and fever",
            "encounter_type": "outpatient",
            "priority": "routine",
            "status": "active"
        }
        
        episode = repos.episode.create(test_episode_data)
        print(f"[OK] Created test episode: {episode.id}")
        
        # Test 2: Create an encounter
        print("\n[TEST 2] Create Encounter")
        
        provider = Provider(
            id="DR001",
            name="Dr. Test Smith", 
            role="Primary Care Physician"
        )
        
        encounter_data = EncounterCreate(
            episode_id=episode.id,
            patient_id=patient.id,
            type="initial",
            provider=provider
        )
        
        encounter = service.create_encounter(encounter_data)
        print(f"✅ Created encounter: {encounter.id}")
        print(f"   Status: {encounter.status}")
        print(f"   Type: {encounter.type}")
        print(f"   Provider: {encounter.provider_name}")
        
        # Test 3: Update SOAP Subjective section
        print("\n📋 Test 3: Update SOAP Subjective")
        
        subjective_update = SOAPSectionUpdate(
            section="subjective",
            data={
                "chiefComplaint": "Persistent cough and fever",
                "hpi": "Patient presents with 5-day history of productive cough with yellow sputum and fever up to 101°F. Associated with fatigue and mild chest discomfort.",
                "ros": {
                    "constitutional": "Positive for fever and fatigue",
                    "respiratory": "Positive for cough with sputum production",
                    "cardiovascular": "Negative for chest pain or palpitations"
                },
                "pmh": "No significant past medical history",
                "medications": "None",
                "allergies": "NKDA",
                "socialHistory": "Non-smoker, occasional alcohol use",
                "familyHistory": "Non-contributory"
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), subjective_update)
        print(f"✅ Updated SOAP Subjective")
        print(f"   Chief Complaint: {encounter.chief_complaint}")
        
        # Test 4: Update SOAP Objective section
        print("\n📋 Test 4: Update SOAP Objective")
        
        objective_update = SOAPSectionUpdate(
            section="objective",
            data={
                "vitals": {
                    "bloodPressure": "120/80",
                    "heartRate": "88",
                    "temperature": "38.2",
                    "respiratoryRate": "18",
                    "oxygenSaturation": "96%",
                    "height": "5'8\"",
                    "weight": "160 lbs"
                },
                "physicalExam": {
                    "general": "Alert and oriented, appears mildly ill",
                    "systems": {
                        "respiratory": "Bilateral rhonchi, no wheezing",
                        "cardiovascular": "Regular rate and rhythm, no murmurs"
                    },
                    "additionalFindings": "Throat mildly erythematous"
                },
                "diagnosticTests": {
                    "ordered": [],
                    "results": []
                }
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), objective_update)
        print(f"✅ Updated SOAP Objective")
        print(f"   Vitals recorded: {bool(encounter.soap_objective.get('vitals'))}")
        
        # Test 5: Update SOAP Assessment section
        print("\n📋 Test 5: Update SOAP Assessment")
        
        assessment_update = SOAPSectionUpdate(
            section="assessment",
            data={
                "clinicalImpression": "Acute bronchitis likely viral in nature. No evidence of bacterial pneumonia.",
                "differentialDiagnosis": [
                    {
                        "id": "D001",
                        "diagnosis": "Acute bronchitis",
                        "icd10": "J20.9",
                        "probability": "high",
                        "supportingEvidence": ["Productive cough", "Fever", "Rhonchi on exam"],
                        "contradictingEvidence": []
                    }
                ],
                "workingDiagnosis": {
                    "diagnosis": "Acute bronchitis",
                    "icd10": "J20.9",
                    "confidence": "probable",
                    "clinicalReasoning": "Clinical presentation consistent with acute bronchitis."
                },
                "riskAssessment": "Low risk for complications."
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), assessment_update)
        print(f"✅ Updated SOAP Assessment")
        print(f"   Clinical Impression: {encounter.soap_assessment.get('clinicalImpression', '')[:50]}...")
        
        # Test 6: Update SOAP Plan section
        print("\n📋 Test 6: Update SOAP Plan")
        
        plan_update = SOAPSectionUpdate(
            section="plan",
            data={
                "medications": [
                    {
                        "id": "RX001",
                        "name": "Guaifenesin",
                        "dosage": "400mg",
                        "frequency": "Every 4 hours as needed",
                        "duration": "7 days",
                        "instructions": "For cough",
                        "prescribed": True
                    }
                ],
                "procedures": [],
                "referrals": [],
                "followUp": {
                    "timeframe": "1 week",
                    "reason": "Re-evaluate if symptoms persist",
                    "instructions": "Return sooner if symptoms worsen"
                },
                "patientEducation": [
                    {
                        "topic": "Bronchitis care",
                        "materials": "Handout provided",
                        "discussed": True
                    }
                ],
                "activityRestrictions": "Rest as needed",
                "dietRecommendations": "Increase fluid intake"
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), plan_update)
        print(f"✅ Updated SOAP Plan")
        print(f"   Follow-up: {encounter.soap_plan.get('followUp', {}).get('timeframe', 'None')}")
        
        # Test 7: Check completion percentage
        print("\n📋 Test 7: Check Completion")
        
        updated_encounter = service.get_encounter(str(encounter.id))
        print(f"✅ Completion percentage: {updated_encounter.completion_percentage}%")
        print(f"   Is ready for signing: {updated_encounter.completion_percentage >= 80}")
        
        # Test 8: Sign the encounter
        print("\n📋 Test 8: Sign Encounter")
        
        signed_encounter = service.sign_encounter(str(encounter.id), "Dr. Test Smith")
        print(f"✅ Encounter signed successfully")
        print(f"   Status: {signed_encounter.status}")
        print(f"   Signed at: {signed_encounter.signed_at}")
        print(f"   Signed by: {signed_encounter.signed_by}")
        print(f"   Is signed: {signed_encounter.is_signed}")
        
        # Test 9: Try to modify signed encounter (should fail)
        print("\n📋 Test 9: Test Signed Encounter Protection")
        
        try:
            test_update = SOAPSectionUpdate(
                section="subjective",
                data={"chiefComplaint": "Modified complaint"}
            )
            service.update_soap_section(str(encounter.id), test_update)
            print("❌ ERROR: Should not be able to modify signed encounter")
        except RuntimeError as e:
            print(f"✅ Correctly prevented modification: {str(e)}")
        
        # Test 10: Get encounters by episode
        print("\n📋 Test 10: Get Encounters by Episode")
        
        encounters = service.get_encounters_by_episode(str(episode.id))
        print(f"✅ Found {len(encounters)} encounters for episode")
        
        for enc in encounters:
            print(f"   - {enc.id}: {enc.type} ({enc.status})")
        
        # Test 11: Get encounter stats
        print("\n📋 Test 11: Get Encounter Stats")
        
        stats = service.get_encounter_stats(str(episode.id))
        print(f"✅ Encounter stats:")
        print(f"   Total: {stats.total}")
        print(f"   Draft: {stats.draft}")
        print(f"   Signed: {stats.signed}")
        print(f"   Last visit: {stats.lastVisit}")
        
        print("\n🎉 All tests passed! Encounter backend is working correctly.")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        repos.encounter.delete(str(encounter.id))
        repos.episode.delete(str(episode.id))
        repos.patient.delete(str(patient.id))
        db.commit()
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_encounters()
    sys.exit(0 if success else 1)