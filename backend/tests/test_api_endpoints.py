"""
API endpoint tests for DiagnoAssist Backend
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.patient import PatientModel, PatientDemographics, MedicalBackground
from app.models.encounter import EncounterModel, EncounterStatusEnum, EncounterTypeEnum, ProviderInfo
from app.models.episode import EpisodeModel, EpisodeCategoryEnum
from app.models.auth import UserModel, UserRoleEnum, UserStatusEnum, UserLoginRequest, UserRegistrationRequest, UserProfile
from app.models.soap import SOAPModel, SOAPSubjective, SOAPAssessment, SOAPPlan
from app.core.security import create_access_token


@pytest.mark.api
@pytest.mark.asyncio
class TestPatientAPI:
    """Test patient API endpoints"""
    
    async def test_create_patient_endpoint(self, sample_patient: PatientModel):
        """Test creating patient via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Mock the repository
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_repo.create.return_value = sample_patient
                
                response = await ac.post(
                    "/api/v1/patients/",
                    json=sample_patient.model_dump()
                )
                
                assert response.status_code == 201
                assert response.json()["demographics"]["name"] == sample_patient.demographics.name
    
    async def test_get_patient_endpoint(self, sample_patient: PatientModel):
        """Test getting patient by ID via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_repo.get_by_id.return_value = sample_patient
                
                response = await ac.get(f"/api/v1/patients/{sample_patient.id}")
                
                assert response.status_code == 200
                assert response.json()["demographics"]["name"] == sample_patient.demographics.name
    
    async def test_get_patient_not_found(self):
        """Test getting non-existent patient"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_repo.get_by_id.return_value = None
                
                response = await ac.get("/api/v1/patients/nonexistent")
                
                assert response.status_code == 404
    
    async def test_update_patient_endpoint(self, sample_patient: PatientModel):
        """Test updating patient via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                updated_patient = sample_patient.model_copy()
                updated_patient.demographics.name = "Updated Name"
                mock_repo.update.return_value = updated_patient
                
                response = await ac.put(
                    f"/api/v1/patients/{sample_patient.id}",
                    json=updated_patient.model_dump()
                )
                
                assert response.status_code == 200
                assert response.json()["demographics"]["name"] == "Updated Name"
    
    async def test_delete_patient_endpoint(self, sample_patient: PatientModel):
        """Test deleting patient via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_repo.delete.return_value = None
                
                response = await ac.delete(f"/api/v1/patients/{sample_patient.id}")
                
                assert response.status_code == 204
    
    async def test_search_patients_endpoint(self):
        """Test searching patients via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_patients = [Mock(), Mock()]
                mock_repo.get_by_demographics_filter.return_value = mock_patients
                
                response = await ac.get("/api/v1/patients/search?name=John")
                
                assert response.status_code == 200
                assert len(response.json()) == 2


@pytest.mark.api
@pytest.mark.asyncio
class TestEncounterAPI:
    """Test encounter API endpoints"""
    
    def get_auth_headers(self, user_id: str = "U001"):
        """Get authentication headers for testing"""
        token = create_access_token(data={"sub": user_id})
        return {"Authorization": f"Bearer {token}"}
    
    async def test_create_encounter_endpoint(self, sample_encounter: EncounterModel):
        """Test creating encounter via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                mock_service.create_encounter.return_value = sample_encounter
                
                response = await ac.post(
                    "/api/v1/encounters/",
                    json=sample_encounter.model_dump(),
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 201
                assert response.json()["patient_id"] == sample_encounter.patient_id
    
    async def test_get_encounter_endpoint(self, sample_encounter: EncounterModel):
        """Test getting encounter by ID via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                mock_service.get_encounter_with_validation.return_value = sample_encounter
                
                response = await ac.get(
                    f"/api/v1/encounters/{sample_encounter.id}",
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["patient_id"] == sample_encounter.patient_id
    
    async def test_update_soap_endpoint(self, sample_encounter: EncounterModel):
        """Test updating SOAP documentation via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                updated_encounter = sample_encounter.model_copy()
                updated_encounter.soap = SOAPModel(
                    subjective=SOAPSubjective(chief_complaint="Updated complaint")
                )
                mock_service.update_soap.return_value = updated_encounter
                
                soap_data = {
                    "subjective": {"chief_complaint": "Updated complaint"}
                }
                
                response = await ac.put(
                    f"/api/v1/encounters/{sample_encounter.id}/soap",
                    json=soap_data,
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["soap"]["subjective"]["chief_complaint"] == "Updated complaint"
    
    async def test_sign_encounter_endpoint(self, sample_encounter: EncounterModel):
        """Test signing encounter via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                signed_encounter = sample_encounter.model_copy()
                signed_encounter.status = EncounterStatusEnum.SIGNED
                signed_encounter.signed_at = datetime.utcnow()
                signed_encounter.signed_by = "U001"
                mock_service.sign_encounter.return_value = signed_encounter
                
                response = await ac.post(
                    f"/api/v1/encounters/{sample_encounter.id}/sign",
                    json={"notes": "Signing encounter"},
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["status"] == "SIGNED"
                assert response.json()["signed_by"] == "U001"
    
    async def test_validate_encounter_endpoint(self, sample_encounter: EncounterModel):
        """Test encounter validation via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                validation_result = {
                    "encounter_id": sample_encounter.id,
                    "can_be_signed": False,
                    "missing_sections": ["Chief Complaint", "Primary Diagnosis"],
                    "warnings": []
                }
                mock_service.validate_encounter_completeness.return_value = validation_result
                
                response = await ac.get(
                    f"/api/v1/encounters/{sample_encounter.id}/validate",
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["can_be_signed"] is False
                assert len(response.json()["missing_sections"]) == 2
    
    async def test_cancel_encounter_endpoint(self, sample_encounter: EncounterModel):
        """Test cancelling encounter via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.encounters.encounter_service') as mock_service:
                cancelled_encounter = sample_encounter.model_copy()
                cancelled_encounter.status = EncounterStatusEnum.CANCELLED
                mock_service.cancel_encounter.return_value = cancelled_encounter
                
                response = await ac.post(
                    f"/api/v1/encounters/{sample_encounter.id}/cancel",
                    json={"reason": "Patient no-show"},
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["status"] == "CANCELLED"


@pytest.mark.api
@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication API endpoints"""
    
    async def test_register_endpoint(self, sample_user: UserModel):
        """Test user registration via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.auth.auth_service') as mock_service:
                mock_service.register_user.return_value = sample_user
                
                registration_data = {
                    "email": sample_user.email,
                    "password": "testpassword",
                    "role": sample_user.role.value,
                    "profile": sample_user.profile.model_dump()
                }
                
                response = await ac.post(
                    "/api/v1/auth/register",
                    json=registration_data
                )
                
                assert response.status_code == 201
                assert response.json()["email"] == sample_user.email
    
    async def test_login_endpoint(self, sample_user: UserModel):
        """Test user login via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.auth.auth_service') as mock_service:
                mock_service.authenticate_user.return_value = sample_user
                
                login_data = {
                    "email": sample_user.email,
                    "password": "testpassword"
                }
                
                response = await ac.post(
                    "/api/v1/auth/login",
                    json=login_data
                )
                
                assert response.status_code == 200
                assert "access_token" in response.json()
                assert response.json()["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.auth.auth_service') as mock_service:
                mock_service.authenticate_user.return_value = None
                
                login_data = {
                    "email": "invalid@test.com",
                    "password": "wrongpassword"
                }
                
                response = await ac.post(
                    "/api/v1/auth/login",
                    json=login_data
                )
                
                assert response.status_code == 401
    
    async def test_get_current_user_endpoint(self, sample_user: UserModel):
        """Test getting current user via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.auth.get_current_user') as mock_get_user:
                mock_get_user.return_value = sample_user
                
                token = create_access_token(data={"sub": sample_user.id})
                headers = {"Authorization": f"Bearer {token}"}
                
                response = await ac.get(
                    "/api/v1/auth/me",
                    headers=headers
                )
                
                assert response.status_code == 200
                assert response.json()["email"] == sample_user.email
    
    async def test_change_password_endpoint(self, sample_user: UserModel):
        """Test changing password via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.auth.auth_service') as mock_service:
                with patch('app.api.v1.auth.get_current_user') as mock_get_user:
                    mock_get_user.return_value = sample_user
                    mock_service.change_password.return_value = True
                    
                    token = create_access_token(data={"sub": sample_user.id})
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    password_data = {
                        "current_password": "oldpassword",
                        "new_password": "newpassword"
                    }
                    
                    response = await ac.post(
                        "/api/v1/auth/change-password",
                        json=password_data,
                        headers=headers
                    )
                    
                    assert response.status_code == 200
                    assert response.json()["message"] == "Password changed successfully"


@pytest.mark.api
@pytest.mark.asyncio
class TestFHIRAPI:
    """Test FHIR API endpoints"""
    
    def get_auth_headers(self, user_id: str = "U001"):
        """Get authentication headers for testing"""
        token = create_access_token(data={"sub": user_id})
        return {"Authorization": f"Bearer {token}"}
    
    async def test_sync_patient_endpoint(self, sample_patient: PatientModel):
        """Test syncing patient with FHIR via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.fhir.patient_repository') as mock_patient_repo:
                with patch('app.api.v1.fhir.fhir_sync_service') as mock_sync_service:
                    mock_patient_repo.get_by_id.return_value = sample_patient
                    
                    mock_sync_response = Mock()
                    mock_sync_response.success = True
                    mock_sync_response.fhir_id = "fhir-123"
                    mock_sync_response.errors = []
                    mock_sync_service.sync_patient.return_value = mock_sync_response
                    
                    response = await ac.post(
                        f"/api/v1/fhir/sync/patient/{sample_patient.id}",
                        headers=self.get_auth_headers()
                    )
                    
                    assert response.status_code == 200
                    assert response.json()["success"] is True
                    assert response.json()["fhir_id"] == "fhir-123"
    
    async def test_get_sync_status_endpoint(self):
        """Test getting sync status via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.fhir.fhir_sync_service') as mock_sync_service:
                mock_status = Mock()
                mock_status.entity_id = "P001"
                mock_status.entity_type = "patient"
                mock_status.fhir_id = "fhir-123"
                mock_status.sync_status = "synced"
                mock_status.last_sync_at = datetime.utcnow()
                mock_sync_service.get_sync_status.return_value = mock_status
                
                response = await ac.get(
                    "/api/v1/fhir/sync/status/P001/patient",
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["entity_id"] == "P001"
                assert response.json()["sync_status"] == "synced"
    
    async def test_test_fhir_connectivity_endpoint(self):
        """Test FHIR connectivity testing via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.fhir.fhir_sync_service') as mock_sync_service:
                mock_connectivity = {
                    "available": True,
                    "connection": True,
                    "capabilities": {"resourceType": "CapabilityStatement"},
                    "error": None
                }
                mock_sync_service.test_fhir_connectivity.return_value = mock_connectivity
                
                response = await ac.get(
                    "/api/v1/fhir/connectivity",
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["available"] is True
                assert response.json()["connection"] is True
    
    async def test_bulk_sync_endpoint(self):
        """Test bulk synchronization via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.fhir.fhir_sync_service') as mock_sync_service:
                mock_results = {
                    "total": 10,
                    "success": 8,
                    "failed": 2,
                    "errors": ["Connection timeout", "Invalid data"]
                }
                mock_sync_service.sync_all_patients.return_value = mock_results
                
                response = await ac.post(
                    "/api/v1/fhir/sync/bulk/patients",
                    params={"max_patients": 10},
                    headers=self.get_auth_headers()
                )
                
                assert response.status_code == 200
                assert response.json()["total"] == 10
                assert response.json()["success"] == 8
                assert response.json()["failed"] == 2


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
class TestAPIIntegration:
    """Test complete API workflows"""
    
    def get_auth_headers(self, user_id: str = "U001"):
        """Get authentication headers for testing"""
        token = create_access_token(data={"sub": user_id})
        return {"Authorization": f"Bearer {token}"}
    
    async def test_complete_patient_encounter_workflow(self):
        """Test complete patient and encounter workflow via API"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Mock all services
            with patch('app.api.v1.patients.patient_repository') as mock_patient_repo, \
                 patch('app.api.v1.episodes.episode_repository') as mock_episode_repo, \
                 patch('app.api.v1.encounters.encounter_service') as mock_encounter_service:
                
                # Create patient
                mock_patient = Mock()
                mock_patient.id = "P001"
                mock_patient.demographics.name = "Test Patient"
                mock_patient_repo.create.return_value = mock_patient
                
                patient_data = {
                    "demographics": {
                        "name": "Test Patient",
                        "email": "test@example.com"
                    },
                    "medical_background": {}
                }
                
                patient_response = await ac.post(
                    "/api/v1/patients/",
                    json=patient_data
                )
                assert patient_response.status_code == 201
                
                # Create episode
                mock_episode = Mock()
                mock_episode.id = "E001"
                mock_episode.patient_id = "P001"
                mock_episode_repo.create.return_value = mock_episode
                
                episode_data = {
                    "patient_id": "P001",
                    "chief_complaint": "Annual checkup",
                    "category": "ROUTINE_CARE"
                }
                
                episode_response = await ac.post(
                    "/api/v1/episodes/",
                    json=episode_data,
                    headers=self.get_auth_headers()
                )
                assert episode_response.status_code == 201
                
                # Create encounter
                mock_encounter = Mock()
                mock_encounter.id = "ENC001"
                mock_encounter.patient_id = "P001"
                mock_encounter.episode_id = "E001"
                mock_encounter.status = EncounterStatusEnum.DRAFT
                mock_encounter_service.create_encounter.return_value = mock_encounter
                
                encounter_data = {
                    "patient_id": "P001",
                    "episode_id": "E001",
                    "type": "ROUTINE_VISIT",
                    "provider": {
                        "id": "U001",
                        "name": "Dr. Test",
                        "specialty": "Internal Medicine",
                        "department": "Internal Medicine"
                    }
                }
                
                encounter_response = await ac.post(
                    "/api/v1/encounters/",
                    json=encounter_data,
                    headers=self.get_auth_headers()
                )
                assert encounter_response.status_code == 201
    
    async def test_error_handling_workflow(self):
        """Test API error handling"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Test 404 for non-existent patient
            with patch('app.api.v1.patients.patient_repository') as mock_repo:
                mock_repo.get_by_id.return_value = None
                
                response = await ac.get("/api/v1/patients/nonexistent")
                assert response.status_code == 404
            
            # Test 401 for unauthenticated access
            response = await ac.get("/api/v1/encounters/test123")
            assert response.status_code == 401
            
            # Test 400 for invalid data
            invalid_patient_data = {
                "demographics": {
                    "name": "",  # Invalid empty name
                    "email": "invalid-email"  # Invalid email format
                }
            }
            
            response = await ac.post(
                "/api/v1/patients/",
                json=invalid_patient_data
            )
            assert response.status_code == 422  # Validation error