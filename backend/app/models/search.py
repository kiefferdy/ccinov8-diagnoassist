"""
Search Models for DiagnoAssist Backend

Advanced search and indexing models for:
- Full-text search across entities
- Faceted search and filtering
- Search analytics and optimization
- Saved searches and search history
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class SearchEntity(str, Enum):
    """Searchable entity types"""
    PATIENT = "patient"
    EPISODE = "episode"
    ENCOUNTER = "encounter"
    TEMPLATE = "template"
    REPORT = "report"
    USER = "user"
    ALL = "all"


class SearchType(str, Enum):
    """Types of search operations"""
    FULL_TEXT = "full_text"
    STRUCTURED = "structured"
    FACETED = "faceted"
    SEMANTIC = "semantic"
    FUZZY = "fuzzy"
    ADVANCED = "advanced"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class SearchScope(str, Enum):
    """Search scope limitations"""
    USER = "user"           # User's own data
    DEPARTMENT = "department"  # Department data
    ORGANIZATION = "organization"  # Organization-wide
    PUBLIC = "public"       # Public/shared data


class FieldType(str, Enum):
    """Search field types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"


class FilterOperator(str, Enum):
    """Filter operators"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_EQUAL = "lte"
    IN = "in"
    NOT_IN = "nin"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    BETWEEN = "between"


class SearchFilter(BaseModel):
    """Individual search filter"""
    field: str = Field(..., description="Field name to filter on")
    operator: FilterOperator = Field(..., description="Filter operator")
    value: Union[str, int, float, bool, List[Any], Dict[str, Any]] = Field(..., description="Filter value")
    field_type: FieldType = Field(FieldType.TEXT, description="Field data type")
    
    @validator('value')
    def validate_value_for_operator(cls, v, values):
        """Validate value matches operator requirements"""
        operator = values.get('operator')
        
        if operator in [FilterOperator.IN, FilterOperator.NOT_IN] and not isinstance(v, list):
            raise ValueError(f"Operator {operator} requires a list value")
        
        if operator == FilterOperator.BETWEEN:
            if not isinstance(v, list) or len(v) != 2:
                raise ValueError("BETWEEN operator requires exactly 2 values")
        
        return v


class SortField(BaseModel):
    """Sort field specification"""
    field: str = Field(..., description="Field name to sort by")
    order: SortOrder = Field(SortOrder.ASC, description="Sort order")
    priority: int = Field(1, description="Sort priority (1 = highest)")


class FacetField(BaseModel):
    """Facet field specification for faceted search"""
    field: str = Field(..., description="Field to create facets for")
    limit: int = Field(10, ge=1, le=100, description="Maximum facet values to return")
    min_count: int = Field(1, ge=1, description="Minimum count for facet values")
    include_counts: bool = Field(True, description="Include document counts")


class SearchHighlight(BaseModel):
    """Search result highlighting configuration"""
    enabled: bool = Field(True, description="Enable highlighting")
    fields: List[str] = Field(default_factory=list, description="Fields to highlight")
    pre_tag: str = Field("<mark>", description="HTML tag before match")
    post_tag: str = Field("</mark>", description="HTML tag after match")
    fragment_size: int = Field(150, description="Size of highlighted fragments")
    number_of_fragments: int = Field(3, description="Number of fragments per field")


class SearchRequest(BaseModel):
    """Search request model"""
    query: Optional[str] = Field(None, description="Search query text")
    entities: List[SearchEntity] = Field([SearchEntity.ALL], description="Entity types to search")
    search_type: SearchType = Field(SearchType.FULL_TEXT, description="Type of search")
    
    # Filtering
    filters: List[SearchFilter] = Field(default_factory=list, description="Search filters")
    
    # Faceted search
    facets: List[FacetField] = Field(default_factory=list, description="Facet fields")
    
    # Sorting
    sort_fields: List[SortField] = Field(default_factory=list, description="Sort specifications")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Results per page")
    
    # Highlighting
    highlight: SearchHighlight = Field(default_factory=SearchHighlight, description="Highlighting configuration")
    
    # Scope and permissions
    scope: SearchScope = Field(SearchScope.USER, description="Search scope")
    include_inactive: bool = Field(False, description="Include inactive/deleted records")
    
    # Advanced options
    fuzzy_threshold: float = Field(0.7, ge=0.1, le=1.0, description="Fuzzy search threshold")
    boost_fields: Dict[str, float] = Field(default_factory=dict, description="Field boost weights")
    minimum_should_match: Optional[str] = Field(None, description="Minimum should match criteria")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate search query"""
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Query cannot be empty")
        return v.strip() if v else None


