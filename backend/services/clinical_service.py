from typing import List, Optional, Dict, Any
from repositories.episode_repository import EpisodeRepository
from repositories.patient_repository import PatientRepository
from services.ai_service import AIService
from schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from schemas.clinical import ClinicalAssessmentRequest, DynamicQuestionsResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ClinicalService:
    """
    Service for clinical assessment and episode management
    """
    
    def __init__(
        self,
        episode_repo: EpisodeRepository,
        ai_service: AIService,
        patient_repo: Optional[PatientRepository] = None
    ):
        self.episode_repo = episode_repo
        self.ai_service = ai_service
        self.patient_repo = patient_repo
    
    async def create_episode(self, episode_data: EpisodeCreate) -> EpisodeResponse:
        """
        Create new medical episode with validation
        
        Args:
            episode_data: Episode creation data
            
        Returns:
            Created episode response
        """
        try:
            # Validate patient exists
            if self.patient_repo:
                patient = self.patient_repo.get(episode_data.patient_id)
                if not patient:
                    raise ValueError(f"Patient {episode_data.patient_id} not found")
            
            # Set default start date if not provided
            episode_dict = episode_data.dict()
            if not episode_dict.get("start_date"):
                episode_dict["start_date"] = datetime.utcnow()
            
            # Set initial status
            if not episode_dict.get("status"):
                episode_dict["status"] = "active"
            
            # Create episode
            episode = self.episode_repo.create(episode_dict)
            
            logger.info(f"Created episode: {episode.id} for patient: {episode_data.patient_id}")
            return EpisodeResponse.from_orm(episode)
            
        except Exception as e:
            logger.error(f"Error creating episode: {str(e)}")
            raise
    
    async def generate_dynamic_questions(
        self, 
        assessment_data: ClinicalAssessmentRequest
    ) -> DynamicQuestionsResponse:
        """
        Generate AI-powered dynamic questions for clinical assessment
        
        Args:
            assessment_data: Current clinical assessment data
            
        Returns:
            Dynamic questions response
        """
        try:
            # Prepare data for AI analysis
            ai_request = {
                "chief_complaint": assessment_data.chief_complaint,
                "symptoms": assessment_data.symptoms or [],
                "patient_demographics": {
                    "age": assessment_data.patient_age,
                    "gender": assessment_data.patient_gender
                } if assessment_data.patient_age else {},
                "current_questions_answered": assessment_data.answered_questions or []
            }
            
            # Get AI-generated questions
            ai_questions = await self.ai_service.generate_dynamic_questions(ai_request)
            
            # Process and prioritize questions
            processed_questions = await self._process_dynamic_questions(
                ai_questions, 
                assessment_data
            )
            
            return DynamicQuestionsResponse(
                questions=processed_questions,
                total_count=len(processed_questions),
                priority_order=["high", "medium", "low"],
                assessment_complete=await self._is_assessment_complete(assessment_data)
            )
            
        except Exception as e:
            logger.error(f"Error generating dynamic questions: {str(e)}")
            raise
    
    async def analyze_clinical_data(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze clinical assessment data for insights
        
        Args:
            clinical_data: Clinical assessment data
            
        Returns:
            Clinical analysis results
        """
        try:
            # Extract key clinical indicators
            analysis = {
                "completeness_score": await self._calculate_completeness(clinical_data),
                "risk_factors": await self._identify_risk_factors(clinical_data),
                "suggested_focus_areas": await self._suggest_focus_areas(clinical_data),
                "red_flags": await self._check_red_flags(clinical_data),
                "next_steps": await self._recommend_next_steps(clinical_data)
            }
            
            # Use AI for additional insights
            ai_insights = await self.ai_service.analyze_symptoms(clinical_data)
            analysis["ai_insights"] = ai_insights
            
            logger.info("Successfully analyzed clinical data")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing clinical data: {str(e)}")
            raise
    
    async def get_episode_summary(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive episode summary
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            Episode summary or None
        """
        try:
            episode = self.episode_repo.get_episode_with_related_data(episode_id)
            if not episode:
                return None
            
            summary = {
                "episode": EpisodeResponse.from_orm(episode).dict(),
                "duration_hours": self._calculate_episode_duration(episode),
                "diagnoses_count": len(episode.diagnoses) if episode.diagnoses else 0,
                "treatments_count": len(episode.treatments) if episode.treatments else 0,
                "status_history": await self._get_status_history(episode_id),
                "key_findings": await self._extract_key_findings(episode)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting episode summary {episode_id}: {str(e)}")
            raise
    
    async def extract_symptoms_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract structured symptoms from free text
        
        Args:
            text: Free text containing symptoms
            
        Returns:
            Extracted symptom data
        """
        try:
            # Use AI service for extraction
            extracted_data = await self.ai_service.extract_symptoms_from_text(text)
            
            # Post-process and validate extracted symptoms
            validated_symptoms = await self._validate_extracted_symptoms(extracted_data)
            
            return {
                "original_text": text,
                "extracted_symptoms": validated_symptoms,
                "confidence_score": extracted_data.get("confidence", 0.0),
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting symptoms from text: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _process_dynamic_questions(
        self, 
        ai_questions: List[Dict[str, Any]], 
        assessment_data: ClinicalAssessmentRequest
    ) -> List[Dict[str, Any]]:
        """Process and prioritize AI-generated questions"""
        processed = []
        
        for question in ai_questions:
            # Add context and validation
            processed_question = {
                **question,
                "id": f"q_{len(processed) + 1}",
                "category": self._categorize_question(question),
                "skip_conditions": self._get_skip_conditions(question, assessment_data),
                "validation_rules": self._get_validation_rules(question)
            }
            processed.append(processed_question)
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        processed.sort(key=lambda q: priority_order.get(q.get("priority", "medium"), 1))
        
        return processed
    
    async def _is_assessment_complete(self, assessment_data: ClinicalAssessmentRequest) -> bool:
        """Check if clinical assessment is complete enough"""
        required_elements = [
            assessment_data.chief_complaint,
            assessment_data.symptoms,
            assessment_data.patient_age,
            assessment_data.patient_gender
        ]
        
        # Basic completeness check
        has_basics = all(element for element in required_elements)
        
        # Minimum number of symptoms or answered questions
        has_sufficient_data = (
            len(assessment_data.symptoms or []) >= 3 or
            len(assessment_data.answered_questions or []) >= 5
        )
        
        return has_basics and has_sufficient_data
    
    async def _calculate_completeness(self, clinical_data: Dict[str, Any]) -> float:
        """Calculate completeness score for clinical data"""
        total_fields = 10  # Expected number of fields
        completed_fields = 0
        
        # Check required fields
        required_checks = [
            clinical_data.get("chief_complaint"),
            clinical_data.get("symptoms"),
            clinical_data.get("physical_exam"),
            clinical_data.get("vital_signs"),
            clinical_data.get("patient_history"),
            clinical_data.get("review_of_systems"),
            clinical_data.get("allergies"),
            clinical_data.get("medications"),
            clinical_data.get("social_history"),
            clinical_data.get("family_history")
        ]
        
        completed_fields = sum(1 for field in required_checks if field)
        return round(completed_fields / total_fields, 2)
    
    async def _identify_risk_factors(self, clinical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk factors from clinical data"""
        risk_factors = []
        
        # Age-related risks
        patient_age = clinical_data.get("patient_age", 0)
        if patient_age > 65:
            risk_factors.append({
                "factor": "Advanced age",
                "risk_level": "medium",
                "description": "Increased risk for various conditions"
            })
        
        # Symptom-based risks
        symptoms = clinical_data.get("symptoms", [])
        if any("chest pain" in str(symptom).lower() for symptom in symptoms):
            risk_factors.append({
                "factor": "Chest pain",
                "risk_level": "high",
                "description": "Requires cardiac evaluation"
            })
        
        return risk_factors
    
    async def _check_red_flags(self, clinical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for red flag symptoms requiring immediate attention"""
        red_flags = []
        symptoms = clinical_data.get("symptoms", [])
        
        # Define red flag symptoms
        critical_symptoms = [
            "severe chest pain",
            "difficulty breathing",
            "loss of consciousness",
            "severe headache",
            "sudden vision loss"
        ]
        
        for symptom in symptoms:
            for critical in critical_symptoms:
                if critical.lower() in str(symptom).lower():
                    red_flags.append({
                        "symptom": symptom,
                        "severity": "critical",
                        "action_required": "Immediate medical attention",
                        "timeframe": "Within 15 minutes"
                    })
        
        return red_flags
