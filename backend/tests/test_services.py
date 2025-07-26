"""
Service layer tests for DiagnoAssist Backend
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.models.encounter import EncounterModel, EncounterStatusEnum, EncounterTypeEnum, ProviderInfo
from app.models.patient import PatientModel
from app.models.episode import EpisodeModel
from app.models.soap import SOAPModel, SOAPSubjective, SOAPAssessment, SOAPPlan
from app.models.auth import UserModel, UserRoleEnum, UserStatusEnum
from app.services.encounter_service import EncounterService
from app.services.auth_service import AuthService
from app.core.exceptions import NotFoundError, ValidationException, AuthenticationException


@pytest.mark.service
@pytest.mark.asyncio
class TestEncounterService:
    """Test encounter service business logic"""
    
    @patch('app.services.encounter_service.patient_repository')
    @patch('app.services.encounter_service.episode_repository')
    @patch('app.services.encounter_service.encounter_repository')
    async def test_create_encounter_with_validation(self, mock_encounter_repo, mock_episode_repo, mock_patient_repo):
        """Test encounter creation with proper validation"""
        # Mock repositories
        mock_patient = Mock()
        mock_patient.id = "P001"
        mock_patient_repo.get_by_id.return_value = mock_patient
        
        mock_episode = Mock()
        mock_episode.id = "E001"
        mock_episode.patient_id = "P001"
        mock_episode_repo.get_by_id.return_value = mock_episode
        
        mock_created_encounter = Mock()
        mock_created_encounter.id = "ENC001"
        mock_encounter_repo.create.return_value = mock_created_encounter
        
        # Create encounter
        encounter = EncounterModel(
            patient_id="P001",
            episode_id="E001",
            type=EncounterTypeEnum.ROUTINE_VISIT,
            provider=ProviderInfo(
                id="U001",
                name="Dr. Test",
                specialty="Internal Medicine",
                department="Internal Medicine"
            )
        )
        
        service = EncounterService()
        created_encounter = await service.create_encounter(encounter)
        
        assert created_encounter.id == "ENC001"
        mock_patient_repo.get_by_id.assert_called_once_with("P001")
        mock_episode_repo.get_by_id.assert_called_once_with("E001")
        mock_encounter_repo.create.assert_called_once()
    
    @patch('app.services.encounter_service.patient_repository')
    async def test_create_encounter_patient_not_found(self, mock_patient_repo):
        """Test encounter creation fails when patient not found"""
        mock_patient_repo.get_by_id.return_value = None
        
        encounter = EncounterModel(
            patient_id="NONEXISTENT",
            type=EncounterTypeEnum.ROUTINE_VISIT,
            provider=ProviderInfo(id="U001", name="Dr. Test", specialty="Test", department="Test")
        )
        
        service = EncounterService()
        
        with pytest.raises(NotFoundError) as exc_info:
            await service.create_encounter(encounter)
        
        assert "Patient" in str(exc_info.value)
        assert "NONEXISTENT" in str(exc_info.value)
    
    @patch('app.services.encounter_service.patient_repository')
    @patch('app.services.encounter_service.episode_repository')
    async def test_create_encounter_episode_patient_mismatch(self, mock_episode_repo, mock_patient_repo):
        """Test encounter creation fails when episode doesn't belong to patient"""
        mock_patient = Mock()
        mock_patient.id = "P001"
        mock_patient_repo.get_by_id.return_value = mock_patient
        
        mock_episode = Mock()
        mock_episode.id = "E001"
        mock_episode.patient_id = "P002"  # Different patient
        mock_episode_repo.get_by_id.return_value = mock_episode
        
        encounter = EncounterModel(
            patient_id="P001",
            episode_id="E001",
            type=EncounterTypeEnum.ROUTINE_VISIT,
            provider=ProviderInfo(id="U001", name="Dr. Test", specialty="Test", department="Test")
        )
        
        service = EncounterService()
        
        with pytest.raises(ValidationException) as exc_info:
            await service.create_encounter(encounter)
        
        assert "Episode does not belong to the specified patient" in str(exc_info.value)
    
    @patch('app.services.encounter_service.encounter_repository')
    async def test_update_encounter_prevents_signed_modification(self, mock_encounter_repo):
        """Test that signed encounters cannot be modified"""
        mock_encounter = Mock()
        mock_encounter.id = "ENC001"
        mock_encounter.status = EncounterStatusEnum.SIGNED
        mock_encounter_repo.get_by_id.return_value = mock_encounter
        
        service = EncounterService()
        
        with pytest.raises(ValidationException) as exc_info:
            await service.update_encounter("ENC001", mock_encounter)
        
        assert "Cannot modify a signed encounter" in str(exc_info.value)
    
    @patch('app.services.encounter_service.encounter_repository')
    @patch('app.services.encounter_service.fhir_sync')
    async def test_sign_encounter_triggers_fhir_sync(self, mock_fhir_sync, mock_encounter_repo):
        """Test that signing an encounter triggers FHIR synchronization"""
        # Mock encounter
        mock_encounter = Mock()
        mock_encounter.id = "ENC001"
        mock_encounter.status = EncounterStatusEnum.IN_PROGRESS
        mock_encounter.soap = SOAPModel(
            subjective=SOAPSubjective(chief_complaint="Test complaint")
        )
        mock_encounter_repo.get_by_id.return_value = mock_encounter
        
        # Mock updated encounter
        mock_signed_encounter = Mock()
        mock_signed_encounter.id = "ENC001"
        mock_signed_encounter.status = EncounterStatusEnum.SIGNED
        mock_encounter_repo.update.return_value = mock_signed_encounter
        
        # Mock FHIR sync
        mock_sync_response = Mock()
        mock_sync_response.success = True
        mock_fhir_sync.auto_sync_on_encounter_sign.return_value = mock_sync_response
        
        service = EncounterService()
        signed_encounter = await service.sign_encounter("ENC001", "U001", "Signing notes")
        
        assert signed_encounter.status == EncounterStatusEnum.SIGNED
        mock_fhir_sync.auto_sync_on_encounter_sign.assert_called_once_with("ENC001")
    
    @patch('app.services.encounter_service.encounter_repository')
    async def test_sign_encounter_validation(self, mock_encounter_repo):
        """Test encounter signing validation"""
        # Test signing already signed encounter
        mock_signed_encounter = Mock()
        mock_signed_encounter.status = EncounterStatusEnum.SIGNED
        mock_encounter_repo.get_by_id.return_value = mock_signed_encounter
        
        service = EncounterService()
        
        with pytest.raises(ValidationException) as exc_info:
            await service.sign_encounter("ENC001", "U001")
        
        assert "Encounter is already signed" in str(exc_info.value)
        
        # Test signing cancelled encounter
        mock_cancelled_encounter = Mock()
        mock_cancelled_encounter.status = EncounterStatusEnum.CANCELLED
        mock_encounter_repo.get_by_id.return_value = mock_cancelled_encounter
        
        with pytest.raises(ValidationException) as exc_info:
            await service.sign_encounter("ENC001", "U001")
        
        assert "Cannot sign a cancelled encounter" in str(exc_info.value)
        
        # Test signing encounter without chief complaint
        mock_incomplete_encounter = Mock()
        mock_incomplete_encounter.status = EncounterStatusEnum.IN_PROGRESS
        mock_incomplete_encounter.soap = SOAPModel()  # Empty SOAP
        mock_encounter_repo.get_by_id.return_value = mock_incomplete_encounter
        
        with pytest.raises(ValidationException) as exc_info:
            await service.sign_encounter("ENC001", "U001")
        
        assert "chief complaint" in str(exc_info.value).lower()
    
    @patch('app.services.encounter_service.encounter_repository')
    async def test_cancel_encounter(self, mock_encounter_repo):
        """Test encounter cancellation"""
        mock_encounter = Mock()
        mock_encounter.id = "ENC001"
        mock_encounter.status = EncounterStatusEnum.IN_PROGRESS
        mock_encounter.soap = SOAPModel(plan=SOAPPlan())
        mock_encounter_repo.get_by_id.return_value = mock_encounter
        
        mock_cancelled_encounter = Mock()
        mock_cancelled_encounter.status = EncounterStatusEnum.CANCELLED
        mock_encounter_repo.update.return_value = mock_cancelled_encounter
        
        service = EncounterService()
        cancelled_encounter = await service.cancel_encounter("ENC001", "Patient no-show", "U001")
        
        assert cancelled_encounter.status == EncounterStatusEnum.CANCELLED
        mock_encounter_repo.update.assert_called_once()
    
    @patch('app.services.encounter_service.encounter_repository')
    async def test_validate_encounter_completeness(self, mock_encounter_repo):
        """Test encounter documentation completeness validation"""
        # Complete encounter
        complete_encounter = Mock()
        complete_encounter.id = "ENC001"
        complete_encounter.soap = SOAPModel(
            subjective=SOAPSubjective(
                chief_complaint="Test complaint",
                history_of_present_illness="Test HPI"
            ),
            assessment=SOAPAssessment(primary_diagnosis="Test diagnosis")
        )
        mock_encounter_repo.get_by_id.return_value = complete_encounter
        
        service = EncounterService()
        validation = await service.validate_encounter_completeness("ENC001")
        
        assert validation["encounter_id"] == "ENC001"
        assert validation["can_be_signed"] is True
        assert len(validation["missing_sections"]) == 0
        
        # Incomplete encounter
        incomplete_encounter = Mock()
        incomplete_encounter.soap = SOAPModel()  # Empty SOAP
        mock_encounter_repo.get_by_id.return_value = incomplete_encounter
        
        validation = await service.validate_encounter_completeness("ENC001")
        
        assert validation["can_be_signed"] is False
        assert "Chief Complaint" in validation["missing_sections"]
        assert "Primary Diagnosis" in validation["missing_sections"]


