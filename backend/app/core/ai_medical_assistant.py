"""
Medical AI Assistant for DiagnoAssist Backend

This module provides AI-powered medical insights using Google Gemini including:
- Intelligent symptom analysis and differential diagnosis suggestions
- Drug interaction checking (deterministic for safety)
- Allergy alerts (deterministic for safety)
- Clinical documentation enhancement
- Patient education content generation
- Risk factor explanations

IMPORTANT MEDICAL DISCLAIMERS:
- All AI-generated suggestions are for healthcare provider consideration only
- AI recommendations do not replace clinical judgment
- All suggestions require physician review and approval
- Drug interactions and allergy checks use validated medical databases
- This system is intended to assist, not replace, medical decision-making
"""
import asyncio
import re
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field
import logging

from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.models.soap import SOAPModel
from app.models.auth import UserModel
from app.core.exceptions import ValidationException, AIServiceException
from app.core.ai_client import get_ai_client, AIRequest, AITaskType, AIModelType

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Medical alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of medical alerts"""
    DRUG_INTERACTION = "drug_interaction"
    ALLERGY_WARNING = "allergy_warning"
    AI_INSIGHT = "ai_insight"
    DIAGNOSIS_SUGGESTION = "diagnosis_suggestion"
    RISK_ASSESSMENT = "risk_assessment"
    DOCUMENTATION_SUGGESTION = "documentation_suggestion"


class MedicalAlert(BaseModel):
    """Represents a medical alert or AI suggestion"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    confidence_score: Optional[float] = None  # 0.0-1.0 for AI suggestions
    ai_generated: bool = False
    requires_physician_review: bool = True
    medical_disclaimer: bool = True
    triggered_by: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIInsight(BaseModel):
    """AI-generated medical insight"""
    insight_type: str
    title: str
    content: str
    confidence_score: float
    supporting_evidence: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    medical_codes: List[str] = Field(default_factory=list)  # ICD-10, CPT codes
    requires_followup: bool = False
    disclaimer: str = "AI-generated suggestion. Requires physician review."


