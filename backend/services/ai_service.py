from typing import List, Dict, Any, Optional
import httpx
import logging
import asyncio
from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class AIService:
    """
    Service for AI model integration and medical analysis
    """
    
    def __init__(self):
        self.api_url = settings.ai_service_url
        self.api_key = settings.ai_service_api_key
        self.timeout = settings.ai_service_timeout
        self.max_retries = settings.ai_service_max_retries
    
    async def analyze_symptoms(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze symptoms and generate differential diagnosis
        
        Args:
            clinical_data: Clinical assessment data
            
        Returns:
            AI analysis results
        """
        try:
            # Prepare data for AI analysis
            analysis_request = {
                "symptoms": clinical_data.get("symptoms", []),
                "physical_exam": clinical_data.get("physical_exam", {}),
                "vital_signs": clinical_data.get("vital_signs", {}),
                "patient_history": clinical_data.get("patient_history", {}),
                "chief_complaint": clinical_data.get("chief_complaint", "")
            }
            
            # Call AI service
            if self.api_url:
                result = await self._call_ai_service("/analyze/symptoms", analysis_request)
            else:
                # Mock AI response for development
                result = await self._generate_mock_diagnosis(analysis_request)
            
            # Process and validate AI response
            processed_result = await self._process_ai_diagnosis(result)
            
            logger.info("Successfully analyzed symptoms with AI")
            return processed_result
            
        except Exception as e:
            logger.error(f"Error in AI symptom analysis: {str(e)}")
            # Return fallback response
            return await self._generate_fallback_diagnosis(clinical_data)
    
    async def generate_dynamic_questions(self, assessment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate dynamic follow-up questions based on current data
        
        Args:
            assessment_data: Current clinical assessment data
            
        Returns:
            List of dynamic questions
        """
        try:
            request_data = {
                "chief_complaint": assessment_data.get("chief_complaint", ""),
                "existing_symptoms": assessment_data.get("symptoms", []),
                "patient_demographics": assessment_data.get("patient_demographics", {}),
                "context": "follow_up_questions"
            }
            
            if self.api_url:
                result = await self._call_ai_service("/generate/questions", request_data)
            else:
                result = await self._generate_mock_questions(request_data)
            
            # Validate and format questions
            questions = await self._process_ai_questions(result)
            
            logger.info(f"Generated {len(questions)} dynamic questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating dynamic questions: {str(e)}")
            return await self._generate_fallback_questions(assessment_data)
    
    async def refine_diagnosis_with_tests(
        self, 
        original_diagnosis: Dict[str, Any], 
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Refine diagnosis based on test results
        
        Args:
            original_diagnosis: Original AI diagnosis
            test_results: New test results
            
        Returns:
            Refined diagnosis
        """
        try:
            refinement_request = {
                "original_diagnosis": original_diagnosis,
                "test_results": test_results,
                "context": "diagnosis_refinement"
            }
            
            if self.api_url:
                result = await self._call_ai_service("/refine/diagnosis", refinement_request)
            else:
                result = await self._generate_mock_refinement(refinement_request)
            
            refined_diagnosis = await self._process_refined_diagnosis(result)
            
            logger.info("Successfully refined diagnosis with test results")
            return refined_diagnosis
            
        except Exception as e:
            logger.error(f"Error refining diagnosis: {str(e)}")
            return original_diagnosis  # Return original if refinement fails
    
    async def extract_symptoms_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract structured symptoms from free text using NLP
        
        Args:
            text: Free text containing symptom information
            
        Returns:
            Structured symptom data
        """
        try:
            extraction_request = {
                "text": text,
                "context": "symptom_extraction",
                "output_format": "structured"
            }
            
            if self.api_url:
                result = await self._call_ai_service("/extract/symptoms", extraction_request)
            else:
                result = await self._generate_mock_extraction(text)
            
            extracted_data = await self._process_extracted_symptoms(result)
            
            logger.info("Successfully extracted symptoms from text")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting symptoms from text: {str(e)}")
            return {"symptoms": [], "confidence": 0.0, "error": str(e)}
    
    async def generate_treatment_recommendations(
        self, 
        diagnosis_data: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate treatment recommendations based on diagnosis
        
        Args:
            diagnosis_data: Confirmed diagnosis information
            patient_data: Patient demographics and medical history
            
        Returns:
            Treatment recommendations
        """
        try:
            treatment_request = {
                "diagnosis": diagnosis_data,
                "patient": patient_data,
                "context": "treatment_planning"
            }
            
            if self.api_url:
                result = await self._call_ai_service("/generate/treatment", treatment_request)
            else:
                result = await self._generate_mock_treatment(treatment_request)
            
            treatment_plan = await self._process_treatment_recommendations(result)
            
            logger.info("Successfully generated treatment recommendations")
            return treatment_plan
            
        except Exception as e:
            logger.error(f"Error generating treatment recommendations: {str(e)}")
            return await self._generate_fallback_treatment(diagnosis_data)
    
    # Private helper methods
    
    async def _call_ai_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP call to AI service with retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    headers = {}
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"
                    
                    response = await client.post(
                        f"{self.api_url}{endpoint}",
                        json=data,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response.json()
                    
            except Exception as e:
                logger.warning(f"AI service call attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _generate_mock_diagnosis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock AI diagnosis for development"""
        symptoms = request_data.get("symptoms", [])
        
        # Simple mock logic based on symptoms
        mock_diagnoses = []
        
        if any("fever" in str(symptom).lower() for symptom in symptoms):
            mock_diagnoses.append({
                "condition": "Viral Upper Respiratory Infection",
                "probability": 0.75,
                "confidence": 0.8,
                "evidence": ["fever", "respiratory symptoms"],
                "icd10_code": "J06.9"
            })
        
        if any("headache" in str(symptom).lower() for symptom in symptoms):
            mock_diagnoses.append({
                "condition": "Tension Headache",
                "probability": 0.65,
                "confidence": 0.7,
                "evidence": ["headache"],
                "icd10_code": "G44.2"
            })
        
        # Default diagnosis if no specific symptoms
        if not mock_diagnoses:
            mock_diagnoses.append({
                "condition": "Symptom requiring further evaluation",
                "probability": 0.5,
                "confidence": 0.6,
                "evidence": symptoms,
                "icd10_code": "R69"
            })
        
        return {
            "differential_diagnoses": mock_diagnoses,
            "analysis_id": "mock_analysis_001",
            "confidence_scores": [d["confidence"] for d in mock_diagnoses],
            "recommendations": ["Consider vital signs", "Review patient history"]
        }
    
    async def _generate_mock_questions(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock dynamic questions"""
        chief_complaint = request_data.get("chief_complaint", "").lower()
        
        base_questions = [
            {
                "question": "How long have you been experiencing these symptoms?",
                "type": "duration",
                "options": ["< 24 hours", "1-3 days", "4-7 days", "> 1 week"],
                "priority": "high"
            },
            {
                "question": "On a scale of 1-10, how would you rate your pain/discomfort?",
                "type": "scale",
                "range": {"min": 1, "max": 10},
                "priority": "medium"
            }
        ]
        
        # Add specific questions based on chief complaint
        if "headache" in chief_complaint:
            base_questions.append({
                "question": "Where is the headache located?",
                "type": "multiple_choice",
                "options": ["Front", "Back", "Sides", "All over"],
                "priority": "high"
            })
        
        return base_questions
    
    async def _process_ai_diagnosis(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate AI diagnosis results"""
        # Ensure all required fields are present
        processed = {
            "differential_diagnoses": ai_result.get("differential_diagnoses", []),
            "confidence_scores": ai_result.get("confidence_scores", []),
            "analysis_id": ai_result.get("analysis_id", "unknown"),
            "recommendations": ai_result.get("recommendations", [])
        }
        
        # Validate confidence scores
        for diagnosis in processed["differential_diagnoses"]:
            if "confidence" not in diagnosis:
                diagnosis["confidence"] = 0.5
            elif diagnosis["confidence"] > 1.0:
                diagnosis["confidence"] = diagnosis["confidence"] / 100  # Convert percentage
        
        return processed
    
    async def _generate_fallback_diagnosis(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback diagnosis when AI service fails"""
        return {
            "differential_diagnoses": [{
                "condition": "Requires clinical evaluation",
                "probability": 0.5,
                "confidence": 0.3,
                "evidence": ["AI service unavailable"],
                "icd10_code": "Z00.00"
            }],
            "confidence_scores": [0.3],
            "analysis_id": "fallback_001",
            "recommendations": ["Manual clinical assessment recommended"],
            "fallback": True
        }
    
    async def _generate_fallback_questions(self, assessment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI service fails"""
        return [
            {
                "question": "Please describe your symptoms in detail",
                "type": "text",
                "priority": "high"
            },
            {
                "question": "When did these symptoms start?",
                "type": "date",
                "priority": "high"
            },
            {
                "question": "Have you taken any medications for this?",
                "type": "yes_no",
                "priority": "medium"
            }
        ]