@pytest.mark.service
@pytest.mark.asyncio
class TestAuthService:
    """Test authentication service"""
    
    @patch('app.services.auth_service.user_repository')
    async def test_register_user(self, mock_user_repo):
        """Test user registration"""
        # Mock no existing user
        mock_user_repo.get_by_email.return_value = None
        
        # Mock created user
        mock_created_user = Mock()
        mock_created_user.id = "U001"
        mock_created_user.email = "test@example.com"
        mock_user_repo.create.return_value = mock_created_user
        
        from app.models.auth import UserRegistrationRequest, UserProfile
        registration_data = UserRegistrationRequest(
            email="test@example.com",
            password="testpassword",
            role=UserRoleEnum.DOCTOR,
            profile=UserProfile(
                first_name="Test",
                last_name="User"
            )
        )
        
        service = AuthService()
        created_user = await service.register_user(registration_data)
        
        assert created_user.id == "U001"
        assert created_user.email == "test@example.com"
        mock_user_repo.create.assert_called_once()
    
    @patch('app.services.auth_service.user_repository')
    async def test_register_duplicate_user(self, mock_user_repo):
        """Test registration with duplicate email"""
        # Mock existing user
        mock_existing_user = Mock()
        mock_user_repo.get_by_email.return_value = mock_existing_user
        
        from app.models.auth import UserRegistrationRequest, UserProfile
        registration_data = UserRegistrationRequest(
            email="existing@example.com",
            password="testpassword",
            role=UserRoleEnum.DOCTOR,
            profile=UserProfile(first_name="Test", last_name="User")
        )
        
        service = AuthService()
        
        with pytest.raises(Exception):  # Should raise ConflictException
            await service.register_user(registration_data)
    
    @patch('app.services.auth_service.user_repository')
    @patch('app.services.auth_service.verify_password')
    async def test_authenticate_user_success(self, mock_verify_password, mock_user_repo):
        """Test successful user authentication"""
        # Mock user
        mock_user = Mock()
        mock_user.id = "U001"
        mock_user.email = "test@example.com"
        mock_user.status = UserStatusEnum.ACTIVE
        mock_user.hashed_password = "hashed_password"
        mock_user_repo.get_by_email.return_value = mock_user
        mock_user_repo.update_last_login.return_value = mock_user
        mock_user_repo.get_by_id.return_value = mock_user
        
        # Mock password verification
        mock_verify_password.return_value = True
        
        from app.models.auth import UserLoginRequest
        login_data = UserLoginRequest(
            email="test@example.com",
            password="testpassword"
        )
        
        service = AuthService()
        authenticated_user = await service.authenticate_user(login_data)
        
        assert authenticated_user is not None
        assert authenticated_user.id == "U001"
        mock_user_repo.update_last_login.assert_called_once_with("U001")
    
    @patch('app.services.auth_service.user_repository')
    @patch('app.services.auth_service.verify_password')
    async def test_authenticate_user_wrong_password(self, mock_verify_password, mock_user_repo):
        """Test authentication with wrong password"""
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Mock password verification failure
        mock_verify_password.return_value = False
        
        from app.models.auth import UserLoginRequest
        login_data = UserLoginRequest(
            email="test@example.com",
            password="wrongpassword"
        )
        
        service = AuthService()
        authenticated_user = await service.authenticate_user(login_data)
        
        assert authenticated_user is None
    
    @patch('app.services.auth_service.user_repository')
    @patch('app.services.auth_service.verify_password')
    async def test_authenticate_suspended_user(self, mock_verify_password, mock_user_repo):
        """Test authentication with suspended user"""
        mock_user = Mock()
        mock_user.status = UserStatusEnum.SUSPENDED
        mock_user.hashed_password = "hashed_password"
        mock_user_repo.get_by_email.return_value = mock_user
        mock_verify_password.return_value = True
        
        from app.models.auth import UserLoginRequest
        login_data = UserLoginRequest(
            email="test@example.com",
            password="testpassword"
        )
        
        service = AuthService()
        
        with pytest.raises(AuthenticationException) as exc_info:
            await service.authenticate_user(login_data)
        
        assert "suspended" in str(exc_info.value).lower()
    
    @patch('app.services.auth_service.user_repository')
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.get_password_hash')
    async def test_change_password(self, mock_get_hash, mock_verify_password, mock_user_repo):
        """Test password change"""
        mock_user = Mock()
        mock_user.id = "U001"
        mock_user.hashed_password = "old_hashed_password"
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_verify_password.return_value = True
        mock_get_hash.return_value = "new_hashed_password"
        
        service = AuthService()
        success = await service.change_password("U001", "oldpassword", "newpassword")
        
        assert success is True
        mock_user_repo.update_password.assert_called_once_with("U001", "new_hashed_password")
    
    @patch('app.services.auth_service.user_repository')
    @patch('app.services.auth_service.verify_password')
    async def test_change_password_wrong_current(self, mock_verify_password, mock_user_repo):
        """Test password change with wrong current password"""
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_verify_password.return_value = False
        
        service = AuthService()
        
        with pytest.raises(AuthenticationException) as exc_info:
            await service.change_password("U001", "wrongpassword", "newpassword")
        
        assert "Current password is incorrect" in str(exc_info.value)


