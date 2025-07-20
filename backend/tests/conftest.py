"""
Test configuration and fixtures for DiagnoAssist Backend
"""
import pytest
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings
from app.models.patient import PatientModel, PatientDemographics, MedicalBackground
from app.models.episode import EpisodeModel, EpisodeCategoryEnum
from app.models.encounter import EncounterModel, EncounterTypeEnum, Provider, WorkflowInfo
from app.models.soap import SOAPModel, SubjectiveSection
from app.models.auth import UserModel, UserProfile, UserRoleEnum, UserStatusEnum
from app.core.security import get_password_hash

# Configure test logging
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database connection."""
    # Use a test-specific database
    test_db_name = f"{settings.mongodb_database}_test"
    
    # Create connection
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[test_db_name]
    
    # Ensure clean state
    await _cleanup_test_db(db)
    
    yield db
    
    # Cleanup after tests
    await _cleanup_test_db(db)
    client.close()


async def _cleanup_test_db(db: AsyncIOMotorDatabase):
    """Clean up test database by dropping all collections."""
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db.drop_collection(collection_name)


@pytest.fixture
async def clean_db(test_db: AsyncIOMotorDatabase) -> AsyncIOMotorDatabase:
    """Provide a clean database for each test."""
    await _cleanup_test_db(test_db)
    return test_db


@pytest.fixture
def sample_patient_data() -> Dict[str, Any]:
    """Sample patient data for testing."""
    return {
        "demographics": PatientDemographics(
            name="John Doe",
            date_of_birth="1985-01-15",
            gender="Male",
            phone="+1-555-0123",
            email="john.doe@test.com",
            address="123 Test St, Test City, TC 12345"
        ),
        "medical_background": MedicalBackground()
    }


@pytest.fixture
def sample_patient(sample_patient_data: Dict[str, Any]) -> PatientModel:
    """Sample patient model for testing."""
    return PatientModel(**sample_patient_data)


@pytest.fixture
def sample_episode_data() -> Dict[str, Any]:
    """Sample episode data for testing."""
    return {
        "patient_id": "P001",
        "chief_complaint": "Annual physical examination",
        "category": EpisodeCategoryEnum.ROUTINE_CARE,
        "tags": ["annual", "physical"],
        "notes": "Routine annual checkup"
    }


@pytest.fixture
def sample_episode(sample_episode_data: Dict[str, Any]) -> EpisodeModel:
    """Sample episode model for testing."""
    return EpisodeModel(**sample_episode_data)


@pytest.fixture
def sample_encounter_data() -> Dict[str, Any]:
    """Sample encounter data for testing."""
    return {
        "patient_id": "P001",
        "episode_id": "E001",
        "type": EncounterTypeEnum.ROUTINE_VISIT,
        "provider": Provider(
            id="U001",
            name="Dr. Test Doctor",
            specialty="Internal Medicine",
            department="Internal Medicine"
        ),
        "soap": SOAPModel(
            subjective=SubjectiveSection(
                chief_complaint="Test complaint"
            )
        ),
        "workflow": WorkflowInfo()
    }


@pytest.fixture
def sample_encounter(sample_encounter_data: Dict[str, Any]) -> EncounterModel:
    """Sample encounter model for testing."""
    return EncounterModel(**sample_encounter_data)


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test.doctor@test.com",
        "hashed_password": get_password_hash("testpassword"),
        "role": UserRoleEnum.DOCTOR,
        "status": UserStatusEnum.ACTIVE,
        "profile": UserProfile(
            first_name="Test",
            last_name="Doctor",
            specialty="Internal Medicine",
            department="Internal Medicine"
        ),
        "is_verified": True
    }


@pytest.fixture
def sample_user(sample_user_data: Dict[str, Any]) -> UserModel:
    """Sample user model for testing."""
    return UserModel(**sample_user_data)


@pytest.fixture
async def patient_repository(test_db: AsyncIOMotorDatabase):
    """Patient repository with test database."""
    from app.repositories.patient_repository import PatientRepository
    
    # Create repository with test database
    repo = PatientRepository()
    repo._db = test_db  # Override database connection
    
    return repo


@pytest.fixture
async def episode_repository(test_db: AsyncIOMotorDatabase):
    """Episode repository with test database."""
    from app.repositories.episode_repository import EpisodeRepository
    
    # Create repository with test database
    repo = EpisodeRepository()
    repo._db = test_db  # Override database connection
    
    return repo


@pytest.fixture
async def encounter_repository(test_db: AsyncIOMotorDatabase):
    """Encounter repository with test database."""
    from app.repositories.encounter_repository import EncounterRepository
    
    # Create repository with test database
    repo = EncounterRepository()
    repo._db = test_db  # Override database connection
    
    return repo


@pytest.fixture
async def user_repository(test_db: AsyncIOMotorDatabase):
    """User repository with test database."""
    from app.repositories.user_repository import UserRepository
    
    # Create repository with test database
    repo = UserRepository()
    repo._db = test_db  # Override database connection
    
    return repo


@pytest.fixture
def mock_fhir_client():
    """Mock FHIR client for testing."""
    from unittest.mock import Mock
    
    mock_client = Mock()
    mock_client.is_available.return_value = True
    mock_client.test_connection.return_value = True
    mock_client.create_patient.return_value = "fhir-patient-123"
    mock_client.update_patient.return_value = True
    mock_client.delete_patient.return_value = True
    mock_client.get_patient.return_value = None
    
    return mock_client


@pytest.fixture
async def sample_data_set(
    patient_repository,
    episode_repository,
    encounter_repository,
    user_repository,
    sample_patient,
    sample_episode,
    sample_encounter,
    sample_user
):
    """Create a complete set of related sample data."""
    # Create user first
    created_user = await user_repository.create(sample_user)
    
    # Create patient
    created_patient = await patient_repository.create(sample_patient)
    
    # Update episode and encounter with actual IDs
    sample_episode.patient_id = created_patient.id
    created_episode = await episode_repository.create(sample_episode)
    
    sample_encounter.patient_id = created_patient.id
    sample_encounter.episode_id = created_episode.id
    sample_encounter.provider.id = created_user.id
    created_encounter = await encounter_repository.create(sample_encounter)
    
    return {
        "user": created_user,
        "patient": created_patient,
        "episode": created_episode,
        "encounter": created_encounter
    }


# Test markers for different test types
pytest_markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "repository: Repository layer tests",
    "service: Service layer tests",
    "fhir: FHIR integration tests",
    "database: Database operation tests",
    "migration: Migration tests",
    "slow: Slow-running tests"
]