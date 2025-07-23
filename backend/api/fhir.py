"""
FHIR API Router for DiagnoAssist - IMPORT FIXED VERSION
FHIR R4 compliant resource management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

# FIXED: Import dependencies properly
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.fhir_resource import (
    FHIRResourceCreate,
    FHIRResourceResponse,
    FHIRResourceListResponse
)
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/fhir", tags=["fhir"])

# =============================================================================
# FHIR Resource Operations
# =============================================================================

@router.post("/", response_model=FHIRResourceResponse, status_code=201)
async def create_fhir_resource(
    resource_data: FHIRResourceCreate,
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Create a new FHIR resource
    
    Args:
        resource_data: FHIR resource creation data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created FHIR resource data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Create FHIR resource through service layer
        fhir_resource = services.fhir.create_resource(resource_data)
        return fhir_resource
    except Exception as e:
        error_message = str(e)
        
        if "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create FHIR resource: {error_message}"
            )

@router.get("/", response_model=FHIRResourceListResponse)
async def get_fhir_resources(
    services = ServiceDep,
    current_user = CurrentUserDep,
    pagination = PaginationDep,
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    patient_reference: Optional[str] = Query(None, description="Filter by patient reference"),
    status_filter: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get paginated list of FHIR resources
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        pagination: Pagination parameters
        resource_type: Resource type filter
        patient_reference: Patient reference filter
        status_filter: Status filter
        
    Returns:
        Paginated list of FHIR resources
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get FHIR resources through service layer
        resources = services.fhir.get_resources(
            pagination=pagination,
            resource_type=resource_type,
            patient_reference=patient_reference,
            status=status_filter
        )
        
        return resources
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FHIR resources: {str(e)}"
        )

@router.get("/{resource_id}", response_model=FHIRResourceResponse)
async def get_fhir_resource(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID")
):
    """
    Get FHIR resource by ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_id: FHIR Resource UUID
        
    Returns:
        FHIR resource data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Get FHIR resource through service layer
        resource = services.fhir.get_resource(str(resource_id))
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        
        return resource
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FHIR resource: {str(e)}"
        )

@router.put("/{resource_id}", response_model=FHIRResourceResponse)
async def update_fhir_resource(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID"),
    resource_data: FHIRResourceCreate = ...
):
    """
    Update FHIR resource
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_id: FHIR Resource UUID
        resource_data: FHIR resource update data
        
    Returns:
        Updated FHIR resource data
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Update FHIR resource through service layer
        resource = services.fhir.update_resource(str(resource_id), resource_data)
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        
        return resource
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update FHIR resource: {error_message}"
            )

@router.delete("/{resource_id}", response_model=StatusResponse)
async def delete_fhir_resource(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID")
):
    """
    Delete FHIR resource
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_id: FHIR Resource UUID
        
    Returns:
        Status response
    """
    # Authorization check (commented out for MVP)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    
    try:
        # Delete FHIR resource through service layer
        success = services.fhir.delete_resource(str(resource_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        
        return StatusResponse(
            success=True,
            message=f"FHIR resource {resource_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete FHIR resource: {error_message}"
            )

# =============================================================================
# FHIR-specific endpoints
# =============================================================================

@router.get("/{resource_type}/{resource_id}")
async def get_fhir_resource_by_type(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_type: str = Path(..., description="FHIR Resource Type"),
    resource_id: str = Path(..., description="FHIR Resource ID")
):
    """
    Get FHIR resource by type and ID (FHIR-compliant endpoint)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_type: FHIR resource type (Patient, Observation, etc.)
        resource_id: FHIR resource ID
        
    Returns:
        FHIR resource data
    """
    try:
        # Get FHIR resource by type through service layer
        resource = services.fhir.get_resource_by_type(resource_type, resource_id)
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR {resource_type} with ID {resource_id} not found"
            )
        
        return resource
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FHIR {resource_type}: {str(e)}"
        )

@router.get("/{resource_type}")
async def search_fhir_resources_by_type(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_type: str = Path(..., description="FHIR Resource Type"),
    pagination = PaginationDep,
    patient: Optional[str] = Query(None, description="Patient reference"),
    subject: Optional[str] = Query(None, description="Subject reference"),
    code: Optional[str] = Query(None, description="Code filter"),
    date: Optional[str] = Query(None, description="Date filter")
):
    """
    Search FHIR resources by type with FHIR search parameters
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_type: FHIR resource type
        pagination: Pagination parameters
        patient: Patient reference filter
        subject: Subject reference filter
        code: Code filter
        date: Date filter
        
    Returns:
        FHIR search results
    """
    try:
        # Search FHIR resources through service layer
        search_params = {
            "patient": patient,
            "subject": subject,
            "code": code,
            "date": date
        }
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        results = services.fhir.search_resources_by_type(
            resource_type=resource_type,
            pagination=pagination,
            search_params=search_params
        )
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FHIR {resource_type}: {str(e)}"
        )

@router.post("/{resource_type}", response_model=FHIRResourceResponse, status_code=201)
async def create_fhir_resource_by_type(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_type: str = Path(..., description="FHIR Resource Type"),
    resource_data: Dict[str, Any] = ...
):
    """
    Create FHIR resource by type (FHIR-compliant endpoint)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_type: FHIR resource type
        resource_data: FHIR resource data as JSON
        
    Returns:
        Created FHIR resource
    """
    try:
        # Create FHIR resource by type through service layer
        resource = services.fhir.create_resource_by_type(resource_type, resource_data)
        return resource
    except Exception as e:
        error_message = str(e)
        
        if "validation" in error_message.lower() or "invalid" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create FHIR {resource_type}: {error_message}"
            )

@router.get("/Patient/{patient_id}/everything")
async def get_patient_everything(
    services = ServiceDep,
    current_user = CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """
    Get all resources for a patient (FHIR $everything operation)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient ID
        
    Returns:
        Bundle of all patient resources
    """
    try:
        # Get patient everything through service layer
        bundle = services.fhir.get_patient_everything(patient_id)
        return bundle
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve patient everything: {error_message}"
            )

@router.get("/metadata")
async def get_capability_statement(
    services = ServiceDep,
    current_user = CurrentUserDep
):
    """
    Get FHIR capability statement (metadata endpoint)
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        FHIR CapabilityStatement
    """
    try:
        # Get capability statement through service layer
        capability = services.fhir.get_capability_statement()
        return capability
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve capability statement: {str(e)}"
        )