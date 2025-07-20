from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.period import Period
from typing import Optional, List
from datetime import datetime

class EncounterFHIRModel:
    """FHIR Encounter model helper"""
    
    @staticmethod
    def create_fhir_encounter(
        encounter_id: str,
        patient_id: str,
        status: str = "in-progress",
        class_code: str = "AMB",
        type_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        reason_code: Optional[str] = None,
        diagnosis: Optional[List[Dict]] = None
    ) -> FHIREncounter:
        """Create FHIR Encounter resource"""
        
        encounter = FHIREncounter()
        encounter.id = encounter_id
        encounter.status = status
        
        # Subject reference
        encounter.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Class
        encounter.class_ = Coding(**{
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": class_code,
            "display": EncounterFHIRModel._get_class_display(class_code)
        })
        
        # Type
        if type_code:
            encounter.type = [CodeableConcept(**{
                "coding": [Coding(**{
                    "system": "http://snomed.info/sct",
                    "code": type_code,
                    "display": "Medical consultation"
                })]
            })]
        
        # Period
        if start_time or end_time:
            period_data = {}
            if start_time:
                period_data["start"] = start_time.isoformat()
            if end_time:
                period_data["end"] = end_time.isoformat()
            encounter.period = Period(**period_data)
        
        # Reason
        if reason_code:
            encounter.reasonCode = [CodeableConcept(**{
                "coding": [Coding(**{
                    "system": "http://snomed.info/sct",
                    "code": reason_code,
                    "display": "Medical evaluation"
                })]
            })]
        
        return encounter
    
    @staticmethod
    def _get_class_display(class_code: str) -> str:
        """Get display name for encounter class"""
        class_displays = {
            "AMB": "ambulatory",
            "EMER": "emergency", 
            "IMP": "inpatient encounter",
            "OBSENC": "observation encounter",
            "PRENC": "pre-admission",
            "SS": "short stay"
        }
        return class_displays.get(class_code, "ambulatory")