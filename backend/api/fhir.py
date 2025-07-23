"""
FHIR API Router for DiagnoAssist - CLEAN VERSION
FHIR R4 compliant resource management
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID

# Import dependencies - FIXED: Import directly from the module
from api.dependencies import get_service_manager, get_current_user, PaginationParams

# Import schemas
from schemas.fhir_resource import (
    FHIRResourceCreate,
    FHIRResourceResponse,
    FHIRResourceListResponse
)
from schemas.common import StatusResponse

# Create router
router = APIRouter(prefix="/fhir", tags=["fhir"])

# Create dependency aliases properly
ServiceDep = Depends(get_service_manager)
CurrentUserDep = Depends(get_current_user)
PaginationDep = Depends(PaginationParams)

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
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
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
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
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


@router.get("/{resource_type}/{resource_id}", response_model=Dict[str, Any])
async def get_fhir_resource(
    services = ServiceDep,
    current_user = CurrentUserDep,
    resource_type: str = Path(..., description="FHIR resource type"),
    resource_id: str = Path(..., description="FHIR resource ID")
):
    """
    Get FHIR resource by type and ID
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        resource_type: FHIR resource type
        resource_id: FHIR resource ID
        
    Returns:
        FHIR resource data
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Get FHIR resource through service layer
        resource = services.fhir.get_resource(resource_type, resource_id)
        return resource
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FHIR resource {resource_type}/{resource_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve FHIR resource: {error_message}"
            )


# =============================================================================
# FHIR Conversion Operations
# =============================================================================

@router.post("/convert/patient/{patient_id}")
async def convert_patient_to_fhir(
    services = ServiceDep,
    current_user = CurrentUserDep,
    patient_id: UUID = Path(..., description="Patient ID")
):
    """
    Convert patient to FHIR Patient resource
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        patient_id: Patient UUID
        
    Returns:
        FHIR Patient resource
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Convert patient to FHIR through service layer
        fhir_patient = services.fhir.convert_patient_to_fhir(str(patient_id))
        return fhir_patient
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert patient to FHIR: {error_message}"
            )


@router.post("/convert/episode/{episode_id}")
async def convert_episode_to_fhir(
    services = ServiceDep,
    current_user = CurrentUserDep,
    episode_id: UUID = Path(..., description="Episode ID")
):
    """
    Convert episode to FHIR Encounter resource
    
    Args:
        services: Injected services
        current_user: Current authenticated user
        episode_id: Episode UUID
        
    Returns:
        FHIR Encounter resource
    """
    # Authorization check
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Convert episode to FHIR through service layer
        fhir_encounter = services.fhir.convert_episode_to_fhir(str(episode_id))
        return fhir_encounter
    except Exception as e:
        error_message = str(e)
        
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode {episode_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert episode to FHIR: {error_message}"
            )


@router.get("/metadata")
async def get_capability_statement():
    """
    Get FHIR capability statement
    
    Returns:
        FHIR CapabilityStatement resource
    """
    return {
        "resourceType": "CapabilityStatement",
        "id": "diagnoassist-server",
        "status": "active",
        "date": "2025-01-23",
        "publisher": "DiagnoAssist",
        "kind": "instance",
        "software": {
            "name": "DiagnoAssist FHIR Server",
            "version": "1.0.0"
        },
        "implementation": {
            "description": "DiagnoAssist FHIR R4 Server"
        },
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ]
                    },
                    {
                        "type": "Encounter",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ]
                    },
                    {
                        "type": "Condition",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ]
                    },
                    {
                        "type": "MedicationRequest",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ]
                    }
                ]
            }
        ]
    }

# Export router
__all__ = ["router"]