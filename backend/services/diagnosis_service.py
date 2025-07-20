from typing import List, Optional, Dict, Any
from repositories.diagnosis_repository import DiagnosisRepository
from repositories.episode_repository import EpisodeRepository
from services.ai_service import AIService
from schemas.diagnosis import DiagnosisCreate, DiagnosisResponse, DifferentialDiagnosisResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DiagnosisService:
    """
    Service for AI-powered diagnosis generation and management
    """
    
    def __init__(
        self,
        diagnosis_repo: DiagnosisRepository,
        ai_service: AIService,
        episode_repo: Optional[EpisodeRepository] = None
    ):
        self.diagnosis_repo = diagnosis_repo
        self.ai_service = ai_service
        self.episode_repo = episode_repo
    
    async def generate_differential_diagnosis(
        self,
        episode_id: str,
        symptoms: List[str],
        physical_exam: Dict[str, Any],
        vital_signs: Dict[str, Any]
    ) -> DifferentialDiagnosisResponse:
        """
        Generate AI-powered differential diagnosis
        
        Args:
            episode_id: Episode identifier
            symptoms: List of patient symptoms
            physical_exam: Physical examination findings
            vital_signs: Vital signs data
            
        Returns:
            Differential diagnosis response
        """
        try:
            # Validate episode exists
            if self.episode_repo:
                episode = self.episode_repo.get(episode_id)
                if not episode:
                    raise ValueError(f"Episode {episode_id} not found")
            
            # Prepare clinical data for AI analysis
            clinical_data = {
                "symptoms": symptoms,
                "physical_exam": physical_exam,
                "vital_signs": vital_signs,
                "patient_history": await self._get_patient_history(episode_id)
            }
            
            # Get AI analysis
            ai_analysis = await self.ai_service.analyze_symptoms(clinical_data)
            
            # Create diagnosis record
            diagnosis_data = DiagnosisCreate(
                episode_id=episode_id,
                differential_diagnoses=ai_analysis["differential_diagnoses"],
                confidence_scores=ai_analysis["confidence_scores"],
                ai_analysis_data={
                    "analysis_id": ai_analysis["analysis_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "input_data": clinical_data,
                    "ai_recommendations": ai_analysis.get("recommendations", [])
                }
            )
            
            # Save diagnosis
            diagnosis = self.diagnosis_repo.create(diagnosis_data)
            
            # Format response
            response = DifferentialDiagnosisResponse(
                id=diagnosis.id,
                episode_id=episode_id,
                differential_diagnoses=ai_analysis["differential_diagnoses"],
                confidence_scores=ai_analysis["confidence_scores"],
                ai_analysis_id=ai_analysis["analysis_id"],
                recommendations=ai_analysis.get("recommendations", []),
                created_at=diagnosis.created_at,
                requires_followup=await self._assess_followup_needs(ai_analysis)
            )
            
            logger.info(f"Generated differential diagnosis for episode: {episode_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating differential diagnosis: {str(e)}")
            raise
    
    async def refine_diagnosis_with_tests(
        self,
        diagnosis_id: str,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Refine existing diagnosis based on test results
        
        Args:
            diagnosis_id: Diagnosis identifier
            test_results: New test results
            
        Returns:
            Refined diagnosis data
        """
        try:
            # Get original diagnosis
            original_diagnosis = self.diagnosis_repo.get(diagnosis_id)
            if not original_diagnosis:
                raise ValueError(f"Diagnosis {diagnosis_id} not found")
            
            # Prepare data for AI refinement
            original_data = {
                "differential_diagnoses": original_diagnosis.differential_diagnoses,
                "confidence_scores": original_diagnosis.confidence_scores,
                "original_analysis": original_diagnosis.ai_analysis_data
            }
            
            # Get AI refinement
            refined_analysis = await self.ai_service.refine_diagnosis_with_tests(
                original_data, test_results
            )
            
            # Update diagnosis record
            update_data = {
                "confidence_scores": refined_analysis.get("updated_confidence_scores"),
                "ai_analysis_data": {
                    **original_diagnosis.ai_analysis_data,
                    "refinement": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "test_results": test_results,
                        "refined_analysis": refined_analysis
                    }
                }
            }
            
            # Check if final diagnosis can be determined
            if refined_analysis.get("final_diagnosis"):
                update_data["final_diagnosis"] = refined_analysis["final_diagnosis"]
            
            updated_diagnosis = self.diagnosis_repo.update(original_diagnosis, update_data)
            
            logger.info(f"Refined diagnosis {diagnosis_id} with test results")
            return {
                "diagnosis_id": diagnosis_id,
                "refined_diagnoses": refined_analysis.get("refined_diagnoses", []),
                "updated_confidence": refined_analysis.get("updated_confidence_scores", []),
                "final_diagnosis": refined_analysis.get("final_diagnosis"),
                "test_correlations": refined_analysis.get("test_correlations", []),
                "updated_at": updated_diagnosis.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error refining diagnosis {diagnosis_id}: {str(e)}")
            raise
    
    async def get_diagnosis_explanation(self, diagnosis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed explanation of AI diagnosis reasoning
        
        Args:
            diagnosis_id: Diagnosis identifier
            
        Returns:
            Diagnosis explanation or None
        """
        try:
            diagnosis = self.diagnosis_repo.get(diagnosis_id)
            if not diagnosis:
                return None
            
            # Extract AI reasoning from stored data
            ai_data = diagnosis.ai_analysis_data or {}
            
            explanation = {
                "diagnosis_id": diagnosis_id,
                "differential_diagnoses": diagnosis.differential_diagnoses,
                "confidence_scores": diagnosis.confidence_scores,
                "ai_reasoning": {
                    "analysis_method": "Machine Learning Ensemble",
                    "key_factors": await self._extract_key_factors(diagnosis),
                    "evidence_summary": await self._summarize_evidence(diagnosis),
                    "confidence_explanation": await self._explain_confidence(diagnosis),
                    "alternative_considerations": await self._get_alternatives(diagnosis)
                },
                "clinical_recommendations": ai_data.get("ai_recommendations", []),
                "follow_up_needed": await self._assess_followup_needs(ai_data)
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error getting diagnosis explanation {diagnosis_id}: {str(e)}")
            raise
    
    async def validate_diagnosis_data(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate diagnosis data for completeness and consistency
        
        Args:
            validation_data: Data to validate
            
        Returns:
            Validation results
        """
        try:
            validation_result = {
                "is_valid": True,
                "completeness_score": 0.0,
                "missing_elements": [],
                "recommendations": [],
                "data_quality_issues": []
            }
            
            # Check required elements
            required_elements = [
                "symptoms", "physical_exam", "vital_signs", 
                "patient_history", "chief_complaint"
            ]
            
            missing = []
            for element in required_elements:
                if not validation_data.get(element):
                    missing.append(element)
            
            validation_result["missing_elements"] = missing
            validation_result["completeness_score"] = 1.0 - (len(missing) / len(required_elements))
            
            # Data quality checks
            if validation_data.get("symptoms"):
                if len(validation_data["symptoms"]) < 2:
                    validation_result["data_quality_issues"].append(
                        "Insufficient symptom detail - consider gathering more specific symptoms"
                    )
            
            # Vital signs validation
            vital_signs = validation_data.get("vital_signs", {})
            if vital_signs:
                issues = await self._validate_vital_signs(vital_signs)
                validation_result["data_quality_issues"].extend(issues)
            
            # Overall validity
            validation_result["is_valid"] = (
                validation_result["completeness_score"] >= 0.7 and
                len(validation_result["data_quality_issues"]) == 0
            )
            
            # Recommendations
            if missing:
                validation_result["recommendations"].append(
                    f"Collect missing data: {', '.join(missing)}"
                )
            
            if validation_result["completeness_score"] < 0.5:
                validation_result["recommendations"].append(
                    "Data insufficient for reliable AI diagnosis - consider manual assessment"
                )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating diagnosis data: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _get_patient_history(self, episode_id: str) -> Dict[str, Any]:
        """Get patient history for the episode"""
        if not self.episode_repo:
            return {}
        
        try:
            episode = self.episode_repo.get_episode_with_related_data(episode_id)
            if episode and episode.patient:
                return episode.patient.medical_history or {}
            return {}
        except Exception:
            return {}
    
    async def _assess_followup_needs(self, ai_analysis: Dict[str, Any]) -> bool:
        """Assess if diagnosis requires follow-up"""
        # Check confidence scores
        confidence_scores = ai_analysis.get("confidence_scores", [])
        if confidence_scores:
            max_confidence = max(confidence_scores)
            if max_confidence < 0.7:  # Low confidence threshold
                return True
        
        # Check for red flags in recommendations
        recommendations = ai_analysis.get("recommendations", [])
        urgent_keywords = ["immediate", "urgent", "emergency", "stat"]
        
        for rec in recommendations:
            if any(keyword in str(rec).lower() for keyword in urgent_keywords):
                return True
        
        return False
    
    async def _extract_key_factors(self, diagnosis) -> List[str]:
        """Extract key factors that influenced the diagnosis"""
        key_factors = []
        
        # Extract from differential diagnoses
        for diag in diagnosis.differential_diagnoses or []:
            evidence = diag.get("evidence", [])
            key_factors.extend(evidence)
        
        # Remove duplicates and return top factors
        unique_factors = list(set(key_factors))
        return unique_factors[:5]  # Top 5 factors
    
    async def _validate_vital_signs(self, vital_signs: Dict[str, Any]) -> List[str]:
        """Validate vital signs for abnormal values"""
        issues = []
        
        # Blood pressure validation
        if "systolic_bp" in vital_signs and "diastolic_bp" in vital_signs:
            systolic = vital_signs["systolic_bp"]
            diastolic = vital_signs["diastolic_bp"]
            
            if systolic > 180 or diastolic > 120:
                issues.append("Critically high blood pressure detected")
            elif systolic < 90 or diastolic < 60:
                issues.append("Low blood pressure detected")
        
        # Heart rate validation
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            if hr > 120:
                issues.append("Elevated heart rate (tachycardia)")
            elif hr < 50:
                issues.append("Low heart rate (bradycardia)")
        
        # Temperature validation
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"]
            # Assuming Fahrenheit
            if temp > 101.3:
                issues.append("Fever detected")
            elif temp < 95.0:
                issues.append("Hypothermia detected")
        
        return issues
