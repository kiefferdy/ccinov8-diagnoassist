"""
FHIR API Router for DiagnoAssist
FHIR R4 compliant endpoints with exception handling
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import List, Optional, Dict, Any
from uuid import UUID

# Import dependencies
from api.dependencies import ServiceDep, CurrentUserDep, PaginationDep

# Import schemas
from schemas.fhir_resource import (
    FHIRResourceCreate,
    FHIRResourceResponse,
    FHIRResourceListResponse
)

# Import exceptions - using the global exception system
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    FHIRValidationException,
    BusinessRuleException,
    AuthenticationException,
    AuthorizationException
)

# Create router
router = APIRouter(prefix="/fhir/R4", tags=["fhir"])


# =============================================================================
# FHIR Capability Statement
# =============================================================================

@router.get("/metadata")
async def get_capability_statement(
    services: ServiceDep = Depends()
):
    """
    Get FHIR server capability statement
    
    Returns:
        FHIR CapabilityStatement resource
    """
    # Get capability statement through FHIR service
    capability = services.fhir.get_capability_statement()
    
    return capability


# =============================================================================
# FHIR Patient Resources
# =============================================================================

@router.get("/Patient", response_model=Dict[str, Any])
async def search_patients(
    name: Optional[str] = Query(None, description="Patient name"),
    family: Optional[str] = Query(None, description="Family name"),
    given: Optional[str] = Query(None, description="Given name"),
    identifier: Optional[str] = Query(None, description="Patient identifier"),
    birthdate: Optional[str] = Query(None, description="Birth date"),
    gender: Optional[str] = Query(None, description="Gender"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Search FHIR Patient resources
    
    Args:
        name: Patient name search
        family: Family name search
        given: Given name search
        identifier: Identifier search
        birthdate: Birth date filter
        gender: Gender filter
        _count: Number of results
        _offset: Pagination offset
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        FHIR Bundle with Patient resources
        
    Raises:
        FHIRValidationException: Invalid FHIR parameters
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required for FHIR access")
    
    # Build search parameters
    search_params = {
        "name": name,
        "family": family,
        "given": given,
        "identifier": identifier,
        "birthdate": birthdate,
        "gender": gender,
        "_count": _count,
        "_offset": _offset
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Search through FHIR service
    bundle = services.fhir.search_patients(search_params)
    
    return bundle


@router.post("/Patient", response_model=Dict[str, Any], status_code=201)
async def create_patient(
    patient_resource: Dict[str, Any],
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Create FHIR Patient resource
    
    Args:
        patient_resource: FHIR Patient resource data
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Created FHIR Patient resource
        
    Raises:
        FHIRValidationException: Invalid FHIR resource
        ValidationException: Business validation error
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create Patient resources",
            required_permission="patient.create"
        )
    
    # Validate resource type
    if patient_resource.get("resourceType") != "Patient":
        raise FHIRValidationException(
            message="Invalid resource type for Patient endpoint",
            resource_type="Patient",
            provided_type=patient_resource.get("resourceType")
        )
    
    # Create patient through FHIR service
    created_patient = services.fhir.create_patient(
        patient_resource=patient_resource,
        created_by=current_user["user_id"]
    )
    
    return created_patient


@router.get("/Patient/{patient_id}", response_model=Dict[str, Any])
async def get_patient(
    patient_id: str = Path(..., description="Patient ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get FHIR Patient resource by ID
    
    Args:
        patient_id: Patient identifier
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        FHIR Patient resource
        
    Raises:
        ResourceNotFoundException: Patient not found
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get patient through FHIR service
    patient = services.fhir.get_patient(patient_id)
    
    return patient


@router.put("/Patient/{patient_id}", response_model=Dict[str, Any])
async def update_patient(
    patient_id: str = Path(..., description="Patient ID"),
    patient_resource: Dict[str, Any] = ...,
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Update FHIR Patient resource
    
    Args:
        patient_id: Patient identifier
        patient_resource: Updated FHIR Patient resource
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        Updated FHIR Patient resource
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("patient.update", False):
        raise AuthorizationException(
            message="Insufficient permissions to update Patient resources",
            required_permission="patient.update"
        )
    
    # Update patient through FHIR service
    updated_patient = services.fhir.update_patient(
        patient_id=patient_id,
        patient_resource=patient_resource,
        updated_by=current_user["user_id"]
    )
    
    return updated_patient


# =============================================================================
# FHIR Encounter Resources
# =============================================================================

@router.get("/Encounter")
async def search_encounters(
    patient: Optional[str] = Query(None, description="Patient reference"),
    status: Optional[str] = Query(None, description="Encounter status"),
    class_: Optional[str] = Query(None, alias="class", description="Encounter class"),
    date: Optional[str] = Query(None, description="Encounter date"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Search FHIR Encounter resources
    
    Returns:
        FHIR Bundle with Encounter resources
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Build search parameters
    search_params = {
        "patient": patient,
        "status": status,
        "class": class_,
        "date": date,
        "_count": _count,
        "_offset": _offset
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Search through FHIR service
    bundle = services.fhir.search_encounters(search_params)
    
    return bundle


@router.post("/Encounter", status_code=201)
async def create_encounter(
    encounter_resource: Dict[str, Any],
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Create FHIR Encounter resource
    
    Returns:
        Created FHIR Encounter resource
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("episode.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create Encounter resources",
            required_permission="episode.create"
        )
    
    # Validate resource type
    if encounter_resource.get("resourceType") != "Encounter":
        raise FHIRValidationException(
            message="Invalid resource type for Encounter endpoint",
            resource_type="Encounter",
            provided_type=encounter_resource.get("resourceType")
        )
    
    # Create encounter through FHIR service
    created_encounter = services.fhir.create_encounter(
        encounter_resource=encounter_resource,
        created_by=current_user["user_id"]
    )
    
    return created_encounter


@router.get("/Encounter/{encounter_id}")
async def get_encounter(
    encounter_id: str = Path(..., description="Encounter ID"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get FHIR Encounter resource by ID
    
    Returns:
        FHIR Encounter resource
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get encounter through FHIR service
    encounter = services.fhir.get_encounter(encounter_id)
    
    return encounter


# =============================================================================
# FHIR Observation Resources
# =============================================================================

@router.get("/Observation")
async def search_observations(
    patient: Optional[str] = Query(None, description="Patient reference"),
    encounter: Optional[str] = Query(None, description="Encounter reference"),
    category: Optional[str] = Query(None, description="Observation category"),
    code: Optional[str] = Query(None, description="Observation code"),
    date: Optional[str] = Query(None, description="Observation date"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Search FHIR Observation resources
    
    Returns:
        FHIR Bundle with Observation resources
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Build search parameters
    search_params = {
        "patient": patient,
        "encounter": encounter,
        "category": category,
        "code": code,
        "date": date,
        "_count": _count,
        "_offset": _offset
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Search through FHIR service
    bundle = services.fhir.search_observations(search_params)
    
    return bundle


@router.post("/Observation", status_code=201)
async def create_observation(
    observation_resource: Dict[str, Any],
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Create FHIR Observation resource
    
    Returns:
        Created FHIR Observation resource
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Validate resource type
    if observation_resource.get("resourceType") != "Observation":
        raise FHIRValidationException(
            message="Invalid resource type for Observation endpoint",
            resource_type="Observation",
            provided_type=observation_resource.get("resourceType")
        )
    
    # Create observation through FHIR service
    created_observation = services.fhir.create_observation(
        observation_resource=observation_resource,
        created_by=current_user["user_id"]
    )
    
    return created_observation


# =============================================================================
# FHIR Condition Resources
# =============================================================================

@router.get("/Condition")
async def search_conditions(
    patient: Optional[str] = Query(None, description="Patient reference"),
    encounter: Optional[str] = Query(None, description="Encounter reference"),
    category: Optional[str] = Query(None, description="Condition category"),
    code: Optional[str] = Query(None, description="Condition code"),
    clinical_status: Optional[str] = Query(None, alias="clinical-status", description="Clinical status"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Search FHIR Condition resources
    
    Returns:
        FHIR Bundle with Condition resources
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Build search parameters
    search_params = {
        "patient": patient,
        "encounter": encounter,
        "category": category,
        "code": code,
        "clinical-status": clinical_status,
        "_count": _count,
        "_offset": _offset
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Search through FHIR service
    bundle = services.fhir.search_conditions(search_params)
    
    return bundle


@router.post("/Condition", status_code=201)
async def create_condition(
    condition_resource: Dict[str, Any],
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Create FHIR Condition resource
    
    Returns:
        Created FHIR Condition resource
    """
    # Authorization check
    if not current_user or not current_user.get("permissions", {}).get("diagnosis.create", False):
        raise AuthorizationException(
            message="Insufficient permissions to create Condition resources",
            required_permission="diagnosis.create"
        )
    
    # Validate resource type
    if condition_resource.get("resourceType") != "Condition":
        raise FHIRValidationException(
            message="Invalid resource type for Condition endpoint",
            resource_type="Condition",
            provided_type=condition_resource.get("resourceType")
        )
    
    # Create condition through FHIR service
    created_condition = services.fhir.create_condition(
        condition_resource=condition_resource,
        created_by=current_user["user_id"]
    )
    
    return created_condition