class SearchResult(BaseModel):
    """Individual search result"""
    entity_type: SearchEntity = Field(..., description="Type of entity")
    entity_id: str = Field(..., description="Entity ID")
    title: str = Field(..., description="Result title")
    description: Optional[str] = Field(None, description="Result description")
    url: Optional[str] = Field(None, description="Result URL/endpoint")
    
    # Match information
    score: float = Field(..., description="Search relevance score")
    highlights: Dict[str, List[str]] = Field(default_factory=dict, description="Highlighted text snippets")
    matched_fields: List[str] = Field(default_factory=list, description="Fields that matched")
    
    # Entity-specific data
    data: Dict[str, Any] = Field(default_factory=dict, description="Entity-specific data")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Entity creation date")
    updated_at: Optional[datetime] = Field(None, description="Entity last update")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")


class FacetValue(BaseModel):
    """Facet value with count"""
    value: str = Field(..., description="Facet value")
    count: int = Field(..., description="Number of documents")
    selected: bool = Field(False, description="Whether this facet is selected")


class SearchFacet(BaseModel):
    """Search facet results"""
    field: str = Field(..., description="Facet field name")
    display_name: str = Field(..., description="Human-readable facet name")
    values: List[FacetValue] = Field(..., description="Facet values and counts")
    total_values: int = Field(..., description="Total number of unique values")


class SearchResponse(BaseModel):
    """Search response model"""
    query: Optional[str] = Field(None, description="Original search query")
    total_results: int = Field(..., description="Total number of results")
    results: List[SearchResult] = Field(..., description="Search results")
    
    # Facets
    facets: List[SearchFacet] = Field(default_factory=list, description="Search facets")
    
    # Pagination
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Results per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    # Performance metrics
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")
    
    # Query suggestions
    suggestions: List[str] = Field(default_factory=list, description="Query suggestions")
    
    # Aggregations
    aggregations: Dict[str, Any] = Field(default_factory=dict, description="Search aggregations")
    
    # Metadata
    searched_entities: List[SearchEntity] = Field(..., description="Entities that were searched")
    filters_applied: List[SearchFilter] = Field(default_factory=list, description="Filters that were applied")
    executed_at: datetime = Field(default_factory=datetime.utcnow, description="Search execution time")


class SavedSearch(BaseModel):
    """Saved search model"""
    id: Optional[str] = Field(None, description="Saved search ID")
    name: str = Field(..., min_length=1, max_length=200, description="Search name")
    description: Optional[str] = Field(None, max_length=500, description="Search description")
    
    # Search configuration
    search_request: SearchRequest = Field(..., description="Saved search parameters")
    
    # Metadata
    created_by: str = Field(..., description="User who created the search")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Usage tracking
    usage_count: int = Field(0, description="Number of times search was executed")
    last_used: Optional[datetime] = Field(None, description="Last execution time")
    
    # Sharing
    is_public: bool = Field(False, description="Whether search is publicly available")
    shared_with: List[str] = Field(default_factory=list, description="User IDs with access")
    
    # Notifications
    is_alert: bool = Field(False, description="Whether to send alerts for new results")
    alert_frequency: Optional[str] = Field(None, description="Alert frequency (daily, weekly, etc.)")
    last_alert_sent: Optional[datetime] = Field(None, description="Last alert timestamp")


class SearchHistory(BaseModel):
    """Search history entry"""
    id: Optional[str] = Field(None, description="History entry ID")
    user_id: str = Field(..., description="User who performed the search")
    query: Optional[str] = Field(None, description="Search query")
    entities: List[SearchEntity] = Field(..., description="Searched entities")
    filters_count: int = Field(0, description="Number of filters applied")
    results_count: int = Field(0, description="Number of results returned")
    execution_time_ms: float = Field(0, description="Execution time")
    
    # Actions
    clicked_results: List[str] = Field(default_factory=list, description="Result IDs that were clicked")
    saved_as_search: Optional[str] = Field(None, description="Saved search ID if saved")
    
    # Metadata
    searched_at: datetime = Field(default_factory=datetime.utcnow, description="Search timestamp")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")


