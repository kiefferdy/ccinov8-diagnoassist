#!/usr/bin/env python3
"""
Validation-Aware CRUD Test for DiagnoAssist
Handles all known validation rules
"""

import requests
import json
import uuid
import random
import string
from datetime import datetime, date

class ValidationAwareCRUDTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = f"{base_url}/api/v1"
        self.test_data = {}
        self.headers = {"Content-Type": "application/json"}
    
    def print_test(self, message):
        print(f"🔄 {message}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def generate_valid_mrn(self):
        """Generate MRN that meets 6-20 alphanumeric requirement"""
        # Generate exactly 16 characters: TEST + 12 random alphanumeric
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        return f"TEST{suffix}"
    
    def generate_unique_email(self):
        """Generate unique email"""
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test.patient.{random_id}@diagnoassist.test"
    
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
                # Show detailed error information
                try:
                    error_data = response.json()
                    print(f"   ❌ Error: {error_data}")
                    return {"error": error_data, "status_code": response.status_code}
                except:
                    print(f"   ❌ Error: {response.text}")
                    return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"   💥 Connection error: {e}")
            return None
    
    def test_health_check(self):
        """Test if API is running"""
        print("\n🏥 Testing API Health")
        # Health endpoint is at root, not under /api/v1
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
    
    def test_patient_crud(self):
        """Test Patient CRUD with proper validation"""
        print("\n👤 Testing Patient CRUD")
        
        # CREATE with validation-compliant data
        self.print_test("Creating patient")
        
        # Generate compliant data
        mrn = self.generate_valid_mrn()
        email = self.generate_unique_email()
        
        self.print_info(f"Generated MRN: {mrn} (length: {len(mrn)})")
        self.print_info(f"Generated email: {email}")
        
        patient_data = {
            "medical_record_number": mrn,
            "first_name": "John",
            "last_name": "TestPatient",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "email": email,
            "phone": "+1-555-1234",
            "address": "123 Test Street, Test City, TC 12345",
            "emergency_contact_name": "Jane TestContact",
            "emergency_contact_phone": "+1-555-5678",
            "emergency_contact_relationship": "spouse",
            "medical_history": "No significant past medical history",
            "allergies": "No known allergies",
            "current_medications": "None"
        }
        
        result = self.request("POST", "/patients/", patient_data)
        
        if result and 'id' in result:
            patient_id = result['id']
            self.test_data['patient_id'] = patient_id
            self.print_success(f"Patient created: {patient_id}")
            self.print_info(f"Patient MRN: {result.get('medical_record_number', 'N/A')}")
        elif result and result.get('error'):
            self.print_error("Failed to create patient")
            self.print_info(f"Validation error details: {result['error']}")
            return False
        else:
            self.print_error("Failed to create patient - no response")
            return False
        
        # READ
        self.print_test("Reading patient")
        result = self.request("GET", f"/patients/{patient_id}")
        if result and not result.get('error'):
            self.print_success("Patient retrieved successfully")
            # Verify data integrity
            if result.get('medical_record_number') == mrn:
                self.print_info("✓ MRN matches")
            if result.get('email') == email:
                self.print_info("✓ Email matches")
        else:
            self.print_error("Failed to read patient")
            return False
        
        # UPDATE
        self.print_test("Updating patient")
        update_data = {
            "phone": "+1-555-9999",
            "address": "456 Updated Street, New City, NC 54321"
        }
        result = self.request("PUT", f"/patients/{patient_id}", update_data)
        if result and not result.get('error'):
            self.print_success("Patient updated successfully")
        else:
            self.print_error("Failed to update patient")
            if result and result.get('error'):
                self.print_info(f"Update error: {result['error']}")
        
        return True
    
    def test_episode_crud(self):
        """Test Episode CRUD with proper validation"""
        print("\n📋 Testing Episode CRUD")
        
        patient_id = self.test_data.get('patient_id')
        if not patient_id:
            self.print_error("No patient ID available")
            return False
        
        # CREATE
        self.print_test("Creating episode")
        episode_data = {
            "patient_id": patient_id,
            "chief_complaint": "Headache and dizziness lasting 2 days, worsening with stress",
            "encounter_type": "outpatient",
            "priority": "routine",
            "symptoms": "Bilateral headache, dizziness, mild nausea, photophobia",
            "physical_exam_findings": "Alert and oriented, no focal neurological deficits",
            "clinical_notes": "Patient reports gradual onset headache with stress triggers",
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 72,
            "temperature": 98.6,
            "respiratory_rate": 16,
            "oxygen_saturation": 98,
            "provider_id": "DR001",
            "location": "Outpatient Clinic"
        }
        
        result = self.request("POST", "/episodes/", episode_data)
        if result and 'id' in result:
            episode_id = result['id']
            self.test_data['episode_id'] = episode_id
            self.print_success(f"Episode created: {episode_id}")
        elif result and result.get('error'):
            self.print_error("Failed to create episode")
            self.print_info(f"Validation error: {result['error']}")
            return False
        else:
            self.print_error("Failed to create episode - no response")
            return False
        
        # READ
        self.print_test("Reading episode")
        result = self.request("GET", f"/episodes/{episode_id}")
        if result and not result.get('error'):
            self.print_success("Episode retrieved successfully")
        else:
            self.print_error("Failed to read episode")
            return False
        
        # UPDATE
        self.print_test("Updating episode")
        update_data = {
            "assessment_notes": "Tension headache likely secondary to stress and poor sleep hygiene",
            "plan_notes": "Prescribe analgesics, recommend stress management techniques, follow-up PRN"
        }
        result = self.request("PUT", f"/episodes/{episode_id}", update_data)
        if result and not result.get('error'):
            self.print_success("Episode updated successfully")
        else:
            self.print_error("Failed to update episode")
        
        return True
    
    def test_diagnosis_crud(self):
        """Test Diagnosis CRUD with proper validation"""
        print("\n🔬 Testing Diagnosis CRUD")
        
        episode_id = self.test_data.get('episode_id')
        if not episode_id:
            self.print_error("No episode ID available")
            return False
        
        # CREATE
        self.print_test("Creating diagnosis")
        diagnosis_data = {
            "episode_id": episode_id,
            "condition_name": "Tension-type headache",
            "icd10_code": "G44.209",
            "snomed_code": "398057008",
            "confidence_level": "medium",
            "ai_probability": 0.78,
            "ai_reasoning": "Patient presents with bilateral, pressing headache associated with stress triggers. No focal neurological signs. Consistent with tension-type headache pattern.",
            "supporting_symptoms": "Bilateral headache, stress-related onset, photophobia, no focal neurological signs",
            "differential_diagnoses": "Migraine without aura, medication overuse headache, cervicogenic headache",
            "red_flags": "None identified - no fever, no neck stiffness, no focal neurological deficits",
            "next_steps": "Trial of analgesics, stress management counseling, monitor response to treatment"
        }
        
        result = self.request("POST", "/diagnoses/", diagnosis_data)
        if result and 'id' in result:
            diagnosis_id = result['id']
            self.test_data['diagnosis_id'] = diagnosis_id
            self.print_success(f"Diagnosis created: {diagnosis_id}")
        elif result and result.get('error'):
            self.print_error("Failed to create diagnosis")
            self.print_info(f"Validation error: {result['error']}")
            return False
        else:
            self.print_error("Failed to create diagnosis - no response")
            return False
        
        # READ
        self.print_test("Reading diagnosis")
        result = self.request("GET", f"/diagnoses/{diagnosis_id}")
        if result and not result.get('error'):
            self.print_success("Diagnosis retrieved successfully")
        else:
            self.print_error("Failed to read diagnosis")
            return False
        
        # UPDATE
        self.print_test("Updating diagnosis")
        update_data = {
            "physician_confirmed": True,
            "physician_notes": "Confirmed after clinical assessment. Responds well to stress management.",
            "confidence_level": "high",
            "final_diagnosis": True
        }
        result = self.request("PUT", f"/diagnoses/{diagnosis_id}", update_data)
        if result and not result.get('error'):
            self.print_success("Diagnosis updated successfully")
        else:
            self.print_error("Failed to update diagnosis")
        
        return True
    
    def test_treatment_crud(self):
        """Test Treatment CRUD with proper validation"""
        print("\n💊 Testing Treatment CRUD")
        
        episode_id = self.test_data.get('episode_id')
        diagnosis_id = self.test_data.get('diagnosis_id')
        
        if not episode_id:
            self.print_error("No episode ID available")
            return False
        
        # CREATE
        self.print_test("Creating treatment")
        treatment_data = {
            "episode_id": episode_id,
            "diagnosis_id": diagnosis_id,
            "treatment_type": "medication",
            "name": "Ibuprofen",
            "description": "Nonsteroidal anti-inflammatory drug for tension headache management",
            "dosage": "400mg",
            "frequency": "Every 6-8 hours as needed",
            "route": "oral",
            "duration": "As needed for 7 days maximum",
            "instructions": "Take with food or milk to reduce gastric irritation. Do not exceed 1200mg in 24 hours.",
            "monitoring_requirements": "Monitor for gastrointestinal upset, allergic reactions, and effectiveness",
            "contraindications": "Active peptic ulcer disease, severe renal impairment, aspirin allergy",
            "side_effects": "Nausea, dyspepsia, dizziness, headache (rare)",
            "drug_interactions": "Warfarin, ACE inhibitors, lithium",
            "lifestyle_modifications": "Stress reduction techniques, regular sleep schedule, adequate hydration",
            "follow_up_instructions": "Return if headaches worsen or persist beyond 1 week",
            "patient_education": "Identify and avoid stress triggers, maintain regular meal and sleep schedule",
            "prescriber": "Dr. Smith",
            "approved_by": "Dr. Smith"
        }
        
        result = self.request("POST", "/treatments/", treatment_data)
        if result and 'id' in result:
            treatment_id = result['id']
            self.test_data['treatment_id'] = treatment_id
            self.print_success(f"Treatment created: {treatment_id}")
        elif result and result.get('error'):
            self.print_error("Failed to create treatment")
            self.print_info(f"Validation error: {result['error']}")
            return False
        else:
            self.print_error("Failed to create treatment - no response")
            return False
        
        # READ
        self.print_test("Reading treatment")
        result = self.request("GET", f"/treatments/{treatment_id}")
        if result and not result.get('error'):
            self.print_success("Treatment retrieved successfully")
        else:
            self.print_error("Failed to read treatment")
            return False
        
        # UPDATE
        self.print_test("Updating treatment")
        update_data = {
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "follow_up_instructions": "Patient tolerating medication well, continue as needed for symptom relief"
        }
        result = self.request("PUT", f"/treatments/{treatment_id}", update_data)
        if result and not result.get('error'):
            self.print_success("Treatment updated successfully")
        else:
            self.print_error("Failed to update treatment")
        
        return True
    
    def test_list_operations(self):
        """Test list/search operations"""
        print("\n📊 Testing List Operations")
        
        operations = [
            ("patients", "Patient list"),
            ("episodes", "Episode list"),
            ("diagnoses", "Diagnosis list"),
            ("treatments", "Treatment list")
        ]
        
        for endpoint, description in operations:
            self.print_test(f"Getting {description.lower()}")
            result = self.request("GET", f"/{endpoint}/")
            if result and not result.get('error'):
                if 'data' in result:
                    count = len(result['data'])
                    total = result.get('total', count)
                    self.print_success(f"{description} retrieved: {count} items (total: {total})")
                else:
                    self.print_success(f"{description} retrieved")
            else:
                self.print_error(f"Failed to get {description.lower()}")
    
    def cleanup(self):
        """Delete test data in correct order"""
        print("\n🧹 Cleaning up test data")
        
        # Delete in reverse dependency order
        cleanup_order = [
            ("treatments", "treatment_id", "Treatment"),
            ("diagnoses", "diagnosis_id", "Diagnosis"), 
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
    
    def run_tests(self):
        """Run comprehensive CRUD tests"""
        print("🚀 Running Validation-Aware CRUD Tests for DiagnoAssist")
        print("=" * 60)
        
        # Health check first
        if not self.test_health_check():
            print("❌ Cannot continue - API is not responding")
            print("💡 Make sure to run: python main.py")
            return
        
        try:
            success_count = 0
            total_tests = 4
            
            # Run tests in dependency order
            tests = [
                ("Patient CRUD", self.test_patient_crud),
                ("Episode CRUD", self.test_episode_crud),
                ("Diagnosis CRUD", self.test_diagnosis_crud),
                ("Treatment CRUD", self.test_treatment_crud)
            ]
            
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                if test_func():
                    success_count += 1
                    self.print_success(f"{test_name} completed successfully")
                else:
                    self.print_error(f"{test_name} failed")
                    break  # Stop on first failure to avoid cascade issues
            
            # Run list operations if we have data
            if success_count > 0:
                print(f"\n{'='*20} List Operations {'='*20}")
                self.test_list_operations()
            
            # Final results
            print(f"\n{'='*60}")
            print(f"🏆 Test Results: {success_count}/{total_tests} test suites passed")
            
            if success_count == total_tests:
                print("🎉 All CRUD operations working perfectly!")
                print("✅ Your DiagnoAssist API is fully functional")
            else:
                print(f"⚠️  {total_tests - success_count} test suite(s) need attention")
                print("🔧 Check the error messages above for details")
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

if __name__ == "__main__":
    print("📋 DiagnoAssist Enhanced CRUD Test Suite")
    print("🎯 Testing all validation rules and CRUD operations")
    print("🔗 API URL: http://localhost:8000/api/v1")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("")
    
    test = ValidationAwareCRUDTest()
    test.run_tests()