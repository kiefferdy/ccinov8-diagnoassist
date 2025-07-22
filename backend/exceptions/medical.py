"""
Medical Domain-Specific Exceptions for DiagnoAssist
Handles medical, clinical, and FHIR-related errors
"""

from typing import Optional, Dict, Any, List
from .base import DiagnoAssistException


class MedicalValidationException(DiagnoAssistException):
    """
    Exception for medical data validation errors
    Handles validation of medical codes, terminology, clinical data
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        medical_code: Optional[str] = None,
        code_system: Optional[str] = None,
        severity: str = "error"
    ):
        self.field = field
        self.value = value
        self.medical_code = medical_code
        self.code_system = code_system
        
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if medical_code:
            details["medical_code"] = medical_code
        if code_system:
            details["code_system"] = code_system
        
        super().__init__(
            message=message,
            error_code="MEDICAL_VALIDATION_ERROR",
            details=details,
            severity=severity
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly medical validation message"""
        if self.medical_code and self.code_system:
            return f"Invalid {self.code_system} code: {self.medical_code}"
        elif self.field:
            return f"Invalid value for {self.field.replace('_', ' ').title()}"
        else:
            return "The medical data provided is not valid. Please check and try again."


class FHIRValidationException(DiagnoAssistException):
    """
    Exception for FHIR resource validation errors
    Handles FHIR R4 compliance issues
    """
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        fhir_path: Optional[str] = None,
        validation_errors: Optional[List[str]] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.fhir_path = fhir_path
        self.validation_errors = validation_errors or []
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "fhir_path": fhir_path,
            "validation_errors": self.validation_errors
        }
        
        super().__init__(
            message=message,
            error_code="FHIR_VALIDATION_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly FHIR validation message"""
        if self.resource_type:
            return f"Invalid {self.resource_type} resource format. Please check the data structure."
        else:
            return "The resource format is not FHIR R4 compliant. Please verify the structure."


class ClinicalDataException(DiagnoAssistException):
    """
    Exception for clinical data integrity and safety issues
    Handles critical clinical data problems
    """
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        patient_id: Optional[str] = None,
        episode_id: Optional[str] = None,
        safety_critical: bool = False
    ):
        self.data_type = data_type
        self.patient_id = patient_id
        self.episode_id = episode_id
        self.safety_critical = safety_critical
        
        details = {
            "data_type": data_type,
            "patient_id": patient_id,
            "episode_id": episode_id,
            "safety_critical": safety_critical
        }
        
        severity = "critical" if safety_critical else "error"
        
        super().__init__(
            message=message,
            error_code="CLINICAL_DATA_ERROR",
            details=details,
            severity=severity
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly clinical data error message"""
        if self.safety_critical:
            return "Critical clinical data error detected. Please review immediately."
        elif self.data_type:
            return f"Error in {self.data_type} data. Please verify and correct."
        else:
            return "Clinical data error detected. Please review and correct the information."


class DiagnosisException(DiagnoAssistException):
    """
    Exception for diagnosis-related errors
    Handles AI diagnosis, differential diagnosis, and clinical reasoning issues
    """
    
    def __init__(
        self,
        message: str,
        diagnosis_id: Optional[str] = None,
        icd_code: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        validation_stage: Optional[str] = None
    ):
        self.diagnosis_id = diagnosis_id
        self.icd_code = icd_code
        self.ai_confidence = ai_confidence
        self.validation_stage = validation_stage
        
        details = {
            "diagnosis_id": diagnosis_id,
            "icd_code": icd_code,
            "ai_confidence": ai_confidence,
            "validation_stage": validation_stage
        }
        
        super().__init__(
            message=message,
            error_code="DIAGNOSIS_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly diagnosis error message"""
        if self.validation_stage:
            return f"Error during {self.validation_stage} validation. Please review the diagnosis."
        elif self.icd_code:
            return f"Invalid diagnosis code: {self.icd_code}. Please verify the ICD-10 code."
        else:
            return "Error processing diagnosis. Please review the clinical information."


class TreatmentException(DiagnoAssistException):
    """
    Exception for treatment-related errors
    Handles treatment plans, medication errors, contraindications
    """
    
    def __init__(
        self,
        message: str,
        treatment_id: Optional[str] = None,
        medication_code: Optional[str] = None,
        contraindication: Optional[str] = None,
        dosage_error: bool = False,
        allergy_alert: bool = False
    ):
        self.treatment_id = treatment_id
        self.medication_code = medication_code
        self.contraindication = contraindication
        self.dosage_error = dosage_error
        self.allergy_alert = allergy_alert
        
        details = {
            "treatment_id": treatment_id,
            "medication_code": medication_code,
            "contraindication": contraindication,
            "dosage_error": dosage_error,
            "allergy_alert": allergy_alert
        }
        
        # Safety-critical if allergy or contraindication
        severity = "critical" if (allergy_alert or contraindication) else "error"
        
        super().__init__(
            message=message,
            error_code="TREATMENT_ERROR",
            details=details,
            severity=severity
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly treatment error message"""
        if self.allergy_alert:
            return "ALLERGY ALERT: This medication may cause an allergic reaction."
        elif self.contraindication:
            return f"WARNING: {self.contraindication}. Please review treatment plan."
        elif self.dosage_error:
            return "Dosage error detected. Please verify medication dosing."
        elif self.medication_code:
            return f"Invalid medication code: {self.medication_code}. Please verify."
        else:
            return "Error in treatment plan. Please review before proceeding."


class PatientSafetyException(DiagnoAssistException):
    """
    Exception for patient safety-critical issues
    Always treated as highest priority
    """
    
    def __init__(
        self,
        message: str,
        patient_id: str,
        safety_rule: str,
        risk_level: str = "HIGH",
        immediate_action_required: bool = True,
        clinical_context: Optional[Dict[str, Any]] = None
    ):
        self.patient_id = patient_id
        self.safety_rule = safety_rule
        self.risk_level = risk_level
        self.immediate_action_required = immediate_action_required
        self.clinical_context = clinical_context or {}
        
        details = {
            "patient_id": patient_id,
            "safety_rule": safety_rule,
            "risk_level": risk_level,
            "immediate_action_required": immediate_action_required,
            "clinical_context": self.clinical_context
        }
        
        super().__init__(
            message=message,
            error_code="PATIENT_SAFETY_ALERT",
            details=details,
            severity="critical"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly patient safety message"""
        if self.immediate_action_required:
            return f"PATIENT SAFETY ALERT: {self.safety_rule}. Immediate review required."
        else:
            return f"Patient Safety Warning: {self.safety_rule}. Please review."
    
    def to_fhir_operation_outcome(self) -> Dict[str, Any]:
        """Convert to FHIR OperationOutcome with safety-specific details"""
        outcome = super().to_fhir_operation_outcome()
        
        # Add safety-specific issue
        safety_issue = {
            "severity": "fatal",
            "code": "security",
            "details": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/issue-type",
                        "code": "security",
                        "display": "Security Problem"
                    }
                ],
                "text": f"Patient Safety Alert: {self.safety_rule}"
            },
            "diagnostics": self.message,
            "expression": [f"Patient/{self.patient_id}"]
        }
        
        outcome["issue"].append(safety_issue)
        return outcome


class AIServiceException(DiagnoAssistException):
    """
    Exception for AI/ML service errors
    Handles AI model failures, confidence issues, bias detection
    """
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        confidence_score: Optional[float] = None,
        bias_detected: bool = False,
        model_version: Optional[str] = None,
        input_data_hash: Optional[str] = None
    ):
        self.model_name = model_name
        self.confidence_score = confidence_score
        self.bias_detected = bias_detected
        self.model_version = model_version
        self.input_data_hash = input_data_hash
        
        details = {
            "model_name": model_name,
            "confidence_score": confidence_score,
            "bias_detected": bias_detected,
            "model_version": model_version,
            "input_data_hash": input_data_hash
        }
        
        # Critical if bias detected
        severity = "critical" if bias_detected else "error"
        
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            details=details,
            severity=severity
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly AI service error message"""
        if self.bias_detected:
            return "Potential bias detected in AI analysis. Manual review recommended."
        elif self.confidence_score is not None and self.confidence_score < 0.5:
            return "AI confidence is low. Please verify results manually."
        elif self.model_name:
            return f"AI model '{self.model_name}' encountered an error. Please try again."
        else:
            return "AI analysis failed. Please try again or proceed with manual analysis."