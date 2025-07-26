"""
Comprehensive Search Tests for DiagnoAssist Backend

Tests for all search functionality including:
- Search service operations
- Search repository queries  
- Search API endpoints
- Search performance and optimization
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

# FastAPI testing
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Application imports
from app.main import app
from app.models.search import (
    SearchRequest, SearchResponse, SearchResult, SearchEntity, SearchType,
    SavedSearch, SearchHistory, SearchAnalytics, SearchSuggestion,
    QuickSearch, SearchTemplate, SearchFacet
)
from app.models.auth import UserModel, UserRoleEnum
from app.models.patient import PatientModel
from app.models.episode import EpisodeModel
from app.models.encounter import EncounterModel
from app.services.search_service import SearchService
from app.repositories.search_repository import SearchRepository
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError


class TestSearchService:
    """Test cases for SearchService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock search repository"""
        return AsyncMock(spec=SearchRepository)
    
    @pytest.fixture
    def search_service(self, mock_repository):
        """Search service with mocked repository"""
        return SearchService(mock_repository)
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True
        )
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample search request"""
        return SearchRequest(
            query="chest pain",
            entities=[SearchEntity.PATIENT, SearchEntity.EPISODE],
            search_type=SearchType.FULL_TEXT,
            limit=20,
            page=1,
            date_range={
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            }
        )
    
    @pytest.fixture
    def sample_search_response(self):
        """Sample search response"""
        return SearchResponse(
            results=[
                SearchResult(
                    id="patient123",
                    entity_type=SearchEntity.PATIENT,
                    title="John Doe",
                    snippet="Patient with chest pain complaint...",
                    score=0.95,
                    highlights=["chest pain"],
                    metadata={"age": 45, "gender": "M"}
                )
            ],
            total_results=1,
            page=1,
            limit=20,
            search_time_ms=150,
            facets=[
                SearchFacet(
                    name="entity_type",
                    values=[{"value": "patient", "count": 1}]
                )
            ],
            suggestions=["chest pain symptoms", "chest pain diagnosis"]
        )
    
    @pytest.mark.asyncio
    async def test_search_basic(self, search_service, mock_repository, mock_user, sample_search_request, sample_search_response):
        """Test basic search functionality"""
        # Setup mock
        mock_repository.search.return_value = sample_search_response
        
        # Execute search
        result = await search_service.search(sample_search_request, mock_user)
        
        # Verify
        assert isinstance(result, SearchResponse)
        assert result.total_results == 1
        assert len(result.results) == 1
        assert result.results[0].entity_type == SearchEntity.PATIENT
        mock_repository.search.assert_called_once_with(sample_search_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_search_with_caching(self, search_service, mock_repository, mock_user, sample_search_request, sample_search_response):
        """Test search with caching functionality"""
        mock_repository.search.return_value = sample_search_response
        
        # First search - should hit repository
        result1 = await search_service.search(sample_search_request, mock_user)
        
        # Second search - should hit cache
        result2 = await search_service.search(sample_search_request, mock_user)
        
        # Repository should only be called once due to caching
        assert mock_repository.search.call_count == 1
        assert result1.total_results == result2.total_results
    
    @pytest.mark.asyncio
    async def test_quick_search(self, search_service, mock_repository, mock_user):
        """Test quick search functionality"""
        # Setup mock
        quick_results = [
            SearchResult(
                id="patient123",
                entity_type=SearchEntity.PATIENT,
                title="John Doe",
                snippet="Quick match",
                score=0.9,
                highlights=["john"],
                metadata={}
            )
        ]
        mock_repository.quick_search.return_value = quick_results
        
        # Execute quick search
        quick_search = QuickSearch(query="john", entity=SearchEntity.PATIENT, limit=5)
        result = await search_service.quick_search(quick_search, mock_user)
        
        # Verify
        assert len(result) == 1
        assert result[0].title == "John Doe"
        mock_repository.quick_search.assert_called_once_with(quick_search, mock_user)
    
    @pytest.mark.asyncio
    async def test_advanced_search(self, search_service, mock_repository, mock_user, sample_search_request, sample_search_response):
        """Test advanced search with enhanced features"""
        mock_repository.search.return_value = sample_search_response
        
        # Execute advanced search
        result = await search_service.advanced_search(sample_search_request, mock_user)
        
        # Verify enhanced response
        assert isinstance(result, SearchResponse)
        assert result.search_time_ms > 0
        assert len(result.facets) > 0
        assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_search_suggestions(self, search_service, mock_repository, mock_user):
        """Test search suggestions functionality"""
        # Setup mock
        suggestions = [
            SearchSuggestion(
                text="chest pain symptoms",
                entity=SearchEntity.PATIENT,
                frequency=10,
                score=0.9
            ),
            SearchSuggestion(
                text="chest pain diagnosis",
                entity=SearchEntity.EPISODE,
                frequency=8,
                score=0.8
            )
        ]
        mock_repository.get_search_suggestions.return_value = suggestions
        
        # Execute
        result = await search_service.get_search_suggestions("chest", mock_user, SearchEntity.PATIENT, 10)
        
        # Verify
        assert len(result) == 2
        assert result[0].text == "chest pain symptoms"
        assert result[0].frequency == 10
    
    @pytest.mark.asyncio
    async def test_save_search(self, search_service, mock_repository, mock_user, sample_search_request):
        """Test saving a search"""
        # Setup mock
        saved_search = SavedSearch(
            id="saved123",
            name="Chest Pain Search",
            description="Search for chest pain cases",
            search_parameters=sample_search_request,
            created_by=mock_user.id,
            created_at=datetime.utcnow(),
            is_public=False,
            usage_count=0
        )
        mock_repository.save_search.return_value = saved_search
        
        # Execute
        result = await search_service.save_search(
            sample_search_request, "Chest Pain Search", "Search for chest pain cases", mock_user
        )
        
        # Verify
        assert result.name == "Chest Pain Search"
        assert result.created_by == mock_user.id
        assert not result.is_public
        mock_repository.save_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_saved_searches(self, search_service, mock_repository, mock_user):
        """Test retrieving saved searches"""
        # Setup mock
        saved_searches = [
            SavedSearch(
                id="saved1",
                name="Search 1",
                description="First search",
                search_parameters=SearchRequest(query="test1"),
                created_by=mock_user.id,
                created_at=datetime.utcnow(),
                is_public=False,
                usage_count=5
            ),
            SavedSearch(
                id="saved2", 
                name="Search 2",
                description="Second search",
                search_parameters=SearchRequest(query="test2"),
                created_by=mock_user.id,
                created_at=datetime.utcnow(),
                is_public=True,
                usage_count=10
            )
        ]
        mock_repository.get_saved_searches.return_value = saved_searches
        
        # Execute
        result = await search_service.get_saved_searches(mock_user)
        
        # Verify
        assert len(result) == 2
        assert result[0].name == "Search 1"
        assert result[1].usage_count == 10
    
    @pytest.mark.asyncio
    async def test_execute_saved_search(self, search_service, mock_repository, mock_user, sample_search_response):
        """Test executing a saved search"""
        # Setup mocks
        saved_search = SavedSearch(
            id="saved123",
            name="Saved Search",
            description="Test saved search",
            search_parameters=SearchRequest(query="test"),
            created_by=mock_user.id,
            created_at=datetime.utcnow(),
            is_public=False,
            usage_count=0
        )
        mock_repository.get_saved_search.return_value = saved_search
        mock_repository.search.return_value = sample_search_response
        
        # Execute
        result = await search_service.execute_saved_search("saved123", mock_user)
        
        # Verify
        assert isinstance(result, SearchResponse)
        mock_repository.get_saved_search.assert_called_once_with("saved123", mock_user)
        mock_repository.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_analytics(self, search_service, mock_repository, mock_user):
        """Test search analytics functionality"""
        # Setup mock
        analytics = SearchAnalytics(
            total_searches=100,
            unique_users=25,
            average_search_time_ms=180,
            top_queries=["chest pain", "diabetes", "hypertension"],
            search_success_rate=0.94,
            entity_distribution={"patient": 40, "episode": 35, "encounter": 25}
        )
        mock_repository.get_search_analytics.return_value = analytics
        
        # Execute
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        result = await search_service.get_search_analytics(mock_user, start_date, end_date)
        
        # Verify
        assert result.total_searches == 100
        assert result.search_success_rate == 0.94
        assert len(result.top_queries) == 3
    
    @pytest.mark.asyncio
    async def test_search_validation_error(self, search_service, mock_user):
        """Test search validation error handling"""
        # Invalid search request (empty query)
        invalid_request = SearchRequest(
            query="",  # Empty query should fail validation
            entities=[SearchEntity.PATIENT],
            search_type=SearchType.FULL_TEXT
        )
        
        # Should raise validation exception
        with pytest.raises(ValidationException):
            await search_service.search(invalid_request, mock_user)
    
    @pytest.mark.asyncio
    async def test_search_permission_error(self, search_service, mock_repository):
        """Test search permission error handling"""
        # Inactive user
        inactive_user = UserModel(
            id="inactive123",
            email="inactive@example.com", 
            name="Inactive User",
            role=UserRoleEnum.NURSE,
            is_active=False
        )
        
        search_request = SearchRequest(
            query="test",
            entities=[SearchEntity.PATIENT],
            search_type=SearchType.FULL_TEXT
        )
        
        # Should raise permission error for inactive user
        with pytest.raises(PermissionDeniedError):
            await search_service.search(search_request, inactive_user)


class TestSearchRepository:
    """Test cases for SearchRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = MagicMock()
        
        # Mock collections
        db.patients = AsyncMock()
        db.episodes = AsyncMock()
        db.encounters = AsyncMock()
        db.templates = AsyncMock()
        db.reports = AsyncMock()
        db.search_history = AsyncMock()
        db.saved_searches = AsyncMock()
        
        return db
    
    @pytest.fixture
    def search_repository(self, mock_db):
        """Search repository with mocked database"""
        return SearchRepository(mock_db)
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True
        )
    
    @pytest.mark.asyncio
    async def test_search_patients(self, search_repository, mock_db, mock_user):
        """Test searching patients in repository"""
        # Setup mock data
        mock_patients = [
            {
                "_id": "patient123",
                "demographics": {
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "medical_background": {
                    "past_medical_history": ["chest pain", "hypertension"]
                }
            }
        ]
        
        # Mock aggregation pipeline
        mock_db.patients.aggregate.return_value.to_list = AsyncMock(return_value=mock_patients)
        
        # Execute search
        search_request = SearchRequest(
            query="john",
            entities=[SearchEntity.PATIENT],
            search_type=SearchType.FULL_TEXT,
            limit=20,
            page=1
        )
        
        result = await search_repository.search(search_request, mock_user)
        
        # Verify
        assert isinstance(result, SearchResponse)
        mock_db.patients.aggregate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_quick_search_patients(self, search_repository, mock_db, mock_user):
        """Test quick search for patients"""
        # Setup mock data
        mock_patients = [
            {
                "_id": "patient123",
                "demographics": {"name": "John Doe", "email": "john@example.com"}
            }
        ]
        mock_db.patients.find.return_value.limit.return_value.to_list = AsyncMock(return_value=mock_patients)
        
        # Execute quick search
        quick_search = QuickSearch(
            query="john",
            entity=SearchEntity.PATIENT,
            limit=5
        )
        
        result = await search_repository.quick_search(quick_search, mock_user)
        
        # Verify
        assert len(result) == 1
        assert result[0].title == "John Doe"
        assert result[0].entity_type == SearchEntity.PATIENT
    
    @pytest.mark.asyncio
    async def test_save_search_repository(self, search_repository, mock_db, mock_user):
        """Test saving search in repository"""
        # Setup mock
        mock_db.saved_searches.insert_one.return_value.inserted_id = "saved123"
        mock_db.saved_searches.find_one.return_value = {
            "_id": "saved123",
            "name": "Test Search",
            "description": "Test description",
            "search_parameters": {"query": "test"},
            "created_by": mock_user.id,
            "created_at": datetime.utcnow(),
            "is_public": False,
            "usage_count": 0
        }
        
        # Execute
        search_request = SearchRequest(query="test")
        result = await search_repository.save_search(
            search_request, "Test Search", "Test description", mock_user
        )
        
        # Verify
        assert result.name == "Test Search"
        assert result.created_by == mock_user.id
        mock_db.saved_searches.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_suggestions_repository(self, search_repository, mock_db, mock_user):
        """Test getting search suggestions from repository"""
        # Setup mock data
        mock_suggestions = [
            {"_id": "chest pain", "count": 10},
            {"_id": "chest pain symptoms", "count": 8}
        ]
        mock_db.search_history.aggregate.return_value.to_list = AsyncMock(return_value=mock_suggestions)
        
        # Execute
        result = await search_repository.get_search_suggestions("chest", mock_user, SearchEntity.PATIENT, 10)
        
        # Verify
        assert len(result) == 2
        assert result[0].text == "chest pain"
        assert result[0].frequency == 10


@pytest.mark.asyncio
class TestSearchAPI:
    """Test cases for Search API endpoints"""
    
    @pytest.fixture
    async def async_client(self):
        """Async test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user_token(self):
        """Mock user authentication token"""
        # This would typically be generated by your auth system
        return "Bearer mock_token_for_testing"
    
    @pytest.mark.asyncio
    async def test_search_endpoint(self, async_client, mock_user_token):
        """Test main search API endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            # Setup mock user
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User", 
                role=UserRoleEnum.DOCTOR,
                is_active=True
            )
            
            # Test search request
            search_data = {
                "query": "chest pain",
                "entities": ["patient"],
                "search_type": "full_text",
                "limit": 20,
                "page": 1
            }
            
            response = await async_client.post(
                "/api/v1/search/",
                json=search_data,
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_quick_search_endpoint(self, async_client, mock_user_token):
        """Test quick search API endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User",
                role=UserRoleEnum.DOCTOR,
                is_active=True
            )
            
            quick_search_data = {
                "query": "john",
                "entity": "patient",
                "limit": 5
            }
            
            response = await async_client.post(
                "/api/v1/search/quick",
                json=quick_search_data,
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "results" in data["data"]
    
    @pytest.mark.asyncio
    async def test_search_patients_endpoint(self, async_client, mock_user_token):
        """Test patient-specific search endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User",
                role=UserRoleEnum.DOCTOR,
                is_active=True
            )
            
            response = await async_client.get(
                "/api/v1/search/patients?q=john&limit=20",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "patients" in data["data"]
    
    @pytest.mark.asyncio
    async def test_search_suggestions_endpoint(self, async_client, mock_user_token):
        """Test search suggestions endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User",
                role=UserRoleEnum.DOCTOR,
                is_active=True
            )
            
            response = await async_client.get(
                "/api/v1/search/suggestions?q=chest&limit=10",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "suggestions" in data["data"]
    
    @pytest.mark.asyncio
    async def test_save_search_endpoint(self, async_client, mock_user_token):
        """Test save search endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User",
                role=UserRoleEnum.DOCTOR,
                is_active=True
            )
            
            save_data = {
                "search_request": {
                    "query": "chest pain",
                    "entities": ["patient"],
                    "search_type": "full_text"
                },
                "name": "My Chest Pain Search",
                "description": "Search for chest pain cases"
            }
            
            response = await async_client.post(
                "/api/v1/search/saved",
                json=save_data,
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "saved_search_id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_search_analytics_endpoint(self, async_client, mock_user_token):
        """Test search analytics endpoint"""
        with patch('app.middleware.auth_middleware.get_current_user') as mock_auth:
            mock_auth.return_value = UserModel(
                id="user123",
                email="test@example.com",
                name="Test User",
                role=UserRoleEnum.DOCTOR,  # Admin access required
                is_active=True
            )
            
            response = await async_client.get(
                "/api/v1/search/analytics?days=30",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "analytics" in data["data"]
    
    @pytest.mark.asyncio
    async def test_search_health_endpoint(self, async_client):
        """Test search health check endpoint"""
        response = await async_client.get("/api/v1/search/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "features" in data["data"]
        assert "supported_entities" in data["data"]


class TestSearchPerformance:
    """Test cases for search performance and optimization"""
    
    @pytest.mark.asyncio
    async def test_search_response_time(self):
        """Test that search response times are acceptable"""
        # Mock search service
        repository = AsyncMock()
        service = SearchService(repository)
        
        # Setup fast response
        fast_response = SearchResponse(
            results=[],
            total_results=0,
            page=1,
            limit=20,
            search_time_ms=50,  # Fast response
            facets=[],
            suggestions=[]
        )
        repository.search.return_value = fast_response
        
        user = UserModel(id="user123", email="test@example.com", name="Test", role=UserRoleEnum.DOCTOR, is_active=True)
        search_request = SearchRequest(query="test", entities=[SearchEntity.PATIENT])
        
        start_time = datetime.utcnow()
        result = await service.search(search_request, user)
        end_time = datetime.utcnow()
        
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Should respond within reasonable time (< 1000ms for this test)
        assert response_time_ms < 1000
        assert result.search_time_ms < 200  # Mock search time
    
    @pytest.mark.asyncio
    async def test_search_caching_performance(self):
        """Test that search caching improves performance"""
        repository = AsyncMock()
        service = SearchService(repository)
        
        search_response = SearchResponse(
            results=[], total_results=0, page=1, limit=20,
            search_time_ms=100, facets=[], suggestions=[]
        )
        repository.search.return_value = search_response
        
        user = UserModel(id="user123", email="test@example.com", name="Test", role=UserRoleEnum.DOCTOR, is_active=True)
        search_request = SearchRequest(query="cached_test", entities=[SearchEntity.PATIENT])
        
        # First search
        start_time = datetime.utcnow()
        await service.search(search_request, user)
        first_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Second search (should be faster due to caching)
        start_time = datetime.utcnow()
        await service.search(search_request, user)
        second_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Cached search should be faster
        assert second_time <= first_time
        # Repository should only be called once due to caching
        assert repository.search.call_count == 1
    
    def test_search_query_validation_performance(self):
        """Test that search query validation is fast"""
        repository = MagicMock()
        service = SearchService(repository)
        
        # Test multiple validation scenarios
        test_queries = [
            "simple query",
            "query with special characters !@#$%^&*()",
            "very long query " * 100,
            "",  # empty query
            "   ",  # whitespace only
        ]
        
        start_time = datetime.utcnow()
        
        for query in test_queries:
            search_request = SearchRequest(
                query=query,
                entities=[SearchEntity.PATIENT],
                search_type=SearchType.FULL_TEXT
            )
            try:
                # This would typically call validation logic
                service._validate_search_request(search_request)
            except ValidationException:
                pass  # Expected for invalid queries
        
        end_time = datetime.utcnow()
        validation_time = (end_time - start_time).total_seconds() * 1000
        
        # Validation should be very fast (< 100ms for all queries)
        assert validation_time < 100


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])