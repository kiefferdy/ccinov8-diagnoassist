from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from services.fhir_interop_service import FHIRInteropService
from api.dependencies import get_fhir_interop_service, get_current_user_optional
from api.exceptions import FHIRValidationException

router = APIRouter()

@router.post("/R4/Bundle", summary="Process FHIR Bundle")
async def process_bundle(
    bundle_data: Dict[str, Any],
    fhir_service: FHIRInteropService = Depends(get_fhir_interop_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Process a FHIR Bundle containing multiple resources.
    
    Supports transaction and batch bundles for bulk operations.
    """
    try:
        processed_bundle = await fhir_service.process_bundle(bundle_data)
        return processed_bundle.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "Bundle")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/R4/Bundle/$validate", summary="Validate FHIR Bundle")
async def validate_bundle(
    bundle_data: Dict[str, Any],
    fhir_service: FHIRInteropService = Depends(get_fhir_interop_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Validate a FHIR Bundle without processing it.
    
    Returns validation results and any errors found.
    """
    try:
        validation_result = await fhir_service.validate_bundle(bundle_data)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))