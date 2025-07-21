"""
Internal Diagnosis API Router
AI-powered diagnosis generation and analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import random

router = APIRouter(prefix="/diagnosis")

# Temporary storage for diagnosis analyses
diagnosis_analyses_store = {}

# Mock diagnosis database for demo purposes
MOCK_DIAGNOSES = {
    "chest_pain": [
        {
            "condition": "Angina Pectoris",
            "icd10_code": "I20.9",
            "probability": 0.85,
            "severity": "moderate",
            "description": "Chest pain due to reduced blood flow to the heart muscle",
            "supporting_factors": ["chest pain", "left arm pain", "exertional symptoms"],
            "risk_factors": ["age", "hypertension", "smoking history"]
        },
        {
            "condition": "Musculoskeletal Chest Pain",
            "icd10_code": "M79.1", 
            "probability": 0.65,
            "severity": "mild",
            "description": "Pain originating from chest wall muscles or ribs",
            "supporting_factors": ["positional pain", "tenderness on palpation"],
            "risk_factors": ["recent activity", "poor posture"]
        },
        {
            "condition": "Gastroesophageal Reflux Disease",
            "icd10_code": "K21.9",
            "probability": 0.45,
            "severity": "mild",
            "description": "Chest pain due to acid reflux",
            "supporting_factors": ["burning sensation", "worse after eating"],
            "risk_factors": ["dietary habits", "stress"]
        }
    ],
    "headache": [
        {
            "condition": "Tension-Type Headache",
            "icd10_code": "G44.2",
            "probability": 0.75,
            "severity": "mild",
            "description": "Common headache often caused by stress or muscle tension",
            "supporting_factors": ["bilateral pain", "pressure sensation"],
            "risk_factors": ["stress", "poor sleep", "dehydration"]
        },
        {
            "condition": "Migraine",
            "icd10_code": "G43.9",
            "probability": 0.60,
            "severity": "moderate", 
            "description": "Recurring headaches with neurological symptoms",
            "supporting_factors": ["unilateral pain", "photophobia", "nausea"],
            "risk_factors": ["family history", "hormonal changes", "triggers"]
        }
    ],
    "fever": [
        {
            "condition": "Viral Upper Respiratory Infection",
            "icd10_code": "J06.9",
            "probability": 0.80,
            "severity": "mild",
            "description": "Common cold or flu-like illness",
            "supporting_factors": ["fever", "cough", "runny nose"],
            "risk_factors": ["seasonal factors", "exposure history"]
        },
        {
            "condition": "Bacterial Infection", 
            "icd10_code": "A49.9",
            "probability": 0.30,
            "severity": "moderate",
            "description": "Bacterial infection requiring antibiotic treatment",
            "supporting_factors": ["high fever", "localized symptoms"],
            "risk_factors": ["immunocompromised state", "recent procedures"]
        }
    ]
}

@router.post("/analyze", summary="Generate Differential Diagnosis")
async def analyze_symptoms(analysis_request: Dict[str, Any]):
    """
    Generate AI-powered differential diagnosis based on symptoms and patient data.
    
    Example request body:
    {
        "patient_id": "uuid-of-patient",
        "episode_id": "uuid-of-episode", 
        "chief_complaint": "chest pain",
        "symptoms": ["chest pain", "shortness of breath", "left arm pain"],
        "vital_signs": {
            "temperature": 98.6,
            "blood_pressure": "140/90",
            "heart_rate": 88
        },
        "patient_history": {
            "age": 55,
            "gender": "male",
            "medical_history": ["hypertension", "diabetes"],
            "medications": ["lisinopril", "metformin"],
            "allergies": ["penicillin"]
        },
        "clinical_findings": {}
    }
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # Extract key information
        chief_complaint = analysis_request.get("chief_complaint", "").lower().replace(" ", "_")
        symptoms = analysis_request.get("symptoms", [])
        vital_signs = analysis_request.get("vital_signs", {})
        patient_history = analysis_request.get("patient_history", {})
        
        # Get potential diagnoses based on chief complaint
        potential_diagnoses = MOCK_DIAGNOSES.get(chief_complaint, [])
        
        # If no specific diagnoses found, provide generic analysis
        if not potential_diagnoses:
            potential_diagnoses = [
                {
                    "condition": "Undifferentiated Symptoms",
                    "icd10_code": "R68.89",
                    "probability": 0.50,
                    "severity": "unknown",
                    "description": "Symptoms require further evaluation for proper diagnosis",
                    "supporting_factors": symptoms,
                    "risk_factors": []
                }
            ]
        
        # Adjust probabilities based on patient factors
        adjusted_diagnoses = []
        for diagnosis in potential_diagnoses:
            adjusted_prob = diagnosis["probability"]
            
            # Simple risk factor adjustments
            risk_factors = diagnosis.get("risk_factors", [])
            patient_age = patient_history.get("age", 0)
            patient_history_conditions = patient_history.get("medical_history", [])
            
            # Age adjustments
            if "age" in risk_factors and patient_age > 50:
                adjusted_prob += 0.1
            
            # Medical history adjustments
            for condition in patient_history_conditions:
                if condition.lower() in str(risk_factors).lower():
                    adjusted_prob += 0.15
            
            # Vital signs adjustments
            if vital_signs.get("temperature", 0) > 100 and "infection" in diagnosis["condition"].lower():
                adjusted_prob += 0.2
                
            adjusted_prob = min(adjusted_prob, 0.95)  # Cap at 95%
            
            adjusted_diagnosis = diagnosis.copy()
            adjusted_diagnosis["probability"] = round(adjusted_prob, 2)
            adjusted_diagnoses.append(adjusted_diagnosis)
        
        # Sort by probability (highest first)
        adjusted_diagnoses.sort(key=lambda x: x["probability"], reverse=True)
        
        # Generate analysis
        analysis = {
            "id": analysis_id,
            "patient_id": analysis_request.get("patient_id"),
            "episode_id": analysis_request.get("episode_id"),
            "chief_complaint": analysis_request.get("chief_complaint"),
            "differential_diagnoses": adjusted_diagnoses,
            "confidence_level": calculate_confidence_level(adjusted_diagnoses),
            "recommendation_level": determine_recommendation_level(adjusted_diagnoses, vital_signs),
            "next_steps": generate_next_steps(adjusted_diagnoses, symptoms),
            "red_flags": identify_red_flags(symptoms, vital_signs, patient_history),
            "created_at": datetime.utcnow().isoformat(),
            "ai_version": "1.0.0"
        }
        
        # Store analysis
        diagnosis_analyses_store[analysis_id] = analysis
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing symptoms: {str(e)}")

