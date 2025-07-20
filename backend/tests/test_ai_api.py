"""
Tests for AI API endpoints

Tests the AI-related API endpoints including voice processing,
clinical insights, chat functionality, and health checks.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
import io

from app.main import app
from app.models.ai_models import (
    ClinicalInsights, ChatResponse, VoiceProcessingResult,
    DocumentationCompletionResponse, ConfidenceLevel
)
from app.models.auth import UserModel, UserRole
from app.core.exceptions import AIServiceException


class TestAIAPI:
    """Test cases for AI API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Create mock authenticated user"""
        return UserModel(
            id="user123",
            email="doctor@example.com",
            name="Dr. Smith",
            role=UserRole.DOCTOR,
            is_active=True,
            is_verified=True
        )

    @pytest.fixture
    def auth_headers(self, mock_user):
        """Create authentication headers"""
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user):
            return {"Authorization": "Bearer fake_token"}

    @pytest.fixture
    def mock_voice_file(self):
        """Create mock voice file for testing"""
        # Create a mock WAV file
        audio_content = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00" + b"\x00" * 100
        return io.BytesIO(audio_content)

    def test_ai_health_check(self, client):
        """Test AI health check endpoint"""
        
        with patch('app.api.v1.ai.get_ai_client') as mock_get_client:
            mock_client_manager = AsyncMock()
            mock_client_manager.health_check.return_value = {
                "status": "healthy",
                "message": "All AI services operational",
                "services": {
                    "gemini": {"status": "healthy", "model_accessible": True}
                }
            }
            mock_get_client.return_value = mock_client_manager
            
            response = client.get("/api/v1/ai/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "services" in data

    def test_get_available_models(self, client, auth_headers, mock_user):
        """Test get available AI models endpoint"""
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user):
            response = client.get("/api/v1/ai/models/available", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert "gemini-1.5-pro" in data["models"]
            assert "gemini-1.5-flash" in data["models"]

    def test_process_voice_to_soap_success(self, client, auth_headers, mock_user, mock_voice_file):
        """Test successful voice processing"""
        
        # Mock the encounter and patient services
        mock_encounter = Mock()
        mock_encounter.patient_id = "P001"
        mock_encounter.soap = Mock()
        mock_encounter.soap.subjective = Mock()
        mock_encounter.soap.subjective.chief_complaint = "Chest pain"
        
        mock_patient = Mock()
        mock_patient.demographics = Mock()
        mock_patient.demographics.name = "John Doe"
        
        # Mock the AI service response
        mock_voice_result = VoiceProcessingResult(
            transcription="Patient reports chest pain that started 2 hours ago",
            soap_extraction={"chief_complaint": "Chest pain"},
            confidence=ConfidenceLevel.HIGH,
            processing_time_ms=1250.5,
            metadata={"language": "en"}
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.encounter_service.encounter_service.get_encounter', return_value=mock_encounter), \
             patch('app.services.patient_service.patient_service.get_patient', return_value=mock_patient), \
             patch('app.services.ai_service.ai_service.process_voice_to_soap', return_value=mock_voice_result):
            
            # Prepare file upload
            files = {
                "audio_file": ("test_audio.wav", mock_voice_file, "audio/wav")
            }
            data = {
                "encounter_id": "ENC001",
                "target_section": "subjective",
                "language": "en"
            }
            
            response = client.post(
                "/api/v1/ai/voice/process",
                files=files,
                data=data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["transcription"] == mock_voice_result.transcription
            assert result["confidence"] == mock_voice_result.confidence.value

    def test_get_clinical_insights_success(self, client, auth_headers, mock_user):
        """Test successful clinical insights generation"""
        
        # Mock the encounter and patient
        mock_encounter = Mock()
        mock_encounter.patient_id = "P001"
        
        mock_patient = Mock()
        mock_patient.id = "P001"
        
        # Mock the AI service response
        mock_insights = ClinicalInsights(
            diagnosis_suggestions=[],
            treatment_recommendations=[],
            risk_assessments=[],
            red_flags=["Chest pain with radiation"],
            follow_up_recommendations=["Order ECG"],
            confidence=ConfidenceLevel.HIGH
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.encounter_service.encounter_service.get_encounter', return_value=mock_encounter), \
             patch('app.services.patient_service.patient_service.get_patient', return_value=mock_patient), \
             patch('app.services.ai_service.ai_service.generate_clinical_insights', return_value=mock_insights):
            
            response = client.get("/api/v1/ai/insights/ENC001", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["confidence"] == ConfidenceLevel.HIGH.value

    def test_ai_chat_success(self, client, auth_headers, mock_user):
        """Test successful AI chat"""
        
        # Mock the AI service response
        mock_chat_response = ChatResponse(
            message="The differential diagnoses for chest pain include acute coronary syndrome, pulmonary embolism, and aortic dissection.",
            conversation_id="conv_123",
            confidence=ConfidenceLevel.HIGH,
            suggestions=["Order ECG", "Check cardiac markers"]
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.ai_service.ai_service.chat_with_ai', return_value=mock_chat_response):
            
            chat_data = {
                "message": "What are the differential diagnoses for chest pain?",
                "encounter_id": "ENC001",
                "include_history": True
            }
            
            response = client.post("/api/v1/ai/chat", json=chat_data, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == mock_chat_response.message
            assert data["conversation_id"] == mock_chat_response.conversation_id

    def test_documentation_completion_success(self, client, auth_headers, mock_user):
        """Test successful documentation completion"""
        
        # Mock the encounter and patient
        mock_encounter = Mock()
        mock_encounter.patient_id = "P001"
        
        mock_patient = Mock()
        mock_patient.id = "P001"
        
        # Mock the AI service response
        mock_completion_response = DocumentationCompletionResponse(
            suggestions=[],
            completed_sections={"assessment": {"primary_diagnosis": "Chest pain, rule out ACS"}},
            quality_score=0.85,
            missing_elements=["vital_signs"]
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.encounter_service.encounter_service.get_encounter', return_value=mock_encounter), \
             patch('app.services.patient_service.patient_service.get_patient', return_value=mock_patient), \
             patch('app.services.ai_service.ai_service.complete_documentation', return_value=mock_completion_response):
            
            completion_data = {
                "encounter_id": "ENC001",
                "current_content": {
                    "subjective": {"chief_complaint": "Chest pain"}
                },
                "target_sections": ["assessment", "plan"]
            }
            
            response = client.post("/api/v1/ai/documentation/complete", json=completion_data, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["quality_score"] == 0.85
            assert "completed_sections" in data

    def test_get_chat_history_success(self, client, auth_headers, mock_user):
        """Test getting chat history"""
        
        from app.models.ai_models import ChatHistory, ChatMessage
        
        # Mock chat history
        mock_history = ChatHistory(
            conversation_id="conv_123",
            encounter_id="ENC001",
            messages=[
                ChatMessage(role="user", content="What are the symptoms of MI?"),
                ChatMessage(role="assistant", content="Symptoms include chest pain, shortness of breath...")
            ]
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.ai_service.ai_service.get_chat_history', return_value=mock_history):
            
            response = client.get("/api/v1/ai/chat/history/conv_123", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "conv_123"
            assert len(data["messages"]) == 2

    def test_clear_chat_history_success(self, client, auth_headers, mock_user):
        """Test clearing chat history"""
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.ai_service.ai_service.clear_chat_history', return_value=True):
            
            response = client.delete("/api/v1/ai/chat/history/conv_123", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_ai_usage_stats_admin_only(self, client, auth_headers):
        """Test AI usage stats endpoint requires admin privileges"""
        
        # Test with non-admin user
        non_admin_user = UserModel(
            id="user456",
            email="nurse@example.com", 
            name="Nurse Jane",
            role=UserRole.NURSE,
            is_active=True,
            is_verified=True
        )
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=non_admin_user):
            response = client.get("/api/v1/ai/usage/stats", headers=auth_headers)
            assert response.status_code == 403

        # Test with admin user
        admin_user = UserModel(
            id="admin123",
            email="admin@example.com",
            name="Admin User", 
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        mock_stats = {
            "voice_processing": {"count": 10},
            "clinical_insights": {"count": 15},
            "ai_chat": {"count": 25}
        }
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=admin_user), \
             patch('app.core.monitoring.monitoring.metrics.get_metric_summary', return_value={"count": 0}):
            
            response = client.get("/api/v1/ai/usage/stats", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "usage_stats" in data

    def test_voice_processing_invalid_file_type(self, client, auth_headers, mock_user):
        """Test voice processing with invalid file type"""
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user):
            
            # Upload a text file instead of audio
            files = {
                "audio_file": ("test.txt", io.StringIO("not audio"), "text/plain")
            }
            data = {
                "encounter_id": "ENC001",
                "target_section": "subjective",
                "language": "en"
            }
            
            response = client.post(
                "/api/v1/ai/voice/process",
                files=files,
                data=data,
                headers=auth_headers
            )
            
            assert response.status_code == 400

    def test_ai_service_error_handling(self, client, auth_headers, mock_user):
        """Test AI service error handling"""
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.ai_service.ai_service.chat_with_ai', side_effect=AIServiceException("AI service unavailable")):
            
            chat_data = {
                "message": "Test message",
                "include_history": True
            }
            
            response = client.post("/api/v1/ai/chat", json=chat_data, headers=auth_headers)
            
            assert response.status_code == 500
            assert "AI chat failed" in response.json()["detail"]

    def test_unauthenticated_access_denied(self, client):
        """Test that unauthenticated requests are denied"""
        
        # Test various AI endpoints without authentication
        endpoints = [
            ("/api/v1/ai/insights/ENC001", "get"),
            ("/api/v1/ai/chat", "post"),
            ("/api/v1/ai/documentation/complete", "post"),
            ("/api/v1/ai/chat/history/conv_123", "get"),
        ]
        
        for endpoint, method in endpoints:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code in [401, 403]  # Unauthorized or Forbidden

    def test_encounter_not_found_handling(self, client, auth_headers, mock_user):
        """Test handling of encounter not found errors"""
        
        from app.core.exceptions import NotFoundError
        
        with patch('app.middleware.auth_middleware.get_current_user', return_value=mock_user), \
             patch('app.services.encounter_service.encounter_service.get_encounter', side_effect=NotFoundError("Encounter", "ENC999")):
            
            response = client.get("/api/v1/ai/insights/ENC999", headers=auth_headers)
            
            assert response.status_code == 404

    def test_ai_health_check_failure(self, client):
        """Test AI health check when service is unhealthy"""
        
        with patch('app.api.v1.ai.get_ai_client', side_effect=Exception("AI service connection failed")):
            
            response = client.get("/api/v1/ai/health")
            
            assert response.status_code == 200  # Health check endpoint should not fail
            data = response.json()
            assert data["status"] == "unhealthy"
            assert "AI service connection failed" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__])