from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any
from services.fhir_diagnosis_service import FHIRDiagnosisService
from api.dependencies import get_fhir_diagnosis_service, get_current_user_optional

router = APIRouter()

@router.post("/R4/DiagnosticReport", summary="Create FHIR DiagnosticReport")
async def create_diagnostic_report(
    report_data: Dict[str, Any],
    fhir_service: FHIRDiagnosisService = Depends(get_fhir_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new diagnostic report using FHIR DiagnosticReport resource format.
    """
    try:
        created_report = await fhir_service.create_fhir_diagnostic_report(report_data)
        return created_report.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/DiagnosticReport/{report_id}", summary="Get FHIR DiagnosticReport")
async def get_diagnostic_report(
    report_id: str = Path(..., description="DiagnosticReport resource ID"),
    fhir_service: FHIRDiagnosisService = Depends(get_fhir_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retrieve a diagnostic report by ID in FHIR DiagnosticReport resource format.
    """
    try:
        report = await fhir_service.get_fhir_diagnostic_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="DiagnosticReport not found")
        return report.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))