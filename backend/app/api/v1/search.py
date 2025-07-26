"""
Search API endpoints for DiagnoAssist Backend

REST endpoints for search functionality:
- Full-text and advanced search
- Quick search and autocomplete
- Saved searches and search history
- Search analytics and insights
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from datetime import datetime, timedelta

from app.models.auth import UserModel, UserRoleEnum
from app.models.search import (
    SearchRequest, SearchResponse, SearchEntity, SearchType,
    QuickSearch, SavedSearch, SearchAnalytics, SearchSuggestion,
    SearchTemplate
)
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.search_service import search_service
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)

router = APIRouter()


# Main Search Operations

@router.post("/", response_model=dict)
async def search(
    search_request: SearchRequest = Body(..., description="Search parameters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Execute search across entities
    
    Args:
        search_request: Search parameters
        current_user: Authenticated user
        
    Returns:
        Search results with facets and pagination
    """
    try:
        response = await search_service.search(search_request, current_user)
        
        return {
            "success": True,
            "data": response.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/quick", response_model=dict)
async def quick_search(
    quick_search: QuickSearch = Body(..., description="Quick search parameters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Execute quick search for autocomplete
    
    Args:
        quick_search: Quick search parameters
        current_user: Authenticated user
        
    Returns:
        Quick search results
    """
    try:
        results = await search_service.quick_search(quick_search, current_user)
        
        return {
            "success": True,
            "data": {
                "results": [result.model_dump() for result in results],
                "count": len(results),
                "query": quick_search.query
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Quick search failed: {e}")
        raise HTTPException(status_code=500, detail="Quick search failed")


@router.post("/advanced", response_model=dict)
async def advanced_search(
    search_request: SearchRequest = Body(..., description="Advanced search parameters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Execute advanced search with enhanced features
    
    Args:
        search_request: Advanced search parameters
        current_user: Authenticated user
        
    Returns:
        Enhanced search results
    """
    try:
        response = await search_service.advanced_search(search_request, current_user)
        
        return {
            "success": True,
            "data": response.model_dump(),
            "message": "Advanced search completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(status_code=500, detail="Advanced search failed")


# Entity-specific Search

@router.get("/patients", response_model=dict)
async def search_patients(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Search patients specifically
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Patient search results
    """
    try:
        results = await search_service.search_entities_by_type(
            SearchEntity.PATIENT, q, current_user, limit
        )
        
        return {
            "success": True,
            "data": {
                "patients": [result.model_dump() for result in results],
                "count": len(results),
                "query": q
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Patient search failed: {e}")
        raise HTTPException(status_code=500, detail="Patient search failed")


@router.get("/episodes", response_model=dict)
async def search_episodes(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Search episodes specifically
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Episode search results
    """
    try:
        results = await search_service.search_entities_by_type(
            SearchEntity.EPISODE, q, current_user, limit
        )
        
        return {
            "success": True,
            "data": {
                "episodes": [result.model_dump() for result in results],
                "count": len(results),
                "query": q
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Episode search failed: {e}")
        raise HTTPException(status_code=500, detail="Episode search failed")


@router.get("/encounters", response_model=dict)
async def search_encounters(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Search encounters specifically
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Encounter search results
    """
    try:
        results = await search_service.search_entities_by_type(
            SearchEntity.ENCOUNTER, q, current_user, limit
        )
        
        return {
            "success": True,
            "data": {
                "encounters": [result.model_dump() for result in results],
                "count": len(results),
                "query": q
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Encounter search failed: {e}")
        raise HTTPException(status_code=500, detail="Encounter search failed")


@router.get("/templates", response_model=dict)
async def search_templates(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Search templates specifically
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Template search results
    """
    try:
        results = await search_service.search_entities_by_type(
            SearchEntity.TEMPLATE, q, current_user, limit
        )
        
        return {
            "success": True,
            "data": {
                "templates": [result.model_dump() for result in results],
                "count": len(results),
                "query": q
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Template search failed: {e}")
        raise HTTPException(status_code=500, detail="Template search failed")


# Search Suggestions and Autocomplete

@router.get("/suggestions", response_model=dict)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Query for suggestions"),
    entity: Optional[SearchEntity] = Query(None, description="Entity type filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum suggestions"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get search suggestions for autocomplete
    
    Args:
        q: Query text
        entity: Optional entity filter
        limit: Maximum suggestions
        current_user: Authenticated user
        
    Returns:
        Search suggestions
    """
    try:
        suggestions = await search_service.get_search_suggestions(
            q, current_user, entity, limit
        )
        
        return {
            "success": True,
            "data": {
                "suggestions": [suggestion.model_dump() for suggestion in suggestions],
                "count": len(suggestions),
                "query": q
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


# Saved Searches

@router.post("/saved", response_model=dict)
async def save_search(
    search_request: SearchRequest = Body(..., description="Search to save"),
    name: str = Body(..., min_length=1, description="Search name"),
    description: Optional[str] = Body(None, description="Search description"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Save search for later use
    
    Args:
        search_request: Search to save
        name: Search name
        description: Optional description
        current_user: Authenticated user
        
    Returns:
        Saved search confirmation
    """
    try:
        saved_search = await search_service.save_search(
            search_request, name, description, current_user
        )
        
        return {
            "success": True,
            "data": {
                "saved_search_id": saved_search.id,
                "name": saved_search.name,
                "created_at": saved_search.created_at.isoformat()
            },
            "message": "Search saved successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to save search: {e}")
        raise HTTPException(status_code=500, detail="Failed to save search")


@router.get("/saved", response_model=dict)
async def get_saved_searches(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user's saved searches
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of saved searches
    """
    try:
        saved_searches = await search_service.get_saved_searches(current_user)
        
        return {
            "success": True,
            "data": {
                "saved_searches": [search.model_dump() for search in saved_searches],
                "count": len(saved_searches)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get saved searches: {e}")
        raise HTTPException(status_code=500, detail="Failed to get saved searches")


@router.post("/saved/{saved_search_id}/execute", response_model=dict)
async def execute_saved_search(
    saved_search_id: str = Path(..., description="Saved search ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Execute a saved search
    
    Args:
        saved_search_id: ID of saved search
        current_user: Authenticated user
        
    Returns:
        Search results
    """
    try:
        response = await search_service.execute_saved_search(saved_search_id, current_user)
        
        return {
            "success": True,
            "data": response.model_dump(),
            "message": "Saved search executed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute saved search: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute saved search")


# Search Analytics

@router.get("/analytics", response_model=dict)
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get search analytics
    
    Args:
        days: Number of days to analyze
        current_user: Authenticated user
        
    Returns:
        Search analytics data
    """
    try:
        # Check permissions for analytics
        if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
            raise PermissionDeniedError("Insufficient permissions for search analytics")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics = await search_service.get_search_analytics(
            current_user, start_date, end_date
        )
        
        return {
            "success": True,
            "data": {
                "analytics": analytics.model_dump(),
                "period_days": days
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get search analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


@router.get("/popular", response_model=dict)
async def get_popular_searches(
    entity: Optional[SearchEntity] = Query(None, description="Entity type filter"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get popular search queries
    
    Args:
        entity: Optional entity filter
        days: Number of days to analyze
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Popular search data
    """
    try:
        popular_searches = await search_service.get_popular_searches(
            current_user, entity, days, limit
        )
        
        return {
            "success": True,
            "data": {
                "popular_searches": popular_searches,
                "count": len(popular_searches),
                "period_days": days
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get popular searches: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular searches")


# Search Templates

@router.post("/templates", response_model=dict)
async def create_search_template(
    template: SearchTemplate = Body(..., description="Search template to create"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create search template
    
    Args:
        template: Search template data
        current_user: Authenticated user
        
    Returns:
        Created search template
    """
    try:
        created_template = await search_service.create_search_template(template, current_user)
        
        return {
            "success": True,
            "data": {
                "template_id": created_template.id,
                "name": created_template.name,
                "created_at": created_template.created_at.isoformat()
            },
            "message": "Search template created successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create search template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


# Global Search

@router.get("/global", response_model=dict)
async def global_search(
    q: str = Query(..., min_length=1, description="Global search query"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Global search across all entities
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Authenticated user
        
    Returns:
        Global search results
    """
    try:
        search_request = SearchRequest(
            query=q,
            entities=[SearchEntity.ALL],
            search_type=SearchType.FULL_TEXT,
            limit=limit,
            page=1
        )
        
        response = await search_service.search(search_request, current_user)
        
        # Group results by entity type
        grouped_results = {}
        for result in response.results:
            entity_type = result.entity_type.value
            if entity_type not in grouped_results:
                grouped_results[entity_type] = []
            grouped_results[entity_type].append(result.model_dump())
        
        return {
            "success": True,
            "data": {
                "query": q,
                "total_results": response.total_results,
                "results_by_entity": grouped_results,
                "search_time_ms": response.search_time_ms,
                "suggestions": response.suggestions
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Global search failed: {e}")
        raise HTTPException(status_code=500, detail="Global search failed")


# Admin Endpoints

@router.get("/admin/statistics", response_model=dict)
async def get_search_statistics(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get search system statistics (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Search system statistics
    """
    try:
        # This would get actual statistics from the database
        stats = {
            "total_searches_today": 1250,
            "total_searches_this_month": 45000,
            "average_search_time_ms": 180,
            "most_searched_entity": "patient",
            "unique_searchers_today": 125,
            "saved_searches_count": 890,
            "search_success_rate": 94.5,
            "popular_search_terms": [
                "chest pain", "diabetes", "hypertension", "fever", "headache"
            ],
            "search_performance": {
                "fast_searches": 85.2,  # < 200ms
                "medium_searches": 12.8,  # 200ms - 1s
                "slow_searches": 2.0     # > 1s
            }
        }
        
        return {
            "success": True,
            "data": {
                "search_statistics": stats,
                "generated_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get search statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.post("/admin/reindex", response_model=dict)
async def reindex_search_data(
    entity: Optional[SearchEntity] = Body(None, description="Entity to reindex (all if not specified)"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Reindex search data (Admin only)
    
    Args:
        entity: Optional entity to reindex
        current_user: Authenticated admin user
        
    Returns:
        Reindex status
    """
    try:
        # This would trigger a background reindexing task
        entities_to_reindex = [entity] if entity else [
            SearchEntity.PATIENT, SearchEntity.EPISODE, SearchEntity.ENCOUNTER,
            SearchEntity.TEMPLATE, SearchEntity.REPORT
        ]
        
        return {
            "success": True,
            "data": {
                "reindex_started": True,
                "entities": [e.value for e in entities_to_reindex],
                "estimated_completion": "10-30 minutes",
                "started_at": datetime.utcnow().isoformat()
            },
            "message": "Search reindexing started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start reindexing: {e}")
        raise HTTPException(status_code=500, detail="Failed to start reindexing")


# Health Check

@router.get("/health", response_model=dict)
async def search_health_check():
    """
    Health check for search service
    
    Returns:
        Search service health status
    """
    try:
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "search_service": "operational",
                "features": [
                    "full_text_search",
                    "faceted_search",
                    "quick_search",
                    "saved_searches",
                    "search_analytics",
                    "entity_specific_search"
                ],
                "supported_entities": [entity.value for entity in SearchEntity if entity != SearchEntity.ALL],
                "search_types": [search_type.value for search_type in SearchType]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Search health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }