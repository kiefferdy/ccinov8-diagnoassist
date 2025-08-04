"""
Tests for AI Service functionality

Tests the AI service including voice processing, clinical insights,
chat functionality, and documentation completion.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.ai_service import ai_service
from app.models.ai_models import (
    VoiceProcessingRequest, ClinicalInsights, ChatRequest, 
    DocumentationCompletionRequest, SOAPSection, ConfidenceLevel
)
from app.models.patient import PatientModel, PatientDemographics, MedicalBackground
from app.models.encounter import EncounterModel, EncounterStatusEnum, EncounterTypeEnum, ProviderInfo
from app.models.soap import SOAPModel, SOAPSubjective
from app.core.exceptions import AIServiceException


class TestAIService:
    """Test cases for AI Service"""

    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient for testing"""
        return PatientModel(
            id="P001",
            demographics=PatientDemographics(
                name="John Doe",
                date_of_birth="1980-01-01",
                gender="male",
                phone="+1234567890",
                email="john.doe@example.com"
            ),
            medical_background=MedicalBackground(
                allergies=[],
                medications=[],
                medical_history=["Hypertension", "Type 2 Diabetes"]
            )
        )

    @pytest.fixture
    def sample_encounter(self):
        """Create a sample encounter for testing"""
        return EncounterModel(
            id="ENC001",
            patient_id="P001",
            episode_id="EP001",
            type=EncounterTypeEnum.INITIAL,
            status=EncounterStatusEnum.DRAFT,
            provider=ProviderInfo(
                id="provider123",
                name="Dr. Test Provider",
                role="Attending Physician",
                specialty="Internal Medicine",
                department="Internal Medicine"
            ),
            soap=SOAPModel(
                subjective=SOAPSubjective(
                    chief_complaint="Chest pain",
                    history_present_illness="Patient reports chest pain that started 2 hours ago"
                )
            )
        )

    @pytest.fixture
    def voice_processing_request(self):
        """Create a sample voice processing request"""
        return VoiceProcessingRequest(
            audio_data=b"fake_audio_data",
            encounter_id="ENC001",
            target_section=SOAPSection.SUBJECTIVE,
            language="en"
        )

    @pytest.fixture
    def chat_request(self):
        """Create a sample chat request"""
        return ChatRequest(
            message="What are the differential diagnoses for chest pain?",
            encounter_id="ENC001",
            include_history=True
        )

    @pytest.fixture
    def documentation_request(self):
        """Create a sample documentation completion request"""
        return DocumentationCompletionRequest(
            encounter_id="ENC001",
            current_content={
                "subjective": {
                    "chief_complaint": "Chest pain"
                }
            },
            target_sections=[SOAPSection.ASSESSMENT, SOAPSection.PLAN]
        )

    @pytest.mark.asyncio
    async def test_process_voice_to_soap_success(
        self, voice_processing_request, sample_patient, sample_encounter
    ):
        """Test successful voice processing"""
        
        # Mock the AI client response
        mock_ai_response = Mock()
        mock_ai_response.content = """
TRANSCRIPTION: Patient reports chest pain that started two hours ago, sharp in nature.

SOAP_EXTRACTION: {
    "chief_complaint": "Chest pain",
    "history_present_illness": "Sharp chest pain, started 2 hours ago"
}
"""
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            
            # Set up the async mock chain properly
            mock_ai_client_manager = AsyncMock()
            mock_ai_client_manager.get_client = AsyncMock(return_value=mock_client)
            mock_get_client.return_value = mock_ai_client_manager
            
            result = await ai_service.process_voice_to_soap(
                voice_processing_request, sample_patient, sample_encounter
            )
            
            assert result.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
            assert result.soap_extraction is not None
            assert "chief_complaint" in result.soap_extraction or "raw_content" in result.soap_extraction

    @pytest.mark.asyncio
    async def test_generate_clinical_insights_success(
        self, sample_patient, sample_encounter
    ):
        """Test successful clinical insights generation"""
        
        # Mock the AI client response
        mock_ai_response = Mock()
        mock_ai_response.content = """{
    "differential_diagnoses": [
        {
            "diagnosis": "Acute myocardial infarction",
            "confidence": "medium",
            "probability": 0.65,
            "evidence": ["Chest pain", "Patient age", "Medical history"]
        }
    ],
    "treatment_recommendations": [
        {
            "treatment": "Aspirin 325mg PO",
            "category": "medication",
            "priority": "urgent",
            "rationale": "Antiplatelet therapy for suspected ACS"
        }
    ],
    "red_flags": ["Chest pain with radiation"]
}"""
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            
            # Set up the async mock chain properly
            mock_ai_client_manager = AsyncMock()
            mock_ai_client_manager.get_client = AsyncMock(return_value=mock_client)
            mock_get_client.return_value = mock_ai_client_manager
            
            result = await ai_service.generate_clinical_insights(
                sample_patient, sample_encounter
            )
            
            assert isinstance(result, ClinicalInsights)
            assert result.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]

    @pytest.mark.asyncio
    async def test_chat_with_ai_success(
        self, chat_request, sample_patient, sample_encounter
    ):
        """Test successful AI chat"""
        
        # Mock the AI client response
        mock_ai_response = Mock()
        mock_ai_response.content = """
The differential diagnoses for chest pain include:

1. Acute coronary syndrome (ACS)
2. Pulmonary embolism
3. Aortic dissection
4. Pneumothorax
5. Musculoskeletal pain

I recommend ordering an ECG and cardiac markers to evaluate for ACS.
"""
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            
            # Set up the async mock chain properly
            mock_ai_client_manager = AsyncMock()
            mock_ai_client_manager.get_client = AsyncMock(return_value=mock_client)
            mock_get_client.return_value = mock_ai_client_manager
            
            result = await ai_service.chat_with_ai(
                chat_request, sample_patient, sample_encounter
            )
            
            assert result.message == mock_ai_response.content
            assert result.conversation_id is not None
            assert len(result.suggestions) >= 0

    @pytest.mark.asyncio
    async def test_complete_documentation_success(
        self, documentation_request, sample_patient
    ):
        """Test successful documentation completion"""
        
        # Mock the AI client response
        mock_ai_response = Mock()
        mock_ai_response.content = """{
    "suggestions": [
        {
            "section": "assessment",
            "field": "primary_diagnosis",
            "suggestion": "Chest pain, rule out acute coronary syndrome",
            "confidence": "medium"
        }
    ],
    "completed_sections": {
        "assessment": {
            "primary_diagnosis": "Chest pain, rule out acute coronary syndrome"
        }
    }
}"""
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            
            # Set up the async mock chain properly
            mock_ai_client_manager = AsyncMock()
            mock_ai_client_manager.get_client = AsyncMock(return_value=mock_client)
            mock_get_client.return_value = mock_ai_client_manager
            
            result = await ai_service.complete_documentation(
                documentation_request, sample_patient
            )
            
            assert result.quality_score >= 0.0
            assert result.quality_score <= 1.0
            assert isinstance(result.suggestions, list)
            assert isinstance(result.completed_sections, dict)

    @pytest.mark.asyncio
    async def test_voice_processing_with_invalid_audio(self, sample_patient, sample_encounter):
        """Test voice processing with invalid audio data"""
        
        request = VoiceProcessingRequest(
            audio_data=b"",  # Empty audio data
            encounter_id="ENC001",
            target_section=SOAPSection.SUBJECTIVE,
            language="en"
        )
        
        # Mock AI client to raise an exception
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.side_effect = Exception("Invalid audio data")
            mock_get_client.return_value.get_client.return_value = mock_client
            
            with pytest.raises(AIServiceException):
                await ai_service.process_voice_to_soap(
                    request, sample_patient, sample_encounter
                )

    @pytest.mark.asyncio
    async def test_chat_history_management(self, chat_request):
        """Test chat history management"""
        
        # Mock the AI client response
        mock_ai_response = Mock()
        mock_ai_response.content = "This is a test response from AI."
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            
            # Set up the async mock chain properly
            mock_ai_client_manager = AsyncMock()
            mock_ai_client_manager.get_client = AsyncMock(return_value=mock_client)
            mock_get_client.return_value = mock_ai_client_manager
            
            # First chat message
            result1 = await ai_service.chat_with_ai(chat_request)
            conversation_id = result1.conversation_id
            
            # Get chat history
            history = await ai_service.get_chat_history(conversation_id)
            assert history is not None
            assert len(history.messages) == 2  # User + AI message
            
            # Second chat message in same conversation
            chat_request.conversation_id = conversation_id
            chat_request.message = "Follow-up question"
            
            result2 = await ai_service.chat_with_ai(chat_request)
            assert result2.conversation_id == conversation_id
            
            # Check updated history
            updated_history = await ai_service.get_chat_history(conversation_id)
            assert len(updated_history.messages) == 4  # 2 user + 2 AI messages
            
            # Clear history
            success = await ai_service.clear_chat_history(conversation_id)
            assert success is True
            
            # Verify history is cleared
            cleared_history = await ai_service.get_chat_history(conversation_id)
            assert cleared_history is None

    @pytest.mark.asyncio
    async def test_ai_service_error_handling(self, chat_request):
        """Test AI service error handling"""
        
        with patch('app.services.ai_service.get_ai_client') as mock_get_client:
            # Mock AI client to raise an exception
            mock_get_client.side_effect = Exception("AI service unavailable")
            
            with pytest.raises(AIServiceException):
                await ai_service.chat_with_ai(chat_request)

    def test_confidence_determination(self):
        """Test confidence level determination logic"""
        
        # Test high confidence (multiple fields)
        high_confidence_data = {
            "chief_complaint": "Chest pain",
            "history_present_illness": "Sharp pain",
            "physical_examination": "Normal"
        }
        confidence = ai_service._determine_confidence(None, high_confidence_data)
        assert confidence == ConfidenceLevel.HIGH
        
        # Test medium confidence (2 fields)
        medium_confidence_data = {
            "chief_complaint": "Chest pain",
            "history_present_illness": "Sharp pain"
        }
        confidence = ai_service._determine_confidence(None, medium_confidence_data)
        assert confidence == ConfidenceLevel.MEDIUM
        
        # Test low confidence (1 field or raw content)
        low_confidence_data = {
            "raw_content": "Unstructured text"
        }
        confidence = ai_service._determine_confidence(None, low_confidence_data)
        assert confidence == ConfidenceLevel.LOW

    def test_suggestion_extraction(self):
        """Test extraction of suggestions from AI response"""
        
        response_text = """
        The patient presents with chest pain. I recommend ordering an ECG immediately.
        You should also consider checking cardiac markers. Please monitor the patient closely.
        """
        
        suggestions = ai_service._extract_suggestions(response_text)
        
        assert len(suggestions) > 0
        assert any("recommend" in sugg.lower() for sugg in suggestions)
        assert any("consider" in sugg.lower() for sugg in suggestions)

    @pytest.mark.asyncio 
    async def test_soap_extraction_parsing(self):
        """Test SOAP data extraction parsing"""
        
        # Test valid JSON response
        valid_response = 'SOAP_EXTRACTION: {"chief_complaint": "Chest pain", "history_present_illness": "Sharp pain"}'
        result = await ai_service._parse_soap_extraction(valid_response, SOAPSection.SUBJECTIVE)
        
        assert "chief_complaint" in result
        assert result["chief_complaint"] == "Chest pain"
        
        # Test invalid JSON response (fallback to manual extraction)
        invalid_response = "Patient has chest pain and feels unwell"
        result = await ai_service._parse_soap_extraction(invalid_response, SOAPSection.SUBJECTIVE)
        
        assert "raw_content" in result

    def test_documentation_quality_calculation(self):
        """Test documentation quality score calculation"""
        
        current_content = {
            "subjective": {
                "chief_complaint": "Chest pain",
                "history_present_illness": "Sharp pain"
            }
        }
        
        completed_sections = {
            "assessment": {
                "primary_diagnosis": "Acute coronary syndrome"
            },
            "plan": {
                "treatment_plan": "Order ECG and cardiac markers"
            }
        }
        
        quality_score = ai_service._calculate_documentation_quality(
            current_content, completed_sections
        )
        
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0  # Should have some content

    def test_missing_elements_identification(self):
        """Test identification of missing critical elements"""
        
        current_content = {
            "subjective": {
                "chief_complaint": "Chest pain"
                # Missing history_present_illness
            }
        }
        
        completed_sections = {}
        
        missing = ai_service._identify_missing_elements(
            current_content, completed_sections
        )
        
        assert len(missing) > 0
        assert any("history_present_illness" in element for element in missing)
        assert any("vital_signs" in element for element in missing)
        assert any("primary_diagnosis" in element for element in missing)


if __name__ == "__main__":
    pytest.main([__file__])