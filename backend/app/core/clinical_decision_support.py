"""
Clinical Decision Support System for DiagnoAssist Backend

This module provides intelligent clinical decision support including
diagnosis suggestions, treatment recommendations, drug interaction checks,
and clinical alerts based on evidence-based medicine.
"""
import asyncio
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
import logging

from app.models.patient import PatientModel, PatientDemographics, MedicalBackground
from app.models.encounter import EncounterModel
from app.models.soap import SOAPModel, SubjectiveSection, ObjectiveSection, AssessmentSection, PlanSection, VitalSigns
from app.models.auth import UserModel
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Clinical alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of clinical alerts"""
    DRUG_INTERACTION = "drug_interaction"
    ALLERGY_WARNING = "allergy_warning"
    CONTRAINDICATION = "contraindication"
    DOSAGE_WARNING = "dosage_warning"
    DUPLICATE_THERAPY = "duplicate_therapy"
    DIAGNOSTIC_REMINDER = "diagnostic_reminder"
    TREATMENT_SUGGESTION = "treatment_suggestion"
    FOLLOW_UP_REMINDER = "follow_up_reminder"
    RISK_ASSESSMENT = "risk_assessment"
    CLINICAL_GUIDELINE = "clinical_guideline"


class ClinicalAlert(BaseModel):
    """Represents a clinical decision support alert"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    triggered_by: List[str] = Field(default_factory=list)  # What triggered this alert
    recommended_actions: List[str] = Field(default_factory=list)
    evidence_level: Optional[str] = None  # A, B, C evidence levels
    references: List[str] = Field(default_factory=list)
    dismissible: bool = True
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiagnosisSuggestion(BaseModel):
    """Represents a suggested diagnosis"""
    diagnosis_code: Optional[str] = None
    diagnosis_name: str
    confidence_score: float  # 0.0 to 1.0
    supporting_symptoms: List[str] = Field(default_factory=list)
    differential_diagnoses: List[str] = Field(default_factory=list)
    recommended_tests: List[str] = Field(default_factory=list)
    urgency_level: str = "routine"  # routine, urgent, emergent
    evidence_summary: Optional[str] = None
    icd10_code: Optional[str] = None


class TreatmentRecommendation(BaseModel):
    """Represents a treatment recommendation"""
    treatment_type: str  # medication, procedure, lifestyle, referral
    treatment_name: str
    indication: str
    dosage: Optional[str] = None
    duration: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)
    monitoring_required: List[str] = Field(default_factory=list)
    cost_effectiveness: Optional[str] = None
    evidence_level: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    """Represents a clinical risk assessment"""
    risk_type: str  # cardiovascular, diabetes, bleeding, etc.
    risk_score: float
    risk_category: str  # low, moderate, high
    calculation_method: str
    factors_assessed: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    follow_up_interval: Optional[str] = None
    validity_period: Optional[timedelta] = None


class ClinicalDecisionEngine(ABC):
    """Abstract base class for clinical decision engines"""
    
    @abstractmethod
    async def analyze(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ClinicalAlert]:
        """Analyze patient and encounter data for clinical alerts"""
        pass


