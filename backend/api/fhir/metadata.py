from fastapi import APIRouter, Depends
from config.capability_statement import create_capability_statement

router = APIRouter()

@router.get("/R4/metadata", summary="FHIR Capability Statement")
async def get_capability_statement():
    """
    Return the FHIR CapabilityStatement describing what this server supports.
    This is required for FHIR compliance.
    """
    capability = create_capability_statement()
    return capability.dict()

@router.get("/R4/.well-known/smart_configuration", summary="SMART on FHIR Configuration")
async def get_smart_configuration():
    """
    SMART on FHIR configuration endpoint
    """
    return {
        "authorization_endpoint": "https://diagnoassist.com/auth/authorize",
        "token_endpoint": "https://diagnoassist.com/auth/token",
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post"
        ],
        "scopes_supported": [
            "patient/Patient.read",
            "patient/Encounter.read",
            "patient/Observation.read",
            "patient/DiagnosticReport.read",
            "user/Patient.read",
            "user/Encounter.read",
            "user/Observation.read",
            "user/DiagnosticReport.read"
        ],
        "capabilities": [
            "launch-ehr",
            "launch-standalone",
            "client-public",
            "client-confidential-symmetric",
            "sso-openid-connect"
        ]
    }