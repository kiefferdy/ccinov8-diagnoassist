"""
AI Client for DiagnoAssist Backend

This module provides integration with Google Gemini 2.5 Pro for AI-powered
clinical decision support and voice processing capabilities.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import base64

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class AIModelType(str, Enum):
    """AI model types"""
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"


class AITaskType(str, Enum):
    """AI task types for monitoring"""
    VOICE_TO_SOAP = "voice_to_soap"
    DIFFERENTIAL_DIAGNOSIS = "differential_diagnosis"
    CLINICAL_INSIGHTS = "clinical_insights"
    CHAT_RESPONSE = "chat_response"
    DOCUMENTATION_COMPLETION = "documentation_completion"


@dataclass
class AIRequest:
    """AI request structure"""
    task_type: AITaskType
    prompt: str
    context: Optional[Dict[str, Any]] = None
    audio_data: Optional[bytes] = None
    model: AIModelType = AIModelType.GEMINI_PRO
    max_tokens: int = 2048
    temperature: float = 0.1  # Low temperature for medical accuracy


@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    safety_ratings: Optional[List[Dict[str, Any]]] = None


class GeminiAIClient:
    """Google Gemini AI client for clinical applications"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._configure_client()
        
        # Safety settings for medical use
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
        
        # Generation config for medical accuracy
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    def _configure_client(self):
        """Configure the Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini AI client configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {e}")
            raise AIServiceException(f"AI client configuration failed: {str(e)}", "client_configuration")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response for given request"""
        try:
            # Log request metrics
            logger.debug(f"AI request: {request.task_type.value} using {request.model.value}")
            
            start_time = asyncio.get_event_loop().time()
            
            # Select model
            model = genai.GenerativeModel(
                model_name=request.model.value,
                safety_settings=self.safety_settings,
                generation_config=self._get_generation_config(request)
            )
            
            # Prepare input
            input_parts = await self._prepare_input(request)
            
            # Generate response
            response = await self._call_model(model, input_parts)
            
            # Process response
            ai_response = self._process_response(response, request.task_type)
            
            # Log metrics
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.debug(f"AI request completed in {duration_ms:.2f}ms")
            
            logger.info(f"AI request completed: {request.task_type.value} in {duration_ms:.2f}ms")
            
            return ai_response
            
        except Exception as e:
            # Log error metrics
            logger.error(f"AI request error: {request.task_type.value} - {type(e).__name__}: {e}")
            
            logger.error(f"AI request failed: {e}")
            raise AIServiceException(f"AI generation failed: {str(e)}", "ai_generation")
    
    def _get_generation_config(self, request: AIRequest) -> Dict[str, Any]:
        """Get generation config for request"""
        config = self.generation_config.copy()
        config["temperature"] = request.temperature
        config["max_output_tokens"] = request.max_tokens
        return config
    
    async def _prepare_input(self, request: AIRequest) -> List[Union[str, Dict[str, Any]]]:
        """Prepare input for the model"""
        input_parts = []
        
        # Add context if provided
        if request.context:
            context_prompt = self._format_context(request.context)
            input_parts.append(f"Context:\n{context_prompt}\n\n")
        
        # Add main prompt
        input_parts.append(request.prompt)
        
        # Add audio data if provided
        if request.audio_data:
            audio_part = {
                "mime_type": "audio/wav",
                "data": base64.b64encode(request.audio_data).decode()
            }
            input_parts.append(audio_part)
        
        return input_parts
    
    async def _call_model(self, model, input_parts: List) -> Any:
        """Call the model with input parts"""
        try:
            # Use async generation if available, otherwise run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(input_parts)
            )
            return response
            
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            raise AIServiceException(f"Model generation failed: {str(e)}", "model_generation")
    
    def _process_response(self, response: Any, task_type: AITaskType) -> AIResponse:
        """Process the model response"""
        try:
            # Extract content
            content = response.text if hasattr(response, 'text') else str(response)
            
            # Extract metadata
            metadata = {}
            if hasattr(response, 'usage_metadata'):
                metadata['usage'] = {
                    'prompt_tokens': getattr(response.usage_metadata, 'prompt_token_count', 0),
                    'completion_tokens': getattr(response.usage_metadata, 'candidates_token_count', 0),
                    'total_tokens': getattr(response.usage_metadata, 'total_token_count', 0)
                }
            
            # Extract safety ratings
            safety_ratings = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'safety_ratings'):
                    safety_ratings = [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in candidate.safety_ratings
                    ]
            
            return AIResponse(
                content=content,
                metadata=metadata,
                safety_ratings=safety_ratings
            )
            
        except Exception as e:
            logger.error(f"Response processing failed: {e}")
            raise AIServiceException(f"Response processing failed: {str(e)}", "response_processing")
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the prompt"""
        formatted_lines = []
        
        # Patient information
        if 'patient' in context:
            patient = context['patient']
            formatted_lines.append("Patient Information:")
            if hasattr(patient, 'demographics'):
                demo = patient.demographics
                formatted_lines.append(f"- Name: {getattr(demo, 'name', 'N/A')}")
                formatted_lines.append(f"- Age: {getattr(demo, 'age', 'N/A')}")
                formatted_lines.append(f"- Gender: {getattr(demo, 'gender', 'N/A')}")
            
            if hasattr(patient, 'medical_background'):
                bg = patient.medical_background
                if getattr(bg, 'allergies', None):
                    allergies = [allergy.allergen for allergy in bg.allergies]
                    formatted_lines.append(f"- Allergies: {', '.join(allergies)}")
                
                if getattr(bg, 'medications', None):
                    meds = [med.name for med in bg.medications]
                    formatted_lines.append(f"- Current Medications: {', '.join(meds)}")
                
                if getattr(bg, 'medical_history', None):
                    formatted_lines.append(f"- Medical History: {', '.join(bg.medical_history)}")
        
        # Encounter information
        if 'encounter' in context:
            encounter = context['encounter']
            formatted_lines.append("\nEncounter Information:")
            formatted_lines.append(f"- Type: {getattr(encounter, 'type', 'N/A')}")
            formatted_lines.append(f"- Status: {getattr(encounter, 'status', 'N/A')}")
            
            if hasattr(encounter, 'soap') and encounter.soap:
                soap = encounter.soap
                if hasattr(soap, 'subjective') and soap.subjective:
                    if soap.subjective.chief_complaint:
                        formatted_lines.append(f"- Chief Complaint: {soap.subjective.chief_complaint}")
                    if soap.subjective.history_present_illness:
                        formatted_lines.append(f"- HPI: {soap.subjective.history_present_illness}")
        
        # Additional context
        for key, value in context.items():
            if key not in ['patient', 'encounter'] and value:
                formatted_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_lines)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on AI service"""
        try:
            # Simple test request
            test_request = AIRequest(
                task_type=AITaskType.CHAT_RESPONSE,
                prompt="Respond with 'OK' if you are functioning properly.",
                model=AIModelType.GEMINI_FLASH,  # Use faster model for health check
                max_tokens=10
            )
            
            response = await self.generate_response(test_request)
            
            is_healthy = "OK" in response.content.upper()
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "message": "AI service is operational" if is_healthy else "AI service health check failed",
                "response_received": bool(response.content),
                "model_accessible": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"AI service health check failed: {str(e)}",
                "model_accessible": False,
                "error": str(e)
            }


