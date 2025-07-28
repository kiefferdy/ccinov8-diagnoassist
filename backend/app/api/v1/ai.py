"""
AI API Endpoints for DiagnoAssist Backend

This module provides API endpoints for AI-powered features including
voice processing, clinical decision support, and AI chat functionality.
"""
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.ai_service import ai_service
from app.services.patient_service import patient_service
from app.services.encounter_service import encounter_service
from app.models.ai_models import (
    VoiceProcessingRequest, VoiceProcessingResult,
    ClinicalInsights, ChatRequest, ChatResponse, ChatHistory,
    DocumentationCompletionRequest, DocumentationCompletionResponse,
    AIHealthCheck, SOAPSection
)
from app.models.auth import UserModel
from app.core.exceptions import AIServiceException, NotFoundError, ValidationException
# Simplified for core functionality - removed enterprise monitoring system
from app.middleware.auth_middleware import get_current_user
from app.core.ai_client import get_ai_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/voice/process", response_model=VoiceProcessingResult)
async def process_voice_to_soap(
    encounter_id: str = Form(...),
    target_section: Optional[str] = Form(None),
    language: str = Form("en"),
    audio_file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Process voice recording and extract SOAP documentation
    
    **Required:**
    - audio_file: WAV audio file containing clinical speech
    - encounter_id: ID of the encounter to associate with
    
    **Optional:**
    - target_section: Specific SOAP section to focus on (subjective, objective, assessment, plan)
    - language: Audio language code (default: en)
    
    **Returns:**
    - Transcription of the audio
    - Extracted SOAP data in structured format
    - Confidence level and processing metadata
    """
    try:
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio'):
            raise ValidationException("File must be an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise ValidationException("Audio file is empty")
        
        # Validate target section
        soap_section = None
        if target_section:
            try:
                soap_section = SOAPSection(target_section.lower())
            except ValueError:
                raise ValidationException(f"Invalid SOAP section: {target_section}")
        
        # Get encounter and patient context
        encounter = await encounter_service.get_encounter(encounter_id, current_user)
        patient = await patient_service.get_patient(encounter.patient_id, current_user)
        
        # Create voice processing request
        request = VoiceProcessingRequest(
            audio_data=audio_data,
            encounter_id=encounter_id,
            target_section=soap_section,
            language=language,
            patient_context={
                "patient_name": patient.demographics.name if patient.demographics else None,
                "chief_complaint": encounter.soap.subjective.chief_complaint if (
                    encounter.soap and encounter.soap.subjective
                ) else None
            }
        )
        
        # Process voice
        result = await ai_service.process_voice_to_soap(request, patient, encounter)
        
        # Log API usage (simplified - monitoring removed)
        logger.debug(f"Voice processing API usage - user role: {current_user.role.value}, target section: {target_section or 'all'}")
        
        logger.info(f"Voice processing completed for encounter {encounter_id} by user {current_user.id}")
        
        return result
        
    except (NotFoundError, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Voice processing API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/insights/{encounter_id}", response_model=ClinicalInsights)
async def get_clinical_insights(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate comprehensive clinical insights for an encounter
    
    **Parameters:**
    - encounter_id: ID of the encounter to analyze
    
    **Returns:**
    - Differential diagnoses with confidence scores
    - Treatment recommendations
    - Risk assessments
    - Red flags and critical findings
    - Follow-up recommendations
    """
    try:
        # Get encounter and patient
        encounter = await encounter_service.get_encounter(encounter_id, current_user)
        patient = await patient_service.get_patient(encounter.patient_id, current_user)
        
        # Generate insights
        insights = await ai_service.generate_clinical_insights(patient, encounter)
        
        # Log API usage (simplified - monitoring removed)
        logger.debug(f"Clinical insights API usage - user role: {current_user.role.value}")
        
        logger.info(f"Clinical insights generated for encounter {encounter_id} by user {current_user.id}")
        
        return insights
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Clinical insights API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Chat with AI assistant for clinical questions
    
    **Request Body:**
    - message: Your clinical question or message
    - conversation_id: Optional conversation ID for context
    - encounter_id: Optional encounter ID for patient context
    - patient_context: Optional additional patient information
    - include_history: Whether to include conversation history (default: true)
    
    **Returns:**
    - AI response with clinical information
    - Conversation ID for follow-up questions
    - Confidence level and suggestions
    """
    try:
        # Get patient and encounter context if provided
        patient = None
        encounter = None
        
        if request.encounter_id:
            encounter = await encounter_service.get_encounter(request.encounter_id, current_user)
            patient = await patient_service.get_patient(encounter.patient_id, current_user)
        
        # Chat with AI
        response = await ai_service.chat_with_ai(request, patient, encounter)
        
        # Log API usage (simplified - monitoring removed)
        logger.debug(f"AI chat API usage - user role: {current_user.role.value}, has encounter context: {request.encounter_id is not None}")
        
        logger.info(f"AI chat request processed for user {current_user.id}")
        
        return response
        
    except (NotFoundError, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")
    except Exception as e:
        logger.error(f"AI chat API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/history/{conversation_id}", response_model=Optional[ChatHistory])
async def get_chat_history(
    conversation_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get chat conversation history
    
    **Parameters:**
    - conversation_id: ID of the conversation
    
    **Returns:**
    - Complete chat history including all messages
    - Conversation metadata
    """
    try:
        history = await ai_service.get_chat_history(conversation_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"Chat history retrieved for conversation {conversation_id} by user {current_user.id}")
        
        return history
        
    except Exception as e:
        logger.error(f"Chat history API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/chat/history/{conversation_id}")
async def clear_chat_history(
    conversation_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Clear chat conversation history
    
    **Parameters:**
    - conversation_id: ID of the conversation to clear
    
    **Returns:**
    - Success confirmation
    """
    try:
        success = await ai_service.clear_chat_history(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"Chat history cleared for conversation {conversation_id} by user {current_user.id}")
        
        return JSONResponse(
            content={"success": True, "message": "Chat history cleared successfully"}
        )
        
    except Exception as e:
        logger.error(f"Clear chat history API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documentation/complete", response_model=DocumentationCompletionResponse)
async def complete_documentation(
    request: DocumentationCompletionRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    AI-powered documentation completion and suggestions
    
    **Request Body:**
    - encounter_id: ID of the encounter
    - current_content: Current SOAP documentation content
    - target_sections: Optional list of sections to focus on
    - patient_context: Optional additional patient context
    
    **Returns:**
    - Documentation suggestions for improvement
    - AI-completed sections
    - Documentation quality score
    - List of missing critical elements
    """
    try:
        # Get encounter and patient context
        encounter = await encounter_service.get_encounter(request.encounter_id, current_user)
        patient = await patient_service.get_patient(encounter.patient_id, current_user)
        
        # Complete documentation
        response = await ai_service.complete_documentation(request, patient)
        
        # Log API usage (simplified - monitoring removed)
        logger.debug(f"Documentation completion API usage - user role: {current_user.role.value}, sections requested: {len(request.target_sections) if request.target_sections else 0}")
        
        logger.info(f"Documentation completion generated for encounter {request.encounter_id} by user {current_user.id}")
        
        return response
        
    except (NotFoundError, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=500, detail=f"Documentation completion failed: {str(e)}")
    except Exception as e:
        logger.error(f"Documentation completion API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=AIHealthCheck)
async def ai_health_check():
    """
    Check AI service health status
    
    **Returns:**
    - Overall AI service status
    - Individual service statuses (Gemini, etc.)
    - Last health check timestamp
    """
    try:
        # Get AI client health
        ai_client_manager = get_ai_client()
        health_status = await ai_client_manager.health_check()
        
        return AIHealthCheck(
            status=health_status["status"],
            message=health_status["message"],
            services=health_status.get("services", {})
        )
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return AIHealthCheck(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            services={}
        )


# Additional endpoints for specific AI features

@router.get("/models/available")
async def get_available_models(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of available AI models and their capabilities
    
    **Returns:**
    - List of available AI models
    - Model capabilities and limitations
    - Recommended use cases
    """
    try:
        models = {
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "capabilities": [
                    "Voice processing",
                    "Clinical decision support",
                    "Chat assistance",
                    "Documentation completion"
                ],
                "max_tokens": 2048,
                "languages": ["en", "es", "fr"],
                "recommended_for": ["Complex clinical analysis", "Voice-to-SOAP conversion"]
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "capabilities": [
                    "Quick responses",
                    "Basic chat",
                    "Health checks"
                ],
                "max_tokens": 1024,
                "languages": ["en"],
                "recommended_for": ["Quick questions", "Health monitoring"]
            }
        }
        
        return JSONResponse(content={"models": models})
        
    except Exception as e:
        logger.error(f"Get available models error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/usage/stats")
async def get_ai_usage_stats(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get AI usage statistics for monitoring
    
    **Note:** Requires admin privileges
    
    **Returns:**
    - API call statistics
    - Model usage statistics
    - Performance metrics
    - Error rates
    """
    try:
        # Check admin privileges
        if current_user.role.value not in ["admin"]:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        # Simplified metrics (monitoring system removed)
        stats = {
            "voice_processing": "metrics simplified - monitoring removed",
            "clinical_insights": "metrics simplified - monitoring removed", 
            "ai_chat": "metrics simplified - monitoring removed",
            "documentation_completion": "metrics simplified - monitoring removed",
            "ai_request_duration": "metrics simplified - monitoring removed",
            "ai_request_errors": "metrics simplified - monitoring removed"
        }
        
        return JSONResponse(content={"usage_stats": stats})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get AI usage stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")