def calculate_confidence_level(diagnoses: List[Dict]) -> str:
    """Calculate overall confidence in the analysis"""
    if not diagnoses:
        return "low"
    
    top_probability = diagnoses[0]["probability"]
    if top_probability >= 0.8:
        return "high"
    elif top_probability >= 0.6:
        return "moderate"
    else:
        return "low"

def determine_recommendation_level(diagnoses: List[Dict], vital_signs: Dict) -> str:
    """Determine the urgency level of recommendations"""
    # Check for high-severity conditions
    for diagnosis in diagnoses:
        if diagnosis.get("severity") == "high" or diagnosis["probability"] >= 0.8:
            return "urgent"
    
    # Check vital signs
    temp = vital_signs.get("temperature", 0)
    if temp >= 102:
        return "urgent"
    
    return "routine"

def generate_next_steps(diagnoses: List[Dict], symptoms: List[str]) -> List[str]:
    """Generate recommended next steps based on analysis"""
    next_steps = []
    
    top_diagnosis = diagnoses[0] if diagnoses else {}
    condition = top_diagnosis.get("condition", "").lower()
    
    if "cardiac" in condition or "angina" in condition:
        next_steps.extend([
            "12-lead ECG",
            "Cardiac enzymes (troponin)",
            "Chest X-ray",
            "Consider cardiology consultation"
        ])
    elif "infection" in condition:
        next_steps.extend([
            "Complete blood count (CBC)",
            "Blood cultures if indicated",
            "Consider antibiotics if bacterial"
        ])
    elif "headache" in condition:
        next_steps.extend([
            "Neurological examination",
            "Consider CT head if red flags present",
            "Review medication history"
        ])
    else:
        next_steps.extend([
            "Complete physical examination",
            "Basic diagnostic tests as indicated",
            "Follow-up in 24-48 hours"
        ])
    
    return next_steps