class DrugInteractionEngine(ClinicalDecisionEngine):
    """Engine for detecting drug interactions and allergies"""
    
    def __init__(self):
        # Simplified drug interaction database
        # In a real system, this would connect to a comprehensive drug database
        self.drug_interactions = {
            ("warfarin", "aspirin"): {
                "severity": AlertSeverity.HIGH,
                "interaction": "Increased bleeding risk",
                "mechanism": "Additive anticoagulant effects",
                "management": "Monitor INR closely, consider dose adjustment"
            },
            ("metformin", "contrast dye"): {
                "severity": AlertSeverity.MEDIUM,
                "interaction": "Risk of lactic acidosis",
                "mechanism": "Contrast-induced nephropathy",
                "management": "Hold metformin 48 hours before and after contrast"
            },
            ("digoxin", "amiodarone"): {
                "severity": AlertSeverity.HIGH,
                "interaction": "Digoxin toxicity",
                "mechanism": "Amiodarone increases digoxin levels",
                "management": "Reduce digoxin dose by 50%, monitor levels"
            }
        }
        
        self.drug_allergies = {
            "penicillin": ["amoxicillin", "ampicillin", "cephalexin"],
            "sulfa": ["sulfamethoxazole", "sulfadiazine", "furosemide"],
            "aspirin": ["ibuprofen", "naproxen", "celecoxib"]
        }
    
    async def analyze(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ClinicalAlert]:
        alerts = []
        
        # Get current medications
        current_meds = self._extract_medications(patient, encounter)
        
        # Check for drug interactions
        interaction_alerts = await self._check_drug_interactions(current_meds, patient.id)
        alerts.extend(interaction_alerts)
        
        # Check for allergy conflicts
        allergy_alerts = await self._check_allergy_conflicts(current_meds, patient)
        alerts.extend(allergy_alerts)
        
        return alerts
    
    def _extract_medications(self, patient: PatientModel, encounter: Optional[EncounterModel]) -> List[str]:
        """Extract medications from patient history and current encounter"""
        medications = []
        
        # From patient medical background
        if patient.medical_background.current_medications:
            medications.extend(patient.medical_background.current_medications)
        
        # From encounter plan
        if encounter and encounter.soap and encounter.soap.plan:
            plan_text = encounter.soap.plan.treatment_plan or ""
            # Simple regex to find medication mentions
            med_pattern = r'\b(metformin|warfarin|aspirin|digoxin|amiodarone|amoxicillin|ibuprofen)\b'
            found_meds = re.findall(med_pattern, plan_text.lower())
            medications.extend(found_meds)
        
        return list(set(medications))  # Remove duplicates
    
    async def _check_drug_interactions(self, medications: List[str], patient_id: str) -> List[ClinicalAlert]:
        """Check for drug-drug interactions"""
        alerts = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction_key = tuple(sorted([med1.lower(), med2.lower()]))
                
                if interaction_key in self.drug_interactions:
                    interaction = self.drug_interactions[interaction_key]
                    
                    alert = ClinicalAlert(
                        alert_id=f"drug_interaction_{med1}_{med2}_{patient_id}",
                        alert_type=AlertType.DRUG_INTERACTION,
                        severity=interaction["severity"],
                        title=f"Drug Interaction: {med1.title()} + {med2.title()}",
                        message=f"Interaction: {interaction['interaction']}. Mechanism: {interaction['mechanism']}.",
                        patient_id=patient_id,
                        triggered_by=[med1, med2],
                        recommended_actions=[interaction["management"]],
                        evidence_level="A",
                        metadata={
                            "drug1": med1,
                            "drug2": med2,
                            "interaction_type": "drug-drug",
                            "mechanism": interaction["mechanism"]
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _check_allergy_conflicts(self, medications: List[str], patient: PatientModel) -> List[ClinicalAlert]:
        """Check for medication allergy conflicts"""
        alerts = []
        
        patient_allergies = patient.medical_background.allergies or []
        
        for medication in medications:
            for allergy in patient_allergies:
                allergy_lower = allergy.lower()
                medication_lower = medication.lower()
                
                # Direct allergy match
                if medication_lower == allergy_lower:
                    alert = ClinicalAlert(
                        alert_id=f"allergy_direct_{medication}_{patient.id}",
                        alert_type=AlertType.ALLERGY_WARNING,
                        severity=AlertSeverity.CRITICAL,
                        title=f"ALLERGY ALERT: {medication.title()}",
                        message=f"Patient has documented allergy to {medication}. DO NOT ADMINISTER.",
                        patient_id=patient.id,
                        triggered_by=[medication, allergy],
                        recommended_actions=[
                            "Do not administer this medication",
                            "Consider alternative therapy",
                            "Verify allergy history with patient"
                        ],
                        dismissible=False
                    )
                    alerts.append(alert)
                
                # Cross-allergy check
                elif allergy_lower in self.drug_allergies:
                    cross_allergic_drugs = self.drug_allergies[allergy_lower]
                    if medication_lower in cross_allergic_drugs:
                        alert = ClinicalAlert(
                            alert_id=f"allergy_cross_{medication}_{allergy}_{patient.id}",
                            alert_type=AlertType.ALLERGY_WARNING,
                            severity=AlertSeverity.HIGH,
                            title=f"Cross-Allergy Risk: {medication.title()}",
                            message=f"Patient allergic to {allergy}. {medication} may cause cross-reaction.",
                            patient_id=patient.id,
                            triggered_by=[medication, allergy],
                            recommended_actions=[
                                "Use with extreme caution",
                                "Consider alternative medication",
                                "Have emergency medications available"
                            ]
                        )
                        alerts.append(alert)
        
        return alerts


class DiagnosisEngine(ClinicalDecisionEngine):
    """Engine for suggesting diagnoses based on symptoms and patient data"""
    
    def __init__(self):
        # Simplified symptom-diagnosis mapping
        # In a real system, this would use machine learning or comprehensive medical knowledge bases
        self.symptom_diagnosis_map = {
            "chest pain": [
                DiagnosisSuggestion(
                    diagnosis_name="Myocardial Infarction",
                    confidence_score=0.7,
                    supporting_symptoms=["chest pain", "shortness of breath", "nausea"],
                    recommended_tests=["ECG", "Troponin", "CXR"],
                    urgency_level="emergent",
                    icd10_code="I21.9"
                ),
                DiagnosisSuggestion(
                    diagnosis_name="Gastroesophageal Reflux Disease",
                    confidence_score=0.4,
                    supporting_symptoms=["chest pain", "heartburn", "regurgitation"],
                    recommended_tests=["Upper endoscopy", "pH monitoring"],
                    urgency_level="routine",
                    icd10_code="K21.9"
                )
            ],
            "headache": [
                DiagnosisSuggestion(
                    diagnosis_name="Tension Headache",
                    confidence_score=0.6,
                    supporting_symptoms=["headache", "neck pain", "stress"],
                    recommended_tests=["Physical examination"],
                    urgency_level="routine",
                    icd10_code="G44.2"
                ),
                DiagnosisSuggestion(
                    diagnosis_name="Migraine",
                    confidence_score=0.5,
                    supporting_symptoms=["headache", "nausea", "photophobia"],
                    recommended_tests=["Neurological examination"],
                    urgency_level="routine",
                    icd10_code="G43.9"
                )
            ]
        }
    
    async def analyze(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ClinicalAlert]:
        alerts = []
        
        if not encounter or not encounter.soap:
            return alerts
        
        # Extract symptoms from chief complaint and HPI
        symptoms = self._extract_symptoms(encounter.soap)
        
        # Generate diagnosis suggestions
        suggestions = await self._generate_diagnosis_suggestions(symptoms, patient)
        
        # Create alerts for high-urgency diagnoses
        for suggestion in suggestions:
            if suggestion.urgency_level == "emergent" and suggestion.confidence_score > 0.6:
                alert = ClinicalAlert(
                    alert_id=f"diagnosis_urgent_{suggestion.diagnosis_name}_{patient.id}",
                    alert_type=AlertType.DIAGNOSTIC_REMINDER,
                    severity=AlertSeverity.CRITICAL,
                    title=f"URGENT: Consider {suggestion.diagnosis_name}",
                    message=f"High probability ({suggestion.confidence_score:.1%}) of {suggestion.diagnosis_name} based on presenting symptoms.",
                    patient_id=patient.id,
                    encounter_id=encounter.id if encounter else None,
                    triggered_by=suggestion.supporting_symptoms,
                    recommended_actions=[
                        f"Immediate evaluation for {suggestion.diagnosis_name}",
                        f"Consider: {', '.join(suggestion.recommended_tests)}"
                    ],
                    metadata={
                        "diagnosis_suggestion": suggestion.model_dump(),
                        "confidence_score": suggestion.confidence_score
                    }
                )
                alerts.append(alert)
        
        return alerts
    
    def _extract_symptoms(self, soap: SOAPModel) -> List[str]:
        """Extract symptoms from SOAP documentation"""
        symptoms = []
        
        if soap.subjective:
            # Extract from chief complaint
            if soap.subjective.chief_complaint:
                symptoms.extend(self._parse_symptoms_from_text(soap.subjective.chief_complaint))
            
            # Extract from HPI
            if soap.subjective.history_of_present_illness:
                symptoms.extend(self._parse_symptoms_from_text(soap.subjective.history_of_present_illness))
        
        return list(set(symptoms))  # Remove duplicates
    
    def _parse_symptoms_from_text(self, text: str) -> List[str]:
        """Parse symptoms from clinical text"""
        common_symptoms = [
            "chest pain", "headache", "nausea", "vomiting", "fever", "fatigue",
            "shortness of breath", "dizziness", "abdominal pain", "back pain",
            "cough", "sore throat", "joint pain", "muscle pain"
        ]
        
        found_symptoms = []
        text_lower = text.lower()
        
        for symptom in common_symptoms:
            if symptom in text_lower:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    async def _generate_diagnosis_suggestions(
        self, 
        symptoms: List[str], 
        patient: PatientModel
    ) -> List[DiagnosisSuggestion]:
        """Generate diagnosis suggestions based on symptoms"""
        suggestions = []
        
        for symptom in symptoms:
            if symptom in self.symptom_diagnosis_map:
                symptom_suggestions = self.symptom_diagnosis_map[symptom]
                
                for suggestion in symptom_suggestions:
                    # Adjust confidence based on patient factors
                    adjusted_suggestion = suggestion.model_copy()
                    adjusted_suggestion.confidence_score = self._adjust_confidence_for_patient(
                        suggestion, patient
                    )
                    suggestions.append(adjusted_suggestion)
        
        # Remove duplicates and sort by confidence
        unique_suggestions = {}
        for suggestion in suggestions:
            key = suggestion.diagnosis_name
            if key not in unique_suggestions or suggestion.confidence_score > unique_suggestions[key].confidence_score:
                unique_suggestions[key] = suggestion
        
        return sorted(unique_suggestions.values(), key=lambda x: x.confidence_score, reverse=True)
    
    def _adjust_confidence_for_patient(
        self, 
        suggestion: DiagnosisSuggestion, 
        patient: PatientModel
    ) -> float:
        """Adjust diagnosis confidence based on patient demographics and history"""
        confidence = suggestion.confidence_score
        
        # Age adjustments
        age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
        
        if age:
            # MI more likely in older patients
            if suggestion.diagnosis_name == "Myocardial Infarction" and age > 50:
                confidence += 0.1
            elif suggestion.diagnosis_name == "Myocardial Infarction" and age < 30:
                confidence -= 0.2
        
        # Medical history adjustments
        if patient.medical_background.medical_history:
            history_lower = " ".join(patient.medical_background.medical_history).lower()
            
            if "diabetes" in history_lower and suggestion.diagnosis_name == "Myocardial Infarction":
                confidence += 0.1
            
            if "gerd" in history_lower and suggestion.diagnosis_name == "Gastroesophageal Reflux Disease":
                confidence += 0.2
        
        return min(1.0, max(0.0, confidence))  # Keep between 0 and 1
    
    def _calculate_age(self, date_of_birth: Union[str, datetime]) -> Optional[int]:
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


class RiskAssessmentEngine(ClinicalDecisionEngine):
    """Engine for calculating clinical risk scores"""
    
    async def analyze(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ClinicalAlert]:
        alerts = []
        
        # Calculate cardiovascular risk
        cv_risk = await self._calculate_cardiovascular_risk(patient)
        if cv_risk and cv_risk.risk_score > 0.2:  # >20% 10-year risk
            alert = ClinicalAlert(
                alert_id=f"cv_risk_{patient.id}",
                alert_type=AlertType.RISK_ASSESSMENT,
                severity=AlertSeverity.MEDIUM if cv_risk.risk_score < 0.3 else AlertSeverity.HIGH,
                title=f"High Cardiovascular Risk ({cv_risk.risk_score:.1%})",
                message=f"Patient has {cv_risk.risk_category} cardiovascular risk. Consider preventive interventions.",
                patient_id=patient.id,
                recommended_actions=cv_risk.recommendations,
                metadata={"risk_assessment": cv_risk.model_dump()}
            )
            alerts.append(alert)
        
        # Calculate falls risk for elderly patients
        age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
        if age and age >= 65:
            falls_risk = await self._calculate_falls_risk(patient)
            if falls_risk and falls_risk.risk_category in ["moderate", "high"]:
                alert = ClinicalAlert(
                    alert_id=f"falls_risk_{patient.id}",
                    alert_type=AlertType.RISK_ASSESSMENT,
                    severity=AlertSeverity.MEDIUM,
                    title=f"Falls Risk Assessment: {falls_risk.risk_category.title()}",
                    message="Patient at increased risk for falls. Consider prevention strategies.",
                    patient_id=patient.id,
                    recommended_actions=falls_risk.recommendations
                )
                alerts.append(alert)
        
        return alerts
    
    async def _calculate_cardiovascular_risk(self, patient: PatientModel) -> Optional[RiskAssessment]:
        """Calculate 10-year cardiovascular disease risk (simplified Framingham-style)"""
        try:
            age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
            if not age:
                return None
            
            # Simplified risk calculation (not medically accurate - for demo only)
            risk_score = 0.0
            factors = []
            
            # Age factor
            if age >= 65:
                risk_score += 0.15
                factors.append("Age ≥65")
            elif age >= 55:
                risk_score += 0.08
                factors.append("Age 55-64")
            
            # Gender factor
            if patient.demographics.gender and patient.demographics.gender.lower() == "male":
                risk_score += 0.05
                factors.append("Male gender")
            
            # Medical history factors
            if patient.medical_background.medical_history:
                history_lower = " ".join(patient.medical_background.medical_history).lower()
                
                if "diabetes" in history_lower:
                    risk_score += 0.1
                    factors.append("Diabetes")
                
                if "hypertension" in history_lower or "high blood pressure" in history_lower:
                    risk_score += 0.08
                    factors.append("Hypertension")
                
                if "smoking" in history_lower or "smoker" in history_lower:
                    risk_score += 0.12
                    factors.append("Smoking")
            
            # Determine risk category
            if risk_score < 0.1:
                risk_category = "low"
                recommendations = ["Continue healthy lifestyle", "Routine screening"]
            elif risk_score < 0.2:
                risk_category = "moderate"
                recommendations = ["Lifestyle counseling", "Consider statin therapy", "Annual monitoring"]
            else:
                risk_category = "high"
                recommendations = ["Intensive lifestyle intervention", "Statin therapy recommended", "Consider cardiology referral"]
            
            return RiskAssessment(
                risk_type="cardiovascular",
                risk_score=risk_score,
                risk_category=risk_category,
                calculation_method="Simplified Framingham",
                factors_assessed=factors,
                recommendations=recommendations,
                follow_up_interval="annually",
                validity_period=timedelta(days=365)
            )
            
        except Exception as e:
            logger.error(f"Error calculating cardiovascular risk: {e}")
            return None
    
    async def _calculate_falls_risk(self, patient: PatientModel) -> Optional[RiskAssessment]:
        """Calculate falls risk for elderly patients"""
        try:
            risk_score = 0
            factors = []
            
            age = self._calculate_age(patient.demographics.date_of_birth) if patient.demographics.date_of_birth else None
            if not age or age < 65:
                return None
            
            # Age factor
            if age >= 80:
                risk_score += 2
                factors.append("Age ≥80")
            elif age >= 75:
                risk_score += 1
                factors.append("Age 75-79")
            
            # Medical history factors
            if patient.medical_background.medical_history:
                history_lower = " ".join(patient.medical_background.medical_history).lower()
                
                if any(term in history_lower for term in ["fall", "falls", "fell"]):
                    risk_score += 2
                    factors.append("Previous falls")
                
                if "dementia" in history_lower or "cognitive" in history_lower:
                    risk_score += 1
                    factors.append("Cognitive impairment")
                
                if "arthritis" in history_lower or "joint pain" in history_lower:
                    risk_score += 1
                    factors.append("Mobility issues")
            
            # Medication factors
            if patient.medical_background.current_medications:
                meds_lower = [med.lower() for med in patient.medical_background.current_medications]
                
                if any("sedative" in med or "benzodiazepine" in med for med in meds_lower):
                    risk_score += 1
                    factors.append("Sedating medications")
            
            # Determine risk category
            if risk_score <= 1:
                risk_category = "low"
                recommendations = ["Annual falls screening", "Home safety assessment"]
            elif risk_score <= 3:
                risk_category = "moderate"
                recommendations = ["Falls prevention program", "Physical therapy evaluation", "Medication review"]
            else:
                risk_category = "high"
                recommendations = ["Comprehensive falls assessment", "Immediate safety measures", "Multidisciplinary care plan"]
            
            return RiskAssessment(
                risk_type="falls",
                risk_score=float(risk_score),
                risk_category=risk_category,
                calculation_method="Clinical Falls Risk Assessment",
                factors_assessed=factors,
                recommendations=recommendations,
                follow_up_interval="6 months"
            )
            
        except Exception as e:
            logger.error(f"Error calculating falls risk: {e}")
            return None
    
    def _calculate_age(self, date_of_birth: Union[str, datetime]) -> Optional[int]:
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


class ClinicalDecisionSupportSystem:
    """Main clinical decision support system coordinator"""
    
    def __init__(self):
        self.engines = [
            DrugInteractionEngine(),
            DiagnosisEngine(),
            RiskAssessmentEngine()
        ]
    
    async def analyze_patient(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive clinical decision support analysis"""
        try:
            start_time = datetime.utcnow()
            
            # Run all engines in parallel
            engine_tasks = [
                engine.analyze(patient, encounter, context) 
                for engine in self.engines
            ]
            
            engine_results = await asyncio.gather(*engine_tasks, return_exceptions=True)
            
            # Collect all alerts
            all_alerts = []
            for i, result in enumerate(engine_results):
                if isinstance(result, Exception):
                    logger.error(f"Engine {i} failed: {result}")
                    continue
                all_alerts.extend(result)
            
            # Sort alerts by severity and confidence
            sorted_alerts = sorted(
                all_alerts, 
                key=lambda x: (
                    ["info", "low", "medium", "high", "critical"].index(x.severity.value),
                    x.created_at
                ), 
                reverse=True
            )
            
            # Generate summary
            summary = self._generate_summary(sorted_alerts, patient, encounter)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "patient_id": patient.id,
                "encounter_id": encounter.id if encounter else None,
                "analysis_timestamp": start_time.isoformat(),
                "execution_time_seconds": execution_time,
                "alerts": [alert.model_dump() for alert in sorted_alerts],
                "summary": summary,
                "alert_counts": {
                    "total": len(sorted_alerts),
                    "critical": len([a for a in sorted_alerts if a.severity == AlertSeverity.CRITICAL]),
                    "high": len([a for a in sorted_alerts if a.severity == AlertSeverity.HIGH]),
                    "medium": len([a for a in sorted_alerts if a.severity == AlertSeverity.MEDIUM]),
                    "low": len([a for a in sorted_alerts if a.severity == AlertSeverity.LOW]),
                    "info": len([a for a in sorted_alerts if a.severity == AlertSeverity.INFO])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in clinical decision support analysis: {e}")
            return {
                "patient_id": patient.id,
                "encounter_id": encounter.id if encounter else None,
                "error": str(e),
                "alerts": [],
                "summary": {"status": "error", "message": "Analysis failed"}
            }
    
    def _generate_summary(
        self, 
        alerts: List[ClinicalAlert], 
        patient: PatientModel, 
        encounter: Optional[EncounterModel]
    ) -> Dict[str, Any]:
        """Generate executive summary of clinical decision support findings"""
        
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        high_alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]
        
        priority_actions = []
        
        # Critical actions
        for alert in critical_alerts:
            priority_actions.extend(alert.recommended_actions)
        
        # High priority actions (limit to 3)
        for alert in high_alerts[:3]:
            priority_actions.extend(alert.recommended_actions)
        
        summary = {
            "status": "completed",
            "risk_level": "low",
            "primary_concerns": [],
            "priority_actions": list(set(priority_actions))[:5],  # Top 5 unique actions
            "recommendations": []
        }
        
        # Determine overall risk level
        if critical_alerts:
            summary["risk_level"] = "critical"
            summary["primary_concerns"] = [a.title for a in critical_alerts]
        elif len(high_alerts) >= 2:
            summary["risk_level"] = "high"
            summary["primary_concerns"] = [a.title for a in high_alerts[:2]]
        elif high_alerts:
            summary["risk_level"] = "medium"
            summary["primary_concerns"] = [high_alerts[0].title]
        
        # Generate recommendations
        if critical_alerts or high_alerts:
            summary["recommendations"] = [
                "Review all critical and high-priority alerts immediately",
                "Document clinical decision-making in encounter notes",
                "Consider specialist consultation if indicated"
            ]
        else:
            summary["recommendations"] = [
                "Continue current care plan",
                "Monitor for changes in patient condition",
                "Follow standard protocols for routine care"
            ]
        
        return summary
    
    async def get_treatment_recommendations(
        self, 
        diagnosis: str, 
        patient: PatientModel
    ) -> List[TreatmentRecommendation]:
        """Get treatment recommendations for a specific diagnosis"""
        
        # Simplified treatment recommendation database
        # In a real system, this would connect to comprehensive clinical guidelines
        treatment_db = {
            "hypertension": [
                TreatmentRecommendation(
                    treatment_type="medication",
                    treatment_name="ACE Inhibitor (Lisinopril)",
                    indication="First-line antihypertensive",
                    dosage="10mg daily, titrate as needed",
                    duration="Long-term",
                    contraindications=["Pregnancy", "Hyperkalemia"],
                    side_effects=["Dry cough", "Hyperkalemia"],
                    monitoring_required=["Blood pressure", "Kidney function", "Electrolytes"],
                    evidence_level="A"
                ),
                TreatmentRecommendation(
                    treatment_type="lifestyle",
                    treatment_name="DASH Diet",
                    indication="Blood pressure reduction",
                    contraindications=[],
                    evidence_level="A"
                )
            ],
            "diabetes": [
                TreatmentRecommendation(
                    treatment_type="medication",
                    treatment_name="Metformin",
                    indication="First-line diabetes medication",
                    dosage="500mg twice daily with meals",
                    contraindications=["Kidney disease", "Liver disease"],
                    side_effects=["GI upset", "Lactic acidosis (rare)"],
                    monitoring_required=["HbA1c", "Kidney function"],
                    evidence_level="A"
                )
            ]
        }
        
        diagnosis_lower = diagnosis.lower()
        return treatment_db.get(diagnosis_lower, [])


# Global clinical decision support system instance
clinical_decision_support = ClinicalDecisionSupportSystem()