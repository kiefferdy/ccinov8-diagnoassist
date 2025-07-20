"""
AI Models for DiagnoAssist Backend

This module defines Pydantic models for AI-powered features including
voice processing, clinical insights, and chat functionality.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class VoiceProcessingStatus(str, Enum):
    """Voice processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Confidence levels for AI predictions"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SOAPSection(str, Enum):
    """SOAP documentation sections"""
    SUBJECTIVE = "subjective"
    OBJECTIVE = "objective"
    ASSESSMENT = "assessment"
    PLAN = "plan"


class DiagnosisType(str, Enum):
    """Types of diagnoses"""
    PRIMARY = "primary"
    DIFFERENTIAL = "differential"
    RULE_OUT = "rule_out"
    PROVISIONAL = "provisional"


# Voice Processing Models

class VoiceProcessingRequest(BaseModel):
    """Request for voice processing"""
    audio_data: bytes = Field(..., description="Audio data in WAV format")
    encounter_id: str = Field(..., description="ID of the encounter")
    patient_context: Optional[Dict[str, Any]] = Field(default=None, description="Patient context information")
    target_section: Optional[SOAPSection] = Field(default=None, description="Target SOAP section")
    language: str = Field(default="en", description="Audio language code")
    
    class Config:
        schema_extra = {
            "example": {
                "encounter_id": "ENC001",
                "target_section": "subjective",
                "language": "en",
                "patient_context": {
                    "patient_name": "John Doe",
                    "chief_complaint": "Chest pain"
                }
            }
        }


class VoiceProcessingResult(BaseModel):
    """Result of voice processing"""
    transcription: str = Field(..., description="Raw transcription of audio")
    soap_extraction: Dict[str, Any] = Field(..., description="Extracted SOAP data")
    confidence: ConfidenceLevel = Field(..., description="Confidence in extraction")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "transcription": "Patient reports chest pain that started 2 hours ago...",
                "soap_extraction": {
                    "chief_complaint": "Chest pain",
                    "history_present_illness": "Sharp chest pain, started 2 hours ago..."
                },
                "confidence": "high",
                "processing_time_ms": 1250.5,
                "metadata": {
                    "audio_duration_seconds": 45,
                    "language_detected": "en"
                }
            }
        }


# Clinical Insights Models

class DiagnosisSuggestion(BaseModel):
    """AI-generated diagnosis suggestion"""
    diagnosis: str = Field(..., description="Suggested diagnosis")
    icd10_code: Optional[str] = Field(default=None, description="ICD-10 code if available")
    confidence: ConfidenceLevel = Field(..., description="Confidence in diagnosis")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability score (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    type: DiagnosisType = Field(default=DiagnosisType.DIFFERENTIAL, description="Type of diagnosis")
    
    class Config:
        schema_extra = {
            "example": {
                "diagnosis": "Acute myocardial infarction",
                "icd10_code": "I21.9",
                "confidence": "medium",
                "probability": 0.65,
                "evidence": ["Chest pain", "Elevated troponin", "ECG changes"],
                "type": "differential"
            }
        }


class TreatmentRecommendation(BaseModel):
    """AI-generated treatment recommendation"""
    treatment: str = Field(..., description="Recommended treatment")
    category: str = Field(..., description="Treatment category (e.g., medication, procedure)")
    priority: str = Field(..., description="Priority level (urgent, routine, etc.)")
    rationale: str = Field(..., description="Rationale for recommendation")
    contraindications: List[str] = Field(default_factory=list, description="Known contraindications")
    monitoring: Optional[str] = Field(default=None, description="Monitoring requirements")
    
    class Config:
        schema_extra = {
            "example": {
                "treatment": "Aspirin 325mg PO once",
                "category": "medication",
                "priority": "urgent",
                "rationale": "Antiplatelet therapy for suspected acute coronary syndrome",
                "contraindications": ["Active bleeding", "Severe renal impairment"],
                "monitoring": "Monitor for bleeding complications"
            }
        }


class RiskAssessment(BaseModel):
    """AI-generated risk assessment"""
    risk_factor: str = Field(..., description="Risk factor or condition")
    risk_level: str = Field(..., description="Risk level (low, moderate, high, critical)")
    score: Optional[float] = Field(default=None, description="Numerical risk score if available")
    recommendations: List[str] = Field(default_factory=list, description="Risk mitigation recommendations")
    time_frame: Optional[str] = Field(default=None, description="Time frame for risk assessment")
    
    class Config:
        schema_extra = {
            "example": {
                "risk_factor": "Cardiovascular disease",
                "risk_level": "high",
                "score": 8.5,
                "recommendations": ["Lipid management", "Blood pressure control", "Lifestyle modifications"],
                "time_frame": "10-year risk"
            }
        }


class ClinicalInsights(BaseModel):
    """Comprehensive clinical insights from AI analysis"""
    diagnosis_suggestions: List[DiagnosisSuggestion] = Field(default_factory=list)
    treatment_recommendations: List[TreatmentRecommendation] = Field(default_factory=list)
    risk_assessments: List[RiskAssessment] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list, description="Critical findings requiring immediate attention")
    follow_up_recommendations: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(..., description="Overall confidence in insights")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "diagnosis_suggestions": [
                    {
                        "diagnosis": "Acute myocardial infarction",
                        "confidence": "medium",
                        "probability": 0.65
                    }
                ],
                "red_flags": ["Chest pain with radiation", "Elevated cardiac markers"],
                "confidence": "high",
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


