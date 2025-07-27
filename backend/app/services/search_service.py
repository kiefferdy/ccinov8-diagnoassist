"""
Search Service for DiagnoAssist Backend

Handles business logic for search operations including:
- Search execution and result processing
- Search optimization and caching
- Search analytics and insights
- Saved searches and search history
"""
import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json

from app.models.search import (
    SearchRequest, SearchResponse, SearchResult, SearchEntity, SearchType,
    SavedSearch, SearchHistory, SearchAnalytics, SearchSuggestion,
    QuickSearch, SearchTemplate, SearchConfiguration
)
from app.models.auth import UserModel, UserRoleEnum
from app.repositories.search_repository import SearchRepository
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError
# Simplified for core functionality - removed enterprise monitoring/performance systems

logger = logging.getLogger(__name__)


class SearchService:
    """Service for search operations and management"""
    
    def __init__(self, search_repository: SearchRepository):
        self.search_repository = search_repository
        self._search_cache = {}
        self._cache_duration = 300  # 5 minutes
        self._search_analytics = {}
    
    # Main Search Operations
    
    async def search(
        self,
        search_request: SearchRequest,
        user: UserModel
    ) -> SearchResponse:
        """
        Execute search with caching and optimization
        
        Args:
            search_request: Search parameters
            user: User performing search
            
        Returns:
            Search response
        """
        try:
            # Validate search request
            await self._validate_search_request(search_request, user)
            
            # Check cache first
            cache_key = self._generate_cache_key(search_request, user)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                logger.info(f"Returning cached search result for user {user.id}")
                return cached_result
            
            # Record search start time
            start_time = datetime.utcnow()
            
            # Execute search
            response = await self.search_repository.search(search_request, user)
            
            # Post-process results
            response = await self._post_process_search_results(response, search_request, user)
            
            # Cache result
            self._cache_search_result(cache_key, response)
            
            # Record analytics
            search_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_search_analytics(search_request, response, search_time, user)
            
            # Log search metrics
            logger.debug(f"Search executed - type: {search_request.search_type.value}, entities: {len(search_request.entities)}, duration: {search_time:.3f}s")
            
            logger.info(f"Search executed for user {user.id} in {search_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Search failed for user {user.id}: {e}")
            raise
    
    async def quick_search(
        self,
        quick_search: QuickSearch,
        user: UserModel
    ) -> List[SearchResult]:
        """
        Execute quick search for autocomplete
        
        Args:
            quick_search: Quick search parameters
            user: User performing search
            
        Returns:
            Quick search results
        """
        try:
            # Convert to full search request
            search_request = SearchRequest(
                query=quick_search.query,
                entities=[quick_search.entity] if quick_search.entity != SearchEntity.ALL else [
                    SearchEntity.PATIENT, SearchEntity.EPISODE, SearchEntity.ENCOUNTER
                ],
                search_type=SearchType.FULL_TEXT,
                limit=quick_search.limit,
                page=1
            )
            
            # Execute search
            response = await self.search(search_request, user)
            
            return response.results
            
        except Exception as e:
            logger.error(f"Quick search failed: {e}")
            raise
    
    async def advanced_search(
        self,
        search_request: SearchRequest,
        user: UserModel
    ) -> SearchResponse:
        """
        Execute advanced search with enhanced processing
        
        Args:
            search_request: Advanced search parameters
            user: User performing search
            
        Returns:
            Enhanced search response
        """
        try:
            # Set search type to advanced
            search_request.search_type = SearchType.ADVANCED
            
            # Execute base search
            response = await self.search(search_request, user)
            
            # Add advanced features
            response = await self._enhance_advanced_search_results(response, user)
            
            return response
            
        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            raise
    
    # Search Suggestions and Autocomplete
    
    async def get_search_suggestions(
        self,
        query: str,
        user: UserModel,
        entity: Optional[SearchEntity] = None,
        limit: int = 10
    ) -> List[SearchSuggestion]:
        """
        Get search suggestions for autocomplete
        
        Args:
            query: Partial query text
            user: User requesting suggestions
            entity: Optional entity filter
            limit: Maximum suggestions
            
        Returns:
            List of search suggestions
        """
        try:
            if len(query) < 2:
                return []
            
            suggestions = []
            
            # Get query completion suggestions
            completion_suggestions = await self._get_query_completions(query, user, limit // 2)
            suggestions.extend(completion_suggestions)
            
            # Get recent search suggestions
            recent_suggestions = await self._get_recent_search_suggestions(query, user, limit // 2)
            suggestions.extend(recent_suggestions)
            
            # Get popular search suggestions
            popular_suggestions = await self._get_popular_search_suggestions(query, limit // 2)
            suggestions.extend(popular_suggestions)
            
            # Remove duplicates and limit results
            unique_suggestions = []
            seen = set()
            
            for suggestion in suggestions:
                if suggestion.suggestion not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion.suggestion)
                    
                if len(unique_suggestions) >= limit:
                    break
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []
    
    async def search_entities_by_type(
        self,
        entity_type: SearchEntity,
        query: str,
        user: UserModel,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Search specific entity type
        
        Args:
            entity_type: Type of entity to search
            query: Search query
            user: User performing search
            limit: Maximum results
            
        Returns:
            Entity-specific search results
        """
        try:
            search_request = SearchRequest(
                query=query,
                entities=[entity_type],
                search_type=SearchType.FULL_TEXT,
                limit=limit,
                page=1
            )
            
            response = await self.search(search_request, user)
            return response.results
            
        except Exception as e:
            logger.error(f"Entity search failed: {e}")
            raise
    
    # Saved Searches
    
    async def save_search(
        self,
        search_request: SearchRequest,
        name: str,
        description: Optional[str],
        user: UserModel
    ) -> SavedSearch:
        """
        Save search for later use
        
        Args:
            search_request: Search to save
            name: Search name
            description: Optional description
            user: User saving search
            
        Returns:
            Saved search
        """
        try:
            saved_search = SavedSearch(
                name=name,
                description=description,
                search_request=search_request,
                created_by=user.id
            )
            
            saved_search = await self.search_repository.save_search(saved_search, user)
            
            logger.info(f"Saved search '{name}' for user {user.id}")
            return saved_search
            
        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            raise
    
    async def get_saved_searches(
        self,
        user: UserModel
    ) -> List[SavedSearch]:
        """
        Get user's saved searches
        
        Args:
            user: User requesting saved searches
            
        Returns:
            List of saved searches
        """
        try:
            return await self.search_repository.get_saved_searches(user)
            
        except Exception as e:
            logger.error(f"Failed to get saved searches: {e}")
            raise
    
    async def execute_saved_search(
        self,
        saved_search_id: str,
        user: UserModel
    ) -> SearchResponse:
        """
        Execute a saved search
        
        Args:
            saved_search_id: ID of saved search
            user: User executing search
            
        Returns:
            Search response
        """
        try:
            # Get saved searches to find the one requested
            saved_searches = await self.get_saved_searches(user)
            saved_search = next((s for s in saved_searches if s.id == saved_search_id), None)
            
            if not saved_search:
                raise NotFoundError("Saved search not found")
            
            # Execute the saved search
            response = await self.search(saved_search.search_request, user)
            
            # Update usage statistics
            await self._update_saved_search_usage(saved_search_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute saved search: {e}")
            raise
    
    # Search Analytics
    
    async def get_search_analytics(
        self,
        user: UserModel,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> SearchAnalytics:
        """
        Get search analytics for user or system
        
        Args:
            user: User requesting analytics
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Search analytics
        """
        try:
            # Default to last 30 days
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get analytics data
            analytics = await self._calculate_search_analytics(user, start_date, end_date)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            raise
    
    async def get_popular_searches(
        self,
        user: UserModel,
        entity: Optional[SearchEntity] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular search queries
        
        Args:
            user: User requesting data
            entity: Optional entity filter
            days: Number of days to analyze
            limit: Maximum results
            
        Returns:
            Popular search data
        """
        try:
            # This would query search history and aggregate popular queries
            # For now, return placeholder data
            
            popular_searches = [
                {"query": "chest pain", "count": 45, "entity": "patient"},
                {"query": "diabetes", "count": 38, "entity": "episode"},
                {"query": "hypertension", "count": 32, "entity": "encounter"},
                {"query": "cardiology template", "count": 28, "entity": "template"},
                {"query": "monthly report", "count": 22, "entity": "report"}
            ]
            
            # Filter by entity if specified
            if entity and entity != SearchEntity.ALL:
                popular_searches = [
                    s for s in popular_searches 
                    if s["entity"] == entity.value
                ]
            
            return popular_searches[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get popular searches: {e}")
            return []
    
    # Search Templates
    
    async def create_search_template(
        self,
        template: SearchTemplate,
        user: UserModel
    ) -> SearchTemplate:
        """
        Create search template
        
        Args:
            template: Search template to create
            user: User creating template
            
        Returns:
            Created search template
        """
        try:
            template.created_by = user.id
            
            # Save template (would use a repository method)
            # For now, just return the template
            import uuid
            template.id = str(uuid.uuid4())
            
            logger.info(f"Created search template '{template.name}' for user {user.id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create search template: {e}")
            raise
    
    # Private helper methods
    
    async def _validate_search_request(
        self,
        search_request: SearchRequest,
        user: UserModel
    ):
        """Validate search request"""
        
        # Check query length
        if search_request.query and len(search_request.query) > 1000:
            raise ValidationException("Query too long")
        
        # Check limit
        if search_request.limit > 100:
            raise ValidationException("Limit too high")
        
        # Check permissions for scope
        if search_request.scope.value == "organization" and user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
            raise PermissionDeniedError("Insufficient permissions for organization-wide search")
    
    def _generate_cache_key(
        self,
        search_request: SearchRequest,
        user: UserModel
    ) -> str:
        """Generate cache key for search request"""
        
        key_data = {
            "query": search_request.query,
            "entities": [e.value for e in search_request.entities],
            "search_type": search_request.search_type.value,
            "filters": [f.model_dump() for f in search_request.filters],
            "page": search_request.page,
            "limit": search_request.limit,
            "scope": search_request.scope.value,
            "user_id": user.id,
            "user_role": user.role.value
        }
        
        import hashlib
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[SearchResponse]:
        """Get cached search result"""
        
        if cache_key in self._search_cache:
            cached_item = self._search_cache[cache_key]
            
            # Check if cache is still valid
            if datetime.utcnow() - cached_item["timestamp"] < timedelta(seconds=self._cache_duration):
                return cached_item["result"]
            else:
                # Remove expired cache
                del self._search_cache[cache_key]
        
        return None
    
    def _cache_search_result(self, cache_key: str, result: SearchResponse):
        """Cache search result"""
        
        self._search_cache[cache_key] = {
            "result": result,
            "timestamp": datetime.utcnow()
        }
        
        # Clean up old cache entries periodically
        if len(self._search_cache) > 1000:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, item in self._search_cache.items():
            if current_time - item["timestamp"] > timedelta(seconds=self._cache_duration):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._search_cache[key]
    
    async def _post_process_search_results(
        self,
        response: SearchResponse,
        search_request: SearchRequest,
        user: UserModel
    ) -> SearchResponse:
        """Post-process search results for enhancement"""
        
        # Add user-specific relevance scoring
        for result in response.results:
            result.score = await self._calculate_user_relevance_score(result, user)
        
        # Re-sort by updated scores
        response.results.sort(key=lambda x: x.score, reverse=True)
        
        # Add related suggestions
        if search_request.query:
            response.suggestions = await self._get_related_suggestions(search_request.query, user)
        
        return response
    
    async def _calculate_user_relevance_score(
        self,
        result: SearchResult,
        user: UserModel
    ) -> float:
        """Calculate user-specific relevance score"""
        
        base_score = result.score
        
        # Boost score based on user's interaction history
        # This would check if user has accessed this entity before
        
        # Boost recent items
        if result.updated_at:
            days_old = (datetime.utcnow() - result.updated_at).days
            if days_old < 7:
                base_score += 0.1
        
        # Boost based on entity type preferences
        # This would analyze user's search history for preferred entity types
        
        return min(base_score, 1.0)
    
    async def _enhance_advanced_search_results(
        self,
        response: SearchResponse,
        user: UserModel
    ) -> SearchResponse:
        """Enhance advanced search results"""
        
        # Add semantic similarity grouping
        response.aggregations["semantic_groups"] = await self._group_results_semantically(response.results)
        
        # Add entity relationship data
        response.aggregations["related_entities"] = await self._find_related_entities(response.results, user)
        
        return response
    
    async def _group_results_semantically(
        self,
        results: List[SearchResult]
    ) -> Dict[str, List[str]]:
        """Group results by semantic similarity"""
        
        # Placeholder implementation
        groups = {
            "patients": [r.entity_id for r in results if r.entity_type == SearchEntity.PATIENT],
            "episodes": [r.entity_id for r in results if r.entity_type == SearchEntity.EPISODE],
            "encounters": [r.entity_id for r in results if r.entity_type == SearchEntity.ENCOUNTER]
        }
        
        return groups
    
    async def _find_related_entities(
        self,
        results: List[SearchResult],
        user: UserModel
    ) -> Dict[str, Any]:
        """Find entities related to search results"""
        
        # Placeholder implementation
        return {
            "related_patients": [],
            "related_episodes": [],
            "suggested_templates": []
        }
    
    async def _get_query_completions(
        self,
        query: str,
        user: UserModel,
        limit: int
    ) -> List[SearchSuggestion]:
        """Get query completion suggestions"""
        
        # Common medical terms and completions
        medical_terms = [
            "chest pain", "shortness of breath", "diabetes", "hypertension",
            "headache", "fever", "cough", "fatigue", "abdominal pain",
            "back pain", "anxiety", "depression", "allergic reaction"
        ]
        
        suggestions = []
        query_lower = query.lower()
        
        for term in medical_terms:
            if term.startswith(query_lower):
                suggestions.append(SearchSuggestion(
                    suggestion=term,
                    type="completion",
                    score=0.8,
                    frequency=100  # Would be actual frequency from data
                ))
        
        return suggestions[:limit]
    
    async def _get_recent_search_suggestions(
        self,
        query: str,
        user: UserModel,
        limit: int
    ) -> List[SearchSuggestion]:
        """Get suggestions from user's recent searches"""
        
        # This would query search history for user's recent queries
        suggestions = []
        
        return suggestions[:limit]
    
    async def _get_popular_search_suggestions(
        self,
        query: str,
        limit: int
    ) -> List[SearchSuggestion]:
        """Get suggestions from popular searches"""
        
        # This would query aggregated search statistics
        suggestions = []
        
        return suggestions[:limit]
    
    async def _get_related_suggestions(
        self,
        query: str,
        user: UserModel
    ) -> List[str]:
        """Get related search suggestions"""
        
        # Simple related suggestions
        if "pain" in query.lower():
            return ["symptoms", "treatment", "medication", "diagnosis"]
        elif "diabetes" in query.lower():
            return ["glucose", "insulin", "medication", "diet"]
        elif "heart" in query.lower():
            return ["cardiology", "ECG", "blood pressure", "chest pain"]
        
        return []
    
    async def _record_search_analytics(
        self,
        search_request: SearchRequest,
        response: SearchResponse,
        search_time: float,
        user: UserModel
    ):
        """Record search analytics data"""
        
        try:
            # This would record analytics in database
            analytics_data = {
                "user_id": user.id,
                "query": search_request.query,
                "entities": [e.value for e in search_request.entities],
                "search_type": search_request.search_type.value,
                "results_count": response.total_results,
                "search_time": search_time,
                "timestamp": datetime.utcnow()
            }
            
            # Store in analytics collection or time-series database
            logger.debug(f"Recording search analytics: {analytics_data}")
            
        except Exception as e:
            logger.error(f"Failed to record search analytics: {e}")
    
    async def _calculate_search_analytics(
        self,
        user: UserModel,
        start_date: datetime,
        end_date: datetime
    ) -> SearchAnalytics:
        """Calculate search analytics for period"""
        
        # Placeholder implementation - would query actual analytics data
        analytics = SearchAnalytics(
            period_start=start_date.date(),
            period_end=end_date.date(),
            total_searches=150,
            unique_users=25,
            avg_results_per_search=12.5,
            avg_execution_time=0.8,
            top_queries=[
                {"query": "chest pain", "count": 25},
                {"query": "diabetes", "count": 20},
                {"query": "hypertension", "count": 18}
            ],
            top_entities=[
                {"entity": "patient", "count": 75},
                {"entity": "episode", "count": 45},
                {"entity": "encounter", "count": 30}
            ],
            failed_searches=2,
            slow_searches=5,
            zero_result_searches=8,
            click_through_rate=68.5,
            search_refinement_rate=22.3,
            saved_search_rate=8.7
        )
        
        return analytics
    
    async def _update_saved_search_usage(self, saved_search_id: str):
        """Update saved search usage statistics"""
        
        try:
            # This would update usage count and last used timestamp
            logger.debug(f"Updating usage for saved search {saved_search_id}")
            
        except Exception as e:
            logger.error(f"Failed to update saved search usage: {e}")


# Service instance (to be initialized with dependencies)
search_service = None