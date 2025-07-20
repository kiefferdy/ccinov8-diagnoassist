from fastapi import APIRouter, Depends
from typing import Optional
from config.capability_statement import create_capability_statement
from api.dependencies import get_current_user_optional

router = APIRouter()

@router.get("/R4/metadata", summary="Get FHIR CapabilityStatement")
async def get_capability_statement(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Return FHIR CapabilityStatement describing server capabilities.
    """
    capability_statement = create_capability_statement()
    return capability_statement.dict()