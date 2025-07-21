"""
Internal Clinical API Router
Clinical assessment and examination endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/clinical")

# Temporary storage for clinical assessments
clinical_assessments_store = {}

# Pre-defined question templates for different chief complaints
QUESTION_TEMPLATES = {
    "chest_pain": [
        {"id": "cp_1", "text": "On a scale of 1-10, how would you rate your chest pain?", "type": "scale", "required": True},
        {"id": "cp_2", "text": "When did the chest pain start?", "type": "datetime", "required": True},
        {"id": "cp_3", "text": "Does the pain radiate to other areas?", "type": "multiple_choice", "options": ["No", "Left arm", "Right arm", "Jaw", "Back", "Neck"], "required": True},
        {"id": "cp_4", "text": "What triggers or worsens the pain?", "type": "multiple_choice", "options": ["Rest", "Activity", "Deep breathing", "Position change", "Eating"], "required": False},
        {"id": "cp_5", "text": "Do you have any associated symptoms?", "type": "multiple_choice", "options": ["Shortness of breath", "Nausea", "Sweating", "Dizziness", "Palpitations"], "required": False}
    ],
    "headache": [
        {"id": "ha_1", "text": "On a scale of 1-10, how severe is your headache?", "type": "scale", "required": True},
        {"id": "ha_2", "text": "Where is the headache located?", "type": "multiple_choice", "options": ["Entire head", "One side", "Forehead", "Back of head", "Top of head"], "required": True},
        {"id": "ha_3", "text": "How long have you had this headache?", "type": "duration", "required": True},
        {"id": "ha_4", "text": "Is this headache different from your usual headaches?", "type": "yes_no", "required": True},
        {"id": "ha_5", "text": "Do you have any associated symptoms?", "type": "multiple_choice", "options": ["Nausea", "Vomiting", "Light sensitivity", "Sound sensitivity", "Visual changes"], "required": False}
    ],
    "fever": [
        {"id": "fv_1", "text": "What is your current temperature?", "type": "temperature", "required": True},
        {"id": "fv_2", "text": "How long have you had a fever?", "type": "duration", "required": True},
        {"id": "fv_3", "text": "Do you have any other symptoms?", "type": "multiple_choice", "options": ["Cough", "Sore throat", "Body aches", "Chills", "Fatigue", "Loss of appetite"], "required": False},
        {"id": "fv_4", "text": "Have you taken any medications for the fever?", "type": "yes_no", "required": False},
        {"id": "fv_5", "text": "Have you been around anyone who was sick recently?", "type": "yes_no", "required": False}
    ]
}

@router.post("/assessment/questions", summary="Get Dynamic Clinical Questions")
async def get_clinical_questions(request_data: Dict[str, Any]):
    """
    Get dynamic questions based on chief complaint and previous answers.
    
    Example request body:
    {
        "chief_complaint": "chest pain",
        "patient_id": "uuid-of-patient",
        "previous_answers": {},
        "stage": "initial"
    }
    """
    try:
        chief_complaint = request_data.get("chief_complaint", "").lower().replace(" ", "_")
        previous_answers = request_data.get("previous_answers", {})
        stage = request_data.get("stage", "initial")
        
        # Get base questions for the chief complaint
        base_questions = QUESTION_TEMPLATES.get(chief_complaint, [])
        
        # If no specific template, provide generic questions
        if not base_questions:
            base_questions = [
                {"id": "gen_1", "text": "On a scale of 1-10, how severe are your symptoms?", "type": "scale", "required": True},
                {"id": "gen_2", "text": "When did your symptoms start?", "type": "datetime", "required": True},
                {"id": "gen_3", "text": "Describe your main symptoms", "type": "text", "required": True},
                {"id": "gen_4", "text": "Have you experienced these symptoms before?", "type": "yes_no", "required": False},
                {"id": "gen_5", "text": "Are there any factors that make symptoms better or worse?", "type": "text", "required": False}
            ]
        
        # Filter out already answered questions
        remaining_questions = []
        for question in base_questions:
            if question["id"] not in previous_answers:
                remaining_questions.append(question)
        
        # Adaptive questioning based on previous answers
        if stage == "follow_up" and previous_answers:
            adaptive_questions = []
            
            # Example adaptive logic for chest pain
            if chief_complaint == "chest_pain":
                if previous_answers.get("cp_1") and int(previous_answers.get("cp_1", 0)) >= 7:
                    adaptive_questions.append({
                        "id": "cp_severe", 
                        "text": "Given the severity of your pain, have you had any episodes of fainting or near-fainting?", 
                        "type": "yes_no", 
                        "required": True
                    })
                
                if "Shortness of breath" in str(previous_answers.get("cp_5", "")):
                    adaptive_questions.append({
                        "id": "cp_sob", 
                        "text": "How severe is your shortness of breath?", 
                        "type": "multiple_choice", 
                        "options": ["Mild", "Moderate", "Severe", "Unable to speak in full sentences"],
                        "required": True
                    })
            
            remaining_questions.extend(adaptive_questions)
        
        response = {
            "questions": remaining_questions[:3],  # Return 3 questions at a time
            "total_questions": len(base_questions),
            "answered_questions": len(previous_answers),
            "progress_percentage": round((len(previous_answers) / len(base_questions)) * 100, 1) if base_questions else 0,
            "stage": stage,
            "chief_complaint": chief_complaint,
            "has_more_questions": len(remaining_questions) > 3
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating questions: {str(e)}")

@router.post("/assessment/submit", summary="Submit Clinical Assessment")
async def submit_clinical_assessment(assessment_data: Dict[str, Any]):
    """
    Submit answers to clinical assessment questions.
    
    Example request body:
    {
        "patient_id": "uuid-of-patient",
        "episode_id": "uuid-of-episode",
        "answers": {
            "cp_1": "8",
            "cp_2": "2024-01-15T10:30:00Z",
            "cp_3": ["Left arm", "Jaw"]
        },
        "stage": "initial"
    }
    """
    try:
        assessment_id = str(uuid.uuid4())
        
        assessment = {
            "id": assessment_id,
            "patient_id": assessment_data.get("patient_id"),
            "episode_id": assessment_data.get("episode_id"),
            "answers": assessment_data.get("answers", {}),
            "stage": assessment_data.get("stage", "initial"),
            "submitted_at": datetime.utcnow().isoformat(),
            "risk_score": None,  # Would be calculated by AI service
            "recommendations": []  # Would be generated by AI service
        }
        
        # Store assessment
        clinical_assessments_store[assessment_id] = assessment
        
        # Generate basic recommendations based on answers
        recommendations = generate_basic_recommendations(assessment_data.get("answers", {}))
        assessment["recommendations"] = recommendations
        
        return {
            "assessment_id": assessment_id,
            "status": "submitted",
            "recommendations": recommendations,
            "next_steps": [
                "Review symptoms with healthcare provider",
                "Consider physical examination",
                "May require diagnostic tests"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error submitting assessment: {str(e)}")

def generate_basic_recommendations(answers: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate basic clinical recommendations based on answers"""
    recommendations = []
    
    # Check for high severity scores
    for key, value in answers.items():
        if "severity" in str(key).lower() or key.endswith("_1"):
            try:
                if isinstance(value, str) and value.isdigit():
                    severity = int(value)
                    if severity >= 8:
                        recommendations.append({
                            "type": "urgent",
                            "message": "High severity symptoms require immediate medical attention",
                            "priority": "high"
                        })
                    elif severity >= 6:
                        recommendations.append({
                            "type": "monitoring",
                            "message": "Moderate symptoms - close monitoring recommended",
                            "priority": "medium"
                        })
            except (ValueError, TypeError):
                pass
    
    # Check for red flag symptoms
    red_flags = ["chest pain", "shortness of breath", "severe headache", "high fever"]
    for answer in answers.values():
        if isinstance(answer, (str, list)):
            answer_str = str(answer).lower()
            for flag in red_flags:
                if flag in answer_str:
                    recommendations.append({
                        "type": "red_flag",
                        "message": f"Symptoms suggest possible serious condition - urgent evaluation needed",
                        "priority": "high"
                    })
                    break
    
    if not recommendations:
        recommendations.append({
            "type": "routine",
            "message": "Continue monitoring symptoms and follow up as planned",
            "priority": "low"
        })
    
    return recommendations

