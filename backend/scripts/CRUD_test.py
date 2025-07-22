#!/usr/bin/env python3
"""
Simple CRUD Test for DiagnoAssist MVP
Tests basic Create, Read, Update, Delete operations
"""

import requests
import json
import uuid

class SimpleCRUDTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = f"{base_url}/api/v1"
        self.test_data = {}
        # Add authentication header for MVP
        self.headers = {"Authorization": "Bearer test-token"}
    
    def print_test(self, message):
        print(f"🔄 {message}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def request(self, method, endpoint, data=None):
        """Make HTTP request"""
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
                return response.json() if response.text else {"status": "ok"}
            elif response.status_code == 204:
                return {"status": "deleted"}
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   Connection error: {e}")
            return None
    
    def test_patient_crud(self):
        """Test Patient CRUD"""
        print("\n📋 Testing Patient CRUD")
        
        # CREATE
        self.print_test("Creating patient")
        patient_data = {
            "medical_record_number": f"TEST-{str(uuid.uuid4())[:8]}",
            "first_name": "John",
            "last_name": "Test",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "email": "john.test@example.com"
        }
        
        result = self.request("POST", "/patients/", patient_data)
        if result and 'id' in result:
            patient_id = result['id']
            self.test_data['patient_id'] = patient_id
            self.print_success(f"Patient created: {patient_id}")
        else:
            self.print_error("Failed to create patient")
            return False
        
        # READ
        self.print_test("Reading patient")
        result = self.request("GET", f"/patients/{patient_id}")
        if result:
            self.print_success("Patient retrieved")
        else:
            self.print_error("Failed to read patient")
        
        # UPDATE
        self.print_test("Updating patient")
        update_data = {"phone": "+1-555-9999"}
        result = self.request("PUT", f"/patients/{patient_id}", update_data)
        if result:
            self.print_success("Patient updated")
        else:
            self.print_error("Failed to update patient")
        
        return True
    
    def test_episode_crud(self):
        """Test Episode CRUD"""
        print("\n📋 Testing Episode CRUD")
        
        patient_id = self.test_data.get('patient_id')
        if not patient_id:
            self.print_error("No patient ID available")
            return False
        
        # CREATE
        self.print_test("Creating episode")
        episode_data = {
            "patient_id": patient_id,
            "chief_complaint": "Headache",
            "status": "active"
        }
        
        result = self.request("POST", "/episodes/", episode_data)
        if result and 'id' in result:
            episode_id = result['id']
            self.test_data['episode_id'] = episode_id
            self.print_success(f"Episode created: {episode_id}")
        else:
            self.print_error("Failed to create episode")
            return False
        
        # READ
        self.print_test("Reading episode")
        result = self.request("GET", f"/episodes/{episode_id}")
        if result:
            self.print_success("Episode retrieved")
        else:
            self.print_error("Failed to read episode")
        
        # UPDATE
        self.print_test("Updating episode")
        update_data = {"status": "completed"}
        result = self.request("PUT", f"/episodes/{episode_id}", update_data)
        if result:
            self.print_success("Episode updated")
        else:
            self.print_error("Failed to update episode")
        
        return True
    
    def test_diagnosis_crud(self):
        """Test Diagnosis CRUD"""
        print("\n📋 Testing Diagnosis CRUD")
        
        episode_id = self.test_data.get('episode_id')
        if not episode_id:
            self.print_error("No episode ID available")
            return False
        
        # CREATE
        self.print_test("Creating diagnosis")
        diagnosis_data = {
            "episode_id": episode_id,
            "condition_name": "Tension Headache",
            "status": "active"
        }
        
        result = self.request("POST", "/diagnoses/", diagnosis_data)
        if result and 'id' in result:
            diagnosis_id = result['id']
            self.test_data['diagnosis_id'] = diagnosis_id
            self.print_success(f"Diagnosis created: {diagnosis_id}")
        else:
            self.print_error("Failed to create diagnosis")
            return False
        
        # READ
        self.print_test("Reading diagnosis")
        result = self.request("GET", f"/diagnoses/{diagnosis_id}")
        if result:
            self.print_success("Diagnosis retrieved")
        else:
            self.print_error("Failed to read diagnosis")
        
        return True
    
    def test_treatment_crud(self):
        """Test Treatment CRUD"""
        print("\n📋 Testing Treatment CRUD")
        
        episode_id = self.test_data.get('episode_id')
        if not episode_id:
            self.print_error("No episode ID available")
            return False
        
        # CREATE
        self.print_test("Creating treatment")
        treatment_data = {
            "episode_id": episode_id,
            "name": "Ibuprofen",
            "dosage": "200mg",
            "status": "active"
        }
        
        result = self.request("POST", "/treatments/", treatment_data)
        if result and 'id' in result:
            treatment_id = result['id']
            self.test_data['treatment_id'] = treatment_id
            self.print_success(f"Treatment created: {treatment_id}")
        else:
            self.print_error("Failed to create treatment")
            return False
        
        # READ
        self.print_test("Reading treatment")
        result = self.request("GET", f"/treatments/{treatment_id}")
        if result:
            self.print_success("Treatment retrieved")
        else:
            self.print_error("Failed to read treatment")
        
        return True
    
    def cleanup(self):
        """Delete test data"""
        print("\n🧹 Cleaning up test data")
        
        # Delete in reverse order
        for resource, id_key in [
            ("treatments", "treatment_id"),
            ("diagnoses", "diagnosis_id"), 
            ("episodes", "episode_id"),
            ("patients", "patient_id")
        ]:
            resource_id = self.test_data.get(id_key)
            if resource_id:
                self.print_test(f"Deleting {resource}")
                result = self.request("DELETE", f"/{resource}/{resource_id}")
                if result:
                    self.print_success(f"{resource} deleted")
                else:
                    self.print_error(f"Failed to delete {resource}")
    
    def run_tests(self):
        """Run all basic CRUD tests"""
        print("🚀 Running Basic CRUD Tests")
        
        try:
            # Test each model
            self.test_patient_crud()
            self.test_episode_crud() 
            self.test_diagnosis_crud()
            self.test_treatment_crud()
            
            print("\n✅ All tests completed!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted")
        finally:
            self.cleanup()

if __name__ == "__main__":
    test = SimpleCRUDTest()
    test.run_tests()