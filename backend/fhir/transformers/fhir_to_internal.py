from typing import Dict, Any, Optional
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport

class FHIRToInternalTransformer:
    """Transform FHIR resources to internal data models"""
    
    def transform_patient(self, fhir_patient: FHIRPatient) -> Dict[str, Any]:
        """Transform FHIR Patient resource to internal patient data"""
        patient_data = {
            'id': fhir_patient.id,
            'active': True
        }
        
        # Extract name
        if fhir_patient.name:
            name = fhir_patient.name[0]
            patient_data['first_name'] = name.given[0] if name.given else ''
            patient_data['last_name'] = name.family or ''
        
        # Extract birth date and gender
        patient_data['date_of_birth'] = fhir_patient.birthDate
        patient_data['gender'] = fhir_patient.gender
        
        # Extract contact info
        contact_info = {}
        if fhir_patient.telecom:
            for telecom in fhir_patient.telecom:
                if telecom.system == 'phone':
                    contact_info['phone'] = telecom.value
                elif telecom.system == 'email':
                    contact_info['email'] = telecom.value
        
        # Extract address
        if fhir_patient.address:
            addr = fhir_patient.address[0]
            contact_info['address'] = {
                'street': addr.line[0] if addr.line else '',
                'city': addr.city or '',
                'state': addr.state or '',
                'zip': addr.postalCode or '',
                'country': addr.country or ''
            }
        
        patient_data['contact_info'] = contact_info
        return patient_data
    
    def transform_encounter(self, fhir_encounter: FHIREncounter) -> Dict[str, Any]:
        """Transform FHIR Encounter resource to internal encounter data"""
        encounter_data = {
            'id': fhir_encounter.id,
            'patient_id': fhir_encounter.subject.reference.split('/')[-1],
            'status': fhir_encounter.status,
            'class': fhir_encounter.class_.code if fhir_encounter.class_ else 'AMB'
        }
        
        # Extract period
        if fhir_encounter.period:
            encounter_data['start_time'] = fhir_encounter.period.start
            encounter_data['end_time'] = fhir_encounter.period.end
        
        # Extract type and reason
        if fhir_encounter.type:
            encounter_data['type'] = fhir_encounter.type[0].coding[0].code
        
        if fhir_encounter.reasonCode:
            encounter_data['reason_code'] = fhir_encounter.reasonCode[0].coding[0].code
        
        return encounter_data
    
    def transform_observation(self, fhir_observation: FHIRObservation) -> Dict[str, Any]:
        """Transform FHIR Observation resource to internal observation data"""
        obs_data = {
            'id': fhir_observation.id,
            'patient_id': fhir_observation.subject.reference.split('/')[-1],
            'status': fhir_observation.status
        }
        
        # Extract encounter reference
        if fhir_observation.encounter:
            obs_data['encounter_id'] = fhir_observation.encounter.reference.split('/')[-1]
        
        # Extract code and category
        if fhir_observation.code:
            coding = fhir_observation.code.coding[0]
            obs_data['code'] = coding.code
            obs_data['display'] = coding.display
            obs_data['system'] = coding.system
        
        if fhir_observation.category:
            obs_data['category'] = fhir_observation.category[0].coding[0].code
        
        # Extract value
        if hasattr(fhir_observation, 'valueQuantity') and fhir_observation.valueQuantity:
            obs_data['value'] = fhir_observation.valueQuantity.value
            obs_data['unit'] = fhir_observation.valueQuantity.unit
        elif hasattr(fhir_observation, 'valueString') and fhir_observation.valueString:
            obs_data['value'] = fhir_observation.valueString
        
        # Extract timestamp
        obs_data['timestamp'] = fhir_observation.effectiveDateTime
        
        return obs_data