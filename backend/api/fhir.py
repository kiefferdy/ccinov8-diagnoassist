"""
FHIR API Router for DiagnoAssist
FHIR R4 compliant resource management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

# Import individual service dependencies
from api.dependencies import (
    FHIRServiceDep,
    CurrentUserDep,
    PaginationDep
)

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

@router.post("/", response_model=None, status_code=201)
async def create_fhir_resource(
    resource_data: FHIRResourceCreate,
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep
):
    """Create a new FHIR resource"""
    try:
        fhir_resource = fhir_service.create_resource(resource_data)
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

@router.get("/", response_model=None)
async def get_fhir_resources(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    patient_reference: Optional[str] = Query(None, description="Filter by patient reference"),
    status_filter: Optional[str] = Query(None, description="Filter by status")
):
    """Get paginated list of FHIR resources"""
    try:
        resources = fhir_service.get_resources(
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

@router.get("/{resource_id}", response_model=None)
async def get_fhir_resource(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID")
):
    """Get FHIR resource by ID"""
    try:
        resource = fhir_service.get_resource(str(resource_id))
        
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

@router.put("/{resource_id}", response_model=None)
async def update_fhir_resource(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID"),
    resource_data: FHIRResourceCreate = ...
):
    """Update FHIR resource"""
    try:
        resource = fhir_service.update_resource(str(resource_id), resource_data)
        
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

@router.delete("/{resource_id}", response_model=None)
async def delete_fhir_resource(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    resource_id: UUID = Path(..., description="FHIR Resource ID")
):
    """Delete FHIR resource"""
    try:
        success = fhir_service.delete_resource(str(resource_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource with ID {resource_id} not found"
            )
        
        return {
            "status": "success",
            "message": f"FHIR resource {resource_id} deleted successfully"
        }
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
# FHIR Special Operations
# =============================================================================

@router.get("/Patient/{patient_id}/everything", response_model=None)
async def get_patient_everything(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    patient_id: str = Path(..., description="Patient ID")
):
    """Get all resources for a patient (FHIR $everything operation)"""
    try:
        bundle = fhir_service.get_patient_everything(patient_id)
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

@router.get("/metadata", response_model=None)
async def get_capability_statement(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep
):
    """Get FHIR capability statement (metadata endpoint)"""
    try:
        capability = fhir_service.get_capability_statement()
        return capability
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve capability statement: {str(e)}"
        )

@router.get("/{resource_type}", response_model=None)
async def search_fhir_resources_by_type(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    pagination: PaginationDep,
    resource_type: str = Path(..., description="FHIR Resource Type"),
    patient: Optional[str] = Query(None, description="Patient reference"),
    subject: Optional[str] = Query(None, description="Subject reference"),
    code: Optional[str] = Query(None, description="Code filter"),
    date: Optional[str] = Query(None, description="Date filter")
):
    """Search FHIR resources by type with FHIR search parameters"""
    try:
        search_params = {
            "patient": patient,
            "subject": subject,
            "code": code,
            "date": date
        }
        
        results = fhir_service.search_resources_by_type(
            resource_type, pagination, **search_params
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search FHIR {resource_type}: {str(e)}"
        )

@router.get("/{resource_type}/{resource_id}", response_model=None)
async def get_fhir_resource_by_type(
    fhir_service: FHIRServiceDep,
    current_user: CurrentUserDep,
    resource_type: str = Path(..., description="FHIR Resource Type"),
    resource_id: str = Path(..., description="FHIR Resource ID")
):
    """Get specific FHIR resource by type and ID"""
    try:
        resource = fhir_service.get_resource_by_type(resource_type, resource_id)
        
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