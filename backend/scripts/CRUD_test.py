#!/usr/bin/env python3
"""
DiagnoAssist Database CRUD Test Suite - FIXED VERSION
Tests all CRUD operations against the DiagnoAssist API
"""

import requests
import json
import uuid
import sys
from datetime import datetime, date
from typing import Optional, Dict, Any

class DiagnoAssistTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.test_data = {}
        
        # Colors for console output
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        }
    
    def print_header(self, text: str):
        print(f"\n{'='*70}")
        print(f"{self.colors['cyan']}{self.colors['bold']}{text}{self.colors['reset']}")
        print(f"{'='*70}")
    
    def print_success(self, text: str):
        print(f"{self.colors['green']}✅ {text}{self.colors['reset']}")
    
    def print_error(self, text: str):
        print(f"{self.colors['red']}❌ {text}{self.colors['reset']}")
    
    def print_warning(self, text: str):
        print(f"{self.colors['yellow']}⚠️ {text}{self.colors['reset']}")
    
    def print_info(self, text: str):
        print(f"{self.colors['blue']}ℹ️ {text}{self.colors['reset']}")
    
    def check_server_health(self) -> bool:
        """Check if the DiagnoAssist server is responding"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("Server is responding")
                return True
            else:
                self.print_error(f"Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("Could not connect to server. Is it running?")
            return False
        except requests.exceptions.Timeout:
            self.print_error("Server connection timed out")
            return False
        except Exception as e:
            self.print_error(f"Health check failed: {str(e)}")
            return False
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                self.print_error(f"Unsupported HTTP method: {method}")
                return None
            
            # Print request details
            self.print_info(f"{method.upper()} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            
            # Handle response
            if response.status_code == expected_status:
                try:
                    return response.json() if response.text else {}
                except json.JSONDecodeError:
                    return {}
            else:
                try:
                    error_detail = response.json()
                    self.print_error(f"Error: {error_detail}")
                except json.JSONDecodeError:
                    self.print_error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.print_error(f"Request timeout for {method} {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            self.print_error(f"Connection error for {method} {endpoint}")
            return None
        except Exception as e:
            self.print_error(f"Request failed: {str(e)}")
            return None
    
    def create_test_patient(self) -> Optional[str]:
        """Create a test patient"""
        test_id = str(uuid.uuid4())[:8]
        patient_data = {
            "medical_record_number": f"TEST-{test_id.upper()}",
            "first_name": "John",
            "last_name": "DatabaseTest", 
            "date_of_birth": "1985-06-15",  # Use string format for date
            "gender": "male",
            "email": f"john.test.{test_id}@example.com",
            "phone": "+1-555-0123",
            "address": "123 Test Street, Test City, TC 12345",
            "emergency_contact_name": "Jane DatabaseTest",
            "emergency_contact_phone": "+1-555-0124",
            "emergency_contact_relationship": "spouse",
            "medical_history": "Hypertension, Type 2 Diabetes",
            "allergies": "Penicillin, Shellfish",
            "current_medications": "Metformin 500mg, Lisinopril 10mg"
        }
        
        result = self.make_request("POST", "/patients/", patient_data, 201)
        if result and 'id' in result:
            patient_id = result['id']
            self.test_data['patient'] = result
            self.print_success(f"Created test patient: {patient_id}")
            return patient_id
        else:
            self.print_error("Failed to create patient")
            return None
    
    def create_test_episode(self, patient_id: str) -> Optional[str]:
        """Create a test episode"""
        episode_data = {
            "patient_id": patient_id,
            "chief_complaint": "Chest pain and shortness of breath",
            "symptoms": "Patient reports chest pain for 2 hours, 7/10 intensity",
            "clinical_notes": "Initial assessment in progress",
            "status": "active"
        }
        
        result = self.make_request("POST", "/episodes/", episode_data, 201)
        if result and 'id' in result:
            episode_id = result['id']
            self.test_data['episode'] = result
            self.print_success(f"Created test episode: {episode_id}")
            return episode_id
        else:
            self.print_error("Failed to create episode")
            return None
    
    def test_patient_crud(self) -> bool:
        """Test patient CRUD operations"""
        self.print_header("🗄️ Patient CRUD Operations")
        
        # Test patient creation
        self.print_info("1️⃣ Testing Patient Creation (POST)")
        patient_id = self.create_test_patient()
        if not patient_id:
            return False
        
        # Test get patient by ID
        self.print_info("2️⃣ Testing Get Patient by ID (GET)")
        result = self.make_request("GET", f"/patients/{patient_id}")
        if not result:
            self.print_error("Failed to get patient by ID")
            return False
        self.print_success("Retrieved patient by ID")
        
        # Test get all patients
        self.print_info("3️⃣ Testing Get All Patients (GET)")
        result = self.make_request("GET", "/patients/")
        if not result:
            self.print_error("Failed to get all patients")
            return False
        self.print_success(f"Retrieved {result.get('total', 0)} patients")
        
        # Test update patient
        self.print_info("4️⃣ Testing Update Patient (PUT)")
        update_data = {
            "phone": "+1-555-9999",
            "address": "456 Updated Street, New City, NC 54321"
        }
        result = self.make_request("PUT", f"/patients/{patient_id}", update_data)
        if not result:
            self.print_error("Failed to update patient")
            return False
        self.print_success("Updated patient successfully")
        
        return True
    
    def test_episode_crud(self) -> bool:
        """Test episode CRUD operations"""
        self.print_header("🗄️ Episode CRUD Operations")
        
        patient_id = self.test_data.get('patient', {}).get('id')
        if not patient_id:
            self.print_error("No patient available for episode testing")
            return False
        
        # Test episode creation
        self.print_info("1️⃣ Testing Episode Creation (POST)")
        episode_id = self.create_test_episode(patient_id)
        if not episode_id:
            return False
        
        # Test get episodes by patient
        self.print_info("2️⃣ Testing Get Episodes by Patient (GET)")
        result = self.make_request("GET", f"/patients/{patient_id}/episodes")
        if not result:
            self.print_error("Failed to get episodes by patient")
            return False
        self.print_success("Retrieved episodes by patient")
        
        # Test update episode
        self.print_info("3️⃣ Testing Update Episode (PUT)")
        update_data = {
            "clinical_notes": "Patient stable, pain reduced to 3/10",
            "assessment_notes": "Likely gastroesophageal reflux",
            "status": "in_progress"
        }
        result = self.make_request("PUT", f"/episodes/{episode_id}", update_data)
        if not result:
            self.print_error("Failed to update episode")
            return False
        self.print_success("Updated episode successfully")
        
        return True
    
    def test_validation_errors(self) -> bool:
        """Test data validation"""
        self.print_header("🗄️ Data Validation Testing")
        
        # Test invalid patient data
        self.print_info("1️⃣ Testing Invalid Patient Data")
        invalid_patient = {
            "medical_record_number": "",  # Empty required field
            "first_name": "",  # Empty required field
            "date_of_birth": "2030-01-01",  # Future date
            "email": "invalid-email"  # Invalid email format
        }
        
        result = self.make_request("POST", "/patients/", invalid_patient, 422)
        if result is not None:  # 422 expected, so result should contain error details
            self.print_success("Validation correctly rejected invalid patient data")
        else:
            self.print_error("Validation failed to catch invalid patient data")
            return False
        
        # Test invalid episode data  
        self.print_info("2️⃣ Testing Invalid Episode Data")
        invalid_episode = {
            "patient_id": "invalid-uuid",  # Invalid UUID
            "chief_complaint": "",  # Empty required field
        }
        
        result = self.make_request("POST", "/episodes/", invalid_episode, 422)
        if result is not None:  # 422 expected
            self.print_success("Validation correctly rejected invalid episode data")
        else:
            self.print_error("Validation failed to catch invalid episode data")
            return False
        
        return True
    
    def test_cleanup(self) -> bool:
        """Clean up test data"""
        self.print_header("🗄️ Delete Operations Testing")
        
        success = True
        
        # Delete episode if exists
        episode_id = self.test_data.get('episode', {}).get('id')
        if episode_id:
            result = self.make_request("DELETE", f"/episodes/{episode_id}", expected_status=204)
            if result is not None:  # 204 returns no content but indicates success
                self.print_success(f"Deleted test episode: {episode_id}")
            else:
                self.print_warning(f"Could not delete episode: {episode_id}")
                success = False
        
        # Delete patient if exists
        patient_id = self.test_data.get('patient', {}).get('id')
        if patient_id:
            result = self.make_request("DELETE", f"/patients/{patient_id}", expected_status=204)
            if result is not None:  # 204 returns no content but indicates success
                self.print_success(f"Deleted test patient: {patient_id}")
            else:
                self.print_warning(f"Could not delete patient: {patient_id}")
                success = False
        
        return success
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print(f"\n{self.colors['bold']}{self.colors['cyan']}🚀 DiagnoAssist Database CRUD Test Suite{self.colors['reset']}")
        print(f"{self.colors['blue']}🎯 Testing server at: {self.base_url}{self.colors['reset']}")
        
        # Check server health
        if not self.check_server_health():
            print(f"\n{self.colors['red']}❌ Server is not responding. Please start the DiagnoAssist server first.{self.colors['reset']}")
            return
        
        # Track test results
        results = {
            'patient_crud': False,
            'episode_crud': False,
            'validation': False,
            'cleanup': False
        }
        
        # Run tests
        try:
            results['patient_crud'] = self.test_patient_crud()
            results['episode_crud'] = self.test_episode_crud()
            results['validation'] = self.test_validation_errors()
            results['cleanup'] = self.test_cleanup()
            
        except KeyboardInterrupt:
            print(f"\n{self.colors['yellow']}⚠️ Tests interrupted by user{self.colors['reset']}")
        except Exception as e:
            print(f"\n{self.colors['red']}❌ Unexpected error: {str(e)}{self.colors['reset']}")
        
        # Print summary
        self.print_test_summary(results)
    
    def print_test_summary(self, results: Dict[str, bool]):
        """Print test results summary"""
        self.print_header("📊 DATABASE CRUD TEST SUMMARY")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        # Print individual results
        for test_name, passed in results.items():
            status = "✅ Passed" if passed else "❌ Failed"
            formatted_name = test_name.replace('_', ' ').title()
            print(f"{formatted_name}: {status}")
        
        # Print totals
        print(f"\n{self.colors['green']}✅ Passed: {passed}{self.colors['reset']}")
        print(f"{self.colors['red']}❌ Failed: {total - passed}{self.colors['reset']}")
        print(f"{self.colors['cyan']}📈 Success Rate: {success_rate:.1f}%{self.colors['reset']}")
        
        # Print recommendations
        if success_rate < 100:
            print(f"{self.colors['yellow']}🔧 Several database issues detected. Check the failed operations above.{self.colors['reset']}")
        else:
            print(f"{self.colors['green']}🎉 All tests passed! Database is working correctly.{self.colors['reset']}")

def main():
    """Main entry point"""
    print("Starting DiagnoAssist Database CRUD Tests...")
    
    # You can customize the server URL here
    server_url = "http://localhost:8000"
    
    # Create and run tester
    tester = DiagnoAssistTester(server_url)
    tester.run_full_test_suite()

if __name__ == "__main__":
    main()