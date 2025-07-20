from typing import Dict, Any, Optional, List
from datetime import datetime, date
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport
from fhir.models.patient import PatientFHIRModel
from fhir.models.encounter import EncounterFHIRModel
from fhir.models.observation import ObservationFHIRModel
from fhir.models.condition import ConditionFHIRModel
from fhir.models.diagnostic_report import DiagnosticReportFHIRModel

class InternalToFHIRTransformer:
    """Transform internal data models to FHIR resources"""
    
    def transform_patient(self, patient_data: Dict[str, Any]) -> FHIRPatient:
        """Transform internal patient data to FHIR Patient resource"""
        return PatientFHIRModel.create_fhir_patient(
            patient_id=patient_data.get('id'),
            first_name=patient_data.get('first_name'),
            last_name=patient_data.get('last_name'),
            birth_date=patient_data.get('date_of_birth'),
            gender=patient_data.get('gender'),
            phone=patient_data.get('phone'),
            email=patient_data.get('email'),
            address=patient_data.get('address')
        )
    
    def transform_encounter(self, encounter_data: Dict[str, Any]) -> FHIREncounter:
        """Transform internal encounter data to FHIR Encounter resource"""
        return EncounterFHIRModel.create_fhir_encounter(
            encounter_id=encounter_data.get('id'),
            patient_id=encounter_data.get('patient_id'),
            status=encounter_data.get('status', 'in-progress'),
            class_code=encounter_data.get('class', 'AMB'),
            type_code=encounter_data.get('type'),
            start_time=encounter_data.get('start_time'),
            end_time=encounter_data.get('end_time'),
            reason_code=encounter_data.get('reason_code'),
            diagnosis=encounter_data.get('diagnosis')
        )
    
    def transform_observation(self, obs_data: Dict[str, Any]) -> FHIRObservation:
        """Transform internal observation data to FHIR Observation resource"""
        if obs_data.get('type') == 'vital_sign':
            return ObservationFHIRModel.create_vital_sign_observation(
                patient_id=obs_data.get('patient_id'),
                encounter_id=obs_data.get('encounter_id'),
                vital_type=obs_data.get('vital_type'),
                value=obs_data.get('value'),
                unit=obs_data.get('unit'),
                timestamp=obs_data.get('timestamp')
            )
        else:
            return ObservationFHIRModel.create_clinical_observation(
                patient_id=obs_data.get('patient_id'),
                encounter_id=obs_data.get('encounter_id'),
                code=obs_data.get('code'),
                display=obs_data.get('display'),
                value=obs_data.get('value'),
                unit=obs_data.get('unit'),
                timestamp=obs_data.get('timestamp'),
                category=obs_data.get('category', 'exam')
            )
    
    def transform_condition(self, condition_data: Dict[str, Any]) -> FHIRCondition:
        """Transform internal condition data to FHIR Condition resource"""
        return ConditionFHIRModel.create_fhir_condition(
            condition_id=condition_data.get('id'),
            patient_id=condition_data.get('patient_id'),
            encounter_id=condition_data.get('encounter_id'),
            code=condition_data.get('code'),
            display=condition_data.get('display'),
            clinical_status=condition_data.get('clinical_status', 'active'),
            verification_status=condition_data.get('verification_status', 'provisional'),
            onset_date=condition_data.get('onset_date'),
            recorded_date=condition_data.get('recorded_date')
        )
    
    def transform_diagnostic_report(self, report_data: Dict[str, Any]) -> FHIRDiagnosticReport:
        """Transform internal diagnostic report to FHIR DiagnosticReport resource"""
        return DiagnosticReportFHIRModel.create_fhir_diagnostic_report(
            report_id=report_data.get('id'),
            patient_id=report_data.get('patient_id'),
            encounter_id=report_data.get('encounter_id'),
            status=report_data.get('status', 'final'),
            category=report_data.get('category', 'LAB'),
            code=report_data.get('code'),
            conclusion=report_data.get('conclusion'),
            effective_date=report_data.get('effective_date'),
            issued_date=report_data.get('issued_date')
        )