#!/usr/bin/env python3
"""
Database CRUD Testing Script for DiagnoAssist
Tests Create, Read, Update, Delete operations with real database interactions
"""

import requests
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import uuid

class DatabaseCRUDTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test data storage
        self.created_patients = []
        self.created_episodes = []
        self.created_treatments = []
        
        # Test counters
        self.passed = 0
        self.failed = 0
    
    def print_header(self, title: str):
        print(f"\n{'='*70}")
        print(f"🗄️  {title}")
        print(f"{'='*70}")
    
    def print_success(self, message: str):
        print(f"✅ {message}")
        self.passed += 1
    
    def print_error(self, message: str):
        print(f"❌ {message}")
        self.failed += 1
    
    def print_info(self, message: str):
        print(f"ℹ️  {message}")
    
    def print_json(self, data: Dict[str, Any], prefix: str = "   "):
        """Pretty print JSON data"""
        print(f"{prefix}{json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                    expected_status: int = 200) -> Optional[Dict[str, Any]]:
        """Make HTTP request and handle response"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                self.print_error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == expected_status:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # For successful non-JSON responses (like DELETE)
                    if response.status_code in [200, 201, 204]:
                        return {"status": "success", "message": "Operation completed"}
                    return None
            else:
                self.print_error(f"{method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
                if response.text:
                    self.print_info(f"Response: {response.text[:200]}...")
                return None
                
        except requests.exceptions.ConnectionError:
            self.print_error(f"Connection Error - Server not running?")
            return None
        except Exception as e:
            self.print_error(f"Request failed: {str(e)}")
            return None

    # =============================================================================
    # PATIENT CRUD OPERATIONS
    # =============================================================================
    
    def test_patient_crud(self):
        """Test complete Patient CRUD operations"""
        self.print_header("Patient CRUD Operations")
        
        # 1. CREATE Patient
        self.print_info("1️⃣  Testing Patient Creation (POST)")
        
        patient_data = {
            "medical_record_number": f"TEST-{uuid.uuid4().hex[:8].upper()}",
            "first_name": "John",
            "last_name": "DatabaseTest", 
            "date_of_birth": "1985-06-15",
            "gender": "male",
            "email": f"john.test.{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+1-555-0123",
            "address": "123 Test Street, Test City, TC 12345",
            "emergency_contact_name": "Jane DatabaseTest",
            "emergency_contact_phone": "+1-555-0124",
            "emergency_contact_relationship": "spouse",
            "medical_history": ["Hypertension", "Type 2 Diabetes"],
            "allergies": ["Penicillin", "Shellfish"],
            "current_medications": ["Metformin 500mg", "Lisinopril 10mg"]
        }
        
        created_patient = self.make_request("POST", "/api/v1/patients/", patient_data, 201)
        
        if created_patient:
            self.print_success("Patient created successfully")
            self.print_json({"id": created_patient.get("id"), "mrn": created_patient.get("medical_record_number")})
            self.created_patients.append(created_patient)
            patient_id = created_patient["id"]
        else:
            self.print_error("Failed to create patient")
            return False
        
        # 2. READ Patient
        self.print_info("2️⃣  Testing Patient Retrieval (GET)")
        
        retrieved_patient = self.make_request("GET", f"/api/v1/patients/{patient_id}")
        
        if retrieved_patient:
            self.print_success("Patient retrieved successfully")
            # Verify key fields match
            if (retrieved_patient.get("medical_record_number") == patient_data["medical_record_number"] and
                retrieved_patient.get("first_name") == patient_data["first_name"]):
                self.print_success("Retrieved data matches created data")
            else:
                self.print_error("Retrieved data doesn't match created data")
        else:
            self.print_error("Failed to retrieve patient")
        
        # 3. UPDATE Patient
        self.print_info("3️⃣  Testing Patient Update (PUT)")
        
        update_data = {
            "phone": "+1-555-9999",
            "address": "456 Updated Avenue, New City, NC 67890",
            "current_medications": ["Metformin 500mg", "Lisinopril 10mg", "Atorvastatin 20mg"]
        }
        
        updated_patient = self.make_request("PUT", f"/api/v1/patients/{patient_id}", update_data)
        
        if updated_patient:
            self.print_success("Patient updated successfully")
            if updated_patient.get("phone") == update_data["phone"]:
                self.print_success("Update data applied correctly")
            else:
                self.print_error("Update data not applied correctly")
        else:
            self.print_error("Failed to update patient")
        
        # 4. LIST Patients (GET all)
        self.print_info("4️⃣  Testing Patient List (GET)")
        
        patients_list = self.make_request("GET", "/api/v1/patients/")
        
        if patients_list:
            self.print_success(f"Retrieved patients list: {len(patients_list.get('patients', []))} patients")
        else:
            self.print_error("Failed to retrieve patients list")
        
        return True

    # =============================================================================
    # EPISODE CRUD OPERATIONS  
    # =============================================================================
    
    def test_episode_crud(self):
        """Test complete Episode CRUD operations"""
        self.print_header("Episode CRUD Operations")
        
        if not self.created_patients:
            self.print_error("No patient available for episode testing")
            return False
        
        patient_id = self.created_patients[0]["id"]
        
        # 1. CREATE Episode
        self.print_info("1️⃣  Testing Episode Creation (POST)")
        
        episode_data = {
            "patient_id": patient_id,
            "chief_complaint": "Chest pain and shortness of breath",
            "encounter_type": "emergency",
            "priority": "urgent",
            "provider_id": "DR001",
            "location": "Emergency Department",
            "vital_signs": {
                "blood_pressure_systolic": 140,
                "blood_pressure_diastolic": 90,
                "heart_rate": 95,
                "respiratory_rate": 20,
                "temperature": 37.2,
                "oxygen_saturation": 98,
                "weight": 75.5,
                "height": 175
            },
            "symptoms": ["chest pain", "shortness of breath", "sweating"],
            "physical_exam_findings": {
                "general_appearance": "Patient appears anxious and diaphoretic",
                "cardiovascular": "Regular rate and rhythm, no murmurs",
                "respiratory": "Clear bilaterally, good air entry"
            },
            "clinical_notes": "55-year-old male presenting with acute onset chest pain",
            "assessment_notes": "Rule out acute coronary syndrome",
            "plan_notes": "ECG, cardiac enzymes, chest X-ray"
        }
        
        created_episode = self.make_request("POST", "/api/v1/episodes/", episode_data, 201)
        
        if created_episode:
            self.print_success("Episode created successfully")
            self.print_json({"id": created_episode.get("id"), "complaint": created_episode.get("chief_complaint")})
            self.created_episodes.append(created_episode)
            episode_id = created_episode["id"]
        else:
            self.print_error("Failed to create episode")
            return False
        
        # 2. READ Episode
        self.print_info("2️⃣  Testing Episode Retrieval (GET)")
        
        retrieved_episode = self.make_request("GET", f"/api/v1/episodes/{episode_id}")
        
        if retrieved_episode:
            self.print_success("Episode retrieved successfully")
            if retrieved_episode.get("chief_complaint") == episode_data["chief_complaint"]:
                self.print_success("Retrieved episode data matches created data")
            else:
                self.print_error("Retrieved episode data doesn't match")
        else:
            self.print_error("Failed to retrieve episode")
        
        # 3. UPDATE Episode
        self.print_info("3️⃣  Testing Episode Update (PUT)")
        
        update_data = {
            "status": "completed",
            "clinical_notes": "Patient's chest pain resolved with treatment. EKG normal. Discharged home.",
            "assessment_notes": "Non-cardiac chest pain. Likely musculoskeletal origin.",
            "plan_notes": "Discharge with pain management advice. Follow up with primary care in 1 week."
        }
        
        updated_episode = self.make_request("PUT", f"/api/v1/episodes/{episode_id}", update_data)
        
        if updated_episode:
            self.print_success("Episode updated successfully")
        else:
            self.print_error("Failed to update episode")
        
        return True

    # =============================================================================
    # TREATMENT CRUD OPERATIONS
    # =============================================================================
    
    def test_treatment_crud(self):
        """Test complete Treatment CRUD operations"""
        self.print_header("Treatment CRUD Operations")
        
        if not self.created_episodes:
            self.print_error("No episode available for treatment testing")
            return False
        
        episode_id = self.created_episodes[0]["id"]
        
        # 1. CREATE Treatment
        self.print_info("1️⃣  Testing Treatment Creation (POST)")
        
        treatment_data = {
            "episode_id": episode_id,
            "treatment_type": "medication",
            "treatment_name": "Ibuprofen for pain management",
            "description": "Anti-inflammatory medication for chest wall pain",
            "medication_details": {
                "medication_name": "Ibuprofen",
                "dosage": "400mg",
                "frequency": "Every 6 hours as needed",
                "route": "oral",
                "duration": "3-5 days",
                "contraindications": ["Active GI bleeding", "Severe kidney disease"],
                "side_effects": ["Stomach upset", "Nausea", "Dizziness"],
                "drug_interactions": ["Warfarin", "ACE inhibitors"]
            },
            "instructions": "Take with food to reduce stomach irritation",
            "status": "approved"
        }
        
        created_treatment = self.make_request("POST", "/api/v1/treatments/", treatment_data, 201)
        
        if created_treatment:
            self.print_success("Treatment created successfully")
            self.print_json({"id": created_treatment.get("id"), "name": created_treatment.get("treatment_name")})
            self.created_treatments.append(created_treatment)
            treatment_id = created_treatment["id"]
        else:
            self.print_error("Failed to create treatment")
            return False
        
        # 2. READ Treatment
        self.print_info("2️⃣  Testing Treatment Retrieval (GET)")
        
        retrieved_treatment = self.make_request("GET", f"/api/v1/treatments/{treatment_id}")
        
        if retrieved_treatment:
            self.print_success("Treatment retrieved successfully")
        else:
            self.print_error("Failed to retrieve treatment")
        
        # 3. UPDATE Treatment
        self.print_info("3️⃣  Testing Treatment Update (PUT)")
        
        update_data = {
            "status": "completed",
            "instructions": "Patient tolerated medication well. Continue as needed for pain."
        }
        
        updated_treatment = self.make_request("PUT", f"/api/v1/treatments/{treatment_id}", update_data)
        
        if updated_treatment:
            self.print_success("Treatment updated successfully")
        else:
            self.print_error("Failed to update treatment")
        
        return True

    # =============================================================================
    # RELATIONSHIP TESTING
    # =============================================================================
    
    def test_data_relationships(self):
        """Test relationships between entities"""
        self.print_header("Data Relationship Testing")
        
        if not self.created_patients:
            self.print_error("No test data available for relationship testing")
            return False
        
        patient_id = self.created_patients[0]["id"]
        
        # Test patient's episodes
        self.print_info("1️⃣  Testing Patient-Episode Relationship")
        
        patient_episodes = self.make_request("GET", f"/api/v1/patients/{patient_id}/episodes")
        
        if patient_episodes:
            episodes_count = len(patient_episodes.get("episodes", []))
            self.print_success(f"Retrieved {episodes_count} episodes for patient")
        else:
            self.print_error("Failed to retrieve patient episodes")
        
        # Test episode's treatments
        if self.created_episodes:
            episode_id = self.created_episodes[0]["id"]
            
            self.print_info("2️⃣  Testing Episode-Treatment Relationship")
            
            episode_treatments = self.make_request("GET", f"/api/v1/episodes/{episode_id}/treatments")
            
            if episode_treatments:
                treatments_count = len(episode_treatments.get("treatments", []))
                self.print_success(f"Retrieved {treatments_count} treatments for episode")
            else:
                self.print_error("Failed to retrieve episode treatments")

    # =============================================================================
    # DATA VALIDATION TESTING
    # =============================================================================
    
    def test_data_validation(self):
        """Test data validation and error handling"""
        self.print_header("Data Validation Testing")
        
        # Test invalid patient data
        self.print_info("1️⃣  Testing Invalid Patient Data")
        
        invalid_patient = {
            "medical_record_number": "",  # Invalid: empty
            "first_name": "",  # Invalid: empty
            "date_of_birth": "2030-01-01",  # Invalid: future date
            "gender": "invalid_gender",  # Invalid: not in allowed values
            "email": "invalid_email"  # Invalid: not a valid email
        }
        
        result = self.make_request("POST", "/api/v1/patients/", invalid_patient, 422)
        
        if result is None:  # Expected 422 validation error
            self.print_success("Validation correctly rejected invalid patient data")
        else:
            self.print_error("Validation failed to catch invalid patient data")
        
        # Test invalid episode data
        self.print_info("2️⃣  Testing Invalid Episode Data")
        
        invalid_episode = {
            "patient_id": "invalid-uuid",  # Invalid: not a valid UUID
            "chief_complaint": "",  # Invalid: empty
            "encounter_type": "invalid_type",  # Invalid: not in allowed values
            "priority": "invalid_priority"  # Invalid: not in allowed values
        }
        
        result = self.make_request("POST", "/api/v1/episodes/", invalid_episode, 422)
        
        if result is None:  # Expected 422 validation error
            self.print_success("Validation correctly rejected invalid episode data")
        else:
            self.print_error("Validation failed to catch invalid episode data")

    # =============================================================================
    # CLEANUP AND DELETE TESTING
    # =============================================================================
    
    def test_delete_operations(self):
        """Test delete operations (cleanup)"""
        self.print_header("Delete Operations Testing")
        
        # Delete treatments first (foreign key constraints)
        for treatment in self.created_treatments:
            treatment_id = treatment["id"]
            self.print_info(f"🗑️  Deleting treatment {treatment_id}")
            
            result = self.make_request("DELETE", f"/api/v1/treatments/{treatment_id}", expected_status=200)
            
            if result:
                self.print_success(f"Treatment {treatment_id} deleted successfully")
            else:
                self.print_error(f"Failed to delete treatment {treatment_id}")
        
        # Delete episodes
        for episode in self.created_episodes:
            episode_id = episode["id"]
            self.print_info(f"🗑️  Deleting episode {episode_id}")
            
            result = self.make_request("DELETE", f"/api/v1/episodes/{episode_id}", expected_status=200)
            
            if result:
                self.print_success(f"Episode {episode_id} deleted successfully")
            else:
                self.print_error(f"Failed to delete episode {episode_id}")
        
        # Delete patients last
        for patient in self.created_patients:
            patient_id = patient["id"]
            self.print_info(f"🗑️  Deleting patient {patient_id}")
            
            result = self.make_request("DELETE", f"/api/v1/patients/{patient_id}", expected_status=200)
            
            if result:
                self.print_success(f"Patient {patient_id} deleted successfully")
            else:
                self.print_error(f"Failed to delete patient {patient_id}")

    # =============================================================================
    # MAIN TEST RUNNER
    # =============================================================================
    
    def run_all_tests(self):
        """Run complete database CRUD test suite"""
        print("🚀 DiagnoAssist Database CRUD Test Suite")
        print(f"🎯 Testing server at: {self.base_url}")
        
        # Test server connectivity first
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.print_success("Server is responding")
            else:
                self.print_error("Server health check failed")
                return False
        except:
            self.print_error("Cannot connect to server")
            return False
        
        # Run all test categories
        test_results = []
        
        test_results.append(self.test_patient_crud())
        test_results.append(self.test_episode_crud())
        test_results.append(self.test_treatment_crud())
        test_results.append(self.test_data_relationships())
        
        # Run validation tests (these should fail validation)
        self.test_data_validation()
        
        # Clean up test data
        self.test_delete_operations()
        
        # Print summary
        self.print_summary()
        
        return all(test_results)
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print(f"📊 DATABASE CRUD TEST SUMMARY")
        print(f"{'='*70}")
        
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n🎉 ALL DATABASE TESTS PASSED!")
            print(f"🗄️  Your database operations are working perfectly!")
        elif success_rate >= 80:
            print(f"\n⚠️  Most tests passed, but {self.failed} issues need attention")
        else:
            print(f"\n🔧 Several database issues detected. Check the failed operations above.")


def main():
    """Main function"""
    tester = DatabaseCRUDTester("http://localhost:8000")
    
    print("Starting DiagnoAssist Database CRUD Tests...")
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()