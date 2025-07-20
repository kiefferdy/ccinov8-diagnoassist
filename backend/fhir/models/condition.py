from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from typing import Optional
from datetime import datetime, date

class ConditionFHIRModel:
    """FHIR Condition model helper"""
    
    @staticmethod
    def create_fhir_condition(
        condition_id: str,
        patient_id: str,
        encounter_id: Optional[str],
        code: str,
        display: str,
        clinical_status: str = "active",
        verification_status: str = "provisional",
        onset_date: Optional[date] = None,
        recorded_date: Optional[datetime] = None
    ) -> FHIRCondition:
        """Create FHIR Condition resource"""
        
        condition = FHIRCondition()
        condition.id = condition_id
        
        # Subject reference
        condition.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Encounter reference
        if encounter_id:
            condition.encounter = Reference(**{
                "reference": f"Encounter/{encounter_id}"
            })
        
        # Clinical status
        condition.clinicalStatus = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": clinical_status,
                "display": clinical_status.title()
            })]
        })
        
        # Verification status
        condition.verificationStatus = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": verification_status,
                "display": verification_status.title()
            })]
        })
        
        # Code
        condition.code = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://snomed.info/sct",
                "code": code,
                "display": display
            })]
        })
        
        # Onset date
        if onset_date:
            condition.onsetDateTime = onset_date.isoformat()
        
        # Recorded date
        condition.recordedDate = (recorded_date or datetime.now()).isoformat()
        
        return condition