@router.get("/assessment/{assessment_id}", summary="Get Clinical Assessment")
async def get_clinical_assessment(assessment_id: str):
    """
    Get clinical assessment by ID.
    """
    try:
        assessment = clinical_assessments_store.get(assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Assessment with ID {assessment_id} not found")
        
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vital-signs", summary="Record Vital Signs")
async def record_vital_signs(vital_signs_data: Dict[str, Any]):
    """
    Record patient vital signs.
    
    Example request body:
    {
        "patient_id": "uuid-of-patient",
        "episode_id": "uuid-of-episode",
        "vital_signs": {
            "temperature": {"value": 98.6, "unit": "F"},
            "blood_pressure": {"systolic": 120, "diastolic": 80, "unit": "mmHg"},
            "heart_rate": {"value": 72, "unit": "bpm"},
            "respiratory_rate": {"value": 16, "unit": "breaths/min"},
            "oxygen_saturation": {"value": 98, "unit": "%"},
            "height": {"value": 68, "unit": "inches"},
            "weight": {"value": 150, "unit": "lbs"}
        }
    }
    """
    try:
        vital_signs_id = str(uuid.uuid4())
        
        # Validate and normalize vital signs
        vital_signs = vital_signs_data.get("vital_signs", {})
        
        # Basic validation
        if "temperature" in vital_signs:
            temp_value = vital_signs["temperature"].get("value", 0)
            if temp_value > 110 or temp_value < 90:  # Basic range check
                raise HTTPException(status_code=400, detail="Temperature value seems unrealistic")
        
        record = {
            "id": vital_signs_id,
            "patient_id": vital_signs_data.get("patient_id"),
            "episode_id": vital_signs_data.get("episode_id"),
            "vital_signs": vital_signs,
            "recorded_at": datetime.utcnow().isoformat(),
            "recorded_by": vital_signs_data.get("recorded_by", "system"),
            "notes": vital_signs_data.get("notes", "")
        }
        
        # Generate alerts for abnormal vitals
        alerts = []
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"].get("value", 0)
            if temp >= 100.4:  # Fever threshold
                alerts.append("Fever detected")
        
        if "blood_pressure" in vital_signs:
            systolic = vital_signs["blood_pressure"].get("systolic", 0)
            if systolic >= 140:
                alerts.append("Elevated systolic blood pressure")
        
        record["alerts"] = alerts
        
        return {
            "vital_signs_id": vital_signs_id,
            "status": "recorded",
            "alerts": alerts,
            "recorded_at": record["recorded_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error recording vital signs: {str(e)}")

@router.get("/patient/{patient_id}/assessments", summary="Get Patient Assessments")
async def get_patient_assessments(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get all clinical assessments for a patient.
    """
    try:
        # Filter assessments by patient_id
        patient_assessments = []
        for assessment in clinical_assessments_store.values():
            if assessment.get("patient_id") == patient_id:
                patient_assessments.append(assessment)
        
        # Sort by submitted_at (newest first)
        patient_assessments.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        # Apply pagination
        start_idx = skip
        end_idx = start_idx + limit
        paginated_assessments = patient_assessments[start_idx:end_idx]
        
        return {
            "assessments": paginated_assessments,
            "total": len(patient_assessments),
            "patient_id": patient_id,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))