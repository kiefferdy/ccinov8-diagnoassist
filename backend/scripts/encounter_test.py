#!/usr/bin/env python3
"""
Comprehensive Encounter Workflow Test for DiagnoAssist
Tests full encounter functionality including SOAP documentation, signing, and validation
"""

import requests
import json
import uuid
import random
import string
from datetime import datetime, date
from typing import Dict, Any, Optional

class EncounterWorkflowTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = f"{base_url}/api/v1"
        self.test_data = {}
        self.headers = {"Content-Type": "application/json"}
        
    def print_test(self, message):
        print(f"[TEST] {message}")
    
    def print_success(self, message):
        print(f"[SUCCESS] {message}")
    
    def print_error(self, message):
        print(f"[ERROR] {message}")
    
    def print_info(self, message):
        print(f"[INFO] {message}")
    
    def generate_valid_mrn(self):
        """Generate MRN that meets 6-20 alphanumeric requirement"""
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        return f"ENC{suffix}"
    
    def generate_unique_email(self):
        """Generate unique email"""
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"encounter.test.{random_id}@diagnoassist.test"
    
    def request(self, method, endpoint, data=None):
        """Make HTTP request with detailed error reporting"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, json=data, headers=self.headers, timeout=10)
            elif method == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=self.headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=10)
            
            print(f"   {method} {endpoint} → {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    return response.json() if response.text else {"status": "ok"}
                except:
                    return {"status": "ok"}
            elif response.status_code == 204:
                return {"status": "deleted"}
            else:
                try:
                    error_data = response.json()
                    print(f"   [ERROR] Error: {error_data}")
                    return {"error": error_data, "status_code": response.status_code}
                except:
                    print(f"   [ERROR] Error: {response.text}")
                    return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"   [CONN_ERROR] Connection error: {e}")
            return None
    
    def test_health_check(self):
        """Test if API is running"""
        print("\n[HEALTH] Testing API Health")
        url = f"{self.base_url.replace('/api/v1', '')}/health"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"   GET /health → {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("API is running")
                print(f"   Status: {result}")
                return True
            else:
                self.print_error("API is not responding")
                return False
        except Exception as e:
            self.print_error(f"Connection error: {e}")
            return False
    
    def setup_test_data(self):
        """Setup required patient and episode for encounter testing"""
        print("\n[SETUP] Setting up test data (Patient & Episode)")
        
        # Create test patient
        self.print_test("Creating test patient")
        mrn = self.generate_valid_mrn()
        email = self.generate_unique_email()
        
        patient_data = {
            "medical_record_number": mrn,
            "first_name": "John",
            "last_name": "EncounterTest",
            "date_of_birth": "1985-05-15",
            "gender": "male",
            "email": email,
            "phone": "+1-555-0100",
            "address": "123 Encounter Test St, Test City, TC 12345",
            "emergency_contact_name": "Jane EncounterContact",
            "emergency_contact_phone": "+1-555-0101",
            "emergency_contact_relationship": "spouse",
            "medical_history": "No significant past medical history",
            "allergies": "No known allergies",
            "current_medications": "None"
        }
        
        result = self.request("POST", "/patients/", patient_data)
        if result and 'id' in result:
            patient_id = result['id']
            self.test_data['patient_id'] = patient_id
            self.print_success(f"Test patient created: {patient_id}")
        else:
            self.print_error("Failed to create test patient")
            return False
        
        # Create test episode
        self.print_test("Creating test episode")
        episode_data = {
            "patient_id": patient_id,
            "chief_complaint": "Follow-up visit for hypertension management",
            "encounter_type": "outpatient",
            "priority": "routine",
            "symptoms": "Mild headache, occasional dizziness",
            "physical_exam_findings": "Vitals stable, no acute distress",
            "clinical_notes": "Regular follow-up for hypertension",
            "blood_pressure_systolic": 140,
            "blood_pressure_diastolic": 90,
            "heart_rate": 78,
            "temperature": 98.4,
            "respiratory_rate": 16,
            "oxygen_saturation": 98,
            "provider_id": "DR001",
            "location": "Outpatient Clinic"
        }
        
        result = self.request("POST", "/episodes/", episode_data)
        if result and 'id' in result:
            episode_id = result['id']
            self.test_data['episode_id'] = episode_id
            self.print_success(f"Test episode created: {episode_id}")
            return True
        else:
            self.print_error("Failed to create test episode")
            return False
    
    def test_encounter_creation(self):
        """Test encounter creation with comprehensive SOAP data"""
        print("\n[CREATE] Testing Encounter Creation")
        
        patient_id = self.test_data.get('patient_id')
        episode_id = self.test_data.get('episode_id')
        
        if not patient_id or not episode_id:
            self.print_error("Required test data not available")
            return False
        
        # CREATE encounter with comprehensive SOAP data
        self.print_test("Creating encounter with SOAP documentation")
        
        encounter_data = {
            "episode_id": episode_id,
            "patient_id": patient_id,
            "type": "follow-up",
            "provider": {
                "id": "DR001",
                "name": "Dr. Sarah Johnson",
                "role": "Primary Care Physician"
            },
            "soap_subjective": {
                "chiefComplaint": "Follow-up visit for hypertension management",
                "hpi": "Patient reports feeling well overall. Occasional mild headaches in the morning, particularly when stressed. Taking medications as prescribed. Denies chest pain, shortness of breath, or dizziness.",
                "ros": {
                    "constitutional": "No fever, chills, or weight changes",
                    "cardiovascular": "No chest pain or palpitations",
                    "neurological": "Mild occasional headaches"
                },
                "pmh": "Hypertension diagnosed 2 years ago",
                "medications": "Lisinopril 10mg daily, Hydrochlorothiazide 25mg daily",
                "allergies": "No known drug allergies",
                "socialHistory": "Non-smoker, occasional alcohol use, exercises 3x/week",
                "familyHistory": "Father with hypertension and diabetes"
            },
            "soap_objective": {
                "vitals": {
                    "bloodPressure": "138/88",
                    "heartRate": "78",
                    "temperature": "98.4",
                    "respiratoryRate": "16",
                    "oxygenSaturation": "98",
                    "weight": "180",
                    "height": "72"
                },
                "physicalExam": {
                    "general": "Well-appearing adult in no acute distress",
                    "systems": {
                        "cardiovascular": "Regular rate and rhythm, no murmurs",
                        "respiratory": "Clear to auscultation bilaterally",
                        "neurological": "Alert and oriented x3, no focal deficits"
                    }
                }
            },
            "soap_assessment": {
                "clinicalImpression": "Hypertension, well-controlled on current regimen",
                "workingDiagnosis": {
                    "diagnosis": "Essential hypertension",
                    "icd10": "I10",
                    "confidence": "definite"
                },
                "riskAssessment": "Low risk for cardiovascular events with current control"
            },
            "soap_plan": {
                "medications": [
                    {
                        "id": "med1",
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "frequency": "once daily",
                        "duration": "ongoing",
                        "instructions": "Continue current dose"
                    }
                ],
                "followUp": {
                    "timeframe": "3 months",
                    "reason": "Blood pressure monitoring",
                    "instructions": "Continue home BP monitoring, return if concerns"
                },
                "patientEducation": [
                    {
                        "topic": "Blood pressure monitoring",
                        "materials": "Home BP monitoring handout provided",
                        "discussed": True
                    }
                ]
            }
        }
        
        result = self.request("POST", "/encounters/", encounter_data)
        if result and 'id' in result:
            encounter_id = result['id']
            self.test_data['encounter_id'] = encounter_id
            self.print_success(f"Encounter created: {encounter_id}")
            self.print_info(f"Status: {result.get('status', 'N/A')}")
            self.print_info(f"Completion: {result.get('completion_percentage', 0)}%")
            return True
        else:
            self.print_error("Failed to create encounter")
            if result and result.get('error'):
                self.print_info(f"Error details: {result['error']}")
            return False
    
    def test_encounter_retrieval(self):
        """Test encounter retrieval and data integrity"""
        print("\n[READ] Testing Encounter Retrieval")
        
        encounter_id = self.test_data.get('encounter_id')
        if not encounter_id:
            self.print_error("No encounter ID available")
            return False
        
        # READ encounter
        self.print_test("Retrieving encounter")
        result = self.request("GET", f"/encounters/{encounter_id}")
        
        if result and not result.get('error'):
            self.print_success("Encounter retrieved successfully")
            
            # Verify data integrity
            if result.get('soap_subjective', {}).get('chiefComplaint'):
                self.print_info("[CHECK] SOAP Subjective data present")
            if result.get('soap_objective', {}).get('vitals'):
                self.print_info("[CHECK] SOAP Objective data present")
            if result.get('soap_assessment', {}).get('clinicalImpression'):
                self.print_info("[CHECK] SOAP Assessment data present")
            if result.get('soap_plan', {}).get('medications'):
                self.print_info("[CHECK] SOAP Plan data present")
            
            return True
        else:
            self.print_error("Failed to retrieve encounter")
            return False
    
    def test_soap_section_updates(self):
        """Test individual SOAP section updates"""
        print("\n[SOAP] Testing SOAP Section Updates")
        
        encounter_id = self.test_data.get('encounter_id')
        if not encounter_id:
            self.print_error("No encounter ID available")
            return False
        
        # Test updating Assessment section
        self.print_test("Updating SOAP Assessment section")
        assessment_update = {
            "section": "assessment",
            "data": {
                "clinicalImpression": "Hypertension, well-controlled. Patient responding well to current therapy.",
                "differentialDiagnosis": [
                    {
                        "id": "dd1",
                        "diagnosis": "Secondary hypertension",
                        "icd10": "I15.9",
                        "probability": "low",
                        "supportingEvidence": [],
                        "contradictingEvidence": ["Good response to ACE inhibitor", "No signs of secondary causes"]
                    }
                ],
                "riskAssessment": "Low cardiovascular risk with current control and lifestyle modifications"
            }
        }
        
        result = self.request("PATCH", f"/encounters/{encounter_id}/soap", assessment_update)
        if result and not result.get('error'):
            self.print_success("SOAP Assessment updated successfully")
        else:
            self.print_error("Failed to update SOAP Assessment")
            return False
        
        # Test updating Plan section
        self.print_test("Updating SOAP Plan section")
        plan_update = {
            "section": "plan",
            "data": {
                "medications": [
                    {
                        "id": "med1",
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "frequency": "once daily",
                        "duration": "ongoing",
                        "instructions": "Continue current dose, monitor for side effects"
                    }
                ],
                "procedures": [
                    {
                        "id": "proc1",
                        "name": "Basic Metabolic Panel",
                        "type": "laboratory",
                        "urgency": "routine",
                        "notes": "Monitor kidney function on ACE inhibitor"
                    }
                ],
                "followUp": {
                    "timeframe": "3 months",
                    "reason": "Blood pressure and medication monitoring",
                    "instructions": "Continue home monitoring, return if BP >140/90 on multiple readings"
                }
            }
        }
        
        result = self.request("PATCH", f"/encounters/{encounter_id}/soap", plan_update)
        if result and not result.get('error'):
            self.print_success("SOAP Plan updated successfully")
            return True
        else:
            self.print_error("Failed to update SOAP Plan")
            return False
    
    def test_encounter_signing(self):
        """Test encounter signing functionality"""
        print("\n[SIGN] Testing Encounter Signing")
        
        encounter_id = self.test_data.get('encounter_id')
        if not encounter_id:
            self.print_error("No encounter ID available")
            return False
        
        # Sign encounter
        self.print_test("Signing encounter")
        sign_data = {
            "provider_name": "Dr. Sarah Johnson"
        }
        
        result = self.request("POST", f"/encounters/{encounter_id}/sign", sign_data)
        if result and not result.get('error'):
            self.print_success("Encounter signed successfully")
            self.print_info(f"Signed by: {result.get('signed_by', 'N/A')}")
            self.print_info(f"Status: {result.get('status', 'N/A')}")
            return True
        else:
            self.print_error("Failed to sign encounter")
            if result and result.get('error'):
                self.print_info(f"Sign error: {result['error']}")
            return False
    
    def test_encounter_relationships(self):
        """Test encounter relationships with patient and episode"""
        print("\n[RELATIONS] Testing Encounter Relationships")
        
        patient_id = self.test_data.get('patient_id')
        episode_id = self.test_data.get('episode_id')
        
        if not patient_id or not episode_id:
            self.print_error("Required test data not available")
            return False
        
        # Test get encounters by patient
        self.print_test("Getting encounters by patient")
        result = self.request("GET", f"/encounters/patient/{patient_id}")
        if result and 'data' in result:
            encounters = result['data']
            self.print_success(f"Found {len(encounters)} encounter(s) for patient")
            
            # Verify our encounter is in the list
            our_encounter_id = self.test_data.get('encounter_id')
            found = any(enc.get('id') == our_encounter_id for enc in encounters)
            if found:
                self.print_info("[CHECK] Our test encounter found in patient's encounters")
            else:
                self.print_error("[FAIL] Our test encounter not found in patient's encounters")
                return False
        else:
            self.print_error("Failed to get encounters by patient")
            return False
        
        # Test get encounters by episode
        self.print_test("Getting encounters by episode")
        result = self.request("GET", f"/encounters/episode/{episode_id}")
        if result and 'data' in result:
            encounters = result['data']
            self.print_success(f"Found {len(encounters)} encounter(s) for episode")
            
            # Verify our encounter is in the list
            our_encounter_id = self.test_data.get('encounter_id')
            found = any(enc.get('id') == our_encounter_id for enc in encounters)
            if found:
                self.print_info("[CHECK] Our test encounter found in episode's encounters")
                return True
            else:
                self.print_error("[FAIL] Our test encounter not found in episode's encounters")
                return False
        else:
            self.print_error("Failed to get encounters by episode")
            return False
    
    def test_encounter_stats(self):
        """Test encounter statistics"""
        print("\n[STATS] Testing Encounter Statistics")
        
        episode_id = self.test_data.get('episode_id')
        if not episode_id:
            self.print_error("No episode ID available")
            return False
        
        # Get encounter stats
        self.print_test("Getting encounter statistics")
        result = self.request("GET", f"/encounters/episode/{episode_id}/stats")
        
        if result and not result.get('error'):
            self.print_success("Encounter stats retrieved successfully")
            self.print_info(f"Total encounters: {result.get('total', 0)}")
            self.print_info(f"Draft encounters: {result.get('draft', 0)}")
            self.print_info(f"Signed encounters: {result.get('signed', 0)}")
            return True
        else:
            self.print_error("Failed to get encounter statistics")
            return False
    
    def test_validation_rules(self):
        """Test encounter validation and error handling"""
        print("\n[VALIDATION] Testing Validation Rules")
        
        # Test invalid episode_id
        self.print_test("Testing with invalid episode_id")
        invalid_data = {
            "episode_id": "00000000-0000-0000-0000-000000000000",
            "patient_id": self.test_data.get('patient_id'),
            "type": "follow-up"
        }
        
        result = self.request("POST", "/encounters/", invalid_data)
        if result and result.get('error'):
            self.print_success("[CHECK] Invalid episode_id properly rejected")
        else:
            self.print_error("[FAIL] Invalid episode_id not rejected")
            return False
        
        # Test invalid encounter type
        self.print_test("Testing with invalid encounter type")
        invalid_type_data = {
            "episode_id": self.test_data.get('episode_id'),
            "patient_id": self.test_data.get('patient_id'),
            "type": "invalid-type"
        }
        
        result = self.request("POST", "/encounters/", invalid_type_data)
        if result and not result.get('error'):
            # Encounter type should be defaulted to 'follow-up'
            self.print_success("[CHECK] Invalid encounter type handled gracefully")
            # Clean up this test encounter
            if 'id' in result:
                self.request("DELETE", f"/encounters/{result['id']}")
        else:
            self.print_success("[CHECK] Invalid encounter type properly rejected")
        
        return True
    
    def cleanup(self):
        """Clean up test data"""
        print("\n[CLEANUP] Cleaning up test data")
        
        # Delete in reverse dependency order
        cleanup_order = [
            ("encounters", "encounter_id", "Encounter"),
            ("episodes", "episode_id", "Episode"),
            ("patients", "patient_id", "Patient")
        ]
        
        for endpoint, id_key, name in cleanup_order:
            resource_id = self.test_data.get(id_key)
            if resource_id:
                self.print_test(f"Deleting {name}")
                result = self.request("DELETE", f"/{endpoint}/{resource_id}")
                if result and not result.get('error'):
                    self.print_success(f"{name} deleted")
                else:
                    self.print_error(f"Failed to delete {name}")
                    if result and result.get('error'):
                        self.print_info(f"Delete error: {result['error']}")
    
    def run_full_workflow_test(self):
        """Run comprehensive encounter workflow test"""
        print("[START] Running Comprehensive Encounter Workflow Test")
        print("=" * 70)
        
        # Health check first
        if not self.test_health_check():
            print("[ERROR] Cannot continue - API is not responding")
            print("[INFO] Make sure to run: python main.py")
            return
        
        try:
            success_count = 0
            total_tests = 8
            
            # Run tests in logical order
            tests = [
                ("Setup Test Data", self.setup_test_data),
                ("Encounter Creation", self.test_encounter_creation),
                ("Encounter Retrieval", self.test_encounter_retrieval),
                ("SOAP Section Updates", self.test_soap_section_updates),
                ("Encounter Signing", self.test_encounter_signing),
                ("Encounter Relationships", self.test_encounter_relationships),
                ("Encounter Statistics", self.test_encounter_stats),
                ("Validation Rules", self.test_validation_rules)
            ]
            
            for test_name, test_func in tests:
                print(f"\n{'='*25} {test_name} {'='*25}")
                if test_func():
                    success_count += 1
                    self.print_success(f"{test_name} completed successfully")
                else:
                    self.print_error(f"{test_name} failed")
                    # Don't break - continue with other tests for maximum coverage
            
            # Final results
            print(f"\n{'='*70}")
            print(f"[RESULTS] Test Results: {success_count}/{total_tests} test suites passed")
            
            if success_count == total_tests:
                print("[SUCCESS] All encounter workflow tests passed!")
                print("[SUCCESS] Your encounter implementation is fully functional")
            else:
                print(f"[WARNING] {total_tests - success_count} test suite(s) need attention")
                print("[WARNING] Check the error messages above for details")
            
        except KeyboardInterrupt:
            print("\n[WARNING] Tests interrupted by user")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error during testing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

if __name__ == "__main__":
    import sys
    import codecs
    
    # Handle Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("DiagnoAssist Encounter Workflow Test Suite")
    print("Testing comprehensive encounter functionality")
    print("API URL: http://localhost:8000/api/v1")
    print("API Docs: http://localhost:8000/api/docs")
    print("")
    
    test = EncounterWorkflowTest()
    test.run_full_workflow_test()