from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from typing import Optional, Dict, Any
from datetime import datetime
from config.fhir_config import FHIRConfig

class ObservationFHIRModel:
    """FHIR Observation model helper"""
    
    # Vital signs codes mapping
    VITAL_SIGNS_CODES = {
        'blood_pressure_systolic': {
            'code': '8480-6',
            'display': 'Systolic blood pressure',
            'system': 'http://loinc.org'
        },
        'blood_pressure_diastolic': {
            'code': '8462-4',
            'display': 'Diastolic blood pressure',
            'system': 'http://loinc.org'
        },
        'heart_rate': {
            'code': '8867-4',
            'display': 'Heart rate',
            'system': 'http://loinc.org'
        },
        'respiratory_rate': {
            'code': '9279-1',
            'display': 'Respiratory rate',
            'system': 'http://loinc.org'
        },
        'body_temperature': {
            'code': '8310-5',
            'display': 'Body temperature',
            'system': 'http://loinc.org'
        },
        'oxygen_saturation': {
            'code': '2708-6',
            'display': 'Oxygen saturation in Arterial blood',
            'system': 'http://loinc.org'
        },
        'body_weight': {
            'code': '29463-7',
            'display': 'Body weight',
            'system': 'http://loinc.org'
        },
        'body_height': {
            'code': '8302-2',
            'display': 'Body height',
            'system': 'http://loinc.org'
        }
    }
    
    @staticmethod
    def create_vital_sign_observation(
        patient_id: str,
        encounter_id: Optional[str],
        vital_type: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None
    ) -> FHIRObservation:
        """Create FHIR Observation for vital signs"""
        
        if vital_type not in ObservationFHIRModel.VITAL_SIGNS_CODES:
            raise ValueError(f"Unknown vital sign type: {vital_type}")
        
        vital_code = ObservationFHIRModel.VITAL_SIGNS_CODES[vital_type]
        
        observation = FHIRObservation()
        observation.id = f"obs-{vital_type}-{patient_id}-{int(datetime.now().timestamp())}"
        observation.status = "final"
        
        # Subject reference
        observation.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Encounter reference
        if encounter_id:
            observation.encounter = Reference(**{
                "reference": f"Encounter/{encounter_id}"
            })
        
        # Category - vital signs
        observation.category = [CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            })]
        })]
        
        # Code
        observation.code = CodeableConcept(**{
            "coding": [Coding(**vital_code)]
        })
        
        # Value
        observation.valueQuantity = Quantity(**{
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit
        })
        
        # Effective DateTime
        observation.effectiveDateTime = (timestamp or datetime.now()).isoformat()
        
        return observation
    
    @staticmethod
    def create_clinical_observation(
        patient_id: str,
        encounter_id: Optional[str],
        code: str,
        display: str,
        value: Any,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        category: str = "exam"
    ) -> FHIRObservation:
        """Create FHIR Observation for clinical findings"""
        
        observation = FHIRObservation()
        observation.id = f"obs-{code}-{patient_id}-{int(datetime.now().timestamp())}"
        observation.status = "final"
        
        # Subject reference
        observation.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Encounter reference
        if encounter_id:
            observation.encounter = Reference(**{
                "reference": f"Encounter/{encounter_id}"
            })
        
        # Category
        category_mapping = {
            "exam": "exam",
            "imaging": "imaging", 
            "laboratory": "laboratory",
            "procedure": "procedure",
            "survey": "survey",
            "therapy": "therapy"
        }
        
        observation.category = [CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": category_mapping.get(category, "exam"),
                "display": category.title()
            })]
        })]
        
        # Code
        observation.code = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://snomed.info/sct",
                "code": code,
                "display": display
            })]
        })
        
        # Value
        if unit and isinstance(value, (int, float)):
            observation.valueQuantity = Quantity(**{
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit
            })
        else:
            observation.valueString = str(value)
        
        # Effective DateTime
        observation.effectiveDateTime = (timestamp or datetime.now()).isoformat()
        
        return observation