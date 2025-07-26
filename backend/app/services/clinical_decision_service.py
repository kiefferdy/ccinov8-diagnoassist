"""
Clinical Decision Support Service for DiagnoAssist Backend

This service provides high-level clinical decision support functionality
integrated with the existing patient and encounter management system.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.core.ai_medical_assistant import (
    ai_medical_assistant, MedicalAlert, AIInsight, AlertSeverity, AlertType
)
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.models.auth import UserModel
from app.repositories.patient_repository import patient_repository
from app.repositories.encounter_repository import encounter_repository
from app.core.exceptions import NotFoundError, ValidationException

logger = logging.getLogger(__name__)


class ClinicalDecisionService:
    """High-level clinical decision support service"""
    
    def __init__(self):
        self.ai_assistant = ai_medical_assistant
        self.patient_repo = patient_repository
        self.encounter_repo = encounter_repository
        
        # Cache for storing recent analyses to avoid redundant processing
        self._analysis_cache = {}
        self._cache_ttl = timedelta(minutes=30)
    
    async def analyze_patient_encounter(
        self, 
        patient_id: str, 
        encounter_id: Optional[str] = None,
        user: Optional[UserModel] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive clinical decision support analysis for a patient encounter
        
        Args:
            patient_id: ID of the patient
            encounter_id: Optional ID of specific encounter
            user: User requesting the analysis
        
        Returns:
            Complete clinical decision support analysis
        """
        try:
            # Get patient data
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            # Get encounter data if specified
            encounter = None
            if encounter_id:
                encounter = await self.encounter_repo.get_by_id(encounter_id)
                if not encounter:
                    raise NotFoundError("Encounter", encounter_id)
            
            # Check cache
            cache_key = f"{patient_id}_{encounter_id or 'none'}_{user.id if user else 'anonymous'}"
            if cache_key in self._analysis_cache:
                cached_result = self._analysis_cache[cache_key]
                cache_age = datetime.utcnow() - cached_result["timestamp"]
                if cache_age < self._cache_ttl:
                    logger.info(f"Returning cached CDS analysis for {cache_key}")
                    return cached_result["analysis"]
            
            # Perform analysis
            context = {
                "user_id": user.id if user else None,
                "user_role": user.role.value if user else None,
                "analysis_type": "encounter" if encounter else "patient"
            }
            
            analysis = await self.ai_assistant.analyze_patient(patient, encounter, context)
            
            # Cache the result
            self._analysis_cache[cache_key] = {
                "analysis": analysis,
                "timestamp": datetime.utcnow()
            }
            
            # Clean old cache entries
            self._cleanup_cache()
            
            logger.info(f"Completed CDS analysis for patient {patient_id}, found {analysis['alert_counts']['total']} alerts")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in clinical decision support analysis: {e}")
            raise
    
    async def get_diagnosis_suggestions(
        self, 
        patient_id: str, 
        encounter_id: str,
        symptoms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get diagnosis suggestions based on patient data and symptoms
        
        Args:
            patient_id: ID of the patient
            encounter_id: ID of the encounter
            symptoms: Optional list of additional symptoms
        
        Returns:
            List of diagnosis suggestions with confidence scores
        """
        try:
            # Get patient and encounter
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            encounter = await self.encounter_repo.get_by_id(encounter_id)
            if not encounter:
                raise NotFoundError("Encounter", encounter_id)
            
            # Use AI assistant for diagnosis suggestions
            context = {"additional_symptoms": symptoms} if symptoms else None
            
            # Get AI analysis with insights
            analysis = await self.ai_assistant.analyze_patient(patient, encounter, context)
            
            # Extract AI insights that are diagnosis-related
            suggestions = []
            for insight_data in analysis.get("ai_insights", []):
                if insight_data.get("insight_type") == "differential_diagnosis":
                    suggestions.append({
                        "title": insight_data.get("title", "AI Diagnosis Suggestion"),
                        "content": insight_data.get("content", ""),
                        "confidence_score": insight_data.get("confidence_score", 0.5),
                        "suggested_actions": insight_data.get("suggested_actions", []),
                        "requires_followup": insight_data.get("requires_followup", True),
                        "ai_generated": True,
                        "disclaimer": insight_data.get("disclaimer", "AI-generated suggestion requiring physician review")
                    })
            
            logger.info(f"Generated {len(suggestions)} diagnosis suggestions for encounter {encounter_id}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting diagnosis suggestions: {e}")
            raise
    
    async def get_treatment_recommendations(
        self, 
        patient_id: str, 
        diagnosis: str
    ) -> List[Dict[str, Any]]:
        """
        Get treatment recommendations for a specific diagnosis
        
        Args:
            patient_id: ID of the patient
            diagnosis: The diagnosis to get treatments for
        
        Returns:
            List of treatment recommendations
        """
        try:
            # Get patient data for personalization
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            # Note: Treatment recommendations are now integrated into AI analysis
            # For specific diagnosis recommendations, use the main analyze_patient method
            logger.warning("get_treatment_recommendations is deprecated. Use analyze_patient_encounter for AI-powered insights.")
            
            # Return basic recommendation to consult AI analysis
            recommendation_dicts = [{
                "treatment_type": "ai_consultation",
                "treatment_name": "AI-Powered Treatment Analysis",
                "indication": f"Treatment recommendations for {diagnosis}",
                "recommendation": "Use the main AI analysis for comprehensive treatment suggestions",
                "ai_generated": True,
                "requires_physician_review": True,
                "disclaimer": "For detailed treatment recommendations, use the comprehensive AI analysis feature"
            }]
            
            logger.info(f"Retrieved {len(recommendation_dicts)} treatment recommendations for {diagnosis}")
            
            return recommendation_dicts
            
        except Exception as e:
            logger.error(f"Error getting treatment recommendations: {e}")
            raise
    
    async def check_drug_interactions(
        self, 
        patient_id: str, 
        medications: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check for drug interactions and allergies
        
        Args:
            patient_id: ID of the patient
            medications: List of medications to check
        
        Returns:
            List of drug interaction and allergy alerts
        """
        try:
            # Get patient data
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            # Use AI assistant's drug safety checker for medication analysis
            drug_interaction_alerts = self.ai_assistant.drug_safety.check_drug_interactions(medications, patient_id)
            allergy_alerts = self.ai_assistant.drug_safety.check_allergy_conflicts(medications, patient)
            
            # Combine all drug-related alerts
            drug_alerts = drug_interaction_alerts + allergy_alerts
            
            logger.info(f"Found {len(drug_alerts)} drug-related alerts for {len(medications)} medications")
            
            return [alert.model_dump() for alert in drug_alerts]
            
        except Exception as e:
            logger.error(f"Error checking drug interactions: {e}")
            raise
    
    async def calculate_risk_scores(
        self, 
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Calculate various clinical risk scores for a patient
        
        Args:
            patient_id: ID of the patient
        
        Returns:
            Dictionary of calculated risk scores
        """
        try:
            # Get patient data
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            # Use main AI assistant analysis for risk assessment
            analysis = await self.ai_assistant.analyze_patient(patient)
            
            # Extract risk-related alerts
            risk_scores = {}
            for alert_data in analysis.get("alerts", []):
                if alert_data.get("alert_type") == "risk_assessment":
                    metadata = alert_data.get("metadata", {})
                    if "risk_assessment" in metadata:
                        risk_data = metadata["risk_assessment"]
                        risk_type = risk_data.get("risk_type", "unknown")
                        risk_scores[risk_type] = risk_data
            
            # If no specific risk scores found, provide basic assessment
            if not risk_scores:
                age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
                if age and age >= 65:
                    risk_scores["general"] = {
                        "risk_type": "general",
                        "risk_category": "age_related",
                        "message": "Patient age indicates need for enhanced monitoring",
                        "ai_note": "Comprehensive risk assessment available through main AI analysis"
                    }
            
            logger.info(f"Calculated {len(risk_scores)} risk scores for patient {patient_id}")
            
            return risk_scores
            
        except Exception as e:
            logger.error(f"Error calculating risk scores: {e}")
            raise
    
    async def get_clinical_reminders(
        self, 
        patient_id: str,
        user: Optional[UserModel] = None
    ) -> List[Dict[str, Any]]:
        """
        Get clinical reminders and preventive care alerts for a patient
        
        Args:
            patient_id: ID of the patient
            user: User requesting reminders
        
        Returns:
            List of clinical reminders
        """
        try:
            # Get patient data
            patient = await self.patient_repo.get_by_id(patient_id)
            if not patient:
                raise NotFoundError("Patient", patient_id)
            
            reminders = []
            
            # Age-based screening reminders
            age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
            
            if age:
                # Mammography for women 40+
                if (patient.demographics.gender and 
                    patient.demographics.gender.lower() in ["female", "f"] and 
                    age >= 40):
                    reminders.append({
                        "type": "screening",
                        "title": "Mammography Screening",
                        "message": "Annual mammography recommended for women 40+",
                        "urgency": "routine",
                        "due_date": self._calculate_next_due_date("annual"),
                        "category": "cancer_screening"
                    })
                
                # Colonoscopy for 45+
                if age >= 45:
                    reminders.append({
                        "type": "screening", 
                        "title": "Colorectal Cancer Screening",
                        "message": "Colonoscopy or alternative screening recommended",
                        "urgency": "routine",
                        "due_date": self._calculate_next_due_date("10_years"),
                        "category": "cancer_screening"
                    })
                
                # Bone density for women 65+
                if (patient.demographics.gender and 
                    patient.demographics.gender.lower() in ["female", "f"] and 
                    age >= 65):
                    reminders.append({
                        "type": "screening",
                        "title": "Bone Density Screening",
                        "message": "DEXA scan recommended for women 65+",
                        "urgency": "routine",
                        "due_date": self._calculate_next_due_date("2_years"),
                        "category": "osteoporosis_screening"
                    })
            
            # Vaccination reminders
            vaccination_reminders = await self._get_vaccination_reminders(patient)
            reminders.extend(vaccination_reminders)
            
            # Chronic disease management reminders
            if patient.medical_background.medical_history:
                chronic_disease_reminders = await self._get_chronic_disease_reminders(patient)
                reminders.extend(chronic_disease_reminders)
            
            logger.info(f"Generated {len(reminders)} clinical reminders for patient {patient_id}")
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting clinical reminders: {e}")
            raise
    
    async def dismiss_alert(
        self, 
        alert_id: str, 
        user: UserModel,
        reason: Optional[str] = None
    ) -> bool:
        """
        Dismiss a clinical alert
        
        Args:
            alert_id: ID of the alert to dismiss
            user: User dismissing the alert
            reason: Optional reason for dismissal
        
        Returns:
            True if successful
        """
        try:
            # In a real implementation, this would update the alert in a database
            # For now, we'll log the dismissal
            logger.info(f"Alert {alert_id} dismissed by {user.id}" + (f" - Reason: {reason}" if reason else ""))
            
            # TODO: Implement alert storage and dismissal in database
            return True
            
        except Exception as e:
            logger.error(f"Error dismissing alert {alert_id}: {e}")
            return False
    
    async def get_alert_history(
        self, 
        patient_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical clinical alerts for a patient
        
        Args:
            patient_id: ID of the patient
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of historical alerts
        """
        try:
            # In a real implementation, this would query alert history from database
            # For now, return empty list as alerts are not persisted
            logger.info(f"Alert history requested for patient {patient_id}")
            
            # TODO: Implement alert history storage and retrieval
            return []
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    def _calculate_age(self, date_of_birth) -> Optional[int]:
        """Calculate age from date of birth"""
        try:
            if isinstance(date_of_birth, str):
                birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            else:
                birth_date = date_of_birth
            
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None
    
    def _calculate_next_due_date(self, interval: str) -> str:
        """Calculate next due date based on interval"""
        today = datetime.now()
        
        if interval == "annual":
            due_date = today + timedelta(days=365)
        elif interval == "2_years":
            due_date = today + timedelta(days=730)
        elif interval == "10_years":
            due_date = today + timedelta(days=3650)
        else:
            due_date = today + timedelta(days=365)  # Default to 1 year
        
        return due_date.strftime("%Y-%m-%d")
    
    async def _get_vaccination_reminders(self, patient: PatientModel) -> List[Dict[str, Any]]:
        """Get vaccination reminders for patient"""
        reminders = []
        age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
        
        if age:
            # Flu vaccine (annual for all adults)
            if age >= 18:
                reminders.append({
                    "type": "vaccination",
                    "title": "Annual Influenza Vaccine",
                    "message": "Annual flu vaccination recommended",
                    "urgency": "routine",
                    "due_date": self._calculate_next_due_date("annual"),
                    "category": "vaccination"
                })
            
            # COVID-19 booster (if age 65+ or high risk)
            if age >= 65:
                reminders.append({
                    "type": "vaccination",
                    "title": "COVID-19 Booster",
                    "message": "COVID-19 booster recommended for adults 65+",
                    "urgency": "routine",
                    "due_date": self._calculate_next_due_date("annual"),
                    "category": "vaccination"
                })
            
            # Shingles vaccine (age 50+)
            if age >= 50:
                reminders.append({
                    "type": "vaccination",
                    "title": "Zoster (Shingles) Vaccine",
                    "message": "Shingles vaccine recommended for adults 50+",
                    "urgency": "routine",
                    "due_date": self._calculate_next_due_date("annual"),
                    "category": "vaccination"
                })
        
        return reminders
    
    async def _get_chronic_disease_reminders(self, patient: PatientModel) -> List[Dict[str, Any]]:
        """Get chronic disease management reminders"""
        reminders = []
        
        if patient.medical_background.medical_history:
            history_lower = " ".join(patient.medical_background.medical_history).lower()
            
            # Diabetes management
            if "diabetes" in history_lower:
                reminders.extend([
                    {
                        "type": "monitoring",
                        "title": "HbA1c Monitoring",
                        "message": "HbA1c testing recommended every 3-6 months",
                        "urgency": "routine",
                        "due_date": self._calculate_next_due_date("annual"),
                        "category": "diabetes_management"
                    },
                    {
                        "type": "screening",
                        "title": "Diabetic Eye Exam",
                        "message": "Annual dilated eye examination recommended",
                        "urgency": "routine",
                        "due_date": self._calculate_next_due_date("annual"),
                        "category": "diabetes_complications"
                    }
                ])
            
            # Hypertension management
            if "hypertension" in history_lower or "high blood pressure" in history_lower:
                reminders.append({
                    "type": "monitoring",
                    "title": "Blood Pressure Monitoring",
                    "message": "Regular blood pressure monitoring recommended",
                    "urgency": "routine",
                    "due_date": self._calculate_next_due_date("annual"),
                    "category": "hypertension_management"
                })
        
        return reminders
    
    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, value in self._analysis_cache.items():
            if current_time - value["timestamp"] > self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._analysis_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Create service instance
clinical_decision_service = ClinicalDecisionService()