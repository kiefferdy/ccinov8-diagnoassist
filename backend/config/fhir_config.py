from typing import Dict, List, Optional

class FHIRConfig:
    """FHIR configuration and constants"""
    
    # Server configuration
    FHIR_VERSION = "4.0.1"
    FHIR_BASE_URL = "https://api.diagnoassist.com/fhir"
    SERVER_NAME = "DiagnoAssist FHIR Server"
    SERVER_VERSION = "1.0.0"
    
    # Code systems
    CODE_SYSTEMS = {
        "loinc": "http://loinc.org",
        "snomed": "http://snomed.info/sct",
        "icd10": "http://hl7.org/fhir/sid/icd-10",
        "rxnorm": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "ucum": "http://unitsofmeasure.org"
    }
    
    # LOINC codes for vital signs
    VITAL_SIGNS_LOINC = {
        "blood_pressure_systolic": "8480-6",
        "blood_pressure_diastolic": "8462-4", 
        "heart_rate": "8867-4",
        "respiratory_rate": "9279-1",
        "body_temperature": "8310-5",
        "oxygen_saturation": "2708-6",
        "body_weight": "29463-7",
        "body_height": "8302-2"
    }
    
    # Structure definitions
    STRUCTURE_DEFINITIONS = {
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