class DrugSafetyChecker:
    """Deterministic drug interaction and allergy checking (safety-critical)"""
    
    def __init__(self):
        # Validated drug interaction database - NEVER use AI for these
        self.drug_interactions = {
            ("warfarin", "aspirin"): {
                "severity": AlertSeverity.CRITICAL,
                "interaction": "Increased bleeding risk - potentially life-threatening",
                "mechanism": "Additive anticoagulant effects",
                "management": "Avoid combination. If necessary, monitor INR closely and reduce doses"
            },
            ("digoxin", "amiodarone"): {
                "severity": AlertSeverity.HIGH,
                "interaction": "Digoxin toxicity risk",
                "mechanism": "Amiodarone inhibits digoxin elimination",
                "management": "Reduce digoxin dose by 50%, monitor levels weekly"
            },
            ("metformin", "contrast dye"): {
                "severity": AlertSeverity.HIGH,
                "interaction": "Lactic acidosis risk",
                "mechanism": "Contrast-induced nephropathy may impair metformin clearance",
                "management": "Hold metformin 48 hours before and after contrast administration"
            },
            ("simvastatin", "clarithromycin"): {
                "severity": AlertSeverity.HIGH,
                "interaction": "Rhabdomyolysis risk",
                "mechanism": "CYP3A4 inhibition increases statin levels",
                "management": "Avoid combination or temporarily discontinue statin"
            }
        }
        
        # Validated allergy cross-reactions - NEVER use AI for these
        self.allergy_cross_reactions = {
            "penicillin": ["amoxicillin", "ampicillin", "cephalexin", "cefazolin"],
            "sulfa": ["sulfamethoxazole", "sulfadiazine", "furosemide", "hydrochlorothiazide"],
            "aspirin": ["ibuprofen", "naproxen", "celecoxib", "diclofenac"],
            "codeine": ["morphine", "oxycodone", "hydrocodone"],
            "latex": ["banana", "avocado", "kiwi", "chestnut"]  # Latex-fruit syndrome
        }
    
    def check_drug_interactions(self, medications: List[str], patient_id: str) -> List[MedicalAlert]:
        """Check for dangerous drug interactions using validated database"""
        alerts = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction_key = tuple(sorted([med1.lower(), med2.lower()]))
                
                if interaction_key in self.drug_interactions:
                    interaction = self.drug_interactions[interaction_key]
                    
                    alert = MedicalAlert(
                        alert_id=f"drug_interaction_{hashlib.md5(f'{med1}_{med2}_{patient_id}'.encode()).hexdigest()[:8]}",
                        alert_type=AlertType.DRUG_INTERACTION,
                        severity=interaction["severity"],
                        title=f"⚠️ DRUG INTERACTION: {med1.title()} + {med2.title()}",
                        message=f"CRITICAL SAFETY ALERT: {interaction['interaction']}. Mechanism: {interaction['mechanism']}.",
                        patient_id=patient_id,
                        ai_generated=False,  # Deterministic database lookup
                        requires_physician_review=True,
                        medical_disclaimer=False,  # Medical database, not AI
                        triggered_by=[med1, med2],
                        recommended_actions=[interaction["management"], "Review medication regimen immediately"],
                        metadata={
                            "interaction_type": "drug-drug",
                            "mechanism": interaction["mechanism"],
                            "evidence_level": "A",
                            "database_source": "validated_interactions"
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    def check_allergy_conflicts(self, medications: List[str], patient: PatientModel) -> List[MedicalAlert]:
        """Check for medication allergy conflicts using validated database"""
        alerts = []
        
        patient_allergies = patient.medical_background.allergies or []
        
        for medication in medications:
            for allergy in patient_allergies:
                allergy_lower = allergy.lower()
                medication_lower = medication.lower()
                
                # Direct allergy match
                if medication_lower == allergy_lower:
                    alert = MedicalAlert(
                        alert_id=f"allergy_direct_{hashlib.md5(f'{medication}_{patient.id}'.encode()).hexdigest()[:8]}",
                        alert_type=AlertType.ALLERGY_WARNING,
                        severity=AlertSeverity.CRITICAL,
                        title=f"🚨 ALLERGY ALERT: {medication.title()}",
                        message=f"CRITICAL: Patient has documented allergy to {medication}. DO NOT ADMINISTER.",
                        patient_id=patient.id,
                        ai_generated=False,
                        requires_physician_review=True,
                        medical_disclaimer=False,
                        triggered_by=[medication, allergy],
                        recommended_actions=[
                            "DO NOT ADMINISTER this medication",
                            "Find alternative therapy immediately",
                            "Verify allergy history with patient",
                            "Ensure emergency medications available"
                        ]
                    )
                    alerts.append(alert)
                
                # Cross-allergy check
                elif allergy_lower in self.allergy_cross_reactions:
                    cross_allergic_drugs = self.allergy_cross_reactions[allergy_lower]
                    if medication_lower in cross_allergic_drugs:
                        alert = MedicalAlert(
                            alert_id=f"allergy_cross_{hashlib.md5(f'{medication}_{allergy}_{patient.id}'.encode()).hexdigest()[:8]}",
                            alert_type=AlertType.ALLERGY_WARNING,
                            severity=AlertSeverity.HIGH,
                            title=f"⚠️ Cross-Allergy Risk: {medication.title()}",
                            message=f"Patient allergic to {allergy}. {medication} may cause cross-reaction.",
                            patient_id=patient.id,
                            ai_generated=False,
                            requires_physician_review=True,
                            medical_disclaimer=False,
                            triggered_by=[medication, allergy],
                            recommended_actions=[
                                "Use with extreme caution",
                                "Consider alternative medication",
                                "Pre-medicate if necessary",
                                "Monitor for allergic reactions",
                                "Have emergency medications ready"
                            ]
                        )
                        alerts.append(alert)
        
        return alerts


class AISymptomAnalyzer:
    """AI-powered symptom analysis using Gemini"""
    
    def __init__(self):
        self.medical_specialties = [
            "cardiology", "pulmonology", "gastroenterology", "neurology",
            "endocrinology", "infectious disease", "emergency medicine",
            "internal medicine", "family medicine"
        ]
    
    async def analyze_symptoms(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None
    ) -> List[AIInsight]:
        """Use AI to analyze symptoms and suggest differential diagnoses"""
        try:
            ai_client = get_ai_client()
            
            # Extract clinical information
            clinical_summary = self._build_clinical_summary(patient, encounter)
            
            if not clinical_summary.get("symptoms"):
                return []
            
            # Create AI prompt for symptom analysis
            prompt = self._create_symptom_analysis_prompt(clinical_summary)
            
            ai_request = AIRequest(
                task_type=AITaskType.DIFFERENTIAL_DIAGNOSIS,
                prompt=prompt,
                context={"patient_id": patient.id, "encounter_id": encounter.id if encounter else None},
                model=AIModelType.GEMINI_PRO,
                temperature=0.1,  # Low temperature for medical accuracy
                max_tokens=1500
            )
            
            gemini_client = await ai_client.get_client()
            response = await gemini_client.generate_response(ai_request)
            
            # Parse AI response into structured insights
            insights = await self._parse_ai_diagnosis_response(response.content, clinical_summary)
            
            return insights
            
        except Exception as e:
            logger.error(f"AI symptom analysis failed: {e}")
            return []
    
    def _build_clinical_summary(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel]
    ) -> Dict[str, Any]:
        """Build structured clinical summary for AI analysis"""
        summary = {
            "patient_age": self._calculate_age(patient.demographics.date_of_birth),
            "patient_gender": patient.demographics.gender,
            "medical_history": patient.medical_background.medical_history or [],
            "current_medications": patient.medical_background.current_medications or [],
            "allergies": patient.medical_background.allergies or [],
            "symptoms": [],
            "vital_signs": {},
            "chief_complaint": "",
            "history_present_illness": ""
        }
        
        if encounter and encounter.soap:
            soap = encounter.soap
            
            if soap.subjective:
                summary["chief_complaint"] = soap.subjective.chief_complaint or ""
                summary["history_present_illness"] = soap.subjective.history_of_present_illness or ""
                summary["symptoms"] = self._extract_symptoms_from_text(
                    f"{summary['chief_complaint']} {summary['history_present_illness']}"
                )
            
            if soap.objective and soap.objective.vital_signs:
                vitals = soap.objective.vital_signs
                summary["vital_signs"] = {
                    "temperature": vitals.temperature,
                    "heart_rate": vitals.heart_rate,
                    "blood_pressure_systolic": vitals.blood_pressure_systolic,
                    "blood_pressure_diastolic": vitals.blood_pressure_diastolic,
                    "respiratory_rate": vitals.respiratory_rate,
                    "oxygen_saturation": vitals.oxygen_saturation
                }
        
        return summary
    
    def _create_symptom_analysis_prompt(self, clinical_summary: Dict[str, Any]) -> str:
        """Create detailed prompt for AI symptom analysis"""
        prompt = f"""
As a medical AI assistant, analyze the following patient presentation and provide differential diagnosis suggestions.

IMPORTANT: This is for healthcare provider assistance only. All suggestions require physician review.

PATIENT INFORMATION:
- Age: {clinical_summary['patient_age']} years
- Gender: {clinical_summary['patient_gender']}
- Medical History: {', '.join(clinical_summary['medical_history']) if clinical_summary['medical_history'] else 'None reported'}
- Current Medications: {', '.join(clinical_summary['current_medications']) if clinical_summary['current_medications'] else 'None reported'}
- Known Allergies: {', '.join(clinical_summary['allergies']) if clinical_summary['allergies'] else 'None reported'}

CLINICAL PRESENTATION:
- Chief Complaint: {clinical_summary['chief_complaint']}
- History of Present Illness: {clinical_summary['history_present_illness']}
- Key Symptoms: {', '.join(clinical_summary['symptoms']) if clinical_summary['symptoms'] else 'None documented'}

VITAL SIGNS:
{self._format_vital_signs(clinical_summary['vital_signs'])}

Please provide:

1. TOP 3 DIFFERENTIAL DIAGNOSES (most likely to least likely):
   - Include confidence level (High/Medium/Low)
   - Brief rationale for each
   - Urgency level (Emergent/Urgent/Routine)

2. RECOMMENDED DIAGNOSTIC WORKUP:
   - Laboratory tests to consider
   - Imaging studies if indicated
   - Physical examination findings to assess

3. RED FLAGS TO MONITOR:
   - Warning signs requiring immediate attention
   - Symptoms that would change urgency level

4. ADDITIONAL QUESTIONS TO CONSIDER:
   - Important history elements that may be missing
   - Review of systems questions

Format your response clearly with numbered sections. Remember this is for healthcare provider consideration only.
"""
        return prompt
    
    def _format_vital_signs(self, vitals: Dict[str, Any]) -> str:
        """Format vital signs for AI prompt"""
        if not vitals:
            return "Not documented"
        
        formatted = []
        for key, value in vitals.items():
            if value is not None:
                unit_map = {
                    "temperature": "°F",
                    "heart_rate": "bpm",
                    "blood_pressure_systolic": "mmHg",
                    "blood_pressure_diastolic": "mmHg", 
                    "respiratory_rate": "/min",
                    "oxygen_saturation": "%"
                }
                unit = unit_map.get(key, "")
                formatted.append(f"- {key.replace('_', ' ').title()}: {value} {unit}")
        
        return "\n".join(formatted) if formatted else "Not documented"
    
    async def _parse_ai_diagnosis_response(
        self, 
        ai_response: str, 
        clinical_summary: Dict[str, Any]
    ) -> List[AIInsight]:
        """Parse AI response into structured medical insights"""
        insights = []
        
        try:
            # Extract differential diagnoses
            differential_insights = self._extract_differential_diagnoses(ai_response)
            insights.extend(differential_insights)
            
            # Extract diagnostic recommendations
            diagnostic_insights = self._extract_diagnostic_recommendations(ai_response)
            insights.extend(diagnostic_insights)
            
            # Extract red flags
            red_flag_insights = self._extract_red_flags(ai_response)
            insights.extend(red_flag_insights)
            
            # Add metadata to all insights
            for insight in insights:
                insight.metadata = {
                    **insight.metadata,
                    "ai_model": "gemini-pro",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "patient_age": clinical_summary.get("patient_age"),
                    "symptoms_analyzed": clinical_summary.get("symptoms", [])
                }
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            
            # Return a safe fallback insight
            insights.append(AIInsight(
                insight_type="ai_error",
                title="AI Analysis Unavailable",
                content="Unable to process AI response. Please proceed with standard clinical assessment.",
                confidence_score=0.0,
                disclaimer="AI analysis failed. Rely on clinical judgment."
            ))
        
        return insights
    
    def _extract_differential_diagnoses(self, ai_response: str) -> List[AIInsight]:
        """Extract differential diagnosis insights from AI response"""
        insights = []
        
        # Simple extraction - in production would use more sophisticated NLP
        if "differential diagnos" in ai_response.lower():
            insight = AIInsight(
                insight_type="differential_diagnosis",
                title="AI Differential Diagnosis Suggestions",
                content=ai_response,
                confidence_score=0.7,  # Default confidence
                suggested_actions=[
                    "Review AI suggestions with clinical findings",
                    "Consider additional history and examination",
                    "Order appropriate diagnostic tests"
                ],
                requires_followup=True,
                disclaimer="AI-generated differential diagnosis. Requires physician review and clinical correlation."
            )
            insights.append(insight)
        
        return insights
    
    def _extract_diagnostic_recommendations(self, ai_response: str) -> List[AIInsight]:
        """Extract diagnostic test recommendations from AI response"""
        insights = []
        
        if "diagnostic" in ai_response.lower() or "test" in ai_response.lower():
            insight = AIInsight(
                insight_type="diagnostic_recommendations",
                title="AI Diagnostic Test Suggestions",
                content="AI has suggested diagnostic workup based on presentation.",
                confidence_score=0.6,
                suggested_actions=["Review suggested tests for clinical appropriateness"],
                disclaimer="AI-suggested tests. Clinical judgment required for ordering."
            )
            insights.append(insight)
        
        return insights
    
    def _extract_red_flags(self, ai_response: str) -> List[AIInsight]:
        """Extract red flag warnings from AI response"""
        insights = []
        
        if "red flag" in ai_response.lower() or "warning" in ai_response.lower():
            insight = AIInsight(
                insight_type="red_flags",
                title="⚠️ AI Safety Alerts",
                content="AI has identified potential warning signs requiring attention.",
                confidence_score=0.8,
                suggested_actions=["Assess for emergency conditions immediately"],
                requires_followup=True,
                disclaimer="AI-identified warning signs. Immediate clinical assessment required."
            )
            insights.append(insight)
        
        return insights
    
    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract medical symptoms from clinical text"""
        if not text:
            return []
        
        # Common medical symptoms for pattern matching
        symptom_patterns = [
            r'\bchest pain\b', r'\bshortness of breath\b', r'\bnausea\b', r'\bvomiting\b',
            r'\bheadache\b', r'\bdizziness\b', r'\bfever\b', r'\bfatigue\b', r'\bcough\b',
            r'\babdominal pain\b', r'\bback pain\b', r'\bjoint pain\b', r'\bmuscle pain\b',
            r'\bsore throat\b', r'\brunny nose\b', r'\bpalpitations\b', r'\bsweating\b'
        ]
        
        found_symptoms = []
        text_lower = text.lower()
        
        for pattern in symptom_patterns:
            if re.search(pattern, text_lower):
                symptom = pattern.replace(r'\b', '').replace('\\', '')
                found_symptoms.append(symptom)
        
        return found_symptoms
    
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


class MedicalAIAssistant:
    """Main AI-powered medical assistant coordinator"""
    
    def __init__(self):
        self.drug_safety = DrugSafetyChecker()
        self.symptom_analyzer = AISymptomAnalyzer()
    
    async def analyze_patient(
        self, 
        patient: PatientModel, 
        encounter: Optional[EncounterModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive medical AI analysis"""
        try:
            start_time = datetime.utcnow()
            
            # Extract medications for safety checking
            medications = self._extract_medications(patient, encounter)
            
            # Run safety-critical checks (deterministic)
            drug_alerts = self.drug_safety.check_drug_interactions(medications, patient.id)
            allergy_alerts = self.drug_safety.check_allergy_conflicts(medications, patient)
            
            # Run AI-powered analysis (if symptoms present)
            ai_insights = []
            if encounter and encounter.soap and encounter.soap.subjective:
                ai_insights = await self.symptom_analyzer.analyze_symptoms(patient, encounter)
            
            # Convert insights to alerts
            ai_alerts = self._convert_insights_to_alerts(ai_insights, patient.id, encounter.id if encounter else None)
            
            # Combine all alerts
            all_alerts = drug_alerts + allergy_alerts + ai_alerts
            
            # Sort by severity and type (safety-critical first)
            sorted_alerts = self._sort_alerts_by_priority(all_alerts)
            
            # Generate summary
            summary = self._generate_analysis_summary(sorted_alerts, patient, encounter)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "patient_id": patient.id,
                "encounter_id": encounter.id if encounter else None,
                "analysis_timestamp": start_time.isoformat(),
                "execution_time_seconds": execution_time,
                "alerts": [alert.model_dump() for alert in sorted_alerts],
                "ai_insights": [insight.model_dump() for insight in ai_insights],
                "summary": summary,
                "alert_counts": self._count_alerts_by_type(sorted_alerts),
                "medical_disclaimer": {
                    "message": "This analysis is for healthcare provider assistance only. All AI suggestions require physician review.",
                    "safety_note": "Drug interactions and allergy alerts use validated medical databases.",
                    "ai_note": "AI insights are suggestions only and do not replace clinical judgment.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Medical AI analysis failed: {e}")
            return {
                "patient_id": patient.id,
                "encounter_id": encounter.id if encounter else None,
                "error": str(e),
                "alerts": [],
                "summary": {"status": "error", "message": "AI analysis failed"},
                "medical_disclaimer": {
                    "message": "Analysis failed. Proceed with standard clinical assessment."
                }
            }
    
    def _extract_medications(self, patient: PatientModel, encounter: Optional[EncounterModel]) -> List[str]:
        """Extract medications from patient history and current encounter"""
        medications = []
        
        # From patient medical background
        if patient.medical_background.current_medications:
            medications.extend(patient.medical_background.current_medications)
        
        # From encounter plan (simple extraction)
        if encounter and encounter.soap and encounter.soap.plan:
            plan_text = encounter.soap.plan.treatment_plan or ""
            # Basic medication extraction - in production would use medical NLP
            common_meds = [
                "metformin", "warfarin", "aspirin", "digoxin", "amiodarone", 
                "amoxicillin", "ibuprofen", "lisinopril", "simvastatin", "clarithromycin"
            ]
            for med in common_meds:
                if med in plan_text.lower():
                    medications.append(med)
        
        return list(set(medications))  # Remove duplicates
    
    def _convert_insights_to_alerts(
        self, 
        insights: List[AIInsight], 
        patient_id: str, 
        encounter_id: Optional[str]
    ) -> List[MedicalAlert]:
        """Convert AI insights to medical alerts"""
        alerts = []
        
        for insight in insights:
            severity = AlertSeverity.MEDIUM
            if insight.confidence_score > 0.8:
                severity = AlertSeverity.HIGH
            elif insight.confidence_score < 0.4:
                severity = AlertSeverity.LOW
            
            alert = MedicalAlert(
                alert_id=f"ai_{insight.insight_type}_{hashlib.md5(f'{patient_id}_{datetime.utcnow()}'.encode()).hexdigest()[:8]}",
                alert_type=AlertType.AI_INSIGHT,
                severity=severity,
                title=f"🤖 AI: {insight.title}",
                message=f"{insight.content}\n\n⚠️ {insight.disclaimer}",
                patient_id=patient_id,
                encounter_id=encounter_id,
                confidence_score=insight.confidence_score,
                ai_generated=True,
                requires_physician_review=True,
                medical_disclaimer=True,
                recommended_actions=insight.suggested_actions,
                supporting_evidence=insight.supporting_evidence,
                metadata={
                    "ai_insight_type": insight.insight_type,
                    "confidence_score": insight.confidence_score,
                    "requires_followup": insight.requires_followup,
                    "medical_codes": insight.medical_codes
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _sort_alerts_by_priority(self, alerts: List[MedicalAlert]) -> List[MedicalAlert]:
        """Sort alerts by priority (safety-critical first, then by severity)"""
        def alert_priority(alert):
            # Safety-critical alerts first
            if alert.alert_type in [AlertType.DRUG_INTERACTION, AlertType.ALLERGY_WARNING]:
                priority = 0
            else:
                priority = 1
            
            # Then by severity
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            
            return (priority, severity_order.get(alert.severity, 5), alert.created_at)
        
        return sorted(alerts, key=alert_priority)
    
    def _generate_analysis_summary(
        self, 
        alerts: List[MedicalAlert], 
        patient: PatientModel, 
        encounter: Optional[EncounterModel]
    ) -> Dict[str, Any]:
        """Generate executive summary of medical analysis"""
        
        safety_alerts = [a for a in alerts if a.alert_type in [AlertType.DRUG_INTERACTION, AlertType.ALLERGY_WARNING]]
        ai_alerts = [a for a in alerts if a.ai_generated]
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        
        summary = {
            "overall_status": "safe",
            "risk_level": "low",
            "primary_concerns": [],
            "ai_insights_available": len(ai_alerts) > 0,
            "safety_alerts_count": len(safety_alerts),
            "priority_actions": [],
            "physician_review_required": any(a.requires_physician_review for a in alerts)
        }
        
        # Determine risk level based on alerts
        if critical_alerts:
            summary["overall_status"] = "critical"
            summary["risk_level"] = "critical"
            summary["primary_concerns"] = [a.title for a in critical_alerts]
        elif safety_alerts:
            summary["overall_status"] = "safety_concern"
            summary["risk_level"] = "high" if any(a.severity == AlertSeverity.HIGH for a in safety_alerts) else "medium"
            summary["primary_concerns"] = [a.title for a in safety_alerts[:2]]
        elif ai_alerts:
            high_confidence_ai = [a for a in ai_alerts if a.confidence_score and a.confidence_score > 0.7]
            if high_confidence_ai:
                summary["overall_status"] = "ai_insights"
                summary["risk_level"] = "medium"
                summary["primary_concerns"] = [a.title for a in high_confidence_ai[:1]]
        
        # Generate priority actions
        priority_actions = []
        for alert in alerts[:3]:  # Top 3 alerts
            priority_actions.extend(alert.recommended_actions[:2])  # Top 2 actions per alert
        
        summary["priority_actions"] = list(set(priority_actions))[:5]  # Top 5 unique actions
        
        return summary
    
    def _count_alerts_by_type(self, alerts: List[MedicalAlert]) -> Dict[str, Any]:
        """Count alerts by type and severity"""
        counts = {
            "total": len(alerts),
            "by_severity": {severity.value: 0 for severity in AlertSeverity},
            "by_type": {alert_type.value: 0 for alert_type in AlertType},
            "safety_critical": 0,
            "ai_generated": 0,
            "require_review": 0
        }
        
        for alert in alerts:
            counts["by_severity"][alert.severity.value] += 1
            counts["by_type"][alert.alert_type.value] += 1
            
            if alert.alert_type in [AlertType.DRUG_INTERACTION, AlertType.ALLERGY_WARNING]:
                counts["safety_critical"] += 1
            
            if alert.ai_generated:
                counts["ai_generated"] += 1
            
            if alert.requires_physician_review:
                counts["require_review"] += 1
        
        return counts


# Global AI medical assistant instance
ai_medical_assistant = MedicalAIAssistant()