class SearchIndex(BaseModel):
    """Search index configuration"""
    id: Optional[str] = Field(None, description="Index ID")
    name: str = Field(..., description="Index name")
    entity_type: SearchEntity = Field(..., description="Entity type being indexed")
    
    # Index configuration
    fields: List[Dict[str, Any]] = Field(..., description="Indexed fields configuration")
    text_fields: List[str] = Field(default_factory=list, description="Full-text searchable fields")
    facet_fields: List[str] = Field(default_factory=list, description="Facetable fields")
    sortable_fields: List[str] = Field(default_factory=list, description="Sortable fields")
    
    # Performance settings
    refresh_interval: int = Field(30, description="Index refresh interval in seconds")
    max_result_window: int = Field(10000, description="Maximum result window size")
    
    # Status
    is_active: bool = Field(True, description="Whether index is active")
    last_updated: Optional[datetime] = Field(None, description="Last index update")
    document_count: int = Field(0, description="Number of indexed documents")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Index creation time")
    created_by: str = Field(..., description="User who created the index")


class SearchAnalytics(BaseModel):
    """Search analytics data"""
    period_start: date = Field(..., description="Analytics period start")
    period_end: date = Field(..., description="Analytics period end")
    
    # Query analytics
    total_searches: int = Field(0, description="Total number of searches")
    unique_users: int = Field(0, description="Number of unique users")
    avg_results_per_search: float = Field(0, description="Average results per search")
    avg_execution_time: float = Field(0, description="Average execution time")
    
    # Popular queries
    top_queries: List[Dict[str, Any]] = Field(default_factory=list, description="Most popular queries")
    top_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Most searched entities")
    top_filters: List[Dict[str, Any]] = Field(default_factory=list, description="Most used filters")
    
    # Performance metrics
    failed_searches: int = Field(0, description="Number of failed searches")
    slow_searches: int = Field(0, description="Number of slow searches (>5s)")
    zero_result_searches: int = Field(0, description="Searches with no results")
    
    # User behavior
    click_through_rate: float = Field(0, description="Click-through rate percentage")
    search_refinement_rate: float = Field(0, description="Search refinement rate")
    saved_search_rate: float = Field(0, description="Rate of saving searches")


class SearchSuggestion(BaseModel):
    """Search suggestion model"""
    suggestion: str = Field(..., description="Suggested query")
    type: str = Field(..., description="Suggestion type (completion, correction, etc.)")
    score: float = Field(..., description="Suggestion relevance score")
    frequency: int = Field(0, description="How often this suggestion appears")


class SearchConfiguration(BaseModel):
    """Global search configuration"""
    # Default settings
    default_limit: int = Field(20, description="Default results per page")
    max_limit: int = Field(100, description="Maximum results per page")
    default_fuzzy_threshold: float = Field(0.7, description="Default fuzzy search threshold")
    
    # Performance settings
    search_timeout_seconds: int = Field(30, description="Search timeout")
    cache_duration_seconds: int = Field(300, description="Search cache duration")
    max_concurrent_searches: int = Field(100, description="Maximum concurrent searches")
    
    # Features
    enable_suggestions: bool = Field(True, description="Enable search suggestions")
    enable_analytics: bool = Field(True, description="Enable search analytics")
    enable_caching: bool = Field(True, description="Enable search result caching")
    enable_highlighting: bool = Field(True, description="Enable result highlighting")
    
    # Security
    max_query_length: int = Field(1000, description="Maximum query length")
    allowed_regex_patterns: bool = Field(False, description="Allow regex in searches")
    sanitize_queries: bool = Field(True, description="Sanitize search queries")


class QuickSearch(BaseModel):
    """Quick search model for simple searches"""
    query: str = Field(..., min_length=1, description="Quick search query")
    entity: SearchEntity = Field(SearchEntity.ALL, description="Entity to search")
    limit: int = Field(10, ge=1, le=50, description="Maximum results")


class SearchTemplate(BaseModel):
    """Search template for predefined searches"""
    id: Optional[str] = Field(None, description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    
    # Template configuration
    search_request: SearchRequest = Field(..., description="Template search configuration")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Template parameters")
    
    # Metadata
    is_system_template: bool = Field(False, description="Whether this is a system template")
    usage_count: int = Field(0, description="Usage count")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")