# =============================================================================
# FHIR Bundle Operations
# =============================================================================

@router.post("/", status_code=200)
async def process_bundle(
    bundle_resource: Dict[str, Any],
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Process FHIR Bundle (transaction or batch)
    
    Args:
        bundle_resource: FHIR Bundle resource
        services: Injected services
        current_user: Current authenticated user
        
    Returns:
        FHIR Bundle response
        
    Raises:
        FHIRValidationException: Invalid bundle
        ValidationException: Bundle validation error
        AuthorizationException: User lacks permission
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required for Bundle operations")
    
    # Validate resource type
    if bundle_resource.get("resourceType") != "Bundle":
        raise FHIRValidationException(
            message="Invalid resource type for Bundle endpoint",
            resource_type="Bundle",
            provided_type=bundle_resource.get("resourceType")
        )
    
    # Process bundle through FHIR service
    response_bundle = services.fhir.process_bundle(
        bundle_resource=bundle_resource,
        processed_by=current_user["user_id"]
    )
    
    return response_bundle


# =============================================================================
# FHIR History and Versioning
# =============================================================================

@router.get("/{resource_type}/_history")
async def get_resource_history(
    resource_type: str = Path(..., description="Resource type"),
    _count: int = Query(20, description="Number of results"),
    _since: Optional[str] = Query(None, description="Since timestamp"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get resource history
    
    Returns:
        FHIR Bundle with historical versions
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get history through FHIR service
    history = services.fhir.get_resource_history(
        resource_type=resource_type,
        count=_count,
        since=_since
    )
    
    return history


@router.get("/{resource_type}/{resource_id}/_history")
async def get_resource_instance_history(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    _count: int = Query(20, description="Number of results"),
    services: ServiceDep = Depends(),
    current_user: CurrentUserDep = Depends()
):
    """
    Get specific resource instance history
    
    Returns:
        FHIR Bundle with resource versions
    """
    # Authorization check
    if not current_user:
        raise AuthenticationException(message="Authentication required")
    
    # Get instance history through FHIR service
    history = services.fhir.get_resource_instance_history(
        resource_type=resource_type,
        resource_id=resource_id,
        count=_count
    )
    
    return history


# Export router
__all__ = ["router"]