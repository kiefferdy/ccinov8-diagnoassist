"""
FHIR integration tests for DiagnoAssist Backend
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.models.patient import PatientModel, PatientDemographics, MedicalBackground
from app.models.encounter import EncounterModel, EncounterTypeEnum, EncounterStatusEnum, Provider
from app.models.soap import SOAPModel, SubjectiveSection, ObjectiveSection, AssessmentSection, PlanSection, VitalSigns
from app.models.fhir_models import FHIRSyncResponse
from app.repositories.fhir_repository import FHIRRepository
from app.services.fhir_sync_service import FHIRSyncService, SyncStrategy
from app.utils.fhir_mappers import FHIRMapper


@pytest.mark.fhir
@pytest.mark.asyncio
class TestFHIRMappers:
    """Test FHIR mapping functionality"""
    
    def test_patient_to_fhir_mapping(self, sample_patient: PatientModel):
        """Test converting patient model to FHIR patient"""
        fhir_patient = FHIRMapper.patient_to_fhir(sample_patient)
        
        assert fhir_patient is not None
        assert fhir_patient.active is True
        
        # Check name mapping
        assert len(fhir_patient.name) > 0
        name = fhir_patient.name[0]
        assert name.text == sample_patient.demographics.name
        
        # Check gender mapping
        expected_gender = sample_patient.demographics.gender.lower() if sample_patient.demographics.gender else "unknown"
        assert fhir_patient.gender == expected_gender
        
        # Check contact info
        if sample_patient.demographics.phone or sample_patient.demographics.email:
            assert fhir_patient.telecom is not None
            assert len(fhir_patient.telecom) > 0
    
    def test_fhir_to_patient_mapping(self):
        """Test converting FHIR patient to patient model"""
        # Create mock FHIR patient
        from fhirclient.models import patient as fhir_patient, humanname, contactpoint, fhirdate
        
        mock_fhir_patient = Mock()
        mock_fhir_patient.id = "fhir-123"
        mock_fhir_patient.active = True
        mock_fhir_patient.gender = "male"
        mock_fhir_patient.birthDate = fhirdate.FHIRDate("1985-01-15")
        
        # Mock name
        mock_name = Mock()
        mock_name.text = "John Doe"
        mock_name.given = ["John"]
        mock_name.family = "Doe"
        mock_fhir_patient.name = [mock_name]
        
        # Mock telecom
        mock_phone = Mock()
        mock_phone.system = "phone"
        mock_phone.value = "+1-555-0123"
        
        mock_email = Mock()
        mock_email.system = "email"
        mock_email.value = "john.doe@test.com"
        
        mock_fhir_patient.telecom = [mock_phone, mock_email]
        
        # Mock identifier
        mock_identifier = Mock()
        mock_identifier.system = "urn:diagnoassist:patient-id"
        mock_identifier.value = "P001"
        mock_fhir_patient.identifier = [mock_identifier]
        
        # Convert to patient model
        patient = FHIRMapper.fhir_to_patient(mock_fhir_patient)
        
        assert patient.id == "P001"
        assert patient.demographics.name == "John Doe"
        assert patient.demographics.gender == "Male"
        assert patient.demographics.phone == "+1-555-0123"
        assert patient.demographics.email == "john.doe@test.com"
    
    def test_soap_to_fhir_observations(self):
        """Test converting SOAP data to FHIR observations"""
        soap = SOAPModel(
            subjective=SubjectiveSection(
                chief_complaint="Chest pain",
                history_of_present_illness="Patient reports chest pain for 2 hours"
            ),
            objective=ObjectiveSection(
                vital_signs=VitalSigns(
                    blood_pressure="140/90 mmHg",
                    heart_rate="85 bpm",
                    temperature="98.6°F"
                ),
                physical_examination="Heart regular rate and rhythm"
            )
        )
        
        observations = FHIRMapper.soap_to_fhir_observations(
            soap, 
            patient_fhir_id="Patient/123"
        )
        
        assert len(observations) > 0
        
        # Check that observations were created for different SOAP sections
        observation_codes = [obs.code.text for obs in observations if obs.code and obs.code.text]
        
        assert "Chief Complaint" in observation_codes
        assert "History of Present Illness" in observation_codes
        assert any("Blood Pressure" in code for code in observation_codes)
    
    def test_encounter_to_fhir_mapping(self):
        """Test converting encounter to FHIR encounter"""
        encounter = EncounterModel(
            patient_id="P001",
            type=EncounterTypeEnum.ROUTINE_VISIT,
            status=EncounterStatusEnum.SIGNED,
            provider=Provider(
                id="U001",
                name="Dr. Test",
                specialty="Internal Medicine",
                department="Internal Medicine"
            ),
            signed_at=datetime.utcnow()
        )
        
        fhir_encounter = FHIRMapper.encounter_to_fhir(encounter, "Patient/123")
        
        assert fhir_encounter.status == "finished"  # SIGNED maps to finished
        assert fhir_encounter.class_.code == "AMB"  # ROUTINE_VISIT maps to ambulatory
        assert fhir_encounter.subject.reference == "Patient/123"
        assert fhir_encounter.period is not None


@pytest.mark.fhir
@pytest.mark.asyncio
class TestFHIRRepository:
    """Test FHIR repository operations"""
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_fhir_repository_availability(self, mock_get_client):
        """Test FHIR repository availability checking"""
        # Test when FHIR client is available
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        repo = FHIRRepository()
        assert repo.is_available() is True
        
        # Test when FHIR client is not available
        mock_get_client.return_value = None
        repo = FHIRRepository()
        assert repo.is_available() is False
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_create_patient_in_fhir(self, mock_get_client, sample_patient: PatientModel):
        """Test creating patient in FHIR"""
        mock_client = Mock()
        mock_client.create_patient.return_value = "fhir-patient-123"
        mock_get_client.return_value = mock_client
        
        repo = FHIRRepository()
        fhir_id = await repo.create_patient(sample_patient)
        
        assert fhir_id == "fhir-patient-123"
        mock_client.create_patient.assert_called_once()
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_sync_patient_data(self, mock_get_client, sample_patient: PatientModel):
        """Test syncing patient data with FHIR"""
        mock_client = Mock()
        mock_client.create_patient.return_value = "fhir-patient-123"
        mock_get_client.return_value = mock_client
        
        repo = FHIRRepository()
        sync_response = await repo.sync_patient_data(sample_patient)
        
        assert sync_response.success is True
        assert sync_response.fhir_id == "fhir-patient-123"
        assert sync_response.errors == []
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_create_soap_observations(self, mock_get_client):
        """Test creating FHIR observations from SOAP data"""
        mock_client = Mock()
        mock_client.create_observation.return_value = "obs-123"
        mock_get_client.return_value = mock_client
        
        soap = SOAPModel(
            subjective=SubjectiveSection(chief_complaint="Test complaint")
        )
        
        repo = FHIRRepository()
        observation_ids = await repo.create_soap_observations(
            soap, 
            "Patient/123", 
            "Encounter/456"
        )
        
        assert len(observation_ids) > 0
        assert "obs-123" in observation_ids
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_fhir_unavailable_handling(self, mock_get_client, sample_patient: PatientModel):
        """Test handling when FHIR is unavailable"""
        mock_get_client.return_value = None
        
        repo = FHIRRepository()
        
        # Test create patient when FHIR unavailable
        fhir_id = await repo.create_patient(sample_patient)
        assert fhir_id is None
        
        # Test sync when FHIR unavailable  
        sync_response = await repo.sync_patient_data(sample_patient)
        assert sync_response.success is False
        assert "FHIR server not available" in str(sync_response.errors)


@pytest.mark.fhir
@pytest.mark.asyncio
class TestFHIRSyncService:
    """Test FHIR synchronization service"""
    
    def test_sync_strategy_management(self):
        """Test sync strategy configuration"""
        service = FHIRSyncService()
        
        # Test default strategies
        assert service.get_sync_strategy("patient") == SyncStrategy.HYBRID_MONGODB_PRIMARY
        assert service.get_sync_strategy("episode") == SyncStrategy.MONGODB_ONLY
        
        # Test setting custom strategy
        service.set_sync_strategy("patient", SyncStrategy.FHIR_ONLY)
        assert service.get_sync_strategy("patient") == SyncStrategy.FHIR_ONLY
    
    async def test_sync_status_tracking(self):
        """Test sync status tracking"""
        service = FHIRSyncService()
        
        # Update sync status
        await service.update_sync_status(
            entity_id="P001",
            entity_type="patient", 
            fhir_id="fhir-123",
            status="synced"
        )
        
        # Get sync status
        status = await service.get_sync_status("P001", "patient")
        assert status is not None
        assert status.entity_id == "P001"
        assert status.entity_type == "patient"
        assert status.fhir_id == "fhir-123"
        assert status.sync_status == "synced"
    
    @patch('app.services.fhir_sync_service.fhir_repository')
    async def test_sync_patient_success(self, mock_fhir_repo, sample_patient: PatientModel):
        """Test successful patient synchronization"""
        # Mock FHIR repository
        mock_fhir_repo.is_available.return_value = True
        mock_sync_response = FHIRSyncResponse(success=True, fhir_id="fhir-123")
        mock_fhir_repo.sync_patient_data.return_value = mock_sync_response
        
        service = FHIRSyncService()
        sync_response = await service.sync_patient(sample_patient)
        
        assert sync_response.success is True
        assert sync_response.fhir_id == "fhir-123"
        
        # Verify sync status was updated
        status = await service.get_sync_status(sample_patient.id, "patient")
        assert status.sync_status == "synced"
    
    @patch('app.services.fhir_sync_service.fhir_repository')
    async def test_sync_patient_fhir_unavailable(self, mock_fhir_repo, sample_patient: PatientModel):
        """Test patient sync when FHIR is unavailable"""
        mock_fhir_repo.is_available.return_value = False
        
        service = FHIRSyncService()
        sync_response = await service.sync_patient(sample_patient)
        
        assert sync_response.success is False
        assert "FHIR server not available" in str(sync_response.errors)
        
        # Verify sync status shows failure
        status = await service.get_sync_status(sample_patient.id, "patient")
        assert status.sync_status == "failed"
    
    @patch('app.services.fhir_sync_service.fhir_repository')
    @patch('app.services.fhir_sync_service.patient_repository')
    @patch('app.services.fhir_sync_service.encounter_repository')
    async def test_sync_encounter_on_sign(self, mock_encounter_repo, mock_patient_repo, mock_fhir_repo):
        """Test automatic encounter sync when signed"""
        # Mock repositories
        mock_encounter = Mock()
        mock_encounter.id = "ENC001"
        mock_encounter.patient_id = "P001"
        mock_encounter.status = EncounterStatusEnum.SIGNED
        mock_encounter_repo.get_by_id.return_value = mock_encounter
        
        mock_patient = Mock()
        mock_patient.id = "P001"
        mock_patient_repo.get_by_id.return_value = mock_patient
        
        mock_fhir_repo.is_available.return_value = True
        mock_patient_sync = FHIRSyncResponse(success=True, fhir_id="patient-fhir-123")
        mock_encounter_sync = FHIRSyncResponse(success=True, fhir_id="encounter-fhir-456")
        mock_fhir_repo.sync_patient_data.return_value = mock_patient_sync
        mock_fhir_repo.sync_encounter_data.return_value = mock_encounter_sync
        
        service = FHIRSyncService()
        sync_response = await service.auto_sync_on_encounter_sign("ENC001")
        
        assert sync_response.success is True
        assert sync_response.fhir_id == "encounter-fhir-456"
    
    async def test_sync_statistics(self):
        """Test sync statistics collection"""
        service = FHIRSyncService()
        
        # Add some sync statuses
        await service.update_sync_status("P001", "patient", fhir_id="fhir-1", status="synced")
        await service.update_sync_status("P002", "patient", fhir_id="fhir-2", status="failed")
        await service.update_sync_status("E001", "encounter", fhir_id="fhir-3", status="synced")
        
        stats = await service.get_sync_statistics()
        
        assert stats["total_entities"] == 3
        assert stats["by_entity_type"]["patient"] == 2
        assert stats["by_entity_type"]["encounter"] == 1
        assert stats["by_status"]["synced"] == 2
        assert stats["by_status"]["failed"] == 1
    
    async def test_failed_sync_retry(self):
        """Test retrying failed synchronizations"""
        service = FHIRSyncService()
        
        # Create failed sync status
        await service.update_sync_status("P001", "patient", status="failed", errors=["Connection error"])
        
        # Get failed syncs
        failed_syncs = await service.get_failed_syncs()
        assert len(failed_syncs) == 1
        assert failed_syncs[0].entity_id == "P001"
        assert failed_syncs[0].sync_status == "failed"
    
    @patch('app.services.fhir_sync_service.fhir_repository')
    async def test_fhir_connectivity_test(self, mock_fhir_repo):
        """Test FHIR connectivity testing"""
        mock_fhir_repo.is_available.return_value = True
        mock_fhir_repo.test_connection.return_value = True
        mock_fhir_repo.get_capability_statement.return_value = {"resourceType": "CapabilityStatement"}
        
        service = FHIRSyncService()
        connectivity = await service.test_fhir_connectivity()
        
        assert connectivity["available"] is True
        assert connectivity["connection"] is True
        assert connectivity["capabilities"] is not None
        assert connectivity["error"] is None


@pytest.mark.fhir
@pytest.mark.integration
@pytest.mark.asyncio
class TestFHIRIntegrationFlow:
    """Test complete FHIR integration workflows"""
    
    @patch('app.repositories.fhir_repository.get_fhir_client')
    async def test_complete_patient_workflow(self, mock_get_client, sample_patient: PatientModel):
        """Test complete patient FHIR workflow"""
        # Mock FHIR client
        mock_client = Mock()
        mock_client.create_patient.return_value = "fhir-patient-123"
        mock_client.update_patient.return_value = True
        mock_client.delete_patient.return_value = True
        mock_get_client.return_value = mock_client
        
        # Test patient creation
        repo = FHIRRepository()
        fhir_id = await repo.create_patient(sample_patient)
        assert fhir_id == "fhir-patient-123"
        
        # Test patient update
        sample_patient.demographics.name = "Updated Name"
        success = await repo.update_patient(fhir_id, sample_patient)
        assert success is True
        
        # Test patient deletion
        success = await repo.delete_patient(fhir_id)
        assert success is True
    
    @patch('app.services.fhir_sync_service.fhir_repository')
    @patch('app.services.fhir_sync_service.patient_repository')
    async def test_bulk_patient_sync(self, mock_patient_repo, mock_fhir_repo):
        """Test bulk patient synchronization"""
        # Mock patient repository
        mock_patients = [
            Mock(id="P001"), 
            Mock(id="P002"), 
            Mock(id="P003")
        ]
        mock_patient_repo.get_all.return_value = mock_patients
        
        # Mock FHIR repository
        mock_fhir_repo.is_available.return_value = True
        mock_sync_response = FHIRSyncResponse(success=True, fhir_id="fhir-123")
        mock_fhir_repo.sync_patient_data.return_value = mock_sync_response
        
        service = FHIRSyncService()
        results = await service.sync_all_patients(max_patients=10)
        
        assert results["total"] == 3
        assert results["success"] == 3
        assert results["failed"] == 0