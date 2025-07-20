from typing import Dict, List, Optional
from dataclasses import dataclass
from .settings import get_settings

settings = get_settings()

@dataclass
class FHIRConfig:
    """
    FHIR-specific configuration and constants
    """
    
    # FHIR Version Information
    FHIR_VERSION = "4.0.1"
    FHIR_RELEASE = "R4"
    
    # Base URLs
    FHIR_BASE_URL = settings.fhir_base_url
    HL7_BASE_URL = "http://hl7.org/fhir"
    
    # Standard Code Systems
    CODE_SYSTEMS = {
        "loinc": "http://loinc.org",
        "snomed": "http://snomed.info/sct", 
        "icd10": "http://hl7.org/fhir/sid/icd-10",
        "icd10cm": "http://hl7.org/fhir/sid/icd-10-cm",
        "cpt": "http://www.ama-assn.org/go/cpt",
        "rxnorm": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "ucum": "http://unitsofmeasure.org",
        "dicom": "http://dicom.nema.org/resources/ontology/DCM"
    }
    
    # Value Sets
    VALUE_SETS = {
        "administrative_gender": "http://hl7.org/fhir/ValueSet/administrative-gender",
        "marital_status": "http://hl7.org/fhir/ValueSet/marital-status",
        "contact_point_system": "http://hl7.org/fhir/ValueSet/contact-point-system",
        "observation_category": "http://hl7.org/fhir/ValueSet/observation-category",
        "diagnostic_report_status": "http://hl7.org/fhir/ValueSet/diagnostic-report-status",
        "condition_clinical_status": "http://hl7.org/fhir/ValueSet/condition-clinical",
        "encounter_status": "http://hl7.org/fhir/ValueSet/encounter-status",
        "care_plan_status": "http://hl7.org/fhir/ValueSet/care-plan-status"
    }
    
    # Common LOINC Codes for Vital Signs
    VITAL_SIGNS_LOINC = {
        "blood_pressure": "85354-9",  # Blood pressure panel
        "systolic_bp": "8480-6",      # Systolic blood pressure
        "diastolic_bp": "8462-4",     # Diastolic blood pressure  
        "heart_rate": "8867-4",       # Heart rate
        "respiratory_rate": "9279-1",  # Respiratory rate
        "body_temperature": "8310-5",  # Body temperature
        "oxygen_saturation": "2708-6", # Oxygen saturation
        "body_weight": "29463-7",     # Body weight
        "body_height": "8302-2",      # Body height
        "bmi": "39156-5",             # Body mass index
        "pain_scale": "72514-3"       # Pain severity scale
    }
    
    # Common SNOMED CT Codes
    SNOMED_CODES = {
        "chief_complaint": "422979000",  # Chief complaint
        "present_illness": "422979000",   # History of present illness
        "past_medical_history": "371529009", # Past medical history
        "family_history": "57177007",    # Family history
        "social_history": "228272008",   # Social history
        "physical_examination": "5880005", # Physical examination
        "assessment": "386053000",       # Assessment
        "plan": "397943006"              # Plan
    }
    
    # DiagnoAssist Specific Extensions
    DIAGNOASSIST_EXTENSIONS = {
        "ai_confidence": f"{FHIR_BASE_URL}/StructureDefinition/ai-confidence-score",
        "ai_reasoning": f"{FHIR_BASE_URL}/StructureDefinition/ai-reasoning",
        "symptom_severity": f"{FHIR_BASE_URL}/StructureDefinition/symptom-severity",
        "differential_ranking": f"{FHIR_BASE_URL}/StructureDefinition/differential-ranking"
    }
    
    # Resource Profiles
    PROFILES = {
        "patient": f"{FHIR_BASE_URL}/StructureDefinition/DiagnoAssist-Patient",
        "encounter": f"{FHIR_BASE_URL}/StructureDefinition/DiagnoAssist-Encounter", 
        "observation": f"{FHIR_BASE_URL}/StructureDefinition/DiagnoAssist-Observation",
        "diagnostic_report": f"{FHIR_BASE_URL}/StructureDefinition/DiagnoAssist-DiagnosticReport",
        "condition": f"{FHIR_BASE_URL}/StructureDefinition/DiagnoAssist-Condition"
    }
    
    # Search Parameters
    SEARCH_PARAMETERS = {
        "patient": ["name", "given", "family", "birthdate", "gender", "identifier", "active"],
        "encounter": ["patient", "date", "class", "status", "type"],
        "observation": ["patient", "encounter", "category", "code", "date", "value-quantity"],
        "diagnostic_report": ["patient", "encounter", "category", "code", "date", "status"],
        "condition": ["patient", "encounter", "category", "code", "clinical-status"]
    }
    
    # Validation Rules
    VALIDATION_RULES = {
        "require_patient_reference": True,
        "validate_code_systems": True,
        "enforce_cardinality": True,
        "check_invariants": True
    }
    
    @classmethod
    def get_loinc_code(cls, vital_sign: str) -> Optional[str]:
        """Get LOINC code for a vital sign"""
        return cls.VITAL_SIGNS_LOINC.get(vital_sign)
    
    @classmethod
    def get_code_system_url(cls, system_name: str) -> Optional[str]:
        """Get code system URL by name"""
        return cls.CODE_SYSTEMS.get(system_name)
    
    @classmethod
    def is_valid_fhir_resource(cls, resource_type: str) -> bool:
        """Check if resource type is supported"""
        supported_resources = [
            "Patient", "Encounter", "Observation", "DiagnosticReport", 
            "Condition", "CarePlan", "Bundle", "Practitioner", "Organization"
        ]
        return resource_type in supported_resources