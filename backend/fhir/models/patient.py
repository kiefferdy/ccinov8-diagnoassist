from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.identifier import Identifier
from fhir.resources.address import Address
from typing import List, Optional
from datetime import date

class PatientFHIRModel:
    @staticmethod
    def create_fhir_patient(
        patient_id: str,
        first_name: str,
        last_name: str,
        birth_date: date,
        gender: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[dict] = None
    ) -> FHIRPatient:
        
        # Create FHIR Patient resource
        patient = FHIRPatient()
        
        # Set identifier
        patient.identifier = [
            Identifier(**{
                "use": "usual",
                "system": "https://diagnoassist.com/patient-id",
                "value": patient_id
            })
        ]
        
        # Set name
        patient.name = [
            HumanName(**{
                "use": "official",
                "family": last_name,
                "given": [first_name]
            })
        ]
        
        # Set birth date and gender
        patient.birthDate = birth_date.isoformat()
        patient.gender = gender.lower()
        
        # Set contact points
        telecom = []
        if phone:
            telecom.append(ContactPoint(**{
                "system": "phone",
                "value": phone,
                "use": "mobile"
            }))
        if email:
            telecom.append(ContactPoint(**{
                "system": "email",
                "value": email
            }))
        if telecom:
            patient.telecom = telecom
            
        # Set address
        if address:
            patient.address = [Address(**{
                "use": "home",
                "line": [address.get("street", "")],
                "city": address.get("city", ""),
                "state": address.get("state", ""),
                "postalCode": address.get("zip", ""),
                "country": address.get("country", "")
            })]
        
        return patient

    @staticmethod
    def from_fhir_patient(fhir_patient: FHIRPatient) -> dict:
        """Convert FHIR Patient back to internal format"""
        patient_data = {
            "id": None,
            "first_name": "",
            "last_name": "",
            "birth_date": None,
            "gender": "",
            "phone": None,
            "email": None,
            "address": None
        }
        
        # Extract ID from identifier
        if fhir_patient.identifier:
            for identifier in fhir_patient.identifier:
                if identifier.system == "https://diagnoassist.com/patient-id":
                    patient_data["id"] = identifier.value
                    break
        
        # Extract name
        if fhir_patient.name:
            name = fhir_patient.name[0]
            patient_data["last_name"] = name.family or ""
            patient_data["first_name"] = name.given[0] if name.given else ""
        
        # Extract birth date and gender
        if fhir_patient.birthDate:
            patient_data["birth_date"] = date.fromisoformat(fhir_patient.birthDate)
        patient_data["gender"] = fhir_patient.gender or ""
        
        # Extract contact info
        if fhir_patient.telecom:
            for contact in fhir_patient.telecom:
                if contact.system == "phone":
                    patient_data["phone"] = contact.value
                elif contact.system == "email":
                    patient_data["email"] = contact.value
        
        return patient_data