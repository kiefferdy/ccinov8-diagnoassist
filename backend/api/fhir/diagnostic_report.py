from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, Dict, Any
from services.fhir_diagnosis_service import FHIRDiagnosisService
from api.dependencies import get_fhir_diagnosis_service, get_current_user_optional
from api.exceptions import FHIRValidationException

router = APIRouter()

@router.post("/R4/DiagnosticReport", summary="Create FHIR DiagnosticReport")
async def create_diagnostic_report(
    report_data: Dict[str, Any],
    fhir_service: FHIRDiagnosisService = Depends(get_fhir_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a new diagnostic report using FHIR DiagnosticReport resource.
    
    This is typically used for AI diagnosis results, lab reports, or imaging results.
    """
    try:
        created_report = await fhir_service.create_fhir_diagnostic_report(report_data)
        return created_report.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "DiagnosticReport")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/R4/DiagnosticReport/ai-diagnosis", summary="Create AI Diagnosis Report")
async def create_ai_diagnosis_report(
    diagnosis_data: Dict[str, Any],
    fhir_service: FHIRDiagnosisService = Depends(get_fhir_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Create a DiagnosticReport specifically for AI diagnosis results.
    
    Expected format:
    {
        "patient_id": "string",
        "encounter_id": "string",
        "symptoms": ["symptom1", "symptom2"],
        "physical_exam": {...},
        "vital_signs": {...},
        "differential_diagnoses": [
            {"condition": "Diagnosis 1", "probability": 0.75, "evidence": [...]}
        ]
    }
    """
    try:
        ai_report = await fhir_service.create_ai_diagnosis_report(diagnosis_data)
        return ai_report.dict()
    except ValueError as e:
        raise FHIRValidationException(str(e), "DiagnosticReport")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/DiagnosticReport/{report_id}", summary="Get FHIR DiagnosticReport by ID")
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

@router.get("/R4/DiagnosticReport", summary="Search FHIR DiagnosticReports")
async def search_diagnostic_reports(
    patient: Optional[str] = Query(None, description="Patient reference"),
    encounter: Optional[str] = Query(None, description="Encounter reference"),
    category: Optional[str] = Query(None, description="Report category"),
    code: Optional[str] = Query(None, description="Report code"),
    date: Optional[str] = Query(None, description="Report date"),
    status: Optional[str] = Query(None, description="Report status"),
    _count: Optional[int] = Query(20, ge=1, le=100, description="Number of results"),
    _offset: Optional[int] = Query(0, ge=0, description="Results offset"),
    fhir_service: FHIRDiagnosisService = Depends(get_fhir_diagnosis_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Search for diagnostic reports using FHIR search parameters.
    """
    try:
        search_params = {
            "patient": patient,
            "encounter": encounter,
            "category": category,
            "code": code,
            "date": date,
            "status": status,
            "_count": _count,
            "_offset": _offset
        }
        
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        bundle = await fhir_service.search_diagnostic_reports(search_params)
        return bundle.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