# Chat Models

class ChatMessage(BaseModel):
    """Chat message in AI conversation"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of {allowed_roles}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "What are the differential diagnoses for chest pain?",
                "timestamp": "2024-01-15T10:30:00Z",
                "metadata": {"encounter_id": "ENC001"}
            }
        }


class ChatHistory(BaseModel):
    """Chat conversation history"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    encounter_id: Optional[str] = Field(default=None, description="Associated encounter ID")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "encounter_id": "ENC001",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the differential diagnoses for chest pain?"
                    }
                ],
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ChatRequest(BaseModel):
    """Request for AI chat response"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    encounter_id: Optional[str] = Field(default=None, description="Encounter ID for context")
    patient_context: Optional[Dict[str, Any]] = Field(default=None, description="Patient context")
    include_history: bool = Field(default=True, description="Include conversation history")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the differential diagnoses for chest pain?",
                "encounter_id": "ENC001",
                "include_history": True
            }
        }


class ChatResponse(BaseModel):
    """AI chat response"""
    message: str = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation ID")
    confidence: ConfidenceLevel = Field(..., description="Confidence in response")
    sources: List[str] = Field(default_factory=list, description="Information sources referenced")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Differential diagnoses for chest pain include acute coronary syndrome...",
                "conversation_id": "conv_123",
                "confidence": "high",
                "sources": ["Clinical guidelines", "Medical literature"],
                "suggestions": ["Order ECG", "Check cardiac markers"]
            }
        }


# Documentation Completion Models

class DocumentationSuggestion(BaseModel):
    """AI suggestion for documentation completion"""
    section: SOAPSection = Field(..., description="SOAP section")
    field: str = Field(..., description="Specific field within section")
    suggestion: str = Field(..., description="Suggested content")
    confidence: ConfidenceLevel = Field(..., description="Confidence in suggestion")
    rationale: Optional[str] = Field(default=None, description="Rationale for suggestion")
    
    class Config:
        schema_extra = {
            "example": {
                "section": "assessment",
                "field": "primary_diagnosis",
                "suggestion": "Acute myocardial infarction",
                "confidence": "medium",
                "rationale": "Based on presenting symptoms and clinical context"
            }
        }


class DocumentationCompletionRequest(BaseModel):
    """Request for AI-powered documentation completion"""
    encounter_id: str = Field(..., description="Encounter ID")
    current_content: Dict[str, Any] = Field(..., description="Current SOAP content")
    target_sections: Optional[List[SOAPSection]] = Field(default=None, description="Specific sections to complete")
    patient_context: Optional[Dict[str, Any]] = Field(default=None, description="Patient context")
    
    class Config:
        schema_extra = {
            "example": {
                "encounter_id": "ENC001",
                "current_content": {
                    "subjective": {
                        "chief_complaint": "Chest pain"
                    }
                },
                "target_sections": ["assessment", "plan"]
            }
        }


class DocumentationCompletionResponse(BaseModel):
    """Response for documentation completion"""
    suggestions: List[DocumentationSuggestion] = Field(default_factory=list)
    completed_sections: Dict[str, Any] = Field(default_factory=dict, description="AI-completed sections")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Documentation quality score")
    missing_elements: List[str] = Field(default_factory=list, description="Missing critical elements")
    
    class Config:
        schema_extra = {
            "example": {
                "suggestions": [
                    {
                        "section": "assessment",
                        "field": "primary_diagnosis",
                        "suggestion": "Acute myocardial infarction",
                        "confidence": "medium"
                    }
                ],
                "quality_score": 0.85,
                "missing_elements": ["Vital signs", "Physical examination findings"]
            }
        }


# AI Service Configuration Models

class AIServiceConfig(BaseModel):
    """Configuration for AI services"""
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    default_model: str = Field(default="gemini-1.5-pro", description="Default model to use")
    max_tokens: int = Field(default=2048, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="AI temperature setting")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "default_model": "gemini-1.5-pro",
                "max_tokens": 2048,
                "temperature": 0.1,
                "timeout_seconds": 30,
                "enable_caching": True,
                "cache_ttl_seconds": 3600
            }
        }


# Response Models for API Endpoints

class AIHealthCheck(BaseModel):
    """AI service health check response"""
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    message: str = Field(..., description="Health status message")
    services: Dict[str, Any] = Field(default_factory=dict, description="Individual service status")
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All AI services operational",
                "services": {
                    "gemini": {
                        "status": "healthy",
                        "model_accessible": True
                    }
                },
                "last_checked": "2024-01-15T10:30:00Z"
            }
        }