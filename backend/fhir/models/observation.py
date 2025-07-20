from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from datetime import datetime
from typing import Optional, Union

class ObservationFHIRModel:
    # LOINC codes for common vital signs
    VITAL_SIGNS_CODES = {
        "blood_pressure_systolic": ("8480-6", "Systolic blood pressure"),
        "blood_pressure_diastolic": ("8462-4", "Diastolic blood pressure"),
        "heart_rate": ("8867-4", "Heart rate"),
        "respiratory_rate": ("9279-1", "Respiratory rate"),
        "body_temperature": ("8310-5", "Body temperature"),
        "oxygen_saturation": ("2708-6", "Oxygen saturation"),
        "body_weight": ("29463-7", "Body weight"),
        "body_height": ("8302-2", "Body height")
    }
    
    @staticmethod
    def create_vital_sign_observation(
        patient_id: str,
        encounter_id: str,
        vital_type: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None
    ) -> Observation:
        
        if vital_type not in ObservationFHIRModel.VITAL_SIGNS_CODES:
            raise ValueError(f"Unknown vital sign type: {vital_type}")
        
        loinc_code, display = ObservationFHIRModel.VITAL_SIGNS_CODES[vital_type]
        
        observation = Observation()
        
        # Set status
        observation.status = "final"
        
        # Set category (vital signs)
        observation.category = [CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            })]
        })]
        
        # Set code (LOINC)
        observation.code = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://loinc.org",
                "code": loinc_code,
                "display": display
            })]
        })
        
        # Set subject (patient reference)
        observation.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Set encounter reference
        if encounter_id:
            observation.encounter = Reference(**{
                "reference": f"Encounter/{encounter_id}"
            })
        
        # Set effective date time
        observation.effectiveDateTime = (timestamp or datetime.utcnow()).isoformat()
        
        # Set value
        observation.valueQuantity = Quantity(**{
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org"
        })
        
        return observation