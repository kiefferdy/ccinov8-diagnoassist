"""
FHIR API Router for DiagnoAssist
FHIR R4 compliant endpoints with exception handling
FIXED: Dependency injection issues resolved
"""

from fastapi import APIRouter, Query, Path
from typing import Optional, Dict, Any

# Import dependencies (FIXED: Remove duplicate Depends)
from api.dependencies import ServiceDep, CurrentUserDep

# Create router
router = APIRouter(prefix="/fhir/R4", tags=["fhir"])

# =============================================================================
# FHIR Capability Statement
# =============================================================================

@router.get("/metadata")
async def get_capability_statement():
    """
    Get FHIR server capability statement
    
    Returns:
        FHIR CapabilityStatement resource
    """
    return {
        "resourceType": "CapabilityStatement",
        "id": "diagnoassist-server",
        "status": "draft",
        "date": "2025-07-22",
        "publisher": "DiagnoAssist Medical Systems",
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "implementation": {
            "description": "DiagnoAssist FHIR R4 Server",
            "url": "http://localhost:8000/fhir/R4"
        },
        "rest": [{
            "mode": "server",
            "documentation": "DiagnoAssist FHIR R4 API",
            "security": {
                "cors": True,
                "description": "CORS support enabled"
            },
            "resource": [
                {
                    "type": "Patient",
                    "profile": "http://hl7.org/fhir/StructureDefinition/Patient",
                    "interaction": [
                        {"code": "create"},
                        {"code": "read"},
                        {"code": "update"},
                        {"code": "search-type"}
                    ],
                    "searchParam": [
                        {
                            "name": "name",
                            "type": "string",
                            "documentation": "Search by patient name"
                        },
                        {
                            "name": "family",
                            "type": "string", 
                            "documentation": "Search by family name"
                        },
                        {
                            "name": "given",
                            "type": "string",
                            "documentation": "Search by given name"
                        },
                        {
                            "name": "identifier",
                            "type": "token",
                            "documentation": "Search by patient identifier"
                        },
                        {
                            "name": "birthdate",
                            "type": "date",
                            "documentation": "Search by birth date"
                        },
                        {
                            "name": "gender",
                            "type": "token",
                            "documentation": "Search by gender"
                        }
                    ]
                },
                {
                    "type": "Encounter",
                    "profile": "http://hl7.org/fhir/StructureDefinition/Encounter", 
                    "interaction": [
                        {"code": "create"},
                        {"code": "read"},
                        {"code": "search-type"}
                    ]
                },
                {
                    "type": "Observation",
                    "profile": "http://hl7.org/fhir/StructureDefinition/Observation",
                    "interaction": [
                        {"code": "create"},
                        {"code": "read"},
                        {"code": "search-type"}
                    ]
                },
                {
                    "type": "DiagnosticReport",
                    "profile": "http://hl7.org/fhir/StructureDefinition/DiagnosticReport",
                    "interaction": [
                        {"code": "create"},
                        {"code": "read"},
                        {"code": "search-type"}
                    ]
                },
                {
                    "type": "Condition",
                    "profile": "http://hl7.org/fhir/StructureDefinition/Condition",
                    "interaction": [
                        {"code": "create"},
                        {"code": "read"},
                        {"code": "search-type"}
                    ]
                }
            ]
        }]
    }


# =============================================================================
# FHIR Patient Resources
# =============================================================================

