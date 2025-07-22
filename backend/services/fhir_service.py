"""
FHIR Service for DiagnoAssist
Business logic for FHIR resource management and interoperability
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
import json

if TYPE_CHECKING:
    from models.fhir_resource import FHIRResource
    from schemas.fhir_resource import FHIRResourceCreate, FHIRResourceResponse
    from repositories.repository_manager import RepositoryManager

from services.base_service import BaseService, ValidationException, BusinessRuleException, ResourceNotFoundException

class FHIRService(BaseService):
    """
    Service class for FHIR resource management and interoperability
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
        self.supported_resource_types = [
            "Patient", "Encounter", "Observation", "DiagnosticReport",
            "Condition", "MedicationRequest", "Procedure", "AllergyIntolerance"
        ]
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate FHIR-specific business rules
        
        Args:
            data: FHIR resource data to validate
            operation: Operation being performed
            
        Raises:
            BusinessRuleException: If business rules are violated
            ValidationException: If validation fails
        """
        # Validate resource type
        if "resource_type" in data and data["resource_type"]:
            if data["resource_type"] not in self.supported_resource_types:
                raise ValidationException(
                    f"Unsupported resource type: {data['resource_type']}. Supported types: {', '.join(self.supported_resource_types)}",
                    field="resource_type",
                    value=data["resource_type"]
                )
        
        # Validate FHIR data structure
        if "fhir_data" in data and data["fhir_data"]:
            self._validate_fhir_resource_structure(data["fhir_data"], data.get("resource_type"))
        
        # Business rule: Resource ID must be unique per resource type
        if operation == "create" and "resource_id" in data and "resource_type" in data:
            existing = self.repos.fhir_resource.get_by_resource_type_and_id(
                data["resource_type"], data["resource_id"]
            )
            if existing:
                raise BusinessRuleException(
                    f"FHIR resource {data['resource_type']}/{data['resource_id']} already exists",
                    rule="unique_resource_id_per_type"
                )
    
    def create_fhir_resource(self, fhir_data: Dict[str, Any]) -> FHIRResourceResponse:
        """
        Create a new FHIR resource from FHIR JSON data
        
        Args:
            fhir_data: Complete FHIR resource as dictionary
            
        Returns:
            FHIRResourceResponse: Created FHIR resource
        """
        try:
            # Extract resource type and ID from FHIR data
            resource_type = fhir_data.get("resourceType")
            resource_id = fhir_data.get("id")
            
            if not resource_type:
                raise ValidationException(
                    "FHIR resource must have a resourceType",
                    field="resourceType",
                    value=None
                )
            
            if not resource_id:
                # Generate resource ID if not provided
                resource_id = self._generate_resource_id(resource_type)
                fhir_data["id"] = resource_id
            
            # Extract references for indexing
            patient_ref = self._extract_patient_reference(fhir_data)
            encounter_ref = self._extract_encounter_reference(fhir_data)
            subject_ref = self._extract_subject_reference(fhir_data)
            
            # Prepare creation data
            create_data = {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "fhir_data": fhir_data,
                "patient_reference": patient_ref,
                "encounter_reference": encounter_ref,
                "subject_reference": subject_ref,
                "source_system": "diagnoassist"
            }
            
            # Validate business rules
            self.validate_business_rules(create_data, operation="create")
            
            # Create resource
            fhir_resource = self.repos.fhir_resource.create(create_data)
            self.safe_commit("FHIR resource creation")
            
            # Audit log
            self.audit_log("create", "FHIRResource", str(fhir_resource.id), {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "patient_reference": patient_ref
            })
            
            return FHIRResourceResponse.model_validate(fhir_resource)
            
        except (ValidationException, BusinessRuleException):
            self.safe_rollback("FHIR resource creation")
            raise
        except Exception as e:
            self.safe_rollback("FHIR resource creation")
            raise
    
    def get_fhir_resource(self, resource_type: str, resource_id: str) -> Optional[FHIRResourceResponse]:
        """
        Get FHIR resource by type and ID
        
        Args:
            resource_type: FHIR resource type
            resource_id: FHIR resource ID
            
        Returns:
            FHIRResourceResponse or None if not found
        """
        fhir_resource = self.repos.fhir_resource.get_by_resource_type_and_id(resource_type, resource_id)
        return FHIRResourceResponse.model_validate(fhir_resource) if fhir_resource else None
    
    def search_fhir_resources(self, 
                             resource_type: Optional[str] = None,
                             patient_reference: Optional[str] = None,
                             encounter_reference: Optional[str] = None,
                             skip: int = 0,
                             limit: int = 100) -> List[FHIRResourceResponse]:
        """
        Search FHIR resources with various criteria
        
        Args:
            resource_type: Filter by resource type
            patient_reference: Filter by patient reference
            encounter_reference: Filter by encounter reference
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of FHIRResourceResponse objects
        """
        if resource_type:
            resources = self.repos.fhir_resource.get_by_resource_type(resource_type, skip, limit)
        elif patient_reference:
            resources = self.repos.fhir_resource.get_by_patient_reference(patient_reference, skip, limit)
        elif encounter_reference:
            resources = self.repos.fhir_resource.get_by_encounter_reference(encounter_reference, skip, limit)
        else:
            resources = self.repos.fhir_resource.get_all(skip, limit)
        
        return [FHIRResourceResponse.model_validate(r) for r in resources]
    
    def convert_patient_to_fhir(self, patient_id: str) -> Dict[str, Any]:
        """
        Convert DiagnoAssist Patient to FHIR Patient resource
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            FHIR Patient resource as dictionary
        """
        from services.patient_service import PatientService
        
        patient_service = PatientService(self.repos)
        patient = patient_service.get_patient(patient_id)
        
        # Build FHIR Patient resource
        fhir_patient = {
            "resourceType": "Patient",
            "id": str(patient.id),
            "meta": {
                "lastUpdated": patient.updated_at.isoformat() if patient.updated_at else None,
                "source": "DiagnoAssist"
            },
            "identifier": [
                {
                    "use": "usual",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR",
                                "display": "Medical Record Number"
                            }
                        ]
                    },
                    "value": patient.medical_record_number
                }
            ],
            "active": patient.active,
            "name": [
                {
                    "use": "official",
                    "family": patient.last_name,
                    "given": [patient.first_name]
                }
            ],
            "gender": self._map_gender_to_fhir(patient.gender),
            "birthDate": patient.date_of_birth.isoformat() if patient.date_of_birth else None
        }
        
        # Add contact information if available
        if patient.email or patient.phone:
            fhir_patient["telecom"] = []
            
            if patient.email:
                fhir_patient["telecom"].append({
                    "system": "email",
                    "value": patient.email,
                    "use": "home"
                })
            
            if patient.phone:
                fhir_patient["telecom"].append({
                    "system": "phone",
                    "value": patient.phone,
                    "use": "home"
                })
        
        return fhir_patient
    
    def convert_episode_to_fhir(self, episode_id: str) -> Dict[str, Any]:
        """
        Convert DiagnoAssist Episode to FHIR Encounter resource
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            FHIR Encounter resource as dictionary
        """
        from services.episode_service import EpisodeService
        
        episode_service = EpisodeService(self.repos)
        episode = episode_service.get_episode(episode_id)
        
        # Map encounter type
        fhir_class = self._map_encounter_type_to_fhir(episode.encounter_type)
        
        fhir_encounter = {
            "resourceType": "Encounter",
            "id": str(episode.id),
            "meta": {
                "lastUpdated": episode.updated_at.isoformat() if episode.updated_at else None,
                "source": "DiagnoAssist"
            },
            "status": self._map_episode_status_to_fhir(episode.status),
            "class": fhir_class,
            "subject": {
                "reference": f"Patient/{episode.patient_id}"
            },
            "period": {
                "start": episode.start_time.isoformat() if episode.start_time else None,
                "end": episode.end_time.isoformat() if episode.end_time else None
            },
            "reasonCode": [
                {
                    "text": episode.chief_complaint
                }
            ]
        }
        
        # Add location if available
        if episode.location:
            fhir_encounter["location"] = [
                {
                    "location": {
                        "display": episode.location
                    }
                }
            ]
        
        # Add participant (provider) if available
        if episode.provider_id:
            fhir_encounter["participant"] = [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "ATND",
                                    "display": "attender"
                                }
                            ]
                        }
                    ],
                    "individual": {
                        "identifier": {
                            "value": episode.provider_id
                        }
                    }
                }
            ]
        
        return fhir_encounter
    
    def convert_diagnosis_to_fhir(self, diagnosis_id: str) -> Dict[str, Any]:
        """
        Convert DiagnoAssist Diagnosis to FHIR Condition resource
        
        Args:
            diagnosis_id: Diagnosis UUID
            
        Returns:
            FHIR Condition resource as dictionary
        """
        from services.diagnosis_service import DiagnosisService
        
        diagnosis_service = DiagnosisService(self.repos)
        diagnosis = diagnosis_service.get_diagnosis(diagnosis_id)
        
        # Get episode for encounter reference
        episode = self.repos.episode.get_by_id(str(diagnosis.episode_id))
        
        fhir_condition = {
            "resourceType": "Condition",
            "id": str(diagnosis.id),
            "meta": {
                "lastUpdated": diagnosis.updated_at.isoformat() if diagnosis.updated_at else None,
                "source": "DiagnoAssist"
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active" if diagnosis.final_diagnosis else "provisional"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed" if diagnosis.physician_confirmed else "provisional"
                    }
                ]
            },
            "code": {
                "text": diagnosis.condition_name
            },
            "subject": {
                "reference": f"Patient/{episode.patient_id}"
            },
            "encounter": {
                "reference": f"Encounter/{diagnosis.episode_id}"
            },
            "recordedDate": diagnosis.created_at.isoformat() if diagnosis.created_at else None
        }
        
        # Add ICD-10 coding if available
        if diagnosis.icd10_code:
            fhir_condition["code"]["coding"] = [
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": diagnosis.icd10_code,
                    "display": diagnosis.condition_name
                }
            ]
        
        # Add SNOMED coding if available
        if diagnosis.snomed_code:
            if "coding" not in fhir_condition["code"]:
                fhir_condition["code"]["coding"] = []
            fhir_condition["code"]["coding"].append({
                "system": "http://snomed.info/sct",
                "code": diagnosis.snomed_code,
                "display": diagnosis.condition_name
            })
        
        return fhir_condition
    
    def create_patient_bundle(self, patient_id: str) -> Dict[str, Any]:
        """
        Create a FHIR Bundle with all resources for a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            FHIR Bundle resource as dictionary
        """
        bundle_entries = []
        
        # Add Patient resource
        patient_fhir = self.convert_patient_to_fhir(patient_id)
        bundle_entries.append({
            "resource": patient_fhir,
            "fullUrl": f"Patient/{patient_id}"
        })
        
        # Add Encounter resources
        from services.episode_service import EpisodeService
        episode_service = EpisodeService(self.repos)
        episodes = episode_service.get_episodes_by_patient(patient_id, limit=10)
        
        for episode in episodes:
            encounter_fhir = self.convert_episode_to_fhir(str(episode.id))
            bundle_entries.append({
                "resource": encounter_fhir,
                "fullUrl": f"Encounter/{episode.id}"
            })
            
            # Add Condition resources for this encounter
            from services.diagnosis_service import DiagnosisService
            diagnosis_service = DiagnosisService(self.repos)
            diagnoses = diagnosis_service.get_diagnoses_by_episode(str(episode.id))
            
            for diagnosis in diagnoses:
                condition_fhir = self.convert_diagnosis_to_fhir(str(diagnosis.id))
                bundle_entries.append({
                    "resource": condition_fhir,
                    "fullUrl": f"Condition/{diagnosis.id}"
                })
        
        # Create Bundle resource
        fhir_bundle = {
            "resourceType": "Bundle",
            "id": f"patient-{patient_id}-bundle",
            "meta": {
                "lastUpdated": datetime.utcnow().isoformat(),
                "source": "DiagnoAssist"
            },
            "type": "collection",
            "timestamp": datetime.utcnow().isoformat(),
            "total": len(bundle_entries),
            "entry": bundle_entries
        }
        
        return fhir_bundle
    
    def _validate_fhir_resource_structure(self, fhir_data: Dict[str, Any], resource_type: str) -> None:
        """
        Basic FHIR resource structure validation
        
        Args:
            fhir_data: FHIR resource data
            resource_type: Expected resource type
            
        Raises:
            ValidationException: If structure is invalid
        """
        if not isinstance(fhir_data, dict):
            raise ValidationException(
                "FHIR resource data must be a JSON object",
                field="fhir_data",
                value=type(fhir_data).__name__
            )
        
        # Check resourceType matches
        if fhir_data.get("resourceType") != resource_type:
            raise ValidationException(
                f"Resource type mismatch. Expected: {resource_type}, Got: {fhir_data.get('resourceType')}",
                field="resourceType",
                value=fhir_data.get("resourceType")
            )
        
        # Basic required fields check (simplified)
        required_fields = {
            "Patient": ["resourceType", "id"],
            "Encounter": ["resourceType", "id", "status", "class", "subject"],
            "Condition": ["resourceType", "id", "code", "subject"],
            "Observation": ["resourceType", "id", "status", "code", "subject"]
        }
        
        if resource_type in required_fields:
            for field in required_fields[resource_type]:
                if field not in fhir_data:
                    raise ValidationException(
                        f"Required field '{field}' missing from {resource_type} resource",
                        field=field,
                        value=None
                    )
    
    def _generate_resource_id(self, resource_type: str) -> str:
        """Generate a unique resource ID"""
        import uuid
        return f"{resource_type.lower()}-{uuid.uuid4().hex[:8]}"
    
    def _extract_patient_reference(self, fhir_data: Dict[str, Any]) -> Optional[str]:
        """Extract patient reference from FHIR resource"""
        # Check various fields where patient reference might be
        for field in ["subject", "patient"]:
            if field in fhir_data and isinstance(fhir_data[field], dict):
                ref = fhir_data[field].get("reference")
                if ref and ref.startswith("Patient/"):
                    return ref
        return None
    
    def _extract_encounter_reference(self, fhir_data: Dict[str, Any]) -> Optional[str]:
        """Extract encounter reference from FHIR resource"""
        if "encounter" in fhir_data and isinstance(fhir_data["encounter"], dict):
            ref = fhir_data["encounter"].get("reference")
            if ref and ref.startswith("Encounter/"):
                return ref
        return None
    
    def _extract_subject_reference(self, fhir_data: Dict[str, Any]) -> Optional[str]:
        """Extract subject reference from FHIR resource"""
        if "subject" in fhir_data and isinstance(fhir_data["subject"], dict):
            return fhir_data["subject"].get("reference")
        return None
    
    def _map_gender_to_fhir(self, gender: str) -> str:
        """Map DiagnoAssist gender to FHIR gender"""
        mapping = {
            "male": "male",
            "female": "female",
            "other": "other",
            "unknown": "unknown"
        }
        return mapping.get(gender.lower() if gender else "", "unknown")
    
    def _map_encounter_type_to_fhir(self, encounter_type: str) -> Dict[str, Any]:
        """Map DiagnoAssist encounter type to FHIR class"""
        mapping = {
            "outpatient": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "inpatient": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "IMP",
                "display": "inpatient encounter"
            },
            "emergency": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EMER",
                "display": "emergency"
            }
        }
        return mapping.get(encounter_type.lower() if encounter_type else "", mapping["outpatient"])
    
    def _map_episode_status_to_fhir(self, status: str) -> str:
        """Map DiagnoAssist episode status to FHIR encounter status"""
        mapping = {
            "in-progress": "in-progress",
            "completed": "finished",
            "cancelled": "cancelled"
        }
        return mapping.get(status.lower() if status else "", "unknown")