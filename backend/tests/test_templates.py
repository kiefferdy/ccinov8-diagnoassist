"""
Tests for Template functionality

Tests the template system including:
- Template CRUD operations
- Template search and discovery
- Template application to encounters
- Template validation and analytics
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.models.auth import UserModel, UserRoleEnum
from app.models.template import (
    TemplateModel, TemplateCreateRequest, TemplateUpdateRequest,
    TemplateSearchRequest, TemplateApplicationRequest, TemplateSection,
    TemplateField, TemplateType, TemplateCategory, TemplateScope, FieldType
)
from app.models.encounter import EncounterModel
from app.services.template_service import TemplateService
from app.repositories.template_repository import TemplateRepository
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError


class TestTemplateService:
    """Test template service functionality"""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def admin_user(self):
        """Create mock admin user"""
        return UserModel(
            id="admin123",
            email="admin@example.com",
            name="Admin User",
            role=UserRoleEnum.ADMIN,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def mock_template_repository(self):
        """Create mock template repository"""
        repo = Mock(spec=TemplateRepository)
        repo.create_template = AsyncMock()
        repo.get_template_by_id = AsyncMock()
        repo.update_template = AsyncMock()
        repo.delete_template = AsyncMock()
        repo.search_templates = AsyncMock()
        repo.get_user_templates = AsyncMock()
        repo.get_popular_templates = AsyncMock()
        repo.record_template_usage = AsyncMock()
        repo.rate_template = AsyncMock()
        repo.get_template_usage_stats = AsyncMock()
        return repo
    
    @pytest.fixture
    def mock_encounter_service(self):
        """Create mock encounter service"""
        service = Mock()
        service.get_encounter = AsyncMock()
        service.update_encounter = AsyncMock()
        return service
    
    @pytest.fixture
    def template_service(self, mock_template_repository, mock_encounter_service):
        """Create template service with mocked dependencies"""
        return TemplateService(mock_template_repository, mock_encounter_service)
    
    @pytest.fixture
    def sample_template_sections(self):
        """Create sample template sections"""
        return [
            TemplateSection(
                section="subjective",
                title="Subjective",
                description="Patient's reported symptoms",
                fields=[
                    TemplateField(
                        id="chief_complaint",
                        label="Chief Complaint",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        order=1
                    ),
                    TemplateField(
                        id="history_present_illness",
                        label="History of Present Illness",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        order=2
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Objective",
                description="Physical examination findings",
                fields=[
                    TemplateField(
                        id="vital_signs",
                        label="Vital Signs",
                        field_type=FieldType.VITAL_SIGNS,
                        section="objective",
                        required=True,
                        order=1
                    )
                ],
                order=2
            )
        ]
    
    @pytest.fixture
    def sample_template_request(self, sample_template_sections):
        """Create sample template creation request"""
        return TemplateCreateRequest(
            name="Test Template",
            description="A test template for unit testing",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            scope=TemplateScope.PERSONAL,
            sections=sample_template_sections,
            tags=["test", "general"],
            encounter_types=["initial", "follow-up"]
        )
    
    # Template CRUD Tests
    
    @pytest.mark.asyncio
    async def test_create_template_success(
        self, 
        template_service, 
        mock_template_repository, 
        sample_template_request, 
        mock_user
    ):
        """Test successful template creation"""
        # Mock repository response
        expected_template = TemplateModel(
            id="template123",
            **sample_template_request.model_dump(),
            owner_id=mock_user.id,
            metadata=Mock(created_by=mock_user.id)
        )
        mock_template_repository.create_template.return_value = expected_template
        
        # Create template
        result = await template_service.create_template(sample_template_request, mock_user)
        
        # Verify result
        assert result == expected_template
        mock_template_repository.create_template.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_template_validation_error(
        self, 
        template_service, 
        sample_template_request, 
        mock_user
    ):
        """Test template creation with validation error"""
        # Create invalid template (empty sections)
        sample_template_request.sections = []
        
        # Attempt to create template
        with pytest.raises(ValidationException):
            await template_service.create_template(sample_template_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_create_template_permission_error(
        self, 
        template_service, 
        sample_template_request
    ):
        """Test template creation with insufficient permissions"""
        # Create user with insufficient permissions
        student_user = UserModel(
            id="student123",
            email="student@example.com",
            name="Student User",
            role=UserRoleEnum.STUDENT,
            is_active=True,
            is_verified=True
        )
        
        # Set organization scope (requires higher permissions)
        sample_template_request.scope = TemplateScope.ORGANIZATION
        
        # Attempt to create template
        with pytest.raises(PermissionDeniedError):
            await template_service.create_template(sample_template_request, student_user)
    
    @pytest.mark.asyncio
    async def test_get_template_success(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test successful template retrieval"""
        template_id = "template123"
        expected_template = TemplateModel(
            id=template_id,
            name="Test Template",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            scope=TemplateScope.PERSONAL,
            sections=[],
            owner_id=mock_user.id,
            metadata=Mock()
        )
        
        mock_template_repository.get_template_by_id.return_value = expected_template
        
        # Get template
        result = await template_service.get_template(template_id, mock_user)
        
        # Verify result
        assert result == expected_template
        mock_template_repository.get_template_by_id.assert_called_once_with(template_id, mock_user)
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test template retrieval when template not found"""
        template_id = "nonexistent"
        mock_template_repository.get_template_by_id.return_value = None
        
        # Attempt to get template
        with pytest.raises(NotFoundError):
            await template_service.get_template(template_id, mock_user)
    
    @pytest.mark.asyncio
    async def test_update_template_success(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test successful template update"""
        template_id = "template123"
        update_request = TemplateUpdateRequest(
            name="Updated Template Name",
            description="Updated description"
        )
        
        expected_template = TemplateModel(
            id=template_id,
            name="Updated Template Name",
            description="Updated description",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            scope=TemplateScope.PERSONAL,
            sections=[],
            owner_id=mock_user.id,
            metadata=Mock()
        )
        
        mock_template_repository.update_template.return_value = expected_template
        
        # Update template
        result = await template_service.update_template(template_id, update_request, mock_user)
        
        # Verify result
        assert result == expected_template
        mock_template_repository.update_template.assert_called_once_with(template_id, update_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_delete_template_success(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test successful template deletion"""
        template_id = "template123"
        mock_template_repository.delete_template.return_value = True
        
        # Delete template
        result = await template_service.delete_template(template_id, mock_user)
        
        # Verify result
        assert result is True
        mock_template_repository.delete_template.assert_called_once_with(template_id, mock_user)
    
    # Template Search Tests
    
    @pytest.mark.asyncio
    async def test_search_templates_success(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test successful template search"""
        search_request = TemplateSearchRequest(
            query="general medicine",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            page=1,
            limit=10
        )
        
        expected_results = {
            "templates": [Mock(), Mock()],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False
            }
        }
        
        mock_template_repository.search_templates.return_value = expected_results
        
        # Search templates
        result = await template_service.search_templates(search_request, mock_user)
        
        # Verify result
        assert result == expected_results
        mock_template_repository.search_templates.assert_called_once_with(search_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_get_recommended_templates(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test getting recommended templates"""
        expected_templates = [Mock(), Mock(), Mock()]
        mock_template_repository.get_user_templates.return_value = expected_templates
        
        # Get recommendations
        result = await template_service.get_recommended_templates(
            mock_user, 
            encounter_type="initial",
            category=TemplateCategory.GENERAL_MEDICINE,
            limit=5
        )
        
        # Verify result
        assert len(result) <= 5  # Should respect limit
        mock_template_repository.get_user_templates.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_popular_templates(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test getting popular templates"""
        expected_templates = [Mock(), Mock()]
        mock_template_repository.get_popular_templates.return_value = expected_templates
        
        # Get popular templates
        result = await template_service.get_popular_templates(
            mock_user,
            category=TemplateCategory.GENERAL_MEDICINE,
            limit=10
        )
        
        # Verify result
        assert result == expected_templates
        mock_template_repository.get_popular_templates.assert_called_once_with(
            mock_user, category=TemplateCategory.GENERAL_MEDICINE, limit=10
        )
    
    # Template Application Tests
    
    @pytest.mark.asyncio
    async def test_apply_template_to_encounter_success(
        self, 
        template_service, 
        mock_template_repository,
        mock_encounter_service,
        sample_template_sections,
        mock_user
    ):
        """Test successful template application to encounter"""
        # Mock template
        template = TemplateModel(
            id="template123",
            name="Test Template",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            scope=TemplateScope.PERSONAL,
            sections=sample_template_sections,
            owner_id=mock_user.id,
            metadata=Mock()
        )
        
        # Mock encounter
        encounter = EncounterModel(
            id="encounter123",
            patient_id="patient123",
            episode_id="episode123",
            type="initial",
            status="draft",
            soap=None,  # No existing SOAP data
            applied_templates=[]
        )
        
        # Mock repository and service responses
        mock_template_repository.get_template_by_id.return_value = template
        mock_encounter_service.get_encounter.return_value = encounter
        mock_encounter_service.update_encounter.return_value = encounter
        mock_template_repository.record_template_usage.return_value = True
        
        # Application request
        application_request = TemplateApplicationRequest(
            template_id="template123",
            encounter_id="encounter123",
            merge_strategy="replace"
        )
        
        # Apply template
        result_encounter, application_info = await template_service.apply_template_to_encounter(
            application_request, mock_user
        )
        
        # Verify results
        assert result_encounter == encounter
        assert application_info.template_id == "template123"
        assert application_info.template_name == "Test Template"
        assert application_info.applied_by == mock_user.id
        
        # Verify service calls
        mock_template_repository.get_template_by_id.assert_called_once()
        mock_encounter_service.get_encounter.assert_called_once()
        mock_encounter_service.update_encounter.assert_called_once()
        mock_template_repository.record_template_usage.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_apply_template_to_signed_encounter_error(
        self, 
        template_service,
        mock_template_repository,
        mock_encounter_service,
        mock_user
    ):
        """Test applying template to signed encounter (should fail)"""
        # Mock signed encounter
        encounter = EncounterModel(
            id="encounter123",
            patient_id="patient123",
            episode_id="episode123",
            type="initial",
            status="signed",  # Already signed
            soap=None,
            applied_templates=[]
        )
        
        mock_template_repository.get_template_by_id.return_value = Mock()
        mock_encounter_service.get_encounter.return_value = encounter
        
        application_request = TemplateApplicationRequest(
            template_id="template123",
            encounter_id="encounter123",
            merge_strategy="replace"
        )
        
        # Attempt to apply template
        with pytest.raises(ValidationException, match="Cannot modify signed encounter"):
            await template_service.apply_template_to_encounter(application_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_get_applicable_templates(
        self, 
        template_service,
        mock_template_repository,
        mock_encounter_service,
        mock_user
    ):
        """Test getting templates applicable to encounter"""
        encounter_id = "encounter123"
        
        # Mock encounter
        encounter = EncounterModel(
            id=encounter_id,
            patient_id="patient123",
            episode_id="episode123",
            type="initial",
            status="draft",
            soap=None,
            applied_templates=[]
        )
        
        # Mock templates
        templates = [Mock(), Mock(), Mock()]
        
        mock_encounter_service.get_encounter.return_value = encounter
        mock_template_repository.get_user_templates.return_value = templates
        
        # Get applicable templates
        result = await template_service.get_applicable_templates(encounter_id, mock_user)
        
        # Verify result
        assert isinstance(result, list)
        mock_encounter_service.get_encounter.assert_called_once_with(encounter_id, mock_user)
    
    # Template Analytics Tests
    
    @pytest.mark.asyncio
    async def test_get_template_usage_stats(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test getting template usage statistics"""
        template_id = "template123"
        expected_stats = Mock()
        
        mock_template_repository.get_template_usage_stats.return_value = expected_stats
        
        # Get usage stats
        result = await template_service.get_template_usage_stats(template_id, mock_user)
        
        # Verify result
        assert result == expected_stats
        mock_template_repository.get_template_usage_stats.assert_called_once_with(template_id, mock_user)
    
    @pytest.mark.asyncio
    async def test_rate_template_success(
        self, 
        template_service, 
        mock_template_repository, 
        mock_user
    ):
        """Test successful template rating"""
        template_id = "template123"
        rating = 4.5
        
        mock_template_repository.rate_template.return_value = True
        
        # Rate template
        result = await template_service.rate_template(template_id, rating, mock_user)
        
        # Verify result
        assert result is True
        mock_template_repository.rate_template.assert_called_once_with(template_id, mock_user, rating)
    
    # Template Validation Tests
    
    @pytest.mark.asyncio
    async def test_validate_template_structure_valid(
        self, 
        template_service, 
        sample_template_sections
    ):
        """Test validation of valid template structure"""
        # Validate template structure
        result = await template_service.validate_template_structure(sample_template_sections)
        
        # Verify result
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_template_structure_empty_sections(
        self, 
        template_service
    ):
        """Test validation of template with empty sections"""
        # Validate empty sections
        result = await template_service.validate_template_structure([])
        
        # Verify result
        assert result.is_valid is False
        assert "Template must have at least one section" in result.errors
    
    @pytest.mark.asyncio
    async def test_validate_template_structure_duplicate_sections(
        self, 
        template_service
    ):
        """Test validation of template with duplicate sections"""
        # Create duplicate sections
        duplicate_sections = [
            TemplateSection(
                section="subjective",
                title="Subjective 1",
                fields=[],
                order=1
            ),
            TemplateSection(
                section="subjective",  # Duplicate
                title="Subjective 2",
                fields=[],
                order=2
            )
        ]
        
        # Validate duplicate sections
        result = await template_service.validate_template_structure(duplicate_sections)
        
        # Verify result
        assert result.is_valid is False
        assert any("Duplicate section" in error for error in result.errors)


class TestTemplateRepository:
    """Test template repository functionality"""
    
    @pytest.fixture
    def mock_collection(self):
        """Create mock MongoDB collection"""
        collection = Mock()
        collection.insert_one = AsyncMock()
        collection.find_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.count_documents = AsyncMock()
        collection.find = Mock()
        collection.aggregate = Mock()
        return collection
    
    @pytest.fixture
    def template_repository(self, mock_collection):
        """Create template repository with mocked collection"""
        return TemplateRepository(mock_collection)
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.mark.asyncio
    async def test_create_template_repository(
        self, 
        template_repository, 
        mock_collection, 
        mock_user
    ):
        """Test template creation in repository"""
        # Mock collection response
        mock_collection.insert_one.return_value = Mock(inserted_id="template123")
        
        # Mock get_by_id to return created template
        with patch.object(template_repository, 'get_by_id') as mock_get:
            mock_template = Mock()
            mock_get.return_value = mock_template
            
            # Create template request
            template_request = TemplateCreateRequest(
                name="Test Template",
                description="Test description",
                template_type=TemplateType.SOAP_COMPLETE,
                category=TemplateCategory.GENERAL_MEDICINE,
                scope=TemplateScope.PERSONAL,
                sections=[]
            )
            
            # Create template
            result = await template_repository.create_template(template_request, mock_user)
            
            # Verify result
            assert result == mock_template
            mock_collection.insert_one.assert_called_once()
            mock_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])