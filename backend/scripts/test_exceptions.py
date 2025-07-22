#!/usr/bin/env python3
"""
DiagnoAssist Exception Handling Test Suite
Step 7: Exception Handling Validation
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExceptionTestSuite:
    """Test suite for DiagnoAssist exception handling system"""
    
    def __init__(self):
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'reset': '\033[0m'
        }
        
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def print_header(self, text: str) -> None:
        """Print a colored header"""
        print(f"\n{self.colors['blue']}{'='*60}{self.colors['reset']}")
        print(f"{self.colors['blue']}{text.center(60)}{self.colors['reset']}")
        print(f"{self.colors['blue']}{'='*60}{self.colors['reset']}")
    
    def print_success(self, text: str) -> None:
        """Print success message"""
        print(f"{self.colors['green']}✅ {text}{self.colors['reset']}")
    
    def print_error(self, text: str) -> None:
        """Print error message"""
        print(f"{self.colors['red']}❌ {text}{self.colors['reset']}")
    
    def print_warning(self, text: str) -> None:
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠️  {text}{self.colors['reset']}")
    
    def print_info(self, text: str) -> None:
        """Print info message"""
        print(f"{self.colors['cyan']}ℹ️  {text}{self.colors['reset']}")
    
    def test_base_exceptions(self) -> bool:
        """Test base exception classes"""
        print(f"\n{self.colors['purple']}Testing Base Exception Classes{self.colors['reset']}")
        
        try:
            from exceptions.base import (
                DiagnoAssistException,
                APIException,
                DatabaseException,
                ExternalServiceException
            )
            
            # Test DiagnoAssistException
            exc = DiagnoAssistException(
                message="Test error",
                error_code="TEST_ERROR",
                details={"test": "data"},
                user_message="User friendly message"
            )
            
            # Test basic properties
            assert exc.message == "Test error"
            assert exc.error_code == "TEST_ERROR"
            assert exc.user_message == "User friendly message"
            assert exc.error_id is not None
            assert exc.timestamp is not None
            self.print_success("DiagnoAssistException basic properties")
            
            # Test to_dict method
            exc_dict = exc.to_dict()
            assert "error_id" in exc_dict
            assert "error_code" in exc_dict
            assert "message" in exc_dict
            assert exc_dict["message"] == "User friendly message"
            self.print_success("DiagnoAssistException to_dict() method")
            
            # Test FHIR format
            fhir_outcome = exc.to_fhir_operation_outcome()
            assert fhir_outcome["resourceType"] == "OperationOutcome"
            assert "issue" in fhir_outcome
            assert len(fhir_outcome["issue"]) > 0
            self.print_success("DiagnoAssistException FHIR format")
            
            # Test APIException with status code
            api_exc = APIException(
                message="API error",
                status_code=404,
                error_code="NOT_FOUND"
            )
            assert api_exc.status_code == 404
            self.print_success("APIException with status code")
            
            # Test DatabaseException
            db_exc = DatabaseException(
                message="Database error",
                operation="INSERT",
                table="patients",
                constraint="unique_email"
            )
            assert db_exc.operation == "INSERT"
            assert db_exc.table == "patients"
            self.print_success("DatabaseException with operation details")
            
            # Test ExternalServiceException
            ext_exc = ExternalServiceException(
                message="Service error",
                service_name="AI Service",
                endpoint="/predict",
                status_code=503,
                timeout=True
            )
            assert ext_exc.service_name == "AI Service"
            assert ext_exc.timeout is True
            self.print_success("ExternalServiceException with service details")
            
            return True
            
        except Exception as e:
            self.print_error(f"Base exceptions test failed: {str(e)}")
            return False
    
    def test_medical_exceptions(self) -> bool:
        """Test medical domain exceptions"""
        print(f"\n{self.colors['purple']}Testing Medical Domain Exceptions{self.colors['reset']}")
        
        try:
            from exceptions.medical import (
                MedicalValidationException,
                FHIRValidationException,
                ClinicalDataException,
                DiagnosisException,
                TreatmentException,
                PatientSafetyException,
                AIServiceException
            )
            
            # Test MedicalValidationException
            med_exc = MedicalValidationException(
                message="Invalid ICD code",
                field="icd10_code",
                value="Z99.999",
                medical_code="Z99.999",
                code_system="ICD-10"
            )
            assert med_exc.field == "icd10_code"
            assert med_exc.medical_code == "Z99.999"
            self.print_success("MedicalValidationException")
            
            # Test FHIRValidationException
            fhir_exc = FHIRValidationException(
                message="Invalid FHIR resource",
                resource_type="Patient",
                resource_id="123",
                validation_errors=["Missing required field: name"]
            )
            assert fhir_exc.resource_type == "Patient"
            assert len(fhir_exc.validation_errors) == 1
            self.print_success("FHIRValidationException")
            
            # Test PatientSafetyException
            safety_exc = PatientSafetyException(
                message="Critical safety violation",
                patient_id="PAT123",
                safety_rule="Drug allergy check",
                risk_level="HIGH",
                immediate_action_required=True
            )
            assert safety_exc.patient_id == "PAT123"
            assert safety_exc.risk_level == "HIGH"
            assert safety_exc.severity == "critical"
            self.print_success("PatientSafetyException")
            
            # Test DiagnosisException
            diag_exc = DiagnosisException(
                message="Diagnosis validation failed",
                diagnosis_id="DIAG123",
                icd_code="A00.0",
                ai_confidence=0.65
            )
            assert diag_exc.diagnosis_id == "DIAG123"
            assert diag_exc.ai_confidence == 0.65
            self.print_success("DiagnosisException")
            
            # Test TreatmentException
            treat_exc = TreatmentException(
                message="Treatment contraindication",
                treatment_id="TREAT123",
                contraindication="Patient allergy to penicillin",
                allergy_alert=True
            )
            assert treat_exc.contraindication == "Patient allergy to penicillin"
            assert treat_exc.allergy_alert is True
            assert treat_exc.severity == "critical"
            self.print_success("TreatmentException")
            
            # Test AIServiceException
            ai_exc = AIServiceException(
                message="AI bias detected",
                model_name="diagnosis_model_v1",
                confidence_score=0.85,
                bias_detected=True
            )
            assert ai_exc.model_name == "diagnosis_model_v1"
            assert ai_exc.bias_detected is True
            assert ai_exc.severity == "critical"
            self.print_success("AIServiceException")
            
            return True
            
        except Exception as e:
            self.print_error(f"Medical exceptions test failed: {str(e)}")
            return False
    
    def test_validation_exceptions(self) -> bool:
        """Test validation exception classes"""
        print(f"\n{self.colors['purple']}Testing Validation Exceptions{self.colors['reset']}")
        
        try:
            from exceptions.validation import (
                ValidationException,
                SchemaValidationException,
                BusinessRuleException,
                DataIntegrityException,
                ConcurrencyException,
                RateLimitException
            )
            
            # Test ValidationException
            val_exc = ValidationException(
                message="Invalid email format",
                field="email",
                value="invalid-email",
                expected_type="email",
                validation_rule="email_format"
            )
            assert val_exc.field == "email"
            assert val_exc.validation_rule == "email_format"
            self.print_success("ValidationException")
            
            # Test SchemaValidationException
            schema_errors = [
                {"loc": ["email"], "msg": "field required", "type": "value_error.missing"},
                {"loc": ["age"], "msg": "ensure this value is greater than 0", "type": "value_error"}
            ]
            schema_exc = SchemaValidationException(
                message="Schema validation failed",
                validation_errors=schema_errors,
                schema_name="PatientCreate"
            )
            assert len(schema_exc.validation_errors) == 2
            assert schema_exc.schema_name == "PatientCreate"
            
            field_errors = schema_exc.get_field_errors()
            assert "email" in field_errors
            assert "age" in field_errors
            self.print_success("SchemaValidationException")
            
            # Test BusinessRuleException
            rule_exc = BusinessRuleException(
                message="Age restriction violated",
                rule_name="minimum_age_18",
                rule_description="Patient must be at least 18 years old",
                suggested_action="Update patient age or contact guardian"
            )
            assert rule_exc.rule_name == "minimum_age_18"
            assert rule_exc.suggested_action is not None
            self.print_success("BusinessRuleException")
            
            # Test DataIntegrityException
            integrity_exc = DataIntegrityException(
                message="Unique constraint violation",
                integrity_type="unique",
                table_name="patients",
                column_name="email",
                constraint_name="unique_patient_email"
            )
            assert integrity_exc.integrity_type == "unique"
            assert integrity_exc.table_name == "patients"
            self.print_success("DataIntegrityException")
            
            # Test ConcurrencyException
            concur_exc = ConcurrencyException(
                message="Version conflict",
                resource_type="Patient",
                resource_id="PAT123",
                expected_version=1,
                actual_version=2,
                conflict_user="dr.smith"
            )
            assert concur_exc.expected_version == 1
            assert concur_exc.actual_version == 2
            self.print_success("ConcurrencyException")
            
            return True
            
        except Exception as e:
            self.print_error(f"Validation exceptions test failed: {str(e)}")
            return False
    
    def test_resource_exceptions(self) -> bool:
        """Test resource management exceptions"""
        print(f"\n{self.colors['purple']}Testing Resource Management Exceptions{self.colors['reset']}")
        
        try:
            from exceptions.resource import (
                ResourceNotFoundException,
                ResourceConflictException,
                ResourcePermissionException,
                ResourceLockedException,
                ResourceStateException
            )
            
            # Test ResourceNotFoundException
            not_found_exc = ResourceNotFoundException(
                resource_type="Patient",
                identifier="PAT999",
                identifier_type="id"
            )
            assert not_found_exc.resource_type == "Patient"
            assert not_found_exc.identifier == "PAT999"
            
            # Test FHIR format for not found
            fhir_outcome = not_found_exc.to_fhir_operation_outcome()
            assert fhir_outcome["issue"][0]["code"] == "not-found"
            self.print_success("ResourceNotFoundException")
            
            # Test ResourceConflictException
            conflict_exc = ResourceConflictException(
                message="Email already exists",
                resource_type="Patient",
                conflict_type="duplicate",
                conflicting_field="email",
                conflicting_value="test@example.com"
            )
            assert conflict_exc.conflict_type == "duplicate"
            assert conflict_exc.conflicting_field == "email"
            self.print_success("ResourceConflictException")
            
            # Test ResourcePermissionException
            perm_exc = ResourcePermissionException(
                message="Access denied",
                resource_type="Patient",
                resource_id="PAT123",
                action="write",
                required_permission="patient.write"
            )
            assert perm_exc.action == "write"
            assert perm_exc.required_permission == "patient.write"
            self.print_success("ResourcePermissionException")
            
            # Test ResourceLockedException
            lock_exc = ResourceLockedException(
                message="Resource locked",
                resource_type="Patient",
                resource_id="PAT123",
                locked_by="dr.smith",
                lock_reason="Currently being edited"
            )
            assert lock_exc.locked_by == "dr.smith"
            assert lock_exc.lock_reason == "Currently being edited"
            self.print_success("ResourceLockedException")
            
            # Test ResourceStateException
            state_exc = ResourceStateException(
                message="Invalid state transition",
                resource_type="Episode",
                resource_id="EP123",
                current_state="completed",
                attempted_action="reopen",
                valid_actions=["archive", "review"]
            )
            assert state_exc.current_state == "completed"
            assert "archive" in state_exc.valid_actions
            self.print_success("ResourceStateException")
            
            return True
            
        except Exception as e:
            self.print_error(f"Resource exceptions test failed: {str(e)}")
            return False
    
    def test_authentication_exceptions(self) -> bool:
        """Test authentication and authorization exceptions"""
        print(f"\n{self.colors['purple']}Testing Authentication Exceptions{self.colors['reset']}")
        
        try:
            from exceptions.authentication import (
                AuthenticationException,
                AuthorizationException,
                TokenException,
                SessionException,
                MFAException
            )
            
            # Test AuthenticationException
            auth_exc = AuthenticationException(
                message="Login failed",
                auth_method="password",
                username="user123",
                failure_reason="invalid_credentials",
                attempt_count=3
            )
            assert auth_exc.auth_method == "password"
            assert auth_exc.failure_reason == "invalid_credentials"
            # Check that username is masked in details
            assert "***" in auth_exc.details["username"]
            self.print_success("AuthenticationException")
            
            # Test AuthorizationException
            authz_exc = AuthorizationException(
                message="Access denied",
                user_id="user123",
                resource="Patient/PAT123",
                action="read",
                required_role="physician"
            )
            assert authz_exc.action == "read"
            assert authz_exc.required_role == "physician"
            self.print_success("AuthorizationException")
            
            # Test TokenException
            token_exc = TokenException(
                message="Token expired",
                token_type="jwt",
                token_error="expired",
                token_id="tok123"
            )
            assert token_exc.token_type == "jwt"
            assert token_exc.token_error == "expired"
            self.print_success("TokenException")
            
            # Test SessionException
            session_exc = SessionException(
                message="Session invalid",
                session_id="sess123",
                session_error="expired",
                user_id="user123"
            )
            assert session_exc.session_error == "expired"
            self.print_success("SessionException")
            
            # Test MFAException
            mfa_exc = MFAException(
                message="Invalid MFA code",
                mfa_method="totp",
                mfa_error="invalid_code",
                attempts_remaining=2
            )
            assert mfa_exc.mfa_method == "totp"
            assert mfa_exc.attempts_remaining == 2
            self.print_success("MFAException")
            
            return True
            
        except Exception as e:
            self.print_error(f"Authentication exceptions test failed: {str(e)}")
            return False
    
    def test_exception_handlers(self) -> bool:
        """Test exception handlers and utilities"""
        print(f"\n{self.colors['purple']}Testing Exception Handlers{self.colors['reset']}")
        
        try:
            from exceptions.handlers import (
                log_exception,
                create_error_response,
                get_status_code_for_exception,
                handle_service_exception,
                raise_for_patient_safety
            )
            from exceptions.base import DiagnoAssistException
            from exceptions.medical import PatientSafetyException
            from exceptions.validation import ValidationException
            
            # Test get_status_code_for_exception
            val_exc = ValidationException("Test validation error")
            status_code = get_status_code_for_exception(val_exc)
            assert status_code == 400
            self.print_success("get_status_code_for_exception")
            
            # Test create_error_response
            error_response = create_error_response(val_exc)
            assert "error" in error_response
            assert "success" in error_response
            assert error_response["success"] is False
            self.print_success("create_error_response")
            
            # Test FHIR format response
            fhir_response = create_error_response(val_exc, fhir_format=True)
            assert fhir_response["resourceType"] == "OperationOutcome"
            self.print_success("create_error_response FHIR format")
            
            # Test raise_for_patient_safety
            try:
                raise_for_patient_safety(
                    condition=True,
                    message="Test safety violation",
                    patient_id="PAT123",
                    safety_rule="Test rule"
                )
                # Should not reach here
                assert False, "Expected PatientSafetyException"
            except PatientSafetyException as safety_exc:
                assert safety_exc.patient_id == "PAT123"
                assert safety_exc.safety_rule == "Test rule"
                self.print_success("raise_for_patient_safety")
            
            # Test handle_service_exception decorator
            @handle_service_exception
            def test_service_method():
                raise ValueError("Test error")
            
            try:
                test_service_method()
                assert False, "Expected DiagnoAssistException"
            except DiagnoAssistException as service_exc:
                assert service_exc.error_code == "SERVICE_ERROR"
                self.print_success("handle_service_exception decorator")
            
            return True
            
        except Exception as e:
            self.print_error(f"Exception handlers test failed: {str(e)}")
            return False
    
    def test_exception_status_mapping(self) -> bool:
        """Test exception to HTTP status code mapping"""
        print(f"\n{self.colors['purple']}Testing Exception Status Mapping{self.colors['reset']}")
        
        try:
            from exceptions import EXCEPTION_STATUS_MAP
            from exceptions.validation import ValidationException
            from exceptions.authentication import AuthenticationException
            from exceptions.resource import ResourceNotFoundException
            
            # Test that mapping contains expected exceptions
            assert ValidationException in EXCEPTION_STATUS_MAP
            assert EXCEPTION_STATUS_MAP[ValidationException] == 400
            self.print_success("ValidationException maps to 400")
            
            assert AuthenticationException in EXCEPTION_STATUS_MAP
            assert EXCEPTION_STATUS_MAP[AuthenticationException] == 401
            self.print_success("AuthenticationException maps to 401")
            
            assert ResourceNotFoundException in EXCEPTION_STATUS_MAP
            assert EXCEPTION_STATUS_MAP[ResourceNotFoundException] == 404
            self.print_success("ResourceNotFoundException maps to 404")
            
            # Check that we have a reasonable number of mappings
            assert len(EXCEPTION_STATUS_MAP) >= 10
            self.print_success(f"Status mapping contains {len(EXCEPTION_STATUS_MAP)} exception types")
            
            return True
            
        except Exception as e:
            self.print_error(f"Exception status mapping test failed: {str(e)}")
            return False
    
    def test_middleware_imports(self) -> bool:
        """Test middleware imports"""
        print(f"\n{self.colors['purple']}Testing Middleware Imports{self.colors['reset']}")
        
        try:
            from exceptions.middleware import (
                DiagnoAssistExceptionMiddleware,
                RequestContextMiddleware,
                ErrorRateLimitingMiddleware,
                setup_middleware
            )
            
            self.print_success("DiagnoAssistExceptionMiddleware imported")
            self.print_success("RequestContextMiddleware imported")
            self.print_success("ErrorRateLimitingMiddleware imported")
            self.print_success("setup_middleware imported")
            
            return True
            
        except Exception as e:
            self.print_error(f"Middleware imports test failed: {str(e)}")
            return False
    
    def test_exception_module_exports(self) -> bool:
        """Test that all exceptions are properly exported"""
        print(f"\n{self.colors['purple']}Testing Exception Module Exports{self.colors['reset']}")
        
        try:
            import exceptions
            
            # Test that __all__ is defined
            assert hasattr(exceptions, "__all__")
            assert len(exceptions.__all__) > 20
            self.print_success(f"Module exports {len(exceptions.__all__)} items")
            
            # Test that key exceptions are exported
            key_exceptions = [
                "DiagnoAssistException",
                "ValidationException",
                "PatientSafetyException",
                "ResourceNotFoundException",
                "AuthenticationException"
            ]
            
            for exc_name in key_exceptions:
                assert exc_name in exceptions.__all__
                assert hasattr(exceptions, exc_name)
                self.print_success(f"{exc_name} properly exported")
            
            # Test that handlers are exported
            handler_functions = [
                "setup_exception_handlers",
                "create_error_response",
                "log_exception"
            ]
            
            for func_name in handler_functions:
                assert func_name in exceptions.__all__
                assert hasattr(exceptions, func_name)
                self.print_success(f"{func_name} properly exported")
            
            return True
            
        except Exception as e:
            self.print_error(f"Exception module exports test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all exception handling tests"""
        self.print_header("DiagnoAssist Exception Handling Test Suite")
        self.print_info("Step 7: Exception Handling Validation")
        
        tests = [
            ("Base Exception Classes", self.test_base_exceptions),
            ("Medical Domain Exceptions", self.test_medical_exceptions),
            ("Validation Exceptions", self.test_validation_exceptions),
            ("Resource Management Exceptions", self.test_resource_exceptions),
            ("Authentication Exceptions", self.test_authentication_exceptions),
            ("Exception Handlers", self.test_exception_handlers),
            ("Exception Status Mapping", self.test_exception_status_mapping),
            ("Middleware Imports", self.test_middleware_imports),
            ("Module Exports", self.test_exception_module_exports)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                    logger.info(f"{test_name}: PASSED")
                else:
                    logger.error(f"{test_name}: FAILED")
                    self.test_results['failed'] += 1
            except Exception as e:
                logger.error(f"{test_name}: ERROR - {str(e)}")
                self.test_results['errors'].append(f"{test_name}: {str(e)}")
                self.test_results['failed'] += 1
        
        self.test_results['passed'] = passed
        
        # Print summary
        self.print_header("Test Results Summary")
        
        if passed == total:
            self.print_success(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
            self.print_success("✅ Step 7: Exception Handling is complete!")
            self.print_success("✅ Comprehensive exception system implemented")
            self.print_success("✅ Medical domain exceptions working")
            self.print_success("✅ FHIR-compliant error responses")
            self.print_success("✅ Patient safety alerting system")
            self.print_success("✅ Ready for Step 8: API Routers")
            
            print("\n🚀 Exception Handling Features:")
            print("   • Base exception hierarchy with rich context")
            print("   • Medical domain-specific exceptions")
            print("   • FHIR R4 compliant OperationOutcome responses")
            print("   • Patient safety critical alerting")
            print("   • Validation and business rule exceptions")
            print("   • Resource management exceptions")
            print("   • Authentication/authorization exceptions")
            print("   • External service integration exceptions")
            print("   • Comprehensive error logging and monitoring")
            print("   • Rate limiting and security event tracking")
            
            print("\n📋 Next Steps (Step 8):")
            print("   1. Create API routers with proper exception handling")
            print("   2. Integrate routers with services layer")
            print("   3. Add endpoint-specific error handling")
            print("   4. Implement FHIR endpoints with exception support")
            
            return True
        else:
            self.print_error(f"❌ TESTS FAILED: {passed}/{total} passed")
            self.print_error(f"Failed tests: {self.test_results['failed']}")
            
            if self.test_results['errors']:
                print(f"\n{self.colors['red']}Errors encountered:{self.colors['reset']}")
                for error in self.test_results['errors'][:5]:  # Show first 5 errors
                    self.print_error(f"  {error}")
            
            return False


def main():
    """Main test runner"""
    test_suite = ExceptionTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()