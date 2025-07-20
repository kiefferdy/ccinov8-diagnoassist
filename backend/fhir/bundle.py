from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any
from services.fhir_interop_service import FHIRInteropService
from api.dependencies import get_fhir_interop_service, get_current_user_optional

router = APIRouter()

@router.post("/R4/Bundle", summary="Process FHIR Bundle")
async def process_bundle(
    bundle_data: Dict[str, Any],
    fhir_service: FHIRInteropService = Depends(get_fhir_interop_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Process FHIR Bundle (transaction or batch processing).
    """
    try:
        processed_bundle = await fhir_service.process_bundle(bundle_data)
        return processed_bundle.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/R4/Bundle/$validate", summary="Validate FHIR Bundle")
async def validate_bundle(
    bundle_data: Dict[str, Any],
    fhir_service: FHIRInteropService = Depends(get_fhir_interop_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Validate FHIR Bundle without processing.
    """
    try:
        validation_result = await fhir_service.validate_bundle(bundle_data)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))