def identify_red_flags(symptoms: List[str], vital_signs: Dict, patient_history: Dict) -> List[Dict]:
    """Identify red flag symptoms requiring immediate attention"""
    red_flags = []
    
    # Symptom-based red flags
    symptom_text = " ".join(symptoms).lower()
    
    if any(flag in symptom_text for flag in ["severe chest pain", "crushing chest pain"]):
        red_flags.append({
            "flag": "Severe chest pain",
            "concern": "Possible acute coronary syndrome",
            "action": "Immediate cardiac evaluation"
        })
    
    if "severe headache" in symptom_text:
        red_flags.append({
            "flag": "Severe headache",
            "concern": "Possible intracranial pathology", 
            "action": "Neurological assessment"
        })
    
    # Vital sign red flags
    temp = vital_signs.get("temperature", 0)
    if temp >= 103:
        red_flags.append({
            "flag": "High fever",
            "concern": "Possible serious infection",
            "action": "Immediate medical evaluation"
        })
    
    # Patient history red flags
    age = patient_history.get("age", 0)
    if age > 65 and "chest pain" in symptom_text:
        red_flags.append({
            "flag": "Elderly with chest pain",
            "concern": "Higher risk for cardiac events",
            "action": "Priority cardiac assessment"
        })
    
    return red_flags

@router.post("/refine", summary="Refine Diagnosis with Test Results")
async def refine_diagnosis(refinement_request: Dict[str, Any]):
    """
    Refine diagnosis based on new test results or clinical findings.
    
    Example request body:
    {
        "analysis_id": "uuid-of-previous-analysis",
        "new_findings": {
            "lab_results": {
                "troponin": {"value": 0.02, "unit": "ng/mL", "normal_range": "<0.04"},
                "white_cell_count": {"value": 12000, "unit": "/uL", "normal_range": "4000-11000"}
            },
            "imaging_results": {
                "chest_xray": "Normal heart size, clear lungs",
                "ecg": "Normal sinus rhythm, no ST changes"
            },
            "physical_exam": {
                "heart_sounds": "Regular rate and rhythm, no murmurs",
                "lung_sounds": "Clear bilaterally"
            }
        }
    }
    """
    try:
        analysis_id = refinement_request.get("analysis_id")
        new_findings = refinement_request.get("new_findings", {})
        
        # Get original analysis
        original_analysis = diagnosis_analyses_store.get(analysis_id)
        if not original_analysis:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")
        
        # Create refined analysis
        refined_analysis_id = str(uuid.uuid4())
        
        # Copy original analysis and modify based on new findings
        refined_analysis = original_analysis.copy()
        refined_analysis["id"] = refined_analysis_id
        refined_analysis["parent_analysis_id"] = analysis_id
        refined_analysis["refined_at"] = datetime.utcnow().isoformat()
        refined_analysis["new_findings"] = new_findings
        
        # Adjust diagnosis probabilities based on findings
        refined_diagnoses = []
        for diagnosis in original_analysis["differential_diagnoses"]:
            refined_diagnosis = diagnosis.copy()
            
            # Simple rule-based refinement
            condition = diagnosis["condition"].lower()
            
            # Lab result refinements
            lab_results = new_findings.get("lab_results", {})
            if "troponin" in lab_results:
                troponin_value = lab_results["troponin"].get("value", 0)
                if "cardiac" in condition or "angina" in condition:
                    if troponin_value > 0.04:  # Elevated troponin
                        refined_diagnosis["probability"] = min(0.9, diagnosis["probability"] + 0.3)
                    else:  # Normal troponin
                        refined_diagnosis["probability"] = max(0.1, diagnosis["probability"] - 0.4)
            
            if "white_cell_count" in lab_results:
                wbc_value = lab_results["white_cell_count"].get("value", 0)
                if "infection" in condition:
                    if wbc_value > 11000:  # Elevated WBC
                        refined_diagnosis["probability"] = min(0.9, diagnosis["probability"] + 0.2)
                    else:  # Normal WBC
                        refined_diagnosis["probability"] = max(0.2, diagnosis["probability"] - 0.2)
            
            # Imaging result refinements
            imaging_results = new_findings.get("imaging_results", {})
            if "ecg" in imaging_results:
                ecg_result = imaging_results["ecg"].lower()
                if "cardiac" in condition:
                    if "normal" in ecg_result:
                        refined_diagnosis["probability"] = max(0.2, diagnosis["probability"] - 0.3)
                    elif "st changes" in ecg_result or "abnormal" in ecg_result:
                        refined_diagnosis["probability"] = min(0.9, diagnosis["probability"] + 0.4)
            
            refined_diagnosis["probability"] = round(refined_diagnosis["probability"], 2)
            refined_diagnoses.append(refined_diagnosis)
        
        # Sort by updated probabilities
        refined_diagnoses.sort(key=lambda x: x["probability"], reverse=True)
        
        refined_analysis["differential_diagnoses"] = refined_diagnoses
        refined_analysis["confidence_level"] = calculate_confidence_level(refined_diagnoses)
        refined_analysis["refinement_summary"] = generate_refinement_summary(original_analysis, refined_analysis)
        
        # Store refined analysis
        diagnosis_analyses_store[refined_analysis_id] = refined_analysis
        
        return refined_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error refining diagnosis: {str(e)}")

