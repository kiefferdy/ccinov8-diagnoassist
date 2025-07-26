"""
Template API endpoints for DiagnoAssist Backend

REST endpoints for template management:
- Template CRUD operations
- Template search and discovery
- Template application to encounters
- Template analytics and ratings
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from datetime import datetime

from app.models.auth import UserModel, UserRoleEnum
from app.models.template import (
    TemplateModel, TemplateCreateRequest, TemplateUpdateRequest,
    TemplateSearchRequest, TemplateApplicationRequest, TemplateType,
    TemplateCategory, TemplateScope, TemplateUsageStats
)
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.template_service import template_service
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)

router = APIRouter()


# Template CRUD Operations

@router.post("/", response_model=dict)
async def create_template(
    template_data: TemplateCreateRequest = Body(..., description="Template creation data"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new template
    
    Args:
        template_data: Template creation data
        current_user: Authenticated user
        
    Returns:
        Created template information
    """
    try:
        template = await template_service.create_template(template_data, current_user)
        
        return {
            "success": True,
            "data": {
                "template_id": template.id,
                "name": template.name,
                "template_type": template.template_type.value,
                "category": template.category.value,
                "scope": template.scope.value,
                "created_at": template.metadata.created_at.isoformat()
            },
            "message": "Template created successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.get("/{template_id}", response_model=dict)
async def get_template(
    template_id: str = Path(..., description="Template ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get template by ID
    
    Args:
        template_id: Template ID
        current_user: Authenticated user
        
    Returns:
        Template data
    """
    try:
        template = await template_service.get_template(template_id, current_user)
        
        return {
            "success": True,
            "data": template.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template")


@router.put("/{template_id}", response_model=dict)
async def update_template(
    template_id: str = Path(..., description="Template ID"),
    update_data: TemplateUpdateRequest = Body(..., description="Template update data"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update template
    
    Args:
        template_id: Template ID
        update_data: Template update data
        current_user: Authenticated user
        
    Returns:
        Updated template information
    """
    try:
        template = await template_service.update_template(template_id, update_data, current_user)
        
        return {
            "success": True,
            "data": {
                "template_id": template.id,
                "name": template.name,
                "version": template.metadata.version,
                "updated_at": template.metadata.updated_at.isoformat() if template.metadata.updated_at else None
            },
            "message": "Template updated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")


@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: str = Path(..., description="Template ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete template
    
    Args:
        template_id: Template ID
        current_user: Authenticated user
        
    Returns:
        Deletion confirmation
    """
    try:
        success = await template_service.delete_template(template_id, current_user)
        
        return {
            "success": success,
            "data": {
                "template_id": template_id,
                "deleted_at": datetime.utcnow().isoformat()
            },
            "message": "Template deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")


# Template Search and Discovery

@router.post("/search", response_model=dict)
async def search_templates(
    search_request: TemplateSearchRequest = Body(..., description="Search parameters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Search templates with filtering and pagination
    
    Args:
        search_request: Search parameters
        current_user: Authenticated user
        
    Returns:
        Search results with pagination
    """
    try:
        results = await template_service.search_templates(search_request, current_user)
        
        return {
            "success": True,
            "data": {
                "templates": [template.model_dump() for template in results["templates"]],
                "pagination": results["pagination"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to search templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to search templates")


@router.get("/", response_model=dict)
async def get_user_templates(
    template_type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    scope: Optional[TemplateScope] = Query(None, description="Filter by scope"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of templates"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get templates accessible to current user
    
    Args:
        template_type: Filter by template type
        category: Filter by category
        scope: Filter by scope
        limit: Maximum number of templates
        current_user: Authenticated user
        
    Returns:
        List of accessible templates
    """
    try:
        search_request = TemplateSearchRequest(
            template_type=template_type,
            category=category,
            scope=scope,
            page=1,
            limit=limit
        )
        
        results = await template_service.search_templates(search_request, current_user)
        
        return {
            "success": True,
            "data": {
                "templates": [template.model_dump() for template in results["templates"]],
                "count": len(results["templates"]),
                "total": results["pagination"]["total"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/recommendations", response_model=dict)
async def get_recommended_templates(
    encounter_type: Optional[str] = Query(None, description="Filter by encounter type"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get recommended templates for current user
    
    Args:
        encounter_type: Filter by encounter type
        category: Filter by category
        limit: Maximum number of recommendations
        current_user: Authenticated user
        
    Returns:
        List of recommended templates
    """
    try:
        templates = await template_service.get_recommended_templates(
            current_user, encounter_type=encounter_type, category=category, limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": [template.model_dump() for template in templates],
                "count": len(templates)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommended templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.get("/popular", response_model=dict)
async def get_popular_templates(
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of templates"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get popular templates
    
    Args:
        category: Filter by category
        limit: Maximum number of templates
        current_user: Authenticated user
        
    Returns:
        List of popular templates
    """
    try:
        templates = await template_service.get_popular_templates(
            current_user, category=category, limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "popular_templates": [template.model_dump() for template in templates],
                "count": len(templates)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get popular templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular templates")


# Template Application

@router.post("/apply", response_model=dict)
async def apply_template_to_encounter(
    application_request: TemplateApplicationRequest = Body(..., description="Template application request"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Apply template to encounter
    
    Args:
        application_request: Template application parameters
        current_user: Authenticated user
        
    Returns:
        Application result
    """
    try:
        encounter, application_info = await template_service.apply_template_to_encounter(
            application_request, current_user
        )
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter.id,
                "template_applied": {
                    "template_id": application_info.template_id,
                    "template_name": application_info.template_name,
                    "applied_sections": application_info.applied_sections,
                    "applied_at": application_info.applied_at.isoformat()
                },
                "updated_encounter": encounter.model_dump()
            },
            "message": "Template applied successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to apply template: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply template")


@router.get("/encounters/{encounter_id}/applicable", response_model=dict)
async def get_applicable_templates(
    encounter_id: str = Path(..., description="Encounter ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get templates applicable to specific encounter
    
    Args:
        encounter_id: Encounter ID
        current_user: Authenticated user
        
    Returns:
        List of applicable templates
    """
    try:
        templates = await template_service.get_applicable_templates(encounter_id, current_user)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "applicable_templates": [template.model_dump() for template in templates],
                "count": len(templates)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get applicable templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get applicable templates")


# Template Analytics and Ratings

@router.get("/{template_id}/stats", response_model=dict)
async def get_template_usage_stats(
    template_id: str = Path(..., description="Template ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get template usage statistics
    
    Args:
        template_id: Template ID
        current_user: Authenticated user
        
    Returns:
        Template usage statistics
    """
    try:
        stats = await template_service.get_template_usage_stats(template_id, current_user)
        
        return {
            "success": True,
            "data": {
                "template_id": template_id,
                "usage_statistics": stats.model_dump()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get template usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")


@router.post("/{template_id}/rate", response_model=dict)
async def rate_template(
    template_id: str = Path(..., description="Template ID"),
    rating: float = Body(..., ge=1, le=5, description="Rating value (1-5)"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Rate a template
    
    Args:
        template_id: Template ID
        rating: Rating value (1-5)
        current_user: Authenticated user
        
    Returns:
        Rating confirmation
    """
    try:
        success = await template_service.rate_template(template_id, rating, current_user)
        
        return {
            "success": success,
            "data": {
                "template_id": template_id,
                "rating": rating,
                "rated_by": current_user.name,
                "rated_at": datetime.utcnow().isoformat()
            },
            "message": "Template rated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to rate template: {e}")
        raise HTTPException(status_code=500, detail="Failed to rate template")


# Template Validation

@router.post("/validate", response_model=dict)
async def validate_template(
    template_data: TemplateCreateRequest = Body(..., description="Template data to validate"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Validate template structure and content
    
    Args:
        template_data: Template data to validate
        current_user: Authenticated user
        
    Returns:
        Validation result
    """
    try:
        validation_result = await template_service.validate_template_structure(template_data.sections)
        
        return {
            "success": True,
            "data": {
                "validation_result": validation_result.model_dump(),
                "is_valid": validation_result.is_valid
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to validate template: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate template")


# Admin Operations

@router.get("/admin/all", response_model=dict)
async def get_all_templates_admin(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    template_type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get all templates (Admin only)
    
    Args:
        page: Page number
        limit: Items per page
        template_type: Filter by template type
        category: Filter by category
        current_user: Authenticated admin user
        
    Returns:
        All templates with pagination
    """
    try:
        search_request = TemplateSearchRequest(
            template_type=template_type,
            category=category,
            page=page,
            limit=limit,
            is_active=None  # Include inactive templates for admin
        )
        
        results = await template_service.search_templates(search_request, current_user)
        
        return {
            "success": True,
            "data": {
                "templates": [template.model_dump() for template in results["templates"]],
                "pagination": results["pagination"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get all templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.post("/{template_id}/publish", response_model=dict)
async def publish_template(
    template_id: str = Path(..., description="Template ID"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Publish template (Admin only)
    
    Args:
        template_id: Template ID
        current_user: Authenticated admin user
        
    Returns:
        Publish confirmation
    """
    try:
        from app.models.template import TemplateUpdateRequest
        update_request = TemplateUpdateRequest(is_published=True)
        
        template = await template_service.update_template(template_id, update_request, current_user)
        
        return {
            "success": True,
            "data": {
                "template_id": template_id,
                "published_at": datetime.utcnow().isoformat(),
                "published_by": current_user.name
            },
            "message": "Template published successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to publish template: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish template")


# Health Check

@router.get("/health", response_model=dict)
async def template_health_check():
    """
    Health check for template service
    
    Returns:
        Template service health status
    """
    try:
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "template_service": "operational",
                "features": [
                    "template_crud",
                    "template_search",
                    "template_application",
                    "template_analytics",
                    "template_validation"
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Template health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }