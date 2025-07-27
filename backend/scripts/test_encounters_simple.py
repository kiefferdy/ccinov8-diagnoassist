"""
Simple test script for encounter functionality
Tests the complete encounter flow from creation to signing
"""

import sys
import os
import uuid
from datetime import datetime, timezone
import json

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_encounters():
    """Test the complete encounter workflow"""
    print("Starting Encounter Backend Tests")
    print("=" * 50)
    
    try:
        # Test imports first
        print("\n[TEST 1] Testing imports...")
        from config.database import SessionLocal
        from repositories.repository_manager import RepositoryManager
        from services.encounter_service import EncounterService
        from schemas.encounter import EncounterCreate, SOAPSectionUpdate, Provider
        print("[OK] All imports successful")
        
        # Test database connection
        print("\n[TEST 2] Testing database connection...")
        db = SessionLocal()
        repos = RepositoryManager(db)
        service = EncounterService(repos)
        print("[OK] Database connection successful")
        
        # Create test patient
        print("\n[TEST 3] Creating test patient...")
        test_patient_data = {
            "medical_record_number": f"TEST{uuid.uuid4().hex[:8].upper()}",
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "status": "active"
        }
        
        patient = repos.patient.create(test_patient_data)
        db.commit()
        print(f"[OK] Created test patient: {patient.id}")
        
        # Create test episode
        print("\n[TEST 4] Creating test episode...")
        test_episode_data = {
            "patient_id": patient.id,
            "chief_complaint": "Persistent cough and fever",
            "encounter_type": "outpatient",
            "priority": "routine",
            "status": "active"
        }
        
        episode = repos.episode.create(test_episode_data)
        db.commit()
        print(f"[OK] Created test episode: {episode.id}")
        
        # Create encounter
        print("\n[TEST 5] Creating encounter...")
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
        print(f"[OK] Created encounter: {encounter.id}")
        print(f"     Status: {encounter.status}")
        print(f"     Type: {encounter.type}")
        print(f"     Provider: {encounter.provider_name}")
        
        # Update SOAP Subjective
        print("\n[TEST 6] Updating SOAP Subjective...")
        subjective_update = SOAPSectionUpdate(
            section="subjective",
            data={
                "chiefComplaint": "Persistent cough and fever",
                "hpi": "Patient presents with 5-day history of productive cough.",
                "ros": {"constitutional": "Positive for fever and fatigue"},
                "pmh": "No significant past medical history",
                "medications": "None",
                "allergies": "NKDA"
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), subjective_update)
        print(f"[OK] Updated SOAP Subjective")
        print(f"     Chief Complaint: {encounter.chief_complaint}")
        
        # Update SOAP Objective
        print("\n[TEST 7] Updating SOAP Objective...")
        objective_update = SOAPSectionUpdate(
            section="objective",
            data={
                "vitals": {
                    "bloodPressure": "120/80",
                    "heartRate": "88",
                    "temperature": "38.2",
                    "respiratoryRate": "18",
                    "oxygenSaturation": "96%"
                },
                "physicalExam": {
                    "general": "Alert and oriented, appears mildly ill",
                    "systems": {"respiratory": "Bilateral rhonchi, no wheezing"}
                }
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), objective_update)
        print(f"[OK] Updated SOAP Objective")
        
        # Update SOAP Assessment
        print("\n[TEST 8] Updating SOAP Assessment...")
        assessment_update = SOAPSectionUpdate(
            section="assessment",
            data={
                "clinicalImpression": "Acute bronchitis likely viral in nature.",
                "workingDiagnosis": {
                    "diagnosis": "Acute bronchitis",
                    "icd10": "J20.9",
                    "confidence": "probable"
                }
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), assessment_update)
        print(f"[OK] Updated SOAP Assessment")
        
        # Update SOAP Plan
        print("\n[TEST 9] Updating SOAP Plan...")
        plan_update = SOAPSectionUpdate(
            section="plan",
            data={
                "medications": [{
                    "id": "RX001",
                    "name": "Guaifenesin",
                    "dosage": "400mg",
                    "frequency": "Every 4 hours as needed",
                    "duration": "7 days"
                }],
                "followUp": {
                    "timeframe": "1 week",
                    "reason": "Re-evaluate if symptoms persist"
                }
            }
        )
        
        encounter = service.update_soap_section(str(encounter.id), plan_update)
        print(f"[OK] Updated SOAP Plan")
        
        # Check completion
        print("\n[TEST 10] Checking completion...")
        updated_encounter = service.get_encounter(str(encounter.id))
        print(f"[OK] Completion percentage: {updated_encounter.completion_percentage}%")
        
        # Sign encounter
        print("\n[TEST 11] Signing encounter...")
        signed_encounter = service.sign_encounter(str(encounter.id), "Dr. Test Smith")
        print(f"[OK] Encounter signed successfully")
        print(f"     Status: {signed_encounter.status}")
        print(f"     Signed by: {signed_encounter.signed_by}")
        
        # Test protection of signed encounter
        print("\n[TEST 12] Testing signed encounter protection...")
        try:
            test_update = SOAPSectionUpdate(
                section="subjective",
                data={"chiefComplaint": "Modified complaint"}
            )
            service.update_soap_section(str(encounter.id), test_update)
            print("[ERROR] Should not be able to modify signed encounter")
            return False
        except RuntimeError as e:
            print(f"[OK] Correctly prevented modification: {str(e)}")
        
        # Get encounters by episode
        print("\n[TEST 13] Getting encounters by episode...")
        encounters = service.get_encounters_by_episode(str(episode.id))
        print(f"[OK] Found {len(encounters)} encounters for episode")
        
        # Get encounter stats
        print("\n[TEST 14] Getting encounter stats...")
        stats = service.get_encounter_stats(str(episode.id))
        print(f"[OK] Stats - Total: {stats.total}, Draft: {stats.draft}, Signed: {stats.signed}")
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! Encounter backend is working correctly.")
        
        # Cleanup
        print("\nCleaning up test data...")
        repos.encounter.delete(str(encounter.id))
        repos.episode.delete(str(episode.id))
        repos.patient.delete(str(patient.id))
        db.commit()
        print("[OK] Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        try:
            db.rollback()
        except:
            pass
        return False
    
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    success = test_encounters()
    if success:
        print("\nAll tests completed successfully!")
    else:
        print("\nSome tests failed!")
    sys.exit(0 if success else 1)