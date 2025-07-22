#!/usr/bin/env python3
"""
Database CRUD Testing Script for DiagnoAssist - FIXED VERSION
Tests Create, Read, Update, Delete operations with proper authentication
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
        
        # ADD AUTHENTICATION HEADERS
        # Your API uses bearer token authentication
        # For development, any token will work since get_current_user returns a mock user
        self.session.headers.update({
            "Authorization": "Bearer dev-token-123",
            "Content-Type": "application/json"
        })
        
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
                    expected_status: int = 200, allow_422: bool = False) -> Optional[Dict[str, Any]]:
        """Make HTTP request and handle response"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                self.print_error(f"Unsupported HTTP method: {method}")
                return None
            
            # Check if status code matches expected
            if response.status_code == expected_status:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # For successful non-JSON responses (like DELETE)
                    if response.status_code in [200, 201, 204]:
                        return {"status": "success", "message": "Operation completed"}
                    return None
            elif allow_422 and response.status_code == 422:
                # For validation tests, 422 is expected
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "validation_error"}
            else:
                self.print_error(f"{method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
                if response.text:
                    try:
                        error_detail = response.json()
                        self.print_info(f"Error: {json.dumps(error_detail, indent=2)}")
                    except:
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
        
        # 2. READ Patient (GET by ID)
        self.print_info("2️⃣  Testing Patient Retrieval (GET)")
        
        retrieved_patient = self.make_request("GET", f"/api/v1/patients/{patient_id}")
        
        if retrieved_patient:
            self.print_success("Patient retrieved successfully")
            # Verify data matches
            if retrieved_patient.get("medical_record_number") == patient_data["medical_record_number"]:
                self.print_success("Patient data integrity verified")
            else:
                self.print_error("Patient data mismatch")
        else:
            self.print_error("Failed to retrieve patient")
        
        # 3. UPDATE Patient (PUT)
        self.print_info("3️⃣  Testing Patient Update (PUT)")
        
        update_data = {
            "medical_record_number": patient_data["medical_record_number"],
            "first_name": "John-Updated",
            "last_name": "DatabaseTest-Updated",
            "date_of_birth": patient_data["date_of_birth"],
            "gender": patient_data["gender"],
            "email": patient_data["email"],
            "phone": "+1-555-0125",  # Updated phone
            "address": "456 Updated Street, Updated City, UC 54321",  # Updated address
            "emergency_contact_name": patient_data["emergency_contact_name"],
            "emergency_contact_phone": patient_data["emergency_contact_phone"],
            "emergency_contact_relationship": patient_data["emergency_contact_relationship"],
            "medical_history": patient_data["medical_history"] + ["Migraine"],  # Added condition
            "allergies": patient_data["allergies"],
            "current_medications": patient_data["current_medications"] + ["Aspirin 81mg"]  # Added medication
        }
        
        updated_patient = self.make_request("PUT", f"/api/v1/patients/{patient_id}", update_data)
        
        if updated_patient:
            self.print_success("Patient updated successfully")
            # Verify updates took effect
            if updated_patient.get("first_name") == "John-Updated":
                self.print_success("Patient update verification passed")
            else:
                self.print_error("Patient update verification failed")
        else:
            self.print_error("Failed to update patient")
        
        # 4. LIST Patients (GET collection)
        self.print_info("4️⃣  Testing Patient List (GET)")
        
        patients_list = self.make_request("GET", "/api/v1/patients/")
        
        if patients_list and isinstance(patients_list.get("data"), list):
            patient_count = len(patients_list["data"])
            self.print_success(f"Patient list retrieved successfully ({patient_count} patients)")
        else:
            self.print_error("Failed to retrieve patient list")
        
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
            "symptoms": ["chest pain", "shortness of breath", "dizziness"],
            "vital_signs": {
                "blood_pressure_systolic": 145,
                "blood_pressure_diastolic": 90,
                "heart_rate": 95,
                "temperature": 98.6,
                "respiratory_rate": 20,
                "oxygen_saturation": 97
            },
            "notes": "Patient presents with acute onset chest pain"
        }
        
        created_episode = self.make_request("POST", "/api/v1/episodes/", episode_data, 201)
        
        if created_episode:
            self.print_success("Episode created successfully")
            self.print_json({"id": created_episode.get("id"), "chief_complaint": created_episode.get("chief_complaint")})
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
        else:
            self.print_error("Failed to retrieve episode")
        
        # 3. UPDATE Episode
        self.print_info("3️⃣  Testing Episode Update (PUT)")
        
        update_data = {
            "patient_id": patient_id,
            "chief_complaint": episode_data["chief_complaint"] + " - Updated",
            "encounter_type": episode_data["encounter_type"],
            "priority": "emergent",  # Escalated priority
            "symptoms": episode_data["symptoms"] + ["nausea"],
            "vital_signs": {
                "blood_pressure_systolic": 150,  # Updated vitals
                "blood_pressure_diastolic": 95,
                "heart_rate": 100,
                "temperature": 98.6,
                "respiratory_rate": 22,
                "oxygen_saturation": 96
            },
            "notes": episode_data["notes"] + " - Condition worsening"
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
        patient_id = self.created_patients[0]["id"]
        
        # 1. CREATE Treatment
        self.print_info("1️⃣  Testing Treatment Creation (POST)")
        
        treatment_data = {
            "episode_id": episode_id,
            "patient_id": patient_id,
            "treatment_type": "medication",
            "name": "Aspirin",
            "dosage": "325mg",
            "frequency": "once daily",
            "duration": "7 days",
            "route": "oral",
            "instructions": "Take with food to reduce stomach irritation",
            "prescriber": "Dr. Smith",
            "start_date": datetime.now().isoformat(),
            "status": "active"
        }
        
        created_treatment = self.make_request("POST", "/api/v1/treatments/", treatment_data, 201)
        
        if created_treatment:
            self.print_success("Treatment created successfully")
            self.print_json({"id": created_treatment.get("id"), "name": created_treatment.get("name")})
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
        
        return True

    # =============================================================================
    # DATA RELATIONSHIP TESTING
    # =============================================================================
    
    def test_data_relationships(self):
        """Test data relationships and foreign keys"""
        self.print_header("Data Relationship Testing")
        
        if not self.created_patients:
            self.print_error("No test data available for relationship testing")
            return False
        
        patient_id = self.created_patients[0]["id"]
        
        # 1. Test Patient -> Episodes relationship
        self.print_info("1️⃣  Testing Patient-Episode Relationships")
        
        patient_episodes = self.make_request("GET", f"/api/v1/patients/{patient_id}/episodes")
        
        if patient_episodes and isinstance(patient_episodes, list):
            episode_count = len(patient_episodes)
            self.print_success(f"Patient has {episode_count} episodes")
        else:
            self.print_error("Failed to retrieve patient episodes")
        
        # 2. Test Episode -> Treatments relationship
        if self.created_episodes:
            episode_id = self.created_episodes[0]["id"]
            self.print_info("2️⃣  Testing Episode-Treatment Relationships")
            
            episode_treatments = self.make_request("GET", f"/api/v1/treatments/episode/{episode_id}/treatments")
            
            if episode_treatments:
                self.print_success("Episode treatments retrieved successfully")
            else:
                self.print_info("No treatments found for episode (expected if none created)")
        
        return True

    # =============================================================================
    # DATA VALIDATION TESTING
    # =============================================================================
    
    def test_data_validation(self):
        """Test data validation with invalid inputs"""
        self.print_header("Data Validation Testing")
        
        # 1. Test Invalid Patient Data
        self.print_info("1️⃣  Testing Invalid Patient Data")
        
        invalid_patient_data = {
            "medical_record_number": "",  # Empty MRN
            "first_name": "",  # Empty name
            # Missing last_name (required field)
            "date_of_birth": "2030-01-01",  # Future date
            "gender": "invalid",  # Invalid gender
            "email": "not-an-email",  # Invalid email format
            "phone": "invalid-phone"
        }
        
        validation_result = self.make_request("POST", "/api/v1/patients/", invalid_patient_data, 422, allow_422=True)
        
        if validation_result:
            self.print_success("Validation correctly rejected invalid patient data")
        else:
            self.print_error("Validation failed to catch invalid patient data")
        
        # 2. Test Invalid Episode Data
        self.print_info("2️⃣  Testing Invalid Episode Data")
        
        invalid_episode_data = {
            "chief_complaint": "",  # Empty complaint
            "encounter_type": "invalid",  # Invalid type
            "priority": "invalid",  # Invalid priority
            "patient_id": "not-a-uuid"  # Invalid UUID
        }
        
        validation_result = self.make_request("POST", "/api/v1/episodes/", invalid_episode_data, 422, allow_422=True)
        
        if validation_result:
            self.print_success("Validation correctly rejected invalid episode data")
        else:
            self.print_error("Validation failed to catch invalid episode data")

    # =============================================================================
    # DELETE OPERATIONS TESTING
    # =============================================================================
    
    def test_delete_operations(self):
        """Test delete operations (cleanup)"""
        self.print_header("Delete Operations Testing")
        
        # Delete treatments first (dependencies)
        for treatment in self.created_treatments:
            treatment_id = treatment["id"]
            self.print_info(f"Deleting treatment: {treatment_id}")
            
            result = self.make_request("DELETE", f"/api/v1/treatments/{treatment_id}", expected_status=204)
            if result:
                self.print_success(f"Treatment {treatment_id} deleted")
            else:
                self.print_info(f"Treatment {treatment_id} delete skipped")
        
        # Delete episodes
        for episode in self.created_episodes:
            episode_id = episode["id"]
            self.print_info(f"Deleting episode: {episode_id}")
            
            result = self.make_request("DELETE", f"/api/v1/episodes/{episode_id}", expected_status=204)
            if result:
                self.print_success(f"Episode {episode_id} deleted")
            else:
                self.print_info(f"Episode {episode_id} delete skipped")
        
        # Delete patients
        for patient in self.created_patients:
            patient_id = patient["id"]
            self.print_info(f"Deleting patient: {patient_id}")
            
            result = self.make_request("DELETE", f"/api/v1/patients/{patient_id}", expected_status=204)
            if result:
                self.print_success(f"Patient {patient_id} deleted")
            else:
                self.print_info(f"Patient {patient_id} delete skipped")

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