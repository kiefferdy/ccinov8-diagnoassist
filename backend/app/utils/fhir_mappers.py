"""
FHIR mappers for converting between internal models and FHIR resources
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from fhirclient.models import patient as fhir_patient
from fhirclient.models import observation as fhir_observation
from fhirclient.models import condition as fhir_condition
from fhirclient.models import encounter as fhir_encounter
from fhirclient.models import humanname, contactpoint, identifier, fhirdate, codeableconcept, coding, fhirreference

from app.models.patient import PatientModel, PatientDemographics, MedicalBackground, AllergyInfo
from app.models.encounter import EncounterModel, EncounterTypeEnum, EncounterStatusEnum
from app.models.episode import EpisodeModel, EpisodeCategoryEnum, EpisodeStatusEnum
from app.models.soap import SOAPModel
from app.models.fhir_models import (
    FHIRPatientGender, FHIRContactPointSystem, FHIRContactPointUse,
    FHIRObservationStatus, FHIRConditionClinicalStatus, FHIREncounterStatus, FHIREncounterClass
)


class FHIRMapper:
    """Mapper class for converting between internal models and FHIR resources"""
    
    @staticmethod
    def patient_to_fhir(patient: PatientModel) -> fhir_patient.Patient:
        """Convert internal PatientModel to FHIR Patient resource"""
        fhir_pat = fhir_patient.Patient()
        
        # Set active status
        fhir_pat.active = True
        
        # Add identifier
        if patient.id:
            pat_identifier = identifier.Identifier()
            pat_identifier.use = "usual"
            pat_identifier.system = "urn:diagnoassist:patient-id"
            pat_identifier.value = patient.id
            fhir_pat.identifier = [pat_identifier]
        
        # Add name
        if patient.demographics:
            name = humanname.HumanName()
            name.use = "official"
            
            # Split full name into family and given names
            full_name = patient.demographics.name
            if full_name:
                name_parts = full_name.strip().split()
                if len(name_parts) >= 2:
                    name.family = name_parts[-1]  # Last part as family name
                    name.given = name_parts[:-1]  # All other parts as given names
                elif len(name_parts) == 1:
                    name.given = [name_parts[0]]
                
                name.text = full_name
            
            fhir_pat.name = [name]
            
            # Add gender
            if patient.demographics.gender:
                gender_map = {
                    "Male": "male",
                    "Female": "female",
                    "Other": "other",
                    "Unknown": "unknown"
                }
                fhir_pat.gender = gender_map.get(patient.demographics.gender, "unknown")
            
            # Add birth date
            if patient.demographics.date_of_birth:
                if isinstance(patient.demographics.date_of_birth, str):
                    fhir_pat.birthDate = fhirdate.FHIRDate(patient.demographics.date_of_birth)
                elif isinstance(patient.demographics.date_of_birth, date):
                    fhir_pat.birthDate = fhirdate.FHIRDate(patient.demographics.date_of_birth.isoformat())
            
            # Add contact information
            telecom = []
            
            # Phone
            if patient.demographics.phone:
                phone_contact = contactpoint.ContactPoint()
                phone_contact.system = "phone"
                phone_contact.use = "home"
                phone_contact.value = patient.demographics.phone
                telecom.append(phone_contact)
            
            # Email
            if patient.demographics.email:
                email_contact = contactpoint.ContactPoint()
                email_contact.system = "email"
                email_contact.use = "home"
                email_contact.value = patient.demographics.email
                telecom.append(email_contact)
            
            if telecom:
                fhir_pat.telecom = telecom
        
        return fhir_pat
    
    @staticmethod
    def fhir_to_patient(fhir_pat: fhir_patient.Patient) -> PatientModel:
        """Convert FHIR Patient resource to internal PatientModel"""
        # Extract basic demographics
        demographics = PatientDemographics()
        
        # Extract name
        if fhir_pat.name and len(fhir_pat.name) > 0:
            name_obj = fhir_pat.name[0]
            if name_obj.text:
                demographics.name = name_obj.text
            elif name_obj.given or name_obj.family:
                name_parts = []
                if name_obj.given:
                    name_parts.extend(name_obj.given)
                if name_obj.family:
                    name_parts.append(name_obj.family)
                demographics.name = " ".join(name_parts)
        
        # Extract gender
        if fhir_pat.gender:
            gender_map = {
                "male": "Male",
                "female": "Female",
                "other": "Other",
                "unknown": "Unknown"
            }
            demographics.gender = gender_map.get(fhir_pat.gender, "Unknown")
        
        # Extract birth date
        if fhir_pat.birthDate:
            demographics.date_of_birth = fhir_pat.birthDate.date
        
        # Extract contact information
        if fhir_pat.telecom:
            for contact in fhir_pat.telecom:
                if contact.system == "phone":
                    demographics.phone = contact.value
                elif contact.system == "email":
                    demographics.email = contact.value
        
        # Extract identifier for internal ID
        patient_id = None
        if fhir_pat.identifier:
            for ident in fhir_pat.identifier:
                if ident.system == "urn:diagnoassist:patient-id":
                    patient_id = ident.value
                    break
        
        # If no internal ID found, use FHIR ID
        if not patient_id and fhir_pat.id:
            patient_id = f"fhir-{fhir_pat.id}"
        
        # Create patient model
        patient = PatientModel(
            id=patient_id,
            demographics=demographics,
            medical_background=MedicalBackground()  # Initialize empty
        )
        
        return patient
    
    @staticmethod
    def soap_to_fhir_observations(
        soap: SOAPModel, 
        patient_fhir_id: str, 
        encounter_fhir_id: Optional[str] = None
    ) -> List[fhir_observation.Observation]:
        """Convert SOAP data to FHIR Observation resources"""
        observations = []
        
        # Subjective observations
        if soap.subjective.chief_complaint:
            obs = fhir_observation.Observation()
            obs.status = "final"
            
            # Code for chief complaint
            obs.code = codeableconcept.CodeableConcept()
            obs.code.text = "Chief Complaint"
            
            # Value
            obs.valueString = soap.subjective.chief_complaint
            
            # Subject reference
            obs.subject = fhirreference.FHIRReference()
            obs.subject.reference = f"Patient/{patient_fhir_id}"
            
            # Encounter reference
            if encounter_fhir_id:
                obs.encounter = fhirreference.FHIRReference()
                obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
            
            # Category
            obs.category = [codeableconcept.CodeableConcept()]
            obs.category[0].text = "survey"
            
            observations.append(obs)
        
        # History of Present Illness
        if soap.subjective.history_of_present_illness:
            obs = fhir_observation.Observation()
            obs.status = "final"
            
            obs.code = codeableconcept.CodeableConcept()
            obs.code.text = "History of Present Illness"
            
            obs.valueString = soap.subjective.history_of_present_illness
            
            obs.subject = fhirreference.FHIRReference()
            obs.subject.reference = f"Patient/{patient_fhir_id}"
            
            if encounter_fhir_id:
                obs.encounter = fhirreference.FHIRReference()
                obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
            
            obs.category = [codeableconcept.CodeableConcept()]
            obs.category[0].text = "survey"
            
            observations.append(obs)
        
        # Review of Systems
        if soap.subjective.review_of_systems:
            obs = fhir_observation.Observation()
            obs.status = "final"
            
            obs.code = codeableconcept.CodeableConcept()
            obs.code.text = "Review of Systems"
            
            obs.valueString = soap.subjective.review_of_systems
            
            obs.subject = fhirreference.FHIRReference()
            obs.subject.reference = f"Patient/{patient_fhir_id}"
            
            if encounter_fhir_id:
                obs.encounter = fhirreference.FHIRReference()
                obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
            
            obs.category = [codeableconcept.CodeableConcept()]
            obs.category[0].text = "survey"
            
            observations.append(obs)
        
        # Objective - Vital Signs
        if soap.objective.vital_signs:
            # Blood Pressure
            if soap.objective.vital_signs.blood_pressure:
                obs = fhir_observation.Observation()
                obs.status = "final"
                
                obs.code = codeableconcept.CodeableConcept()
                obs.code.text = "Blood Pressure"
                
                obs.valueString = soap.objective.vital_signs.blood_pressure
                
                obs.subject = fhirreference.FHIRReference()
                obs.subject.reference = f"Patient/{patient_fhir_id}"
                
                if encounter_fhir_id:
                    obs.encounter = fhirreference.FHIRReference()
                    obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
                
                obs.category = [codeableconcept.CodeableConcept()]
                obs.category[0].text = "vital-signs"
                
                observations.append(obs)
            
            # Heart Rate
            if soap.objective.vital_signs.heart_rate:
                obs = fhir_observation.Observation()
                obs.status = "final"
                
                obs.code = codeableconcept.CodeableConcept()
                obs.code.text = "Heart Rate"
                
                obs.valueString = soap.objective.vital_signs.heart_rate
                
                obs.subject = fhirreference.FHIRReference()
                obs.subject.reference = f"Patient/{patient_fhir_id}"
                
                if encounter_fhir_id:
                    obs.encounter = fhirreference.FHIRReference()
                    obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
                
                obs.category = [codeableconcept.CodeableConcept()]
                obs.category[0].text = "vital-signs"
                
                observations.append(obs)
            
            # Temperature
            if soap.objective.vital_signs.temperature:
                obs = fhir_observation.Observation()
                obs.status = "final"
                
                obs.code = codeableconcept.CodeableConcept()
                obs.code.text = "Body Temperature"
                
                obs.valueString = soap.objective.vital_signs.temperature
                
                obs.subject = fhirreference.FHIRReference()
                obs.subject.reference = f"Patient/{patient_fhir_id}"
                
                if encounter_fhir_id:
                    obs.encounter = fhirreference.FHIRReference()
                    obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
                
                obs.category = [codeableconcept.CodeableConcept()]
                obs.category[0].text = "vital-signs"
                
                observations.append(obs)
        
        # Physical Examination
        if soap.objective.physical_examination:
            obs = fhir_observation.Observation()
            obs.status = "final"
            
            obs.code = codeableconcept.CodeableConcept()
            obs.code.text = "Physical Examination"
            
            obs.valueString = soap.objective.physical_examination
            
            obs.subject = fhirreference.FHIRReference()
            obs.subject.reference = f"Patient/{patient_fhir_id}"
            
            if encounter_fhir_id:
                obs.encounter = fhirreference.FHIRReference()
                obs.encounter.reference = f"Encounter/{encounter_fhir_id}"
            
            obs.category = [codeableconcept.CodeableConcept()]
            obs.category[0].text = "exam"
            
            observations.append(obs)
        
        return observations
    
    @staticmethod
    def assessment_to_fhir_conditions(
        assessment_data: str, 
        patient_fhir_id: str,
        encounter_fhir_id: Optional[str] = None
    ) -> List[fhir_condition.Condition]:
        """Convert assessment data to FHIR Condition resources"""
        conditions = []
        
        if not assessment_data:
            return conditions
        
        # Create a condition for the assessment
        condition = fhir_condition.Condition()
        
        # Clinical status
        condition.clinicalStatus = codeableconcept.CodeableConcept()
        condition.clinicalStatus.text = "active"
        
        # Verification status
        condition.verificationStatus = codeableconcept.CodeableConcept()
        condition.verificationStatus.text = "provisional"
        
        # Code (using assessment text)
        condition.code = codeableconcept.CodeableConcept()
        condition.code.text = assessment_data
        
        # Subject reference
        condition.subject = fhirreference.FHIRReference()
        condition.subject.reference = f"Patient/{patient_fhir_id}"
        
        # Encounter reference
        if encounter_fhir_id:
            condition.encounter = fhirreference.FHIRReference()
            condition.encounter.reference = f"Encounter/{encounter_fhir_id}"
        
        # Record date
        condition.recordedDate = fhirdate.FHIRDate(datetime.utcnow().date().isoformat())
        
        conditions.append(condition)
        
        return conditions
    
    @staticmethod
    def encounter_to_fhir(
        encounter: EncounterModel, 
        patient_fhir_id: str
    ) -> fhir_encounter.Encounter:
        """Convert internal EncounterModel to FHIR Encounter resource"""
        fhir_enc = fhir_encounter.Encounter()
        
        # Status mapping
        status_map = {
            EncounterStatusEnum.DRAFT: "planned",
            EncounterStatusEnum.IN_PROGRESS: "in-progress",
            EncounterStatusEnum.SIGNED: "finished",
            EncounterStatusEnum.CANCELLED: "cancelled"
        }
        fhir_enc.status = status_map.get(encounter.status, "unknown")
        
        # Class (encounter type)
        fhir_enc.class_ = coding.Coding()
        type_map = {
            EncounterTypeEnum.ROUTINE_VISIT: "AMB",
            EncounterTypeEnum.EMERGENCY: "EMER",
            EncounterTypeEnum.CONSULTATION: "AMB",
            EncounterTypeEnum.FOLLOW_UP: "AMB",
            EncounterTypeEnum.TELEMEDICINE: "VR"
        }
        fhir_enc.class_.code = type_map.get(encounter.type, "AMB")
        fhir_enc.class_.system = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
        
        # Subject reference
        fhir_enc.subject = fhirreference.FHIRReference()
        fhir_enc.subject.reference = f"Patient/{patient_fhir_id}"
        
        # Period
        if encounter.created_at:
            period_dict = {}
            period_dict["start"] = encounter.created_at.isoformat()
            if encounter.status == EncounterStatusEnum.SIGNED and encounter.signed_at:
                period_dict["end"] = encounter.signed_at.isoformat()
            fhir_enc.period = period_dict
        
        return fhir_enc
    
    @staticmethod
    def get_fhir_patient_id(patient: PatientModel) -> Optional[str]:
        """Get FHIR patient ID from internal patient model"""
        # This would typically be stored in a mapping table or as metadata
        # For now, we'll use a simple prefix-based approach
        if patient.id and patient.id.startswith("fhir-"):
            return patient.id[5:]  # Remove "fhir-" prefix
        return None
    
    @staticmethod
    def create_patient_identifier(internal_id: str) -> identifier.Identifier:
        """Create a FHIR identifier for an internal patient ID"""
        ident = identifier.Identifier()
        ident.use = "usual"
        ident.system = "urn:diagnoassist:patient-id"
        ident.value = internal_id
        return ident
    
    @staticmethod
    def create_encounter_identifier(internal_id: str) -> identifier.Identifier:
        """Create a FHIR identifier for an internal encounter ID"""
        ident = identifier.Identifier()
        ident.use = "usual"
        ident.system = "urn:diagnoassist:encounter-id"
        ident.value = internal_id
        return ident


# Create mapper instance
fhir_mapper = FHIRMapper()