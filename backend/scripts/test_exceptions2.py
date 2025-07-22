#!/usr/bin/env python3
"""
Simple Exception System Test Script
Tests just the exception handling integration without requiring full app
"""

import asyncio
import sys
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

class SimpleExceptionTester:
    """Simple tester for exception system integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
        # Colors for output
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        }
    
    def print_header(self, message: str):
        """Print a styled header"""
        print(f"\n{self.colors['purple']}{self.colors['bold']}{'='*50}")
        print(f"{message}")
        print(f"{'='*50}{self.colors['reset']}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{self.colors['green']}✅ {message}{self.colors['reset']}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{self.colors['red']}❌ {message}{self.colors['reset']}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠️  {message}{self.colors['reset']}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{self.colors['cyan']}ℹ️  {message}{self.colors['reset']}")
    
    def test_basic_connectivity(self):
        """Test basic server connectivity"""
        self.print_header("Testing Basic Connectivity")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Server is responding")
                self.print_info(f"Version: {data.get('version', 'Unknown')}")
                
                exception_available = data.get('exception_handling', False)
                if exception_available:
                    self.print_success("Exception handling system is loaded")
                else:
                    self.print_warning("Exception handling system not available")
                
                self.results.append({"test": "connectivity", "passed": True, "exception_system": exception_available})
                return True, exception_available
            else:
                self.print_error(f"Server returned status {response.status_code}")
                self.results.append({"test": "connectivity", "passed": False, "status": response.status_code})
                return False, False
                
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server - is it running?")
            self.print_info("Try running: python test_app.py")
            self.results.append({"test": "connectivity", "passed": False, "error": "connection_error"})
            return False, False
        except Exception as e:
            self.print_error(f"Connection test failed: {e}")
            self.results.append({"test": "connectivity", "passed": False, "error": str(e)})
            return False, False
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        self.print_header("Testing Health Endpoints")
        
        success = True
        
        # Test basic health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Health endpoint: {data.get('status', 'unknown')}")
                self.results.append({"test": "health_basic", "passed": True})
            else:
                self.print_error(f"Health endpoint returned {response.status_code}")
                self.results.append({"test": "health_basic", "passed": False})
                success = False
        except Exception as e:
            self.print_error(f"Health endpoint failed: {e}")
            self.results.append({"test": "health_basic", "passed": False, "error": str(e)})
            success = False
        
        # Test exception system health
        try:
            response = requests.get(f"{self.base_url}/health/exception-system", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                self.print_success(f"Exception system health: {status}")
                
                if 'exception_mappings' in data:
                    self.print_info(f"Exception mappings: {data['exception_mappings']}")
                
                if 'features' in data:
                    features = data['features']
                    for feature, enabled in features.items():
                        self.print_info(f"  {feature}: {'✅' if enabled else '❌'}")
                
                self.results.append({"test": "health_exception", "passed": True, "status": status})
            
            elif response.status_code == 503:
                data = response.json()
                self.print_warning(f"Exception system unavailable: {data.get('message', 'Unknown')}")
                self.results.append({"test": "health_exception", "passed": False, "status": "unavailable"})
                success = False
            else:
                self.print_error(f"Exception health endpoint returned {response.status_code}")
                self.results.append({"test": "health_exception", "passed": False})
                success = False
                
        except Exception as e:
            self.print_error(f"Exception health test failed: {e}")
            self.results.append({"test": "health_exception", "passed": False, "error": str(e)})
            success = False
        
        return success
    
    def test_basic_error_handling(self):
        """Test basic error handling"""
        self.print_header("Testing Basic Error Handling")
        
        try:
            response = requests.get(f"{self.base_url}/test/basic-error", timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                self.print_success("Basic error endpoint working")
                
                # Check response structure
                if 'error' in data or 'detail' in data:
                    self.print_info("Error response has expected structure")
                    self.results.append({"test": "basic_error", "passed": True})
                    return True
                else:
                    self.print_warning("Error response missing expected fields")
                    self.results.append({"test": "basic_error", "passed": False, "issue": "missing_fields"})
                    return False
            else:
                self.print_error(f"Basic error test returned unexpected status: {response.status_code}")
                self.results.append({"test": "basic_error", "passed": False, "status": response.status_code})
                return False
                
        except Exception as e:
            self.print_error(f"Basic error test failed: {e}")
            self.results.append({"test": "basic_error", "passed": False, "error": str(e)})
            return False
    
    def test_exception_endpoints(self, exception_system_available: bool):
        """Test exception handling endpoints"""
        self.print_header("Testing Exception Endpoints")
        
        if not exception_system_available:
            self.print_warning("Exception system not available - testing fallback behavior")
            
            try:
                response = requests.get(f"{self.base_url}/test/exception/validation", timeout=10)
                if response.status_code == 503:
                    data = response.json()
                    if 'system_unavailable' in data.get('error', {}).get('type', ''):
                        self.print_success("Fallback behavior working correctly")
                        self.results.append({"test": "exception_fallback", "passed": True})
                        return True
                    else:
                        self.print_error("Unexpected fallback response")
                        self.results.append({"test": "exception_fallback", "passed": False})
                        return False
                else:
                    self.print_error(f"Expected 503, got {response.status_code}")
                    self.results.append({"test": "exception_fallback", "passed": False})
                    return False
            except Exception as e:
                self.print_error(f"Fallback test failed: {e}")
                self.results.append({"test": "exception_fallback", "passed": False, "error": str(e)})
                return False
        
        # Test actual exception endpoints
        exception_types = ["validation", "patient_safety", "clinical_data", "general", "standard"]
        success = True
        
        for exc_type in exception_types:
            try:
                response = requests.get(f"{self.base_url}/test/exception/{exc_type}", timeout=10)
                
                # All exception endpoints should return errors (4xx or 5xx)
                if 400 <= response.status_code < 600:
                    data = response.json()
                    self.print_success(f"{exc_type} exception test (status: {response.status_code})")
                    
                    # Check for expected error structure
                    error_info = data.get('error', {})
                    if 'message' in error_info:
                        self.print_info(f"  Message: {error_info['message'][:50]}...")
                    
                    if 'error_code' in error_info:
                        self.print_info(f"  Error code: {error_info['error_code']}")
                    
                    # Check for tracking headers
                    if 'x-request-id' in response.headers:
                        self.print_info(f"  Request ID: {response.headers['x-request-id']}")
                    
                    self.results.append({"test": f"exception_{exc_type}", "passed": True, "status": response.status_code})
                else:
                    self.print_error(f"{exc_type} test returned unexpected status: {response.status_code}")
                    self.results.append({"test": f"exception_{exc_type}", "passed": False})
                    success = False
                    
            except Exception as e:
                self.print_error(f"{exc_type} exception test failed: {e}")
                self.results.append({"test": f"exception_{exc_type}", "passed": False, "error": str(e)})
                success = False
        
        return success
    
    def test_request_tracking(self):
        """Test request tracking functionality"""
        self.print_header("Testing Request Tracking")
        
        try:
            response = requests.get(f"{self.base_url}/test/basic-error", timeout=10)
            
            # Check for tracking headers
            tracking_headers = ['x-request-id', 'x-processing-time']
            found_headers = [h for h in tracking_headers if h in response.headers]
            
            if found_headers:
                self.print_success(f"Request tracking headers found: {found_headers}")
                for header in found_headers:
                    self.print_info(f"  {header}: {response.headers[header]}")
                self.results.append({"test": "request_tracking", "passed": True, "headers": found_headers})
                return True
            else:
                self.print_warning("No request tracking headers found")
                self.print_info("This might be expected if exception middleware isn't configured")
                self.results.append({"test": "request_tracking", "passed": False, "issue": "no_headers"})
                return False
                
        except Exception as e:
            self.print_error(f"Request tracking test failed: {e}")
            self.results.append({"test": "request_tracking", "passed": False, "error": str(e)})
            return False
    
    def generate_report(self):
        """Generate test report"""
        self.print_header("Test Report")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.get('passed', False))
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {self.colors['green']}{passed_tests}{self.colors['reset']}")
        print(f"Failed: {self.colors['red']}{failed_tests}{self.colors['reset']}")
        
        if failed_tests == 0:
            print(f"\n{self.colors['green']}🎉 All tests passed! Exception system integration is working.{self.colors['reset']}")
        else:
            print(f"\n{self.colors['yellow']}⚠️  Some tests failed. This might be expected if exception system isn't fully loaded.{self.colors['reset']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("Exception System Integration Test")
        self.print_info("Testing Step 7.5 integration with minimal app")
        
        # Test connectivity first
        connected, exception_system_available = self.test_basic_connectivity()
        if not connected:
            print(f"\n{self.colors['red']}❌ Cannot connect to server. Please start the test server first:{self.colors['reset']}")
            print(f"{self.colors['cyan']}   python test_app.py{self.colors['reset']}")
            return {"error": "no_connection"}
        
        # Run other tests
        self.test_health_endpoints()
        self.test_basic_error_handling()
        self.test_exception_endpoints(exception_system_available)
        self.test_request_tracking()
        
        return self.generate_report()

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Exception System Integration Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()
    
    tester = SimpleExceptionTester(args.url)
    report = tester.run_all_tests()
    
    if "error" in report:
        sys.exit(1)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit based on results
    if report.get('failed', 0) == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()