"""
AI Service for DiagnoAssist Backend

This service provides high-level AI functionality including voice processing,
clinical decision support, and intelligent documentation assistance.
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.core.ai_client import get_ai_client, AIRequest, AITaskType, AIModelType
from app.models.ai_models import (
    VoiceProcessingRequest, VoiceProcessingResult, VoiceProcessingStatus,
    ClinicalInsights, DiagnosisSuggestion, TreatmentRecommendation, RiskAssessment,
    ChatRequest, ChatResponse, ChatHistory, ChatMessage,
    DocumentationCompletionRequest, DocumentationCompletionResponse,
    DocumentationSuggestion, ConfidenceLevel, SOAPSection, DiagnosisType
)
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.core.exceptions import AIServiceException, ValidationException
# Simplified for core functionality - removed enterprise monitoring/performance/resilience systems

logger = logging.getLogger(__name__)


class AIService:
    """Main AI service for clinical decision support"""
    
    def __init__(self):
        self._chat_histories: Dict[str, ChatHistory] = {}
        self._processing_cache = {}
        
    async def process_voice_to_soap(
        self, 
        request: VoiceProcessingRequest,
        patient: Optional[PatientModel] = None,
        encounter: Optional[EncounterModel] = None
    ) -> VoiceProcessingResult:
        """
        Process voice recording and extract SOAP documentation
        
        Args:
            request: Voice processing request with audio data
            patient: Patient context for better extraction
            encounter: Encounter context for better extraction
            
        Returns:
            Processed SOAP data extracted from voice
        """
        try:
            logger.info(f"Starting voice processing for encounter {request.encounter_id}")
            
            # Build context for AI
            context = await self._build_context(patient, encounter, {
                "target_section": request.target_section.value if request.target_section else None,
                "encounter_id": request.encounter_id
            })
            
            # Create specialized prompt for voice-to-SOAP extraction
            prompt = self._create_voice_to_soap_prompt(request.target_section)
            
            # Create AI request
            ai_request = AIRequest(
                task_type=AITaskType.VOICE_TO_SOAP,
                prompt=prompt,
                context=context,
                audio_data=request.audio_data,
                model=AIModelType.GEMINI_PRO,
                temperature=0.1  # Low temperature for accuracy
            )
            
            # Process with AI
            ai_client = await get_ai_client().get_client()
            ai_response = await ai_client.generate_response(ai_request)
            
            # Parse SOAP extraction from response
            soap_extraction = await self._parse_soap_extraction(ai_response.content, request.target_section)
            
            # Determine confidence level
            confidence = self._determine_confidence(ai_response, soap_extraction)
            
            result = VoiceProcessingResult(
                transcription=ai_response.content.split("SOAP_EXTRACTION:")[0].strip() if "SOAP_EXTRACTION:" in ai_response.content else ai_response.content,
                soap_extraction=soap_extraction,
                confidence=confidence,
                processing_time_ms=0,  # Simplified - removed complex monitoring
                metadata={
                    "language": request.language,
                    "target_section": request.target_section.value if request.target_section else None,
                    "patient_id": patient.id if patient else None,
                    "model_used": ai_request.model.value
                }
            )
            
            # Log successful processing
            logger.debug(f"Voice processing success: {request.target_section.value if request.target_section else 'all'}")
            
            logger.info(f"Voice processing completed successfully for encounter {request.encounter_id}")
            
            return result
            
        except Exception as e:
            # Log processing error
            logger.error(f"Voice processing error: {type(e).__name__}")
            
            logger.error(f"Voice processing failed for encounter {request.encounter_id}: {e}")
            raise AIServiceException(f"Voice processing failed: {str(e)}", "voice_processing")
    
    async def generate_clinical_insights(
        self,
        patient: PatientModel,
        encounter: EncounterModel,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ClinicalInsights:
        """
        Generate comprehensive clinical insights for patient encounter
        
        Args:
            patient: Patient information
            encounter: Encounter information
            additional_context: Additional context for analysis
            
        Returns:
            Clinical insights including diagnoses, treatments, and risk assessments
        """
        try:
            logger.info(f"Generating clinical insights for patient {patient.id}, encounter {encounter.id}")
            
            # Build comprehensive context
            context = await self._build_context(patient, encounter, additional_context or {})
            
            # Create clinical insights prompt
            prompt = self._create_clinical_insights_prompt()
            
            # Create AI request
            ai_request = AIRequest(
                task_type=AITaskType.CLINICAL_INSIGHTS,
                prompt=prompt,
                context=context,
                model=AIModelType.GEMINI_PRO,
                temperature=0.2,  # Slightly higher for creative insights
                max_tokens=3000   # More tokens for comprehensive analysis
            )
            
            # Process with AI
            ai_client = await get_ai_client().get_client()
            ai_response = await ai_client.generate_response(ai_request)
            
            # Parse clinical insights
            insights = await self._parse_clinical_insights(ai_response.content)
            
            # Log successful analysis
            logger.debug(f"Clinical insights generated for patient age group: {self._get_age_group(patient)}")
            
            logger.info(f"Clinical insights generated successfully for patient {patient.id}")
            
            return insights
            
        except Exception as e:
            # Log insight generation error
            logger.error(f"Clinical insights error: {type(e).__name__}")
            
            logger.error(f"Clinical insights generation failed: {e}")
            raise AIServiceException(f"Clinical insights generation failed: {str(e)}", "clinical_insights")
    
    async def chat_with_ai(
        self,
        request: ChatRequest,
        patient: Optional[PatientModel] = None,
        encounter: Optional[EncounterModel] = None
    ) -> ChatResponse:
        """
        Chat with AI assistant for clinical questions
        
        Args:
            request: Chat request with message and context
            patient: Optional patient context
            encounter: Optional encounter context
            
        Returns:
            AI response with clinical information
        """
        try:
            # Get or create conversation
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            if conversation_id not in self._chat_histories:
                self._chat_histories[conversation_id] = ChatHistory(
                    conversation_id=conversation_id,
                    encounter_id=request.encounter_id
                )
            
            chat_history = self._chat_histories[conversation_id]
            
            # Add user message to history
            user_message = ChatMessage(
                role="user",
                content=request.message,
                metadata={"encounter_id": request.encounter_id}
            )
            chat_history.messages.append(user_message)
            
            # Build context
            context = await self._build_context(patient, encounter, request.patient_context or {})
            
            # Create chat prompt with history
            prompt = self._create_chat_prompt(request.message, chat_history if request.include_history else None)
            
            # Create AI request
            ai_request = AIRequest(
                task_type=AITaskType.CHAT_RESPONSE,
                prompt=prompt,
                context=context,
                model=AIModelType.GEMINI_PRO,
                temperature=0.3  # Higher temperature for conversational responses
            )
            
            # Process with AI
            ai_client = await get_ai_client().get_client()
            ai_response = await ai_client.generate_response(ai_request)
            
            # Add AI response to history
            ai_message = ChatMessage(
                role="assistant",
                content=ai_response.content,
                metadata={"model": ai_request.model.value}
            )
            chat_history.messages.append(ai_message)
            chat_history.updated_at = datetime.utcnow()
            
            # Parse response for suggestions
            suggestions = self._extract_suggestions(ai_response.content)
            
            response = ChatResponse(
                message=ai_response.content,
                conversation_id=conversation_id,
                confidence=ConfidenceLevel.HIGH,  # Default for chat
                suggestions=suggestions,
                metadata={
                    "model_used": ai_request.model.value,
                    "message_count": len(chat_history.messages)
                }
            )
            
            # Log chat interaction
            logger.debug(f"AI chat interaction - has patient context: {patient is not None}")
            
            logger.info(f"AI chat response generated for conversation {conversation_id}")
            
            return response
            
        except Exception as e:
            # Log chat error
            logger.error(f"AI chat error: {type(e).__name__}")
            
            logger.error(f"AI chat failed: {e}")
            raise AIServiceException(f"AI chat failed: {str(e)}", "ai_chat")
    
    async def complete_documentation(
        self,
        request: DocumentationCompletionRequest,
        patient: Optional[PatientModel] = None
    ) -> DocumentationCompletionResponse:
        """
        AI-powered documentation completion and suggestions
        
        Args:
            request: Documentation completion request
            patient: Patient context
            
        Returns:
            Documentation suggestions and completions
        """
        try:
            logger.info(f"Starting documentation completion for encounter {request.encounter_id}")
            
            # Build context
            context = await self._build_context(patient, None, {
                "current_content": request.current_content,
                "target_sections": [s.value for s in request.target_sections] if request.target_sections else None
            })
            
            # Create documentation completion prompt
            prompt = self._create_documentation_prompt(request.current_content, request.target_sections)
            
            # Create AI request
            ai_request = AIRequest(
                task_type=AITaskType.DOCUMENTATION_COMPLETION,
                prompt=prompt,
                context=context,
                model=AIModelType.GEMINI_PRO,
                temperature=0.1  # Low temperature for factual completion
            )
            
            # Process with AI
            ai_client = await get_ai_client().get_client()
            ai_response = await ai_client.generate_response(ai_request)
            
            # Parse documentation suggestions
            suggestions, completed_sections = await self._parse_documentation_response(ai_response.content)
            
            # Calculate quality score
            quality_score = self._calculate_documentation_quality(request.current_content, completed_sections)
            
            # Identify missing elements
            missing_elements = self._identify_missing_elements(request.current_content, completed_sections)
            
            response = DocumentationCompletionResponse(
                suggestions=suggestions,
                completed_sections=completed_sections,
                quality_score=quality_score,
                missing_elements=missing_elements
            )
            
            # Log completion
            logger.debug(f"Documentation completion - sections completed: {len(completed_sections)}")
            
            logger.info(f"Documentation completion generated for encounter {request.encounter_id}")
            
            return response
            
        except Exception as e:
            # Log documentation error
            logger.error(f"Documentation completion error: {type(e).__name__}")
            
            logger.error(f"Documentation completion failed: {e}")
            raise AIServiceException(f"Documentation completion failed: {str(e)}", "documentation_completion")
    
    # Helper Methods
    
    async def _build_context(
        self,
        patient: Optional[PatientModel],
        encounter: Optional[EncounterModel],
        additional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI requests"""
        context = additional_context.copy()
        
        if patient:
            context["patient"] = patient
        
        if encounter:
            context["encounter"] = encounter
        
        return context
    
    def _create_voice_to_soap_prompt(self, target_section: Optional[SOAPSection]) -> str:
        """Create prompt for voice-to-SOAP processing"""
        base_prompt = """
You are a medical AI assistant specialized in converting clinical speech to structured SOAP documentation.

Please transcribe the audio and extract relevant clinical information into appropriate SOAP sections.

Guidelines:
- Maintain medical accuracy and terminology
- Structure information appropriately
- Include only information mentioned in the audio
- Use standard medical abbreviations where appropriate
- Preserve clinical context and patient safety information

"""
        
        if target_section:
            section_guidance = {
                SOAPSection.SUBJECTIVE: "Focus on patient-reported symptoms, history, and concerns.",
                SOAPSection.OBJECTIVE: "Focus on physical examination findings, vital signs, and observations.",
                SOAPSection.ASSESSMENT: "Focus on clinical impressions, diagnoses, and analysis.",
                SOAPSection.PLAN: "Focus on treatment plans, medications, and follow-up instructions."
            }
            
            base_prompt += f"\nSpecial focus on {target_section.value.upper()} section: {section_guidance.get(target_section, '')}\n"
        
        base_prompt += """
Format your response as:
TRANSCRIPTION: [Raw transcription of the audio]

SOAP_EXTRACTION: [JSON format with extracted SOAP data]
"""
        
        return base_prompt
    
    def _create_clinical_insights_prompt(self) -> str:
        """Create prompt for clinical insights generation"""
        return """
You are an experienced clinical AI assistant. Based on the patient information and encounter data provided, generate comprehensive clinical insights.

Please provide:

1. DIFFERENTIAL DIAGNOSES:
   - List potential diagnoses with probability scores
   - Include ICD-10 codes where applicable
   - Provide supporting evidence for each diagnosis

2. TREATMENT RECOMMENDATIONS:
   - Suggest appropriate treatments and interventions
   - Include medication recommendations with dosages
   - Specify monitoring requirements

3. RISK ASSESSMENTS:
   - Identify clinical risk factors
   - Calculate risk scores where applicable
   - Provide risk mitigation strategies

4. RED FLAGS:
   - Identify any critical findings requiring immediate attention
   - Flag potential emergency situations

5. FOLLOW-UP RECOMMENDATIONS:
   - Suggest appropriate follow-up care
   - Recommend additional testing or consultations

Format your response as structured JSON with the above categories.
Ensure all recommendations follow evidence-based medical guidelines.
"""
    
    def _create_chat_prompt(self, message: str, chat_history: Optional[ChatHistory]) -> str:
        """Create prompt for AI chat"""
        prompt = """
You are a knowledgeable medical AI assistant helping healthcare providers with clinical questions.

Guidelines:
- Provide accurate, evidence-based medical information
- Suggest appropriate clinical actions when relevant
- Maintain professional medical tone
- Reference guidelines and best practices
- Always emphasize the importance of clinical judgment

"""
        
        if chat_history and len(chat_history.messages) > 1:
            prompt += "\nConversation history:\n"
            for msg in chat_history.messages[-6:]:  # Include last 6 messages for context
                prompt += f"{msg.role.title()}: {msg.content}\n"
            prompt += "\n"
        
        prompt += f"Current question: {message}\n\nPlease provide a helpful clinical response:"
        
        return prompt
    
    def _create_documentation_prompt(
        self,
        current_content: Dict[str, Any],
        target_sections: Optional[List[SOAPSection]]
    ) -> str:
        """Create prompt for documentation completion"""
        prompt = f"""
You are a medical documentation AI assistant. Help complete the SOAP documentation based on the current content.

Current documentation:
{json.dumps(current_content, indent=2)}

"""
        
        if target_sections:
            sections_str = ", ".join([s.value for s in target_sections])
            prompt += f"Focus on completing these sections: {sections_str}\n\n"
        
        prompt += """
Please provide:
1. Suggestions for improving existing content
2. Completed sections based on available information
3. Identification of missing critical elements

Format response as JSON with suggestions, completed_sections, and missing_elements.
Ensure all content follows medical documentation standards.
"""
        
        return prompt
    
    async def _parse_soap_extraction(
        self,
        ai_response: str,
        target_section: Optional[SOAPSection]
    ) -> Dict[str, Any]:
        """Parse SOAP data from AI response"""
        try:
            # Look for JSON in the response
            if "SOAP_EXTRACTION:" in ai_response:
                json_part = ai_response.split("SOAP_EXTRACTION:")[1].strip()
            else:
                json_part = ai_response
            
            # Try to parse JSON
            try:
                soap_data = json.loads(json_part)
                return soap_data
            except json.JSONDecodeError:
                # Fallback: extract key information manually
                return self._extract_soap_manually(ai_response, target_section)
                
        except Exception as e:
            logger.warning(f"SOAP extraction parsing failed: {e}")
            return {"raw_content": ai_response}
    
    def _extract_soap_manually(self, content: str, target_section: Optional[SOAPSection]) -> Dict[str, Any]:
        """Manually extract SOAP information from unstructured content"""
        soap_data = {}
        
        # Simple keyword-based extraction
        content_lower = content.lower()
        
        if not target_section or target_section == SOAPSection.SUBJECTIVE:
            if "chief complaint" in content_lower or "cc:" in content_lower:
                soap_data["chief_complaint"] = content[:200]  # First 200 chars as fallback
        
        if not target_section or target_section == SOAPSection.OBJECTIVE:
            if "vital signs" in content_lower or "bp:" in content_lower or "hr:" in content_lower:
                soap_data["vital_signs"] = content[:200]
        
        # Add raw content for manual review
        soap_data["raw_content"] = content
        
        return soap_data
    
    async def _parse_clinical_insights(self, ai_response: str) -> ClinicalInsights:
        """Parse clinical insights from AI response"""
        try:
            # Try to parse as JSON first
            try:
                insights_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to manual parsing
                insights_data = self._parse_insights_manually(ai_response)
            
            # Convert to structured data
            diagnosis_suggestions = []
            treatment_recommendations = []
            risk_assessments = []
            red_flags = []
            follow_up_recommendations = []
            
            # Parse diagnoses
            if "differential_diagnoses" in insights_data or "diagnoses" in insights_data:
                diagnoses = insights_data.get("differential_diagnoses", insights_data.get("diagnoses", []))
                for diag in diagnoses:
                    if isinstance(diag, str):
                        diagnosis_suggestions.append(DiagnosisSuggestion(
                            diagnosis=diag,
                            confidence=ConfidenceLevel.MEDIUM,
                            probability=0.5,
                            type=DiagnosisType.DIFFERENTIAL
                        ))
                    elif isinstance(diag, dict):
                        diagnosis_suggestions.append(DiagnosisSuggestion(
                            diagnosis=diag.get("diagnosis", "Unknown"),
                            icd10_code=diag.get("icd10_code"),
                            confidence=ConfidenceLevel(diag.get("confidence", "medium")),
                            probability=diag.get("probability", 0.5),
                            evidence=diag.get("evidence", []),
                            type=DiagnosisType(diag.get("type", "differential"))
                        ))
            
            # Parse treatments
            if "treatment_recommendations" in insights_data or "treatments" in insights_data:
                treatments = insights_data.get("treatment_recommendations", insights_data.get("treatments", []))
                for treatment in treatments:
                    if isinstance(treatment, str):
                        treatment_recommendations.append(TreatmentRecommendation(
                            treatment=treatment,
                            category="general",
                            priority="routine",
                            rationale="AI recommendation"
                        ))
                    elif isinstance(treatment, dict):
                        treatment_recommendations.append(TreatmentRecommendation(
                            treatment=treatment.get("treatment", "Unknown"),
                            category=treatment.get("category", "general"),
                            priority=treatment.get("priority", "routine"),
                            rationale=treatment.get("rationale", "AI recommendation"),
                            contraindications=treatment.get("contraindications", []),
                            monitoring=treatment.get("monitoring")
                        ))
            
            # Parse risk assessments
            if "risk_assessments" in insights_data or "risks" in insights_data:
                risks = insights_data.get("risk_assessments", insights_data.get("risks", []))
                for risk in risks:
                    if isinstance(risk, str):
                        risk_assessments.append(RiskAssessment(
                            risk_factor=risk,
                            risk_level="moderate"
                        ))
                    elif isinstance(risk, dict):
                        risk_assessments.append(RiskAssessment(
                            risk_factor=risk.get("risk_factor", "Unknown"),
                            risk_level=risk.get("risk_level", "moderate"),
                            score=risk.get("score"),
                            recommendations=risk.get("recommendations", []),
                            time_frame=risk.get("time_frame")
                        ))
            
            # Parse red flags
            if "red_flags" in insights_data:
                red_flags = insights_data["red_flags"]
                if isinstance(red_flags, str):
                    red_flags = [red_flags]
            
            # Parse follow-up
            if "follow_up_recommendations" in insights_data or "follow_up" in insights_data:
                follow_up = insights_data.get("follow_up_recommendations", insights_data.get("follow_up", []))
                if isinstance(follow_up, str):
                    follow_up_recommendations = [follow_up]
                else:
                    follow_up_recommendations = follow_up
            
            return ClinicalInsights(
                diagnosis_suggestions=diagnosis_suggestions,
                treatment_recommendations=treatment_recommendations,
                risk_assessments=risk_assessments,
                red_flags=red_flags,
                follow_up_recommendations=follow_up_recommendations,
                confidence=ConfidenceLevel.HIGH
            )
            
        except Exception as e:
            logger.warning(f"Clinical insights parsing failed: {e}")
            return ClinicalInsights(
                confidence=ConfidenceLevel.LOW,
                red_flags=[f"Parsing error: {str(e)}"]
            )
    
    def _parse_insights_manually(self, content: str) -> Dict[str, Any]:
        """Manually parse insights from unstructured content"""
        insights = {}
        
        # Simple pattern matching for common medical terms
        content_lower = content.lower()
        
        if "diagnosis" in content_lower or "differential" in content_lower:
            insights["diagnoses"] = [content[:100]]  # Simplified extraction
        
        if "treatment" in content_lower or "medication" in content_lower:
            insights["treatments"] = [content[:100]]
        
        if "risk" in content_lower or "warning" in content_lower:
            insights["risks"] = [content[:100]]
        
        return insights
    
    async def _parse_documentation_response(self, ai_response: str) -> tuple[List[DocumentationSuggestion], Dict[str, Any]]:
        """Parse documentation completion response"""
        try:
            response_data = json.loads(ai_response)
            
            suggestions = []
            if "suggestions" in response_data:
                for sugg in response_data["suggestions"]:
                    suggestions.append(DocumentationSuggestion(
                        section=SOAPSection(sugg.get("section", "subjective")),
                        field=sugg.get("field", "general"),
                        suggestion=sugg.get("suggestion", ""),
                        confidence=ConfidenceLevel(sugg.get("confidence", "medium")),
                        rationale=sugg.get("rationale")
                    ))
            
            completed_sections = response_data.get("completed_sections", {})
            
            return suggestions, completed_sections
            
        except Exception as e:
            logger.warning(f"Documentation response parsing failed: {e}")
            return [], {}
    
    def _determine_confidence(self, ai_response, soap_extraction: Dict[str, Any]) -> ConfidenceLevel:
        """Determine confidence level for voice processing"""
        # Simple heuristic based on content completeness
        if not soap_extraction or "raw_content" in soap_extraction:
            return ConfidenceLevel.LOW
        
        field_count = len([v for v in soap_extraction.values() if v and v.strip()])
        
        if field_count >= 3:
            return ConfidenceLevel.HIGH
        elif field_count >= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _extract_suggestions(self, content: str) -> List[str]:
        """Extract actionable suggestions from AI response"""
        suggestions = []
        
        # Look for common suggestion patterns
        suggestion_patterns = [
            "recommend", "suggest", "consider", "should", "advise",
            "order", "prescribe", "follow up", "monitor", "check"
        ]
        
        sentences = content.split('. ')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(pattern in sentence_lower for pattern in suggestion_patterns):
                suggestions.append(sentence.strip())
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _calculate_documentation_quality(
        self,
        current_content: Dict[str, Any],
        completed_sections: Dict[str, Any]
    ) -> float:
        """Calculate documentation quality score"""
        # Simple scoring based on completeness
        total_fields = 10  # Expected number of fields in complete documentation
        filled_fields = 0
        
        # Count filled fields in current content
        for section in current_content.values():
            if isinstance(section, dict):
                filled_fields += len([v for v in section.values() if v and str(v).strip()])
            elif section and str(section).strip():
                filled_fields += 1
        
        # Count additional fields from completion
        for section in completed_sections.values():
            if isinstance(section, dict):
                filled_fields += len([v for v in section.values() if v and str(v).strip()])
            elif section and str(section).strip():
                filled_fields += 1
        
        return min(filled_fields / total_fields, 1.0)
    
    def _identify_missing_elements(
        self,
        current_content: Dict[str, Any],
        completed_sections: Dict[str, Any]
    ) -> List[str]:
        """Identify missing critical documentation elements"""
        missing = []
        
        # Define critical elements
        critical_elements = {
            "subjective": ["chief_complaint", "history_present_illness"],
            "objective": ["vital_signs", "physical_examination"],
            "assessment": ["primary_diagnosis"],
            "plan": ["treatment_plan"]
        }
        
        for section, elements in critical_elements.items():
            section_data = current_content.get(section, {})
            completed_data = completed_sections.get(section, {})
            
            for element in elements:
                if (not section_data.get(element) and 
                    not completed_data.get(element)):
                    missing.append(f"{section}.{element}")
        
        return missing
    
    def _get_age_group(self, patient: PatientModel) -> str:
        """Get age group for metrics"""
        # Simple age grouping for analytics
        try:
            if patient.demographics and patient.demographics.date_of_birth:
                birth_year = int(patient.demographics.date_of_birth.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
                
                if age < 18:
                    return "pediatric"
                elif age < 65:
                    return "adult"
                else:
                    return "geriatric"
        except:
            pass
        
        return "unknown"
    
    async def get_chat_history(self, conversation_id: str) -> Optional[ChatHistory]:
        """Get chat history for conversation"""
        return self._chat_histories.get(conversation_id)
    
    async def clear_chat_history(self, conversation_id: str) -> bool:
        """Clear chat history for conversation"""
        if conversation_id in self._chat_histories:
            del self._chat_histories[conversation_id]
            return True
        return False


# Create service instance
ai_service = AIService()