class AIClientManager:
    """Manager for AI client instances"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_client = GeminiAIClient(gemini_api_key)
    
    async def get_client(self, model_type: AIModelType = AIModelType.GEMINI_PRO) -> GeminiAIClient:
        """Get AI client instance"""
        # For now, we only have Gemini client
        # Could be extended to support multiple AI providers
        return self.gemini_client
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all AI services"""
        try:
            gemini_health = await self.gemini_client.health_check()
            
            overall_healthy = gemini_health["status"] == "healthy"
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": "All AI services operational" if overall_healthy else "Some AI services unhealthy",
                "services": {
                    "gemini": gemini_health
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"AI health check failed: {str(e)}",
                "error": str(e)
            }


# Global AI client manager instance will be initialized in main.py
ai_client_manager: Optional[AIClientManager] = None


def get_ai_client() -> AIClientManager:
    """Get the global AI client manager"""
    if ai_client_manager is None:
        raise AIServiceException("AI client manager not initialized", "client_initialization")
    return ai_client_manager


def initialize_ai_client(gemini_api_key: str) -> AIClientManager:
    """Initialize the global AI client manager"""
    global ai_client_manager
    ai_client_manager = AIClientManager(gemini_api_key)
    logger.info("AI client manager initialized")
    return ai_client_manager