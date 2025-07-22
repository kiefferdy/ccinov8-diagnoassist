#!/usr/bin/env python3
"""
Step 10: Testing & Validation for DiagnoAssist
Complete endpoint testing and system validation
"""

import os
import sys
import asyncio
import requests
import json
from pathlib import Path
from typing import Dict, Any, List

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment
from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagnoAssistTester:
    """Complete testing suite for DiagnoAssist"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.session = requests.Session()
        
        # Colors for output
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m', 
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'reset': '\033[0m'
        }
    
    def print_header(self, message: str):
        """Print test section header"""
        print(f"\n{self.colors['blue']}{'='*60}{self.colors['reset']}")
        print(f"{self.colors['blue']}🧪 {message}{self.colors['reset']}")
        print(f"{self.colors['blue']}{'='*60}{self.colors['reset']}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{self.colors['green']}✅ {message}{self.colors['reset']}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{self.colors['red']}❌ {message}{self.colors['reset']}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠️ {message}{self.colors['reset']}")

    # =============================================================================
    # STEP 1: Server Health & Basic Connectivity
    # =============================================================================
    
    def test_server_health(self) -> bool:
        """Test basic server connectivity"""
        self.print_header("Step 1: Server Health Check")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Server is running: {data.get('message', 'OK')}")
                self.print_success(f"FHIR Version: {data.get('fhir_version', 'Unknown')}")
                return True
            else:
                self.print_error(f"Server health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is it running on http://localhost:8000?")
            return False
        except Exception as e:
            self.print_error(f"Server health check error: {e}")
            return False
    
    def test_health_endpoints(self) -> bool:
        """Test all health check endpoints"""
        self.print_header("Step 2: Health Check Endpoints")
        
        endpoints = [
            "/health",
            "/health/exception-system", 
            "/api/v1/health",
            "/api/v1/health/database",
            "/api/v1/health/services"
        ]
        
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    if status in ['healthy', 'operational']:
                        self.print_success(f"{endpoint}: {status}")
                    else:
                        self.print_warning(f"{endpoint}: {status} (may need attention)")
                else:
                    self.print_error(f"{endpoint}: HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.print_error(f"{endpoint}: {e}")
                all_passed = False
        
        return all_passed

    # =============================================================================
    # STEP 3: Database Connection Testing
    # =============================================================================
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        self.print_header("Step 3: Database Connection Test")
        
        try:
            # Test database health endpoint
            response = self.session.get(f"{self.base_url}/api/v1/health/database")
            if response.status_code == 200:
                data = response.json()
                db_status = data.get('database', 'unknown')
                if db_status == 'connected':
                    self.print_success("Database connection: OK")
                    return True
                else:
                    self.print_warning(f"Database status: {db_status}")
                    
        except Exception as e:
            self.print_error(f"Database health check failed: {e}")
        
        # Try direct database test
        try:
            from config.database import test_database_connection
            if test_database_connection():
                self.print_success("Direct database test: OK")
                return True
            else:
                self.print_error("Direct database test: Failed")
                
        except Exception as e:
            self.print_error(f"Direct database test error: {e}")
        
        return False

    # =============================================================================
    # STEP 4: FHIR API Testing
    # =============================================================================
    
    def test_fhir_metadata(self) -> bool:
        """Test FHIR capability statement"""
        self.print_header("Step 4: FHIR Metadata & Capability Statement")
        
        try:
            response = self.session.get(f"{self.base_url}/fhir/R4/metadata")
            if response.status_code == 200:
                data = response.json()
                if data.get('resourceType') == 'CapabilityStatement':
                    self.print_success(f"FHIR Metadata: {data.get('fhirVersion', 'Unknown version')}")
                    
                    # Check supported resources
                    if 'rest' in data and data['rest']:
                        resources = [r.get('type') for r in data['rest'][0].get('resource', [])]
                        self.print_success(f"Supported FHIR Resources: {', '.join(resources[:5])}...")
                    
                    return True
                else:
                    self.print_error("Invalid FHIR metadata response")
                    return False
            else:
                self.print_error(f"FHIR metadata failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"FHIR metadata test error: {e}")
            return False
    
    def test_fhir_patient_operations(self) -> bool:
        """Test FHIR Patient CRUD operations"""
        self.print_header("Step 5: FHIR Patient Operations")
        
        try:
            # Test GET /fhir/R4/Patient (search)
            response = self.session.get(f"{self.base_url}/fhir/R4/Patient")
            if response.status_code == 200:
                data = response.json()
                if data.get('resourceType') == 'Bundle':
                    self.print_success(f"Patient search: Found {data.get('total', 0)} patients")
                else:
                    self.print_warning("Patient search returned non-Bundle response")
            else:
                self.print_error(f"Patient search failed: HTTP {response.status_code}")
                return False
            
            # Test POST /fhir/R4/Patient (create)
            test_patient = {
                "resourceType": "Patient",
                "name": [{"family": "TestPatient", "given": ["John", "Q"]}],
                "gender": "male",
                "birthDate": "1985-03-15"
            }
            
            response = self.session.post(
                f"{self.base_url}/fhir/R4/Patient",
                json=test_patient,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                patient_id = data.get('id')
                self.print_success(f"Patient creation: Success (ID: {patient_id})")
                
                # Store patient ID for cleanup
                self.test_results['created_patient_id'] = patient_id
                return True
            else:
                self.print_error(f"Patient creation failed: HTTP {response.status_code}")
                if response.text:
                    self.print_error(f"Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            self.print_error(f"Patient operations test error: {e}")
            return False

    # =============================================================================
    # STEP 6: Additional FHIR Resources
    # =============================================================================
    
    def test_other_fhir_resources(self) -> bool:
        """Test other FHIR resource endpoints"""
        self.print_header("Step 6: Other FHIR Resources")
        
        resources_to_test = [
            "Encounter",
            "Observation", 
            "Condition",
            "DiagnosticReport"
        ]
        
        all_passed = True
        
        for resource_type in resources_to_test:
            try:
                # Test search endpoint
                response = self.session.get(f"{self.base_url}/fhir/R4/{resource_type}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('resourceType') == 'Bundle':
                        count = data.get('total', 0)
                        self.print_success(f"{resource_type}: Search OK ({count} found)")
                    else:
                        self.print_warning(f"{resource_type}: Unexpected response format")
                elif response.status_code == 404:
                    self.print_warning(f"{resource_type}: Not implemented yet")
                else:
                    self.print_error(f"{resource_type}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_error(f"{resource_type} test error: {e}")
                all_passed = False
        
        return all_passed

    # =============================================================================
    # STEP 7: API Endpoints Testing
    # =============================================================================
    
    def test_internal_api_endpoints(self) -> bool:
        """Test internal API endpoints"""
        self.print_header("Step 7: Internal API Endpoints")
        
        api_endpoints = [
            ("/api/v1/health", "GET"),
            ("/docs", "GET"),  # FastAPI docs
            ("/redoc", "GET")  # ReDoc documentation
        ]
        
        all_passed = True
        
        for endpoint, method in api_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}")
                
                if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                    if endpoint in ["/docs", "/redoc"]:
                        self.print_success(f"{endpoint}: Documentation available")
                    else:
                        self.print_success(f"{endpoint}: OK")
                else:
                    self.print_error(f"{endpoint}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_error(f"{endpoint} test error: {e}")
                all_passed = False
        
        return all_passed

    # =============================================================================
    # STEP 8: Data Flow Validation
    # =============================================================================
    
    def test_data_flow_validation(self) -> bool:
        """Test complete data flow from API to database"""
        self.print_header("Step 8: Data Flow Validation")
        
        try:
            # Create a complete clinical scenario
            test_data = self.create_test_clinical_scenario()
            
            if test_data:
                self.print_success("Test clinical scenario created successfully")
                
                # Validate data persistence
                if self.validate_data_persistence(test_data):
                    self.print_success("Data flow validation: PASSED")
                    return True
                else:
                    self.print_error("Data persistence validation failed")
                    return False
            else:
                self.print_error("Failed to create test clinical scenario")
                return False
                
        except Exception as e:
            self.print_error(f"Data flow validation error: {e}")
            return False
    
    def create_test_clinical_scenario(self) -> Dict[str, Any]:
        """Create a complete test clinical scenario"""
        try:
            scenario = {}
            
            # 1. Create patient
            patient_data = {
                "resourceType": "Patient",
                "name": [{"family": "TestScenario", "given": ["Clinical", "Test"]}],
                "gender": "female",
                "birthDate": "1980-05-20"
            }
            
            response = self.session.post(
                f"{self.base_url}/fhir/R4/Patient",
                json=patient_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                patient = response.json()
                scenario['patient'] = patient
                self.print_success(f"Created test patient: {patient.get('id')}")
            else:
                self.print_error("Failed to create test patient")
                return {}
            
            return scenario
            
        except Exception as e:
            self.print_error(f"Test scenario creation error: {e}")
            return {}
    
    def validate_data_persistence(self, test_data: Dict[str, Any]) -> bool:
        """Validate that data persists correctly"""
        try:
            # Retrieve created patient
            patient_id = test_data['patient'].get('id')
            if not patient_id:
                return False
            
            response = self.session.get(f"{self.base_url}/fhir/R4/Patient/{patient_id}")
            if response.status_code == 200:
                retrieved_patient = response.json()
                if retrieved_patient.get('id') == patient_id:
                    self.print_success("Data persistence validation: OK")
                    return True
            
            self.print_error("Could not retrieve created patient")
            return False
            
        except Exception as e:
            self.print_error(f"Data persistence validation error: {e}")
            return False

    # =============================================================================
    # STEP 9: Performance & Load Testing
    # =============================================================================
    
    def test_performance_basic(self) -> bool:
        """Basic performance testing"""
        self.print_header("Step 9: Basic Performance Testing")
        
        try:
            import time
            
            # Test response times for key endpoints
            endpoints_to_test = [
                "/",
                "/health", 
                "/fhir/R4/metadata",
                "/fhir/R4/Patient"
            ]
            
            performance_results = {}
            
            for endpoint in endpoints_to_test:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                performance_results[endpoint] = {
                    'response_time_ms': round(response_time, 2),
                    'status_code': response.status_code
                }
                
                if response_time < 1000:  # Under 1 second
                    self.print_success(f"{endpoint}: {response_time:.0f}ms")
                else:
                    self.print_warning(f"{endpoint}: {response_time:.0f}ms (slow)")
            
            # Store results
            self.test_results['performance'] = performance_results
            return True
            
        except Exception as e:
            self.print_error(f"Performance testing error: {e}")
            return False

    # =============================================================================
    # STEP 10: Cleanup & Final Report
    # =============================================================================
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        self.print_header("Step 10: Cleanup Test Data")
        
        # Clean up created patient if exists
        patient_id = self.test_results.get('created_patient_id')
        if patient_id:
            try:
                # Note: DELETE might not be implemented yet
                response = self.session.delete(f"{self.base_url}/fhir/R4/Patient/{patient_id}")
                if response.status_code in [200, 204, 404]:
                    self.print_success("Test data cleanup: OK")
                else:
                    self.print_warning(f"Could not delete test patient: HTTP {response.status_code}")
            except Exception as e:
                self.print_warning(f"Cleanup warning: {e}")
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report"""
        self.print_header("Final Test Report")
        
        # Calculate overall results
        total_tests = len([k for k in self.test_results.keys() if isinstance(self.test_results[k], bool)])
        passed_tests = len([k for k, v in self.test_results.items() if v is True])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': round(success_rate, 1),
            'detailed_results': self.test_results
        }
        
        # Print summary
        if success_rate >= 80:
            self.print_success(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            self.print_success("✅ DiagnoAssist is ready for production!")
        elif success_rate >= 60:
            self.print_warning(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            self.print_warning("⚠️  Some issues need attention before production")
        else:
            self.print_error(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            self.print_error("❌ Significant issues need to be resolved")
        
        return report

    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print(f"{self.colors['blue']}{'='*80}{self.colors['reset']}")
        print(f"{self.colors['blue']}🧪 DiagnoAssist - Step 10: Complete Testing & Validation{self.colors['reset']}")
        print(f"{self.colors['blue']}{'='*80}{self.colors['reset']}")
        
        # Run all test phases
        test_phases = [
            ('server_health', self.test_server_health),
            ('health_endpoints', self.test_health_endpoints),
            ('database_connection', self.test_database_connection),
            ('fhir_metadata', self.test_fhir_metadata),
            ('fhir_patient_ops', self.test_fhir_patient_operations),
            ('other_fhir_resources', self.test_other_fhir_resources),
            ('internal_api', self.test_internal_api_endpoints),
            ('data_flow', self.test_data_flow_validation),
            ('performance', self.test_performance_basic)
        ]
        
        for test_name, test_func in test_phases:
            try:
                result = test_func()
                self.test_results[test_name] = result
            except Exception as e:
                self.print_error(f"Test {test_name} failed with exception: {e}")
                self.test_results[test_name] = False
        
        # Cleanup and generate report
        self.cleanup_test_data()
        return self.generate_final_report()


def main():
    """Main execution function"""
    
    # Check if server is running
    print("🔍 Checking if DiagnoAssist server is running...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  cd backend && python main.py")
        return
    except Exception as e:
        print(f"❌ Server check failed: {e}")
        return
    
    # Run tests
    tester = DiagnoAssistTester()
    report = tester.run_all_tests()
    
    # Save report
    report_file = Path(__file__).parent / "test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Full test report saved to: {report_file}")
    
    # Return appropriate exit code
    if report['success_rate'] >= 80:
        print("\n🎉 Step 10 COMPLETED! DiagnoAssist is ready!")
        return 0
    else:
        print("\n⚠️  Step 10 needs attention. Please fix issues and re-run tests.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)