@pytest.mark.service
@pytest.mark.integration
@pytest.mark.asyncio
class TestServiceIntegration:
    """Test service layer integration"""
    
    async def test_encounter_service_with_real_data(self, sample_data_set):
        """Test encounter service with real data"""
        user = sample_data_set["user"]
        patient = sample_data_set["patient"]
        episode = sample_data_set["episode"]
        encounter = sample_data_set["encounter"]
        
        # Test getting encounter with validation
        from app.services.encounter_service import encounter_service
        retrieved_encounter = await encounter_service.get_encounter_with_validation(encounter.id)
        
        assert retrieved_encounter.id == encounter.id
        assert retrieved_encounter.patient_id == patient.id
        assert retrieved_encounter.episode_id == episode.id
    
    async def test_encounter_validation_flow(self, sample_data_set):
        """Test complete encounter validation flow"""
        encounter = sample_data_set["encounter"]
        
        from app.services.encounter_service import encounter_service
        
        # Test validation of incomplete encounter
        validation = await encounter_service.validate_encounter_completeness(encounter.id)
        
        assert validation["encounter_id"] == encounter.id
        # Should have warnings or missing sections for incomplete encounter
        assert len(validation["missing_sections"]) > 0 or len(validation["warnings"]) > 0
    
    @patch('app.services.encounter_service.fhir_sync')
    async def test_encounter_signing_workflow(self, mock_fhir_sync, sample_data_set):
        """Test complete encounter signing workflow"""
        encounter = sample_data_set["encounter"]
        user = sample_data_set["user"]
        
        # Mock FHIR sync
        mock_sync_response = Mock()
        mock_sync_response.success = True
        mock_fhir_sync.auto_sync_on_encounter_sign.return_value = mock_sync_response
        
        from app.services.encounter_service import encounter_service
        
        # First, update SOAP to make it signable
        from app.models.soap import SOAPModel, SOAPSubjective, SOAPAssessment
        complete_soap = SOAPModel(
            subjective=SOAPSubjective(chief_complaint="Complete chief complaint"),
            assessment=SOAPAssessment(primary_diagnosis="Complete diagnosis")
        )
        
        await encounter_service.update_soap(encounter.id, complete_soap)
        
        # Now sign the encounter
        signed_encounter = await encounter_service.sign_encounter(
            encounter.id, 
            user.id, 
            "Test signing"
        )
        
        assert signed_encounter.status == EncounterStatusEnum.SIGNED
        assert signed_encounter.signed_by == user.id
        assert signed_encounter.signed_at is not None
        
        # Verify FHIR sync was triggered
        mock_fhir_sync.auto_sync_on_encounter_sign.assert_called_once_with(encounter.id)