"""
Patient repository for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.base_repository import BaseRepository
from app.models.patient import PatientModel, PatientDemographics, MedicalBackground, AllergyInfo, MedicationInfo, ChronicCondition
from app.core.exceptions import DatabaseException


class PatientRepository(BaseRepository[PatientModel]):
    """Repository for Patient entities"""
    
    def __init__(self):
        super().__init__("patients")
        self._id_counter = 1
    
    def _to_dict(self, patient: PatientModel) -> Dict[str, Any]:
        """Convert PatientModel to dictionary for MongoDB storage"""
        return {
            "id": patient.id,
            "demographics": {
                "name": patient.demographics.name,
                "date_of_birth": patient.demographics.date_of_birth.isoformat(),
                "gender": patient.demographics.gender.value,
                "phone": patient.demographics.phone,
                "email": patient.demographics.email,
                "address": patient.demographics.address
            },
            "medical_background": {
                "allergies": [
                    {
                        "allergen": allergy.allergen,
                        "reaction": allergy.reaction,
                        "severity": allergy.severity,
                        "notes": allergy.notes
                    } for allergy in patient.medical_background.allergies
                ],
                "medications": [
                    {
                        "name": med.name,
                        "dosage": med.dosage,
                        "frequency": med.frequency,
                        "start_date": med.start_date.isoformat() if med.start_date else None,
                        "prescribing_doctor": med.prescribing_doctor,
                        "notes": med.notes
                    } for med in patient.medical_background.medications
                ],
                "chronic_conditions": [
                    {
                        "condition": condition.condition,
                        "diagnosed_date": condition.diagnosed_date.isoformat() if condition.diagnosed_date else None,
                        "severity": condition.severity,
                        "notes": condition.notes
                    } for condition in patient.medical_background.chronic_conditions
                ],
                "past_medical_history": patient.medical_background.past_medical_history,
                "family_history": patient.medical_background.family_history,
                "social_history": patient.medical_background.social_history
            },
            "fhir_patient_id": patient.fhir_patient_id,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at
        }
    
    def _from_dict(self, data: Dict[str, Any]) -> PatientModel:
        """Convert dictionary from MongoDB to PatientModel"""
        from datetime import date
        
        # Parse demographics
        demographics_data = data.get("demographics", {})
        demographics = PatientDemographics(
            name=demographics_data.get("name", ""),
            date_of_birth=date.fromisoformat(demographics_data.get("date_of_birth")),
            gender=demographics_data.get("gender", "unknown"),
            phone=demographics_data.get("phone"),
            email=demographics_data.get("email"),
            address=demographics_data.get("address")
        )
        
        # Parse medical background
        medical_bg_data = data.get("medical_background", {})
        
        # Parse allergies
        allergies = []
        for allergy_data in medical_bg_data.get("allergies", []):
            allergies.append(AllergyInfo(
                allergen=allergy_data.get("allergen", ""),
                reaction=allergy_data.get("reaction"),
                severity=allergy_data.get("severity"),
                notes=allergy_data.get("notes")
            ))
        
        # Parse medications
        medications = []
        for med_data in medical_bg_data.get("medications", []):
            medications.append(MedicationInfo(
                name=med_data.get("name", ""),
                dosage=med_data.get("dosage"),
                frequency=med_data.get("frequency"),
                start_date=date.fromisoformat(med_data["start_date"]) if med_data.get("start_date") else None,
                prescribing_doctor=med_data.get("prescribing_doctor"),
                notes=med_data.get("notes")
            ))
        
        # Parse chronic conditions
        chronic_conditions = []
        for condition_data in medical_bg_data.get("chronic_conditions", []):
            chronic_conditions.append(ChronicCondition(
                condition=condition_data.get("condition", ""),
                diagnosed_date=date.fromisoformat(condition_data["diagnosed_date"]) if condition_data.get("diagnosed_date") else None,
                severity=condition_data.get("severity"),
                notes=condition_data.get("notes")
            ))
        
        medical_background = MedicalBackground(
            allergies=allergies,
            medications=medications,
            chronic_conditions=chronic_conditions,
            past_medical_history=medical_bg_data.get("past_medical_history"),
            family_history=medical_bg_data.get("family_history"),
            social_history=medical_bg_data.get("social_history")
        )
        
        return PatientModel(
            id=data.get("id"),
            demographics=demographics,
            medical_background=medical_background,
            fhir_patient_id=data.get("fhir_patient_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages"""
        return "Patient"
    
    def _generate_id(self) -> str:
        """Generate unique patient ID"""
        patient_id = f"P{self._id_counter:03d}"
        self._id_counter += 1
        return patient_id
    
    async def get_by_email(self, email: str) -> Optional[PatientModel]:
        """Get patient by email address"""
        return await self.get_by_field("demographics.email", email)
    
    async def search_by_name(self, name_query: str) -> List[PatientModel]:
        """Search patients by name (case-insensitive partial match)"""
        try:
            collection = await self.get_collection()
            
            # Use regex for case-insensitive partial match
            query = {
                "demographics.name": {
                    "$regex": name_query,
                    "$options": "i"
                }
            }
            
            cursor = collection.find(query).sort("demographics.name", 1)
            documents = await cursor.to_list(length=100)  # Limit to 100 results
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching patients by name: {str(e)}",
                "search"
            )
    
    async def get_by_demographics_filter(
        self,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PatientModel]:
        """Get patients by demographics filters"""
        try:
            # Build filter query
            filter_dict = {}
            
            if name:
                filter_dict["demographics.name"] = {
                    "$regex": name,
                    "$options": "i"
                }
            
            if gender:
                filter_dict["demographics.gender"] = gender
            
            if email:
                filter_dict["demographics.email"] = {
                    "$regex": email,
                    "$options": "i"
                }
            
            if phone:
                filter_dict["demographics.phone"] = {
                    "$regex": phone,
                    "$options": "i"
                }
            
            return await self.get_all(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="demographics.name",
                sort_direction=1
            )
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while filtering patients: {str(e)}",
                "search"
            )
    
    async def get_patients_with_allergies(self, allergen: str) -> List[PatientModel]:
        """Get patients with specific allergy"""
        try:
            collection = await self.get_collection()
            
            query = {
                "medical_background.allergies": {
                    "$elemMatch": {
                        "allergen": {
                            "$regex": allergen,
                            "$options": "i"
                        }
                    }
                }
            }
            
            cursor = collection.find(query).sort("demographics.name", 1)
            documents = await cursor.to_list(length=100)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching patients by allergy: {str(e)}",
                "search"
            )
    
    async def get_patients_with_condition(self, condition: str) -> List[PatientModel]:
        """Get patients with specific chronic condition"""
        try:
            collection = await self.get_collection()
            
            query = {
                "medical_background.chronic_conditions": {
                    "$elemMatch": {
                        "condition": {
                            "$regex": condition,
                            "$options": "i"
                        }
                    }
                }
            }
            
            cursor = collection.find(query).sort("demographics.name", 1)
            documents = await cursor.to_list(length=100)
            
            return [self._from_dict(doc) for doc in documents]
            
        except Exception as e:
            raise DatabaseException(
                f"Database error while searching patients by condition: {str(e)}",
                "search"
            )
    
    async def update_fhir_reference(self, patient_id: str, fhir_patient_id: str) -> PatientModel:
        """Update FHIR patient reference"""
        return await self.update_fields(patient_id, {"fhir_patient_id": fhir_patient_id})
    
    async def get_recent_patients(self, limit: int = 10) -> List[PatientModel]:
        """Get recently created or updated patients"""
        return await self.get_all(
            limit=limit,
            sort_field="updated_at",
            sort_direction=-1
        )


# Create repository instance
patient_repository = PatientRepository()