def generate_refinement_summary(original: Dict, refined: Dict) -> Dict:
    """Generate a summary of how the diagnosis changed with new findings"""
    original_top = original["differential_diagnoses"][0] if original["differential_diagnoses"] else {}
    refined_top = refined["differential_diagnoses"][0] if refined["differential_diagnoses"] else {}
    
    summary = {
        "original_top_diagnosis": original_top.get("condition", "None"),
        "original_probability": original_top.get("probability", 0),
        "refined_top_diagnosis": refined_top.get("condition", "None"),
        "refined_probability": refined_top.get("probability", 0),
        "diagnosis_changed": original_top.get("condition") != refined_top.get("condition"),
        "confidence_improved": refined["confidence_level"] != original["confidence_level"]
    }
    
    return summary

@router.get("/{analysis_id}", summary="Get Diagnosis Analysis")
async def get_diagnosis_analysis(analysis_id: str):
    """
    Get diagnosis analysis by ID.
    """
    try:
        analysis = diagnosis_analyses_store.get(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}/analyses", summary="Get Patient Diagnosis Analyses")
async def get_patient_analyses(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get all diagnosis analyses for a patient.
    """
    try:
        # Filter analyses by patient_id
        patient_analyses = []
        for analysis in diagnosis_analyses_store.values():
            if analysis.get("patient_id") == patient_id:
                patient_analyses.append(analysis)
        
        # Sort by created_at (newest first)
        patient_analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        start_idx = skip
        end_idx = start_idx + limit
        paginated_analyses = patient_analyses[start_idx:end_idx]
        
        return {
            "analyses": paginated_analyses,
            "total": len(patient_analyses),
            "patient_id": patient_id,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", summary="Validate Diagnosis with Physician Input")
async def validate_diagnosis(validation_request: Dict[str, Any]):
    """
    Allow physicians to validate or override AI diagnosis.
    
    Example request body:
    {
        "analysis_id": "uuid-of-analysis",
        "physician_diagnosis": {
            "condition": "Confirmed Angina Pectoris",
            "icd10_code": "I20.9",
            "confidence": "high"
        },
        "physician_notes": "Patient responded well to nitroglycerin, confirming anginal chest pain",
        "validated_by": "Dr. Smith"
    }
    """
    try:
        analysis_id = validation_request.get("analysis_id")
        analysis = diagnosis_analyses_store.get(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")
        
        # Add validation information
        validation = {
            "validated_at": datetime.utcnow().isoformat(),
            "validated_by": validation_request.get("validated_by"),
            "physician_diagnosis": validation_request.get("physician_diagnosis"),
            "physician_notes": validation_request.get("physician_notes"),
            "ai_accuracy": calculate_ai_accuracy(analysis, validation_request.get("physician_diagnosis"))
        }
        
        analysis["physician_validation"] = validation
        
        return {
            "message": "Diagnosis validated successfully",
            "validation": validation,
            "ai_accuracy": validation["ai_accuracy"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating diagnosis: {str(e)}")

def calculate_ai_accuracy(analysis: Dict, physician_diagnosis: Dict) -> Dict:
    """Calculate how accurate the AI diagnosis was compared to physician diagnosis"""
    ai_top_diagnosis = analysis["differential_diagnoses"][0] if analysis["differential_diagnoses"] else {}
    physician_condition = physician_diagnosis.get("condition", "").lower()
    ai_condition = ai_top_diagnosis.get("condition", "").lower()
    
    # Simple accuracy calculation
    exact_match = physician_condition in ai_condition or ai_condition in physician_condition
    
    # Check if physician diagnosis was in AI's differential list
    in_differential = False
    ai_rank = None
    for i, diagnosis in enumerate(analysis["differential_diagnoses"]):
        if physician_condition in diagnosis["condition"].lower():
            in_differential = True
            ai_rank = i + 1
            break
    
    return {
        "exact_match": exact_match,
        "in_differential": in_differential,
        "ai_rank": ai_rank,
        "ai_top_probability": ai_top_diagnosis.get("probability", 0),
        "accuracy_score": 1.0 if exact_match else (0.7 if in_differential else 0.3)
    }