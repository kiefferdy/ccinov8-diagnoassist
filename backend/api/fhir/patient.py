"""
FHIR R4 Patient Resource endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

router = APIRouter()

# Temporary in-memory storage for demo purposes
# In production, this would be replaced with database operations
patients_store = {}

@router.post("/R4/Patient", summary="Create FHIR Patient")
async def create_patient(patient_data: Dict[str, Any]):
    """
    Create a new patient using FHIR Patient resource format.
    
    Accepts standard FHIR Patient JSON and returns created patient with server-assigned ID.
    """
    try:
        # Basic validation
        if not patient_data.get("resourceType") == "Patient":
            raise HTTPException(status_code=400, detail="Resource must be of type 'Patient'")
        
        # Generate ID and add metadata
        patient_id = str(uuid.uuid4())
        patient_data["id"] = patient_id
        patient_data["meta"] = {
            "versionId": "1",
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        }
        
        # Store patient (in production, save to database)
        patients_store[patient_id] = patient_data
        
        return patient_data
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid patient data: {str(e)}")

@router.get("/R4/Patient/{patient_id}", summary="Get FHIR Patient by ID")
async def get_patient(patient_id: str = Path(..., description="Patient resource ID")):
    """
    Retrieve a patient by ID in FHIR Patient resource format.
    """
    try:
        patient = patients_store.get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/R4/Patient/{patient_id}", summary="Update FHIR Patient")
async def update_patient(
    patient_id: str = Path(..., description="Patient resource ID"),
    patient_data: Dict[str, Any] = None
):
    """
    Update an existing patient using FHIR Patient resource format.
    """
    try:
        if patient_id not in patients_store:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        
        # Basic validation
        if not patient_data.get("resourceType") == "Patient":
            raise HTTPException(status_code=400, detail="Resource must be of type 'Patient'")
        
        # Update metadata
        current_version = int(patients_store[patient_id].get("meta", {}).get("versionId", "1"))
        patient_data["id"] = patient_id
        patient_data["meta"] = {
            "versionId": str(current_version + 1),
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        }
        
        # Store updated patient
        patients_store[patient_id] = patient_data
        
        return patient_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/R4/Patient", summary="Search FHIR Patients")
async def search_patients(
    family: Optional[str] = Query(None, description="Family name of the patient"),
    given: Optional[str] = Query(None, description="Given name of the patient"),
    identifier: Optional[str] = Query(None, description="Patient identifier"),
    birthdate: Optional[str] = Query(None, description="Patient birth date (YYYY-MM-DD)"),
    gender: Optional[str] = Query(None, description="Patient gender"),
    _count: Optional[int] = Query(20, ge=1, le=100, description="Number of results"),
    _offset: Optional[int] = Query(0, ge=0, description="Results offset")
):
    """
    Search for patients using FHIR search parameters.
    Returns a FHIR Bundle with matching Patient resources.
    """
    try:
        # Get all patients (in production, this would be a database query)
        all_patients = list(patients_store.values())
        
        # Apply filters (basic implementation)
        filtered_patients = []
        for patient in all_patients:
            match = True
            
            if family:
                patient_family_names = []
                for name in patient.get("name", []):
                    if name.get("family"):
                        patient_family_names.append(name["family"].lower())
                if not any(family.lower() in fname for fname in patient_family_names):
                    match = False
            
            if given:
                patient_given_names = []
                for name in patient.get("name", []):
                    for given_name in name.get("given", []):
                        patient_given_names.append(given_name.lower())
                if not any(given.lower() in gname for gname in patient_given_names):
                    match = False
            
            if gender and patient.get("gender", "").lower() != gender.lower():
                match = False
                
            if birthdate and patient.get("birthDate") != birthdate:
                match = False
            
            if match:
                filtered_patients.append(patient)
        
        # Apply pagination
        start_idx = _offset
        end_idx = start_idx + _count
        paginated_patients = filtered_patients[start_idx:end_idx]
        
        # Create FHIR Bundle response
        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "meta": {
                "lastUpdated": datetime.utcnow().isoformat() + "Z"
            },
            "type": "searchset",
            "total": len(filtered_patients),
            "link": [
                {
                    "relation": "self",
                    "url": f"http://localhost:8000/fhir/R4/Patient"
                }
            ],
            "entry": [
                {
                    "fullUrl": f"http://localhost:8000/fhir/R4/Patient/{patient['id']}",
                    "resource": patient,
                    "search": {
                        "mode": "match"
                    }
                }
                for patient in paginated_patients
            ]
        }
        
        return bundle
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/R4/Patient/{patient_id}", summary="Delete FHIR Patient")
async def delete_patient(patient_id: str = Path(..., description="Patient resource ID")):
    """
    Delete a patient by ID.
    """
    try:
        if patient_id not in patients_store:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        
        del patients_store[patient_id]
        
        return {"message": f"Patient {patient_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))