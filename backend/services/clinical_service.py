"""
Clinical Service for DiagnoAssist
High-level clinical workflow orchestration
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from uuid import UUID

if TYPE_CHECKING:
    from repositories.repository_manager import RepositoryManager
    from schemas.patient import PatientResponse
    from schemas.episode import EpisodeResponse, VitalSigns
    from schemas.diagnosis import DiagnosisResponse
    from schemas.treatment import TreatmentResponse

from services.base_service import BaseService
from services.patient_service import PatientService
from services.episode_service import EpisodeService
from services.diagnosis_service import DiagnosisService
from services.treatment_service import TreatmentService

class ClinicalService(BaseService):
    """
    High-level clinical service that orchestrates patient care workflows
    """
    
    def __init__(self, repositories):
        super().__init__(repositories)
        
        # Initialize individual services
        self.patient_service = PatientService(repositories)
        self.episode_service = EpisodeService(repositories)
        self.diagnosis_service = DiagnosisService(repositories)
        self.treatment_service = TreatmentService(repositories)
    
    def validate_business_rules(self, data: Dict[str, Any], operation: str = "create") -> None:
        """
        Validate clinical workflow business rules
        
        Args:
            data: Data to validate
            operation: Operation being performed
        """
        # Clinical workflows typically span multiple entities,
        # so individual service validation is sufficient
        pass
    
    def start_clinical_encounter(self, 
                                patient_mrn: str,
                                chief_complaint: str,
                                encounter_type: str = "outpatient",
                                vital_signs: Optional[Dict[str, Any]] = None,
                                provider_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new clinical encounter for a patient
        
        Args:
            patient_mrn: Patient medical record number
            chief_complaint: Chief complaint for the visit
            encounter_type: Type of encounter (outpatient, inpatient, emergency)
            vital_signs: Initial vital signs
            provider_id: Healthcare provider identifier
            
        Returns:
            Dictionary with patient and episode information
        """
        try:
            # Find patient by MRN
            patient = self.patient_service.get_patient_by_mrn(patient_mrn)
            if not patient:
                raise LookupError("Patient", f"MRN: {patient_mrn}")
            
            # Create new episode
            from schemas.episode import EpisodeCreate, VitalSigns
            
            episode_data = EpisodeCreate(
                patient_id=patient.id,
                chief_complaint=chief_complaint,
                encounter_type=encounter_type,
                provider_id=provider_id,
                vital_signs=VitalSigns(**vital_signs) if vital_signs else None
            )
            
            episode = self.episode_service.create_episode(episode_data)
            
            # Audit log for clinical encounter
            self.audit_log("start_encounter", "ClinicalEncounter", str(episode.id), {
                "patient_mrn": patient_mrn,
                "chief_complaint": chief_complaint,
                "encounter_type": encounter_type
            })
            
            return {
                "status": "encounter_started",
                "patient": patient,
                "episode": episode,
                "message": f"Clinical encounter started for {patient.first_name} {patient.last_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start clinical encounter: {e}")
            raise
    
    def complete_clinical_assessment(self, 
                                   episode_id: str,
                                   diagnoses: List[Dict[str, Any]],
                                   treatments: List[Dict[str, Any]],
                                   assessment_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete clinical assessment with diagnoses and treatment plans
        
        Args:
            episode_id: Episode UUID
            diagnoses: List of diagnosis data
            treatments: List of treatment plan data
            assessment_notes: Clinical assessment notes
            
        Returns:
            Dictionary with assessment results
        """
        try:
            # Validate episode exists and is active
            episode = self.episode_service.get_episode(episode_id)
            if episode.status != "in-progress":
                raise RuntimeError(
                    "Cannot complete assessment for non-active episode"
                )
            
            created_diagnoses = []
            created_treatments = []
            
            # Create diagnoses
            for diag_data in diagnoses:
                from schemas.diagnosis import DiagnosisCreate
                
                diagnosis_create = DiagnosisCreate(
                    episode_id=UUID(episode_id),
                    **diag_data
                )
                
                diagnosis = self.diagnosis_service.create_diagnosis(diagnosis_create)
                created_diagnoses.append(diagnosis)
            
            # Create treatments (link to primary diagnosis if available)
            primary_diagnosis_id = None
            if created_diagnoses:
                # Find the highest probability diagnosis as primary
                primary_diagnosis = max(created_diagnoses, 
                                      key=lambda d: d.ai_probability or 0)
                primary_diagnosis_id = primary_diagnosis.id
            
            for treat_data in treatments:
                from schemas.treatment import TreatmentCreate
                
                # Add diagnosis link if not specified and primary diagnosis exists
                if primary_diagnosis_id and "diagnosis_id" not in treat_data:
                    treat_data["diagnosis_id"] = primary_diagnosis_id
                
                treatment_create = TreatmentCreate(
                    episode_id=UUID(episode_id),
                    **treat_data
                )
                
                treatment = self.treatment_service.create_treatment(treatment_create)
                created_treatments.append(treatment)
            
            # Update episode with assessment notes
            if assessment_notes:
                from schemas.episode import EpisodeUpdate
                episode_update = EpisodeUpdate(assessment_notes=assessment_notes)
                episode = self.episode_service.update_episode(episode_id, episode_update)
            
            # Audit log
            self.audit_log("complete_assessment", "ClinicalAssessment", episode_id, {
                "diagnoses_count": len(created_diagnoses),
                "treatments_count": len(created_treatments)
            })
            
            return {
                "status": "assessment_completed",
                "episode": episode,
                "diagnoses": created_diagnoses,
                "treatments": created_treatments,
                "summary": {
                    "total_diagnoses": len(created_diagnoses),
                    "total_treatments": len(created_treatments),
                    "primary_diagnosis": created_diagnoses[0].condition_name if created_diagnoses else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to complete clinical assessment: {e}")
            raise
    
    def finalize_encounter(self, 
                          episode_id: str,
                          final_diagnosis_id: Optional[str] = None,
                          discharge_instructions: Optional[str] = None,
                          follow_up_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Finalize clinical encounter with discharge planning
        
        Args:
            episode_id: Episode UUID
            final_diagnosis_id: UUID of the final diagnosis
            discharge_instructions: Patient discharge instructions
            follow_up_instructions: Follow-up care instructions
            
        Returns:
            Dictionary with encounter completion data
        """
        try:
            # Get episode and validate
            episode = self.episode_service.get_episode(episode_id)
            if episode.status != "in-progress":
                raise RuntimeError(
                    "Cannot finalize non-active episode"
                )
            
            # Set final diagnosis if provided
            if final_diagnosis_id:
                final_diagnosis = self.diagnosis_service.set_final_diagnosis(final_diagnosis_id)
            else:
                # Auto-select highest probability diagnosis as final
                diagnoses = self.diagnosis_service.get_diagnoses_by_episode(episode_id)
                if diagnoses:
                    highest_prob = max(diagnoses, key=lambda d: d.ai_probability or 0)
                    final_diagnosis = self.diagnosis_service.set_final_diagnosis(str(highest_prob.id))
                else:
                    final_diagnosis = None
            
            # Prepare completion notes
            completion_notes = []
            if discharge_instructions:
                completion_notes.append(f"Discharge Instructions:\n{discharge_instructions}")
            if follow_up_instructions:
                completion_notes.append(f"Follow-up Instructions:\n{follow_up_instructions}")
            
            completion_text = "\n\n".join(completion_notes) if completion_notes else None
            
            # Complete the episode
            completed_episode = self.episode_service.complete_episode(episode_id, completion_text)
            
            # Get encounter summary
            encounter_summary = self.get_encounter_summary(episode_id)
            
            # Audit log
            self.audit_log("finalize_encounter", "ClinicalEncounter", episode_id, {
                "final_diagnosis": final_diagnosis.condition_name if final_diagnosis else None,
                "duration_minutes": encounter_summary.get("duration_minutes")
            })
            
            return {
                "status": "encounter_finalized",
                "episode": completed_episode,
                "final_diagnosis": final_diagnosis,
                "encounter_summary": encounter_summary,
                "message": "Clinical encounter successfully completed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to finalize encounter: {e}")
            raise
    
    def get_encounter_summary(self, episode_id: str) -> Dict[str, Any]:
        """
        Get comprehensive encounter summary
        
        Args:
            episode_id: Episode UUID
            
        Returns:
            Dictionary with complete encounter data
        """
        # Get episode timeline (includes diagnoses and treatments)
        timeline = self.episode_service.get_episode_timeline(episode_id)
        episode = timeline["episode"]
        
        # Calculate encounter duration
        duration_minutes = None
        if episode.duration_seconds:
            duration_minutes = round(episode.duration_seconds / 60, 1)
        
        # Get patient information
        patient = self.patient_service.get_patient(str(episode.patient_id))
        
        # Analyze diagnoses
        final_diagnosis = None
        differential_count = 0
        for diag in timeline["diagnoses"]:
            if diag.get("final_diagnosis"):
                final_diagnosis = diag
            differential_count += 1
        
        # Analyze treatments
        active_treatments = [t for t in timeline["treatments"] if t.get("status") == "active"]
        medication_count = len([t for t in timeline["treatments"] 
                              if t.get("treatment_type") == "medication"])
        
        return {
            "episode_id": episode_id,
            "patient": {
                "id": str(patient.id),
                "name": f"{patient.first_name} {patient.last_name}",
                "mrn": patient.medical_record_number,
                "age": patient.age_years
            },
            "encounter_details": {
                "chief_complaint": episode.chief_complaint,
                "encounter_type": episode.encounter_type,
                "status": episode.status,
                "start_time": episode.start_time,
                "end_time": episode.end_time,
                "duration_minutes": duration_minutes,
                "provider_id": episode.provider_id,
                "location": episode.location
            },
            "clinical_data": {
                "vital_signs": episode.vital_signs,
                "symptoms": episode.symptoms,
                "physical_exam_findings": episode.physical_exam_findings
            },
            "assessment": {
                "total_diagnoses": differential_count,
                "final_diagnosis": final_diagnosis,
                "differential_diagnoses": [d for d in timeline["diagnoses"] 
                                         if not d.get("final_diagnosis")]
            },
            "treatment_plan": {
                "total_treatments": len(timeline["treatments"]),
                "active_treatments": len(active_treatments),
                "medication_count": medication_count,
                "treatments": timeline["treatments"]
            },
            "notes": {
                "clinical_notes": episode.clinical_notes,
                "assessment_notes": episode.assessment_notes,
                "plan_notes": episode.plan_notes
            }
        }
    
    def get_patient_care_plan(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive care plan for a patient across all episodes
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Dictionary with patient care plan data
        """
        # Get patient summary
        patient_summary = self.patient_service.get_patient_summary(patient_id)
        patient = patient_summary["patient"]
        
        # Get active treatments across all episodes
        active_treatments = self.treatment_service.get_active_treatments_by_patient(patient_id)
        
        # Get recent episodes with final diagnoses
        recent_episodes = self.episode_service.get_episodes_by_patient(
            patient_id, status="completed", limit=10
        )
        
        # Compile chronic conditions (final diagnoses from multiple episodes)
        chronic_conditions = []
        condition_episodes = {}
        
        for episode in recent_episodes:
            episode_diagnoses = self.diagnosis_service.get_diagnoses_by_episode(str(episode.id))
            for diag in episode_diagnoses:
                if diag.final_diagnosis:
                    condition = diag.condition_name
                    if condition not in condition_episodes:
                        condition_episodes[condition] = []
                    condition_episodes[condition].append({
                    "episode_id": str(episode.id),
                    "date": episode.start_date,
                    "chief_complaint": episode.chief_complaint
                })
        
        # Identify chronic conditions (appearing in multiple episodes)
        for condition, episodes in condition_episodes.items():
            if len(episodes) > 1 or any(
                (datetime.now() - ep["date"]).days > 90 for ep in episodes
            ):
                chronic_conditions.append({
                    "condition": condition,
                    "episodes": episodes,
                    "first_diagnosed": min(ep["date"] for ep in episodes),
                    "last_seen": max(ep["date"] for ep in episodes)
                })
        
        # Generate current medication list
        medication_list = self.treatment_service.generate_medication_list(patient_id)
        
        return {
            "patient": patient,
            "care_plan_generated": datetime.utcnow(),
            "chronic_conditions": chronic_conditions,
            "active_treatments": {
                "count": len(active_treatments),
                "treatments": [
                    {
                        "id": str(t.id),
                        "treatment_name": t.name,
                        "treatment_type": t.treatment_type,
                        "start_date": t.start_date,
                        "status": t.status
                    } for t in active_treatments
                ]
            },
            "current_medications": medication_list,
            "recent_encounters": {
                "count": len(recent_episodes),
                "encounters": [
                    {
                        "id": str(ep.id),
                        "date": ep.start_date,
                        "chief_complaint": ep.chief_complaint,
                        "status": ep.status
                    } for ep in recent_episodes[:5]
                ]
            },
            "care_alerts": self._generate_care_alerts(patient, active_treatments, chronic_conditions)
        }
    
    def _generate_care_alerts(self, 
                            patient: PatientResponse,
                            active_treatments: List[TreatmentResponse],
                            chronic_conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate care alerts based on patient data
        
        Args:
            patient: Patient information
            active_treatments: List of active treatments
            chronic_conditions: List of chronic conditions
            
        Returns:
            List of care alert dictionaries
        """
        alerts = []
        
        # Age-based alerts
        if patient.age_years and patient.age_years > 65:
            alerts.append({
                "type": "age_related",
                "severity": "low",
                "message": "Senior patient - consider age-appropriate medication dosing",
                "recommendation": "Review medication doses for elderly patient"
            })
        
        # Medication alerts
        medication_treatments = [t for t in active_treatments if t.treatment_type == "medication"]
        if len(medication_treatments) > 5:
            alerts.append({
                "type": "polypharmacy",
                "severity": "medium",
                "message": f"Patient on {len(medication_treatments)} medications",
                "recommendation": "Review for potential drug interactions and medication optimization"
            })
        
        # Chronic condition alerts
        if len(chronic_conditions) > 3:
            alerts.append({
                "type": "complex_patient",
                "severity": "medium",
                "message": f"Patient has {len(chronic_conditions)} chronic conditions",
                "recommendation": "Consider care coordination and comprehensive management plan"
            })
        
        # Follow-up alerts (placeholder - would need more sophisticated logic)
        for condition in chronic_conditions:
            last_seen = condition["last_seen"]
            days_since = (datetime.now() - last_seen).days
            
            if days_since > 180:  # 6 months
                alerts.append({
                    "type": "follow_up_needed",
                    "severity": "medium",
                    "message": f"No recent follow-up for {condition['condition']}",
                    "recommendation": f"Consider scheduling follow-up for {condition['condition']}"
                })
        
        return alerts