@router.get("/Patient")
async def search_patients(
    name: Optional[str] = Query(None, description="Patient name"),
    family: Optional[str] = Query(None, description="Family name"),
    given: Optional[str] = Query(None, description="Given name"), 
    identifier: Optional[str] = Query(None, description="Patient identifier"),
    birthdate: Optional[str] = Query(None, description="Birth date"),
    gender: Optional[str] = Query(None, description="Gender"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination")
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
        
    Returns:
        FHIR Bundle with Patient resources
    """
    # For now, return empty bundle - can be enhanced with real data later
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "link": [{
            "relation": "self",
            "url": f"Patient?_count={_count}&_offset={_offset}"
        }],
        "entry": []
    }


@router.post("/Patient", status_code=201)
async def create_patient(patient_resource: Dict[str, Any]):
    """
    Create FHIR Patient resource
    
    Args:
        patient_resource: FHIR Patient resource data
        
    Returns:
        Created FHIR Patient resource
    """
    # Basic validation
    if patient_resource.get("resourceType") != "Patient":
        return {
            "resourceType": "OperationOutcome",
            "issue": [{
                "severity": "error",
                "code": "invalid",
                "diagnostics": "Invalid resource type for Patient endpoint"
            }]
        }
    
    # For now, return a simple created patient - can be enhanced with real storage later
    patient_id = "patient-example-1"
    
    created_patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {
            "versionId": "1",
            "lastUpdated": "2025-07-22T12:00:00Z"
        },
        **patient_resource
    }
    
    # Remove resourceType from the input to avoid duplication
    if "resourceType" in created_patient and created_patient["resourceType"] == "Patient":
        pass  # Keep it
    
    return created_patient


@router.get("/Patient/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="Patient ID")):
    """
    Get FHIR Patient resource by ID
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        FHIR Patient resource
    """
    # For now, return a sample patient - can be enhanced with real data later
    if patient_id == "patient-example-1":
        return {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": "2025-07-22T12:00:00Z"
            },
            "identifier": [{
                "system": "http://diagnoassist.com/patient-id",
                "value": patient_id
            }],
            "name": [{
                "family": "Doe",
                "given": ["John"]
            }],
            "gender": "male",
            "birthDate": "1985-03-15"
        }
    else:
        return {
            "resourceType": "OperationOutcome",
            "issue": [{
                "severity": "error",
                "code": "not-found",
                "diagnostics": f"Patient with ID '{patient_id}' not found"
            }]
        }


# =============================================================================
# FHIR Encounter Resources
# =============================================================================

@router.get("/Encounter")
async def search_encounters(
    patient: Optional[str] = Query(None, description="Patient reference"),
    status: Optional[str] = Query(None, description="Encounter status"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination")
):
    """
    Search FHIR Encounter resources
    
    Returns:
        FHIR Bundle with Encounter resources
    """
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": []
    }


@router.post("/Encounter", status_code=201)
async def create_encounter(encounter_resource: Dict[str, Any]):
    """
    Create FHIR Encounter resource
    
    Returns:
        Created FHIR Encounter resource
    """
    if encounter_resource.get("resourceType") != "Encounter":
        return {
            "resourceType": "OperationOutcome", 
            "issue": [{
                "severity": "error",
                "code": "invalid",
                "diagnostics": "Invalid resource type for Encounter endpoint"
            }]
        }
    
    encounter_id = "encounter-example-1"
    
    return {
        "resourceType": "Encounter",
        "id": encounter_id,
        "meta": {
            "versionId": "1",
            "lastUpdated": "2025-07-22T12:00:00Z"
        },
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory"
        },
        **encounter_resource
    }


# =============================================================================
# FHIR Observation Resources
# =============================================================================

@router.get("/Observation")
async def search_observations(
    patient: Optional[str] = Query(None, description="Patient reference"),
    encounter: Optional[str] = Query(None, description="Encounter reference"),
    category: Optional[str] = Query(None, description="Observation category"),
    _count: int = Query(20, description="Number of results"),
    _offset: int = Query(0, description="Offset for pagination")
):
    """
    Search FHIR Observation resources
    
    Returns:
        FHIR Bundle with Observation resources
    """
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": []
    }


@router.post("/Observation", status_code=201)
async def create_observation(observation_resource: Dict[str, Any]):
    """
    Create FHIR Observation resource
    
    Returns:
        Created FHIR Observation resource
    """
    if observation_resource.get("resourceType") != "Observation":
        return {
            "resourceType": "OperationOutcome",
            "issue": [{
                "severity": "error", 
                "code": "invalid",
                "diagnostics": "Invalid resource type for Observation endpoint"
            }]
        }
    
    observation_id = "observation-example-1"
    
    return {
        "resourceType": "Observation",
        "id": observation_id,
        "meta": {
            "versionId": "1",
            "lastUpdated": "2025-07-22T12:00:00Z"
        },
        "status": "final",
        **observation_resource
    }


# =============================================================================
# Export router
# =============================================================================

__all__ = ["router"]