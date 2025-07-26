"""
Search Repository for DiagnoAssist Backend

Handles data access operations for search including:
- Full-text search across entities
- Faceted search and filtering
- Search indexing and optimization
- Search analytics and tracking
"""
import logging
import re
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from bson import ObjectId, regex
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.repositories.base_repository import BaseRepository
from app.models.search import (
    SearchRequest, SearchResponse, SearchResult, SearchEntity, SearchType,
    SearchFilter, FilterOperator, SearchFacet, FacetValue, SavedSearch,
    SearchHistory, SearchAnalytics, SearchSuggestion, QuickSearch,
    SearchIndex, SortField, SortOrder
)
from app.models.auth import UserModel, UserRoleEnum
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)


class SearchRepository:
    """Repository for search operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        
        # Collections for searchable entities
        self.patients_collection = database.patients
        self.episodes_collection = database.episodes
        self.encounters_collection = database.encounters
        self.templates_collection = database.templates
        self.reports_collection = database.reports
        self.users_collection = database.users
        
        # Search-specific collections
        self.saved_searches_collection = database.saved_searches
        self.search_history_collection = database.search_history
        self.search_indexes_collection = database.search_indexes
        
        # Entity mapping for search
        self.entity_collections = {
            SearchEntity.PATIENT: self.patients_collection,
            SearchEntity.EPISODE: self.episodes_collection,
            SearchEntity.ENCOUNTER: self.encounters_collection,
            SearchEntity.TEMPLATE: self.templates_collection,
            SearchEntity.REPORT: self.reports_collection,
            SearchEntity.USER: self.users_collection
        }
    
    # Main Search Operations
    
    async def search(
        self,
        search_request: SearchRequest,
        user: UserModel
    ) -> SearchResponse:
        """
        Execute search request
        
        Args:
            search_request: Search parameters
            user: User performing search
            
        Returns:
            Search response with results
        """
        start_time = datetime.utcnow()
        
        try:
            # Track search in history
            await self._record_search_history(search_request, user)
            
            # Determine entities to search
            entities_to_search = self._get_entities_to_search(search_request.entities)
            
            # Execute search for each entity
            all_results = []
            all_facets = []
            
            for entity in entities_to_search:
                entity_results, entity_facets = await self._search_entity(
                    entity, search_request, user
                )
                all_results.extend(entity_results)
                all_facets.extend(entity_facets)
            
            # Sort and paginate results
            sorted_results = self._sort_results(all_results, search_request.sort_fields)
            total_results = len(sorted_results)
            
            # Apply pagination
            start_idx = (search_request.page - 1) * search_request.limit
            end_idx = start_idx + search_request.limit
            paginated_results = sorted_results[start_idx:end_idx]
            
            # Merge facets
            merged_facets = self._merge_facets(all_facets)
            
            # Calculate response metrics
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            total_pages = (total_results + search_request.limit - 1) // search_request.limit
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(search_request.query, user)
            
            response = SearchResponse(
                query=search_request.query,
                total_results=total_results,
                results=paginated_results,
                facets=merged_facets,
                page=search_request.page,
                limit=search_request.limit,
                total_pages=total_pages,
                has_next=search_request.page < total_pages,
                has_prev=search_request.page > 1,
                search_time_ms=search_time,
                suggestions=suggestions,
                searched_entities=entities_to_search,
                filters_applied=search_request.filters
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def quick_search(
        self,
        quick_search: QuickSearch,
        user: UserModel
    ) -> List[SearchResult]:
        """
        Execute quick search for autocomplete/suggestions
        
        Args:
            quick_search: Quick search parameters
            user: User performing search
            
        Returns:
            List of quick search results
        """
        try:
            # Build basic search request
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
    
    # Entity-specific search methods
    
    async def _search_entity(
        self,
        entity: SearchEntity,
        search_request: SearchRequest,
        user: UserModel
    ) -> Tuple[List[SearchResult], List[SearchFacet]]:
        """
        Search specific entity type
        
        Args:
            entity: Entity type to search
            search_request: Search parameters
            user: User performing search
            
        Returns:
            Tuple of (results, facets)
        """
        collection = self.entity_collections[entity]
        
        # Build query
        query = await self._build_search_query(entity, search_request, user)
        
        # Execute search
        cursor = collection.find(query)
        
        # Apply sorting
        if search_request.sort_fields:
            sort_criteria = self._build_sort_criteria(search_request.sort_fields)
            cursor = cursor.sort(sort_criteria)
        
        # Get documents
        documents = await cursor.to_list(length=search_request.limit * 2)  # Get extra for ranking
        
        # Convert to search results
        results = []
        for doc in documents:
            result = await self._document_to_search_result(entity, doc, search_request)
            if result:
                results.append(result)
        
        # Generate facets if requested
        facets = []
        if search_request.facets:
            facets = await self._generate_facets(entity, search_request, user)
        
        return results, facets
    
    async def _build_search_query(
        self,
        entity: SearchEntity,
        search_request: SearchRequest,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Build MongoDB query for search
        
        Args:
            entity: Entity type
            search_request: Search parameters
            user: User context
            
        Returns:
            MongoDB query
        """
        query = {}
        
        # Access control based on entity type
        query.update(await self._build_access_control_query(entity, user))
        
        # Text search
        if search_request.query:
            text_query = await self._build_text_search_query(
                entity, search_request.query, search_request.search_type
            )
            query.update(text_query)
        
        # Filters
        if search_request.filters:
            filter_query = self._build_filter_query(search_request.filters)
            query.update(filter_query)
        
        # Include/exclude inactive records
        if not search_request.include_inactive:
            inactive_query = self._build_active_only_query(entity)
            query.update(inactive_query)
        
        return query
    
    async def _build_text_search_query(
        self,
        entity: SearchEntity,
        query_text: str,
        search_type: SearchType
    ) -> Dict[str, Any]:
        """
        Build text search query based on search type
        
        Args:
            entity: Entity type
            query_text: Search text
            search_type: Type of search
            
        Returns:
            Text search query
        """
        if search_type == SearchType.FULL_TEXT:
            return {"$text": {"$search": query_text}}
        
        elif search_type == SearchType.FUZZY:
            # Build regex-based fuzzy search
            escaped_query = re.escape(query_text)
            fuzzy_pattern = escaped_query.replace(r"\ ", r".*")
            return {
                "$or": await self._get_searchable_fields_query(entity, fuzzy_pattern)
            }
        
        elif search_type == SearchType.STRUCTURED:
            # Parse structured query (field:value format)
            return self._parse_structured_query(query_text)
        
        else:
            # Default to text search
            return {"$text": {"$search": query_text}}
    
    async def _get_searchable_fields_query(
        self,
        entity: SearchEntity,
        pattern: str
    ) -> List[Dict[str, Any]]:
        """
        Get searchable fields for entity with regex pattern
        
        Args:
            entity: Entity type
            pattern: Regex pattern
            
        Returns:
            List of field queries
        """
        field_mapping = {
            SearchEntity.PATIENT: [
                "demographics.name", "demographics.email", "id",
                "medical_background.past_medical_history"
            ],
            SearchEntity.EPISODE: [
                "chief_complaint", "id", "category"
            ],
            SearchEntity.ENCOUNTER: [
                "id", "soap.subjective.chief_complaint",
                "soap.assessment.primary_diagnosis"
            ],
            SearchEntity.TEMPLATE: [
                "name", "description", "tags"
            ],
            SearchEntity.REPORT: [
                "title", "description"
            ],
            SearchEntity.USER: [
                "name", "email"
            ]
        }
        
        fields = field_mapping.get(entity, [])
        
        return [
            {field: {"$regex": pattern, "$options": "i"}}
            for field in fields
        ]
    
    def _build_filter_query(self, filters: List[SearchFilter]) -> Dict[str, Any]:
        """
        Build filter query from search filters
        
        Args:
            filters: List of search filters
            
        Returns:
            Filter query
        """
        if not filters:
            return {}
        
        query_parts = []
        
        for filter_item in filters:
            field_query = self._build_single_filter_query(filter_item)
            if field_query:
                query_parts.append(field_query)
        
        if len(query_parts) == 1:
            return query_parts[0]
        elif len(query_parts) > 1:
            return {"$and": query_parts}
        
        return {}
    
    def _build_single_filter_query(self, filter_item: SearchFilter) -> Dict[str, Any]:
        """
        Build query for single filter
        
        Args:
            filter_item: Search filter
            
        Returns:
            Filter query
        """
        field = filter_item.field
        operator = filter_item.operator
        value = filter_item.value
        
        operator_mapping = {
            FilterOperator.EQUALS: {field: value},
            FilterOperator.NOT_EQUALS: {field: {"$ne": value}},
            FilterOperator.GREATER_THAN: {field: {"$gt": value}},
            FilterOperator.GREATER_THAN_EQUAL: {field: {"$gte": value}},
            FilterOperator.LESS_THAN: {field: {"$lt": value}},
            FilterOperator.LESS_THAN_EQUAL: {field: {"$lte": value}},
            FilterOperator.IN: {field: {"$in": value}},
            FilterOperator.NOT_IN: {field: {"$nin": value}},
            FilterOperator.CONTAINS: {field: {"$regex": str(value), "$options": "i"}},
            FilterOperator.NOT_CONTAINS: {field: {"$not": {"$regex": str(value), "$options": "i"}}},
            FilterOperator.STARTS_WITH: {field: {"$regex": f"^{re.escape(str(value))}", "$options": "i"}},
            FilterOperator.ENDS_WITH: {field: {"$regex": f"{re.escape(str(value))}$", "$options": "i"}},
            FilterOperator.EXISTS: {field: {"$exists": True}},
            FilterOperator.NOT_EXISTS: {field: {"$exists": False}},
            FilterOperator.BETWEEN: {field: {"$gte": value[0], "$lte": value[1]}} if isinstance(value, list) and len(value) == 2 else {}
        }
        
        return operator_mapping.get(operator, {})
    
    async def _build_access_control_query(
        self,
        entity: SearchEntity,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Build access control query based on user permissions
        
        Args:
            entity: Entity type
            user: User context
            
        Returns:
            Access control query
        """
        # Admin users can see everything
        if user.role == UserRoleEnum.ADMIN:
            return {}
        
        # Entity-specific access control
        if entity == SearchEntity.PATIENT:
            # Users can see patients they have access to
            return {}  # Implement based on your access control logic
        
        elif entity == SearchEntity.TEMPLATE:
            # Users can see their own templates or public ones
            return {
                "$or": [
                    {"owner_id": user.id},
                    {"scope": {"$in": ["public", "organization"]}},
                    {"shared_with_users": user.id},
                    {"shared_with_roles": user.role.value}
                ]
            }
        
        elif entity == SearchEntity.REPORT:
            # Users can see their own reports or shared ones
            return {
                "$or": [
                    {"requested_by": user.id},
                    {"shared_with": user.id},
                    {"is_public": True}
                ]
            }
        
        elif entity == SearchEntity.USER:
            # Users can see other users (basic info only)
            return {"is_active": True}
        
        return {}
    
    def _build_active_only_query(self, entity: SearchEntity) -> Dict[str, Any]:
        """
        Build query to exclude inactive records
        
        Args:
            entity: Entity type
            
        Returns:
            Active records query
        """
        active_field_mapping = {
            SearchEntity.PATIENT: {"is_active": {"$ne": False}},
            SearchEntity.EPISODE: {"status": {"$ne": "deleted"}},
            SearchEntity.ENCOUNTER: {"status": {"$ne": "deleted"}},
            SearchEntity.TEMPLATE: {"is_active": {"$ne": False}},
            SearchEntity.REPORT: {"status": {"$ne": "deleted"}},
            SearchEntity.USER: {"is_active": True}
        }
        
        return active_field_mapping.get(entity, {})
    
    def _parse_structured_query(self, query_text: str) -> Dict[str, Any]:
        """
        Parse structured query in field:value format
        
        Args:
            query_text: Structured query text
            
        Returns:
            Structured query
        """
        # Simple implementation - can be enhanced
        parts = query_text.split()
        query = {}
        
        for part in parts:
            if ":" in part:
                field, value = part.split(":", 1)
                query[field] = {"$regex": value, "$options": "i"}
        
        return {"$and": [query]} if query else {}
    
    def _build_sort_criteria(self, sort_fields: List[SortField]) -> List[Tuple[str, int]]:
        """
        Build MongoDB sort criteria
        
        Args:
            sort_fields: Sort field specifications
            
        Returns:
            MongoDB sort criteria
        """
        criteria = []
        
        # Sort by priority first
        sorted_fields = sorted(sort_fields, key=lambda x: x.priority)
        
        for sort_field in sorted_fields:
            direction = 1 if sort_field.order == SortOrder.ASC else -1
            criteria.append((sort_field.field, direction))
        
        # Default sort by relevance score if no sort specified
        if not criteria:
            criteria.append(("score", -1))
        
        return criteria
    
    def _sort_results(
        self,
        results: List[SearchResult],
        sort_fields: List[SortField]
    ) -> List[SearchResult]:
        """
        Sort search results
        
        Args:
            results: Search results to sort
            sort_fields: Sort specifications
            
        Returns:
            Sorted results
        """
        if not sort_fields:
            # Default sort by score descending
            return sorted(results, key=lambda x: x.score, reverse=True)
        
        # Build sort key function
        def sort_key(result):
            keys = []
            for sort_field in sorted(sort_fields, key=lambda x: x.priority):
                value = self._get_result_field_value(result, sort_field.field)
                if sort_field.order == SortOrder.DESC:
                    if isinstance(value, (int, float)):
                        value = -value
                keys.append(value)
            return tuple(keys)
        
        return sorted(results, key=sort_key)
    
    def _get_result_field_value(self, result: SearchResult, field: str) -> Any:
        """
        Get field value from search result for sorting
        
        Args:
            result: Search result
            field: Field name
            
        Returns:
            Field value
        """
        if hasattr(result, field):
            return getattr(result, field)
        
        return result.data.get(field, 0)
    
    async def _document_to_search_result(
        self,
        entity: SearchEntity,
        document: Dict[str, Any],
        search_request: SearchRequest
    ) -> Optional[SearchResult]:
        """
        Convert database document to search result
        
        Args:
            entity: Entity type
            document: Database document
            search_request: Search request for context
            
        Returns:
            Search result or None if conversion fails
        """
        try:
            # Calculate relevance score
            score = self._calculate_relevance_score(document, search_request.query)
            
            # Generate highlights
            highlights = {}
            if search_request.highlight.enabled and search_request.query:
                highlights = self._generate_highlights(
                    entity, document, search_request.query, search_request.highlight
                )
            
            # Entity-specific result formatting
            if entity == SearchEntity.PATIENT:
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=document.get("demographics", {}).get("name", "Unknown Patient"),
                    description=f"Patient ID: {document.get('id')}",
                    url=f"/patients/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "demographics": document.get("demographics", {}),
                        "age": self._calculate_age(document.get("demographics", {}).get("date_of_birth")),
                        "gender": document.get("demographics", {}).get("gender")
                    },
                    created_at=document.get("created_at"),
                    updated_at=document.get("updated_at")
                )
            
            elif entity == SearchEntity.EPISODE:
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=document.get("chief_complaint", "Episode"),
                    description=f"Category: {document.get('category', 'Unknown')}",
                    url=f"/episodes/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "patient_id": document.get("patient_id"),
                        "category": document.get("category"),
                        "status": document.get("status")
                    },
                    created_at=document.get("created_at"),
                    updated_at=document.get("updated_at")
                )
            
            elif entity == SearchEntity.ENCOUNTER:
                soap = document.get("soap", {})
                chief_complaint = soap.get("subjective", {}).get("chief_complaint", "")
                
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=chief_complaint or f"Encounter {document.get('id')}",
                    description=f"Type: {document.get('type', 'Unknown')}",
                    url=f"/encounters/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "patient_id": document.get("patient_id"),
                        "episode_id": document.get("episode_id"),
                        "type": document.get("type"),
                        "status": document.get("status")
                    },
                    created_at=document.get("created_at"),
                    updated_at=document.get("updated_at")
                )
            
            elif entity == SearchEntity.TEMPLATE:
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=document.get("name", "Template"),
                    description=document.get("description", ""),
                    url=f"/templates/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "template_type": document.get("template_type"),
                        "category": document.get("category"),
                        "scope": document.get("scope"),
                        "usage_count": document.get("metadata", {}).get("usage_count", 0)
                    },
                    created_at=document.get("metadata", {}).get("created_at"),
                    updated_at=document.get("metadata", {}).get("updated_at")
                )
            
            elif entity == SearchEntity.REPORT:
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=document.get("title", "Report"),
                    description=document.get("description", ""),
                    url=f"/reports/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "report_type": document.get("report_type"),
                        "status": document.get("status"),
                        "requested_by": document.get("requested_by")
                    },
                    created_at=document.get("requested_at"),
                    updated_at=document.get("generated_at")
                )
            
            elif entity == SearchEntity.USER:
                return SearchResult(
                    entity_type=entity,
                    entity_id=document.get("id", str(document.get("_id"))),
                    title=document.get("name", "User"),
                    description=f"Role: {document.get('role', 'Unknown')}",
                    url=f"/users/{document.get('id')}",
                    score=score,
                    highlights=highlights,
                    data={
                        "email": document.get("email"),
                        "role": document.get("role"),
                        "is_active": document.get("is_active")
                    },
                    created_at=document.get("created_at"),
                    updated_at=document.get("updated_at")
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to convert document to search result: {e}")
            return None
    
    def _calculate_relevance_score(
        self,
        document: Dict[str, Any],
        query: Optional[str]
    ) -> float:
        """
        Calculate relevance score for document
        
        Args:
            document: Database document
            query: Search query
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not query:
            return 1.0
        
        # Simple TF-IDF-like scoring
        score = 0.0
        query_lower = query.lower()
        
        # Check common fields for matches
        searchable_text = ""
        
        # Extract searchable text based on document type
        if "demographics" in document:  # Patient
            demo = document["demographics"]
            searchable_text += f" {demo.get('name', '')} {demo.get('email', '')}"
        
        if "name" in document:  # Template, User
            searchable_text += f" {document['name']}"
        
        if "title" in document:  # Report
            searchable_text += f" {document['title']}"
        
        if "chief_complaint" in document:  # Episode
            searchable_text += f" {document['chief_complaint']}"
        
        # Calculate score based on matches
        text_lower = searchable_text.lower()
        query_words = query_lower.split()
        
        for word in query_words:
            if word in text_lower:
                # Boost score for exact matches
                score += 0.3
                
                # Additional boost for matches in important fields
                if "name" in document and word in document.get("name", "").lower():
                    score += 0.2
        
        # Normalize score
        return min(score, 1.0)
    
    def _generate_highlights(
        self,
        entity: SearchEntity,
        document: Dict[str, Any],
        query: str,
        highlight_config: Any
    ) -> Dict[str, List[str]]:
        """
        Generate highlighted text snippets
        
        Args:
            entity: Entity type
            document: Database document
            query: Search query
            highlight_config: Highlight configuration
            
        Returns:
            Highlighted snippets by field
        """
        highlights = {}
        
        if not query:
            return highlights
        
        query_words = query.lower().split()
        
        # Get highlightable fields based on entity
        fields_to_highlight = self._get_highlightable_fields(entity, document)
        
        for field_name, field_value in fields_to_highlight.items():
            if isinstance(field_value, str) and field_value:
                highlighted_snippets = self._highlight_text(
                    field_value, query_words, highlight_config
                )
                if highlighted_snippets:
                    highlights[field_name] = highlighted_snippets
        
        return highlights
    
    def _get_highlightable_fields(
        self,
        entity: SearchEntity,
        document: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Get fields that can be highlighted for entity
        
        Args:
            entity: Entity type
            document: Database document
            
        Returns:
            Dictionary of field names to text values
        """
        fields = {}
        
        if entity == SearchEntity.PATIENT:
            demo = document.get("demographics", {})
            fields["name"] = demo.get("name", "")
            fields["medical_history"] = document.get("medical_background", {}).get("past_medical_history", "")
        
        elif entity == SearchEntity.EPISODE:
            fields["chief_complaint"] = document.get("chief_complaint", "")
        
        elif entity == SearchEntity.ENCOUNTER:
            soap = document.get("soap", {})
            fields["chief_complaint"] = soap.get("subjective", {}).get("chief_complaint", "")
            fields["assessment"] = soap.get("assessment", {}).get("primary_diagnosis", "")
        
        elif entity == SearchEntity.TEMPLATE:
            fields["name"] = document.get("name", "")
            fields["description"] = document.get("description", "")
        
        elif entity == SearchEntity.REPORT:
            fields["title"] = document.get("title", "")
            fields["description"] = document.get("description", "")
        
        return fields
    
    def _highlight_text(
        self,
        text: str,
        query_words: List[str],
        highlight_config: Any
    ) -> List[str]:
        """
        Highlight query words in text
        
        Args:
            text: Text to highlight
            query_words: Words to highlight
            highlight_config: Highlight configuration
            
        Returns:
            List of highlighted text snippets
        """
        snippets = []
        text_lower = text.lower()
        
        for word in query_words:
            if word in text_lower:
                # Find word positions
                start = text_lower.find(word)
                if start != -1:
                    # Create snippet around the match
                    snippet_start = max(0, start - highlight_config.fragment_size // 2)
                    snippet_end = min(len(text), start + len(word) + highlight_config.fragment_size // 2)
                    
                    snippet = text[snippet_start:snippet_end]
                    
                    # Highlight the word
                    highlighted_snippet = re.sub(
                        re.escape(word),
                        f"{highlight_config.pre_tag}{word}{highlight_config.post_tag}",
                        snippet,
                        flags=re.IGNORECASE
                    )
                    
                    snippets.append(highlighted_snippet)
                    
                    if len(snippets) >= highlight_config.number_of_fragments:
                        break
        
        return snippets
    
    def _calculate_age(self, date_of_birth: Optional[str]) -> Optional[int]:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        
        try:
            from datetime import datetime
            dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            today = datetime.now(dob.tzinfo)
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return None
    
    # Additional helper methods for facets, suggestions, etc.
    
    async def _generate_facets(
        self,
        entity: SearchEntity,
        search_request: SearchRequest,
        user: UserModel
    ) -> List[SearchFacet]:
        """Generate facets for search results"""
        # Placeholder implementation
        return []
    
    def _merge_facets(self, facet_lists: List[List[SearchFacet]]) -> List[SearchFacet]:
        """Merge facets from multiple entity searches"""
        # Placeholder implementation
        return []
    
    async def _generate_suggestions(
        self,
        query: Optional[str],
        user: UserModel
    ) -> List[str]:
        """Generate search suggestions"""
        if not query or len(query) < 2:
            return []
        
        # Simple suggestions based on common searches
        suggestions = [
            f"{query} patient",
            f"{query} episode",
            f"{query} template"
        ]
        
        return suggestions[:5]
    
    def _get_entities_to_search(self, entities: List[SearchEntity]) -> List[SearchEntity]:
        """Get actual entities to search"""
        if SearchEntity.ALL in entities:
            return [
                SearchEntity.PATIENT,
                SearchEntity.EPISODE,
                SearchEntity.ENCOUNTER,
                SearchEntity.TEMPLATE,
                SearchEntity.REPORT
            ]
        
        return entities
    
    # Search history and analytics
    
    async def _record_search_history(
        self,
        search_request: SearchRequest,
        user: UserModel
    ):
        """Record search in history"""
        try:
            history_entry = SearchHistory(
                user_id=user.id,
                query=search_request.query,
                entities=search_request.entities,
                filters_count=len(search_request.filters)
            )
            
            await self.search_history_collection.insert_one(
                history_entry.model_dump()
            )
            
        except Exception as e:
            logger.error(f"Failed to record search history: {e}")
    
    # Saved searches
    
    async def save_search(
        self,
        saved_search: SavedSearch,
        user: UserModel
    ) -> SavedSearch:
        """Save a search for later use"""
        try:
            saved_search.created_by = user.id
            saved_search.id = str(ObjectId())
            
            document = saved_search.model_dump()
            await self.saved_searches_collection.insert_one(document)
            
            return saved_search
            
        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            raise
    
    async def get_saved_searches(
        self,
        user: UserModel
    ) -> List[SavedSearch]:
        """Get user's saved searches"""
        try:
            cursor = self.saved_searches_collection.find({
                "$or": [
                    {"created_by": user.id},
                    {"is_public": True},
                    {"shared_with": user.id}
                ]
            }).sort("created_at", -1)
            
            documents = await cursor.to_list(length=100)
            
            return [SavedSearch(**doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Failed to get saved searches: {e}")
            raise