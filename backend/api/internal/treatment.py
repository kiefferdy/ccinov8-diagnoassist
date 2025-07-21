"""
Internal Treatment API Router
Treatment planning and medication recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/treatment")

# Temporary storage for treatment plans
treatment_plans_store = {}
medication_interactions_store = {}

# Mock treatment database
TREATMENT_PROTOCOLS = {
    "angina pectoris": {
        "medications": [
            {
                "name": "Nitroglycerin",
                "dosage": "0.4 mg sublingual",
                "frequency": "As needed for chest pain",
                "route": "Sublingual",
                "category": "immediate_relief",
                "contraindications": ["severe hypotension", "sildenafil use"],
                "side_effects": ["headache", "dizziness", "hypotension"]
            },
            {
                "name": "Metoprolol",
                "dosage": "25-50 mg",
                "frequency": "Twice daily",
                "route": "Oral",
                "category": "long_term",
                "contraindications": ["severe bradycardia", "heart block"],
                "side_effects": ["fatigue", "dizziness", "cold extremities"]
            },
            {
                "name": "Atorvastatin",
                "dosage": "20-40 mg",
                "frequency": "Once daily",
                "route": "Oral", 
                "category": "long_term",
                "contraindications": ["active liver disease", "pregnancy"],
                "side_effects": ["muscle pain", "liver enzyme elevation"]
            }
        ],
        "non_pharmacological": [
            "Lifestyle modification: diet and exercise",
            "Smoking cessation if applicable",
            "Stress management",
            "Regular cardiology follow-up",
            "Cardiac rehabilitation program"
        ],
        "monitoring": [
            "Blood pressure monitoring",
            "Lipid profile every 3 months",
            "Liver function tests if on statins",
            "Exercise tolerance assessment"
        ],
        "follow_up": {
            "initial": "2-4 weeks",
            "routine": "3-6 months",
            "emergency_return": ["Worsening chest pain", "New symptoms", "Medication side effects"]
        }
    },
    "tension-type headache": {
        "medications": [
            {
                "name": "Ibuprofen",
                "dosage": "400-600 mg",
                "frequency": "Every 6-8 hours as needed",
                "route": "Oral",
                "category": "acute_treatment",
                "contraindications": ["GI bleeding", "kidney disease"],
                "side_effects": ["GI upset", "kidney effects"]
            },
            {
                "name": "Acetaminophen",
                "dosage": "500-1000 mg", 
                "frequency": "Every 6 hours as needed",
                "route": "Oral",
                "category": "acute_treatment",
                "contraindications": ["liver disease"],
                "side_effects": ["hepatotoxicity with overdose"]
            }
        ],
        "non_pharmacological": [
            "Stress management techniques",
            "Regular sleep schedule",
            "Hydration maintenance",
            "Neck and shoulder stretching",
            "Cold or heat therapy"
        ],
        "monitoring": [
            "Headache frequency and intensity",
            "Medication usage tracking",
            "Sleep quality assessment"
        ],
        "follow_up": {
            "initial": "2 weeks if not improving",
            "routine": "As needed",
            "emergency_return": ["Sudden severe headache", "Fever with headache", "Vision changes"]
        }
    },
    "viral upper respiratory infection": {
        "medications": [
            {
                "name": "Acetaminophen",
                "dosage": "500-1000 mg",
                "frequency": "Every 6 hours as needed",
                "route": "Oral",
                "category": "symptomatic",
                "contraindications": ["liver disease"],
                "side_effects": ["hepatotoxicity with overdose"]
            },
            {
                "name": "Dextromethorphan",
                "dosage": "15 mg",
                "frequency": "Every 4 hours as needed",
                "route": "Oral",
                "category": "symptomatic",
                "contraindications": ["MAOI use"],
                "side_effects": ["drowsiness", "dizziness"]
            }
        ],
        "non_pharmacological": [
            "Rest and adequate sleep",
            "Increased fluid intake",
            "Warm salt water gargles",
            "Humidified air",
            "Honey for cough (if >1 year old)"
        ],
        "monitoring": [
            "Fever monitoring",
            "Symptom progression",
            "Hydration status"
        ],
        "follow_up": {
            "initial": "If no improvement in 7-10 days",
            "routine": "As needed",
            "emergency_return": ["High fever >103°F", "Difficulty breathing", "Severe ear pain"]
        }
    }
}

@router.post("/plan", summary="Generate Treatment Plan")
async def generate_treatment_plan(treatment_request: Dict[str, Any]):
    """
    Generate comprehensive treatment plan based on diagnosis.
    
    Example request body:
    {
        "patient_id": "uuid-of-patient",
        "episode_id": "uuid-of-episode",
        "diagnosis": {
            "condition": "Angina Pectoris",
            "icd10_code": "I20.9",
            "severity": "moderate"
        },
        "patient_factors": {
            "age": 55,
            "weight": 180,
            "allergies": ["penicillin"],
            "current_medications": ["lisinopril 10mg daily"],
            "medical_history": ["hypertension", "diabetes"],
            "kidney_function": "normal",
            "liver_function": "normal"
        },
        "preferences": {
            "route_preference": "oral",
            "cost_consideration": "moderate"
        }
    }
    """
    try:
        plan_id = str(uuid.uuid4())
        
        # Extract information
        diagnosis = treatment_request.get("diagnosis", {})
        condition = diagnosis.get("condition", "").lower()
        patient_factors = treatment_request.get("patient_factors", {})
        
        # Find matching treatment protocol
        treatment_protocol = None
        for protocol_condition, protocol in TREATMENT_PROTOCOLS.items():
            if protocol_condition in condition:
                treatment_protocol = protocol
                break
        
        # Default protocol if no match found
        if not treatment_protocol:
            treatment_protocol = {
                "medications": [],
                "non_pharmacological": ["Symptomatic care", "Follow-up with primary care"],
                "monitoring": ["Symptom monitoring"],
                "follow_up": {"initial": "2-4 weeks", "routine": "As needed"}
            }
        
        # Customize medications based on patient factors
        customized_medications = customize_medications(
            treatment_protocol["medications"], 
            patient_factors
        )
        
        # Create treatment plan
        treatment_plan = {
            "id": plan_id,
            "patient_id": treatment_request.get("patient_id"),
            "episode_id": treatment_request.get("episode_id"),
            "diagnosis": diagnosis,
            "medications": customized_medications,
            "non_pharmacological_interventions": treatment_protocol["non_pharmacological"],
            "monitoring_plan": treatment_protocol["monitoring"],
            "follow_up_plan": treatment_protocol["follow_up"],
            "patient_education": generate_patient_education(condition),
            "precautions": generate_precautions(customized_medications, patient_factors),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "ai_system",
            "status": "draft"
        }
        
        # Store treatment plan
        treatment_plans_store[plan_id] = treatment_plan
        
        return treatment_plan
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating treatment plan: {str(e)}")

def customize_medications(base_medications: List[Dict], patient_factors: Dict) -> List[Dict]:
    """Customize medication recommendations based on patient factors"""
    customized = []
    
    patient_allergies = [allergy.lower() for allergy in patient_factors.get("allergies", [])]
    age = patient_factors.get("age", 0)
    weight = patient_factors.get("weight", 70)  # Default 70kg
    kidney_function = patient_factors.get("kidney_function", "normal")
    current_medications = patient_factors.get("current_medications", [])
    
    for med in base_medications:
        customized_med = med.copy()
        
        # Check for allergies
        med_name = med["name"].lower()
        if any(allergy in med_name for allergy in patient_allergies):
            customized_med["alert"] = f"CONTRAINDICATED: Patient allergic to {med['name']}"
            customized_med["recommended"] = False
            customized.append(customized_med)
            continue
        
        # Age-based adjustments
        if age >= 65:
            if "metoprolol" in med_name:
                customized_med["dosage"] = "12.5-25 mg"  # Lower starting dose for elderly
                customized_med["note"] = "Reduced dose due to age"
        
        # Kidney function adjustments
        if kidney_function == "impaired":
            if "ibuprofen" in med_name:
                customized_med["alert"] = "CAUTION: Avoid in kidney impairment"
                customized_med["alternative"] = "Consider acetaminophen instead"
        
        # Drug interaction checks
        interactions = check_drug_interactions(med_name, current_medications)
        if interactions:
            customized_med["interactions"] = interactions
        
        customized_med["recommended"] = True
        customized.append(customized_med)
    
    return customized

def check_drug_interactions(new_medication: str, current_medications: List[str]) -> List[Dict]:
    """Basic drug interaction checking"""
    interactions = []
    new_med_lower = new_medication.lower()
    
    for current_med in current_medications:
        current_med_lower = current_med.lower()
        
        # Known interactions (simplified)
        if "warfarin" in current_med_lower and "ibuprofen" in new_med_lower:
            interactions.append({
                "medication": current_med,
                "interaction": "Increased bleeding risk",
                "severity": "moderate",
                "action": "Monitor closely, consider alternative"
            })
        
        if "lisinopril" in current_med_lower and "ibuprofen" in new_med_lower:
            interactions.append({
                "medication": current_med,
                "interaction": "Reduced antihypertensive effect",
                "severity": "mild",
                "action": "Monitor blood pressure"
            })
    
    return interactions

def generate_patient_education(condition: str) -> List[Dict]:
    """Generate patient education materials"""
    education_materials = []
    
    if "angina" in condition.lower():
        education_materials = [
            {
                "topic": "Understanding Angina",
                "content": "Angina is chest pain caused by reduced blood flow to the heart. It's often triggered by physical activity or stress.",
                "importance": "high"
            },
            {
                "topic": "When to Use Nitroglycerin",
                "content": "Take nitroglycerin at the first sign of chest pain. If pain persists after 5 minutes, take another dose. Call 911 if pain continues.",
                "importance": "critical"
            },
            {
                "topic": "Lifestyle Changes",
                "content": "Eat a heart-healthy diet, exercise as tolerated, quit smoking, and manage stress to reduce angina episodes.",
                "importance": "high"
            }
        ]
    elif "headache" in condition.lower():
        education_materials = [
            {
                "topic": "Headache Triggers",
                "content": "Common triggers include stress, lack of sleep, dehydration, certain foods, and poor posture.",
                "importance": "medium"
            },
            {
                "topic": "When to Seek Help",
                "content": "Seek immediate care for sudden severe headache, headache with fever, or headache with vision changes.",
                "importance": "critical"
            }
        ]
    else:
        education_materials = [
            {
                "topic": "General Care",
                "content": "Follow medication instructions carefully and return for follow-up as scheduled.",
                "importance": "medium"
            }
        ]
    
    return education_materials

def generate_precautions(medications: List[Dict], patient_factors: Dict) -> List[Dict]:
    """Generate precautions based on medications and patient factors"""
    precautions = []
    
    for med in medications:
        med_name = med["name"].lower()
        
        if "nitroglycerin" in med_name:
            precautions.append({
                "medication": med["name"],
                "precaution": "May cause dizziness - sit down before taking",
                "type": "safety"
            })
        
        if "ibuprofen" in med_name:
            precautions.append({
                "medication": med["name"],
                "precaution": "Take with food to reduce stomach upset",
                "type": "administration"
            })
    
    # Patient-specific precautions
    age = patient_factors.get("age", 0)
    if age >= 65:
        precautions.append({
            "general": "Elderly patients may be more sensitive to medications",
            "precaution": "Start with lower doses and monitor closely",
            "type": "age_related"
        })
    
    return precautions

@router.post("/medications", summary="Get Medication Recommendations")
async def get_medication_recommendations(medication_request: Dict[str, Any]):
    """
    Get specific medication recommendations with dosing and interactions.
    
    Example request body:
    {
        "condition": "hypertension",
        "patient_factors": {
            "age": 45,
            "weight": 75,
            "kidney_function": "normal",
            "current_medications": ["metformin"],
            "allergies": []
        },
        "severity": "moderate",
        "comorbidities": ["diabetes"]
    }
    """
    try:
        condition = medication_request.get("condition", "").lower()
        patient_factors = medication_request.get("patient_factors", {})
        
        # Basic medication recommendations
        recommendations = []
        
        if "hypertension" in condition:
            recommendations.append({
                "name": "Lisinopril",
                "class": "ACE Inhibitor",
                "dosage": "10 mg daily",
                "rationale": "First-line treatment for hypertension, beneficial for diabetes",
                "monitoring": ["Blood pressure", "Kidney function", "Potassium levels"]
            })
        
        elif "diabetes" in condition:
            recommendations.append({
                "name": "Metformin",
                "class": "Biguanide",
                "dosage": "500 mg twice daily",
                "rationale": "First-line treatment for type 2 diabetes",
                "monitoring": ["Blood glucose", "HbA1c", "Kidney function"]
            })
        
        return {
            "condition": condition,
            "recommendations": recommendations,
            "general_considerations": [
                "Start with lowest effective dose",
                "Monitor for side effects",
                "Adjust based on response and tolerance"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating medication recommendations: {str(e)}")

@router.post("/interactions/check", summary="Check Drug Interactions")
async def check_drug_interactions_endpoint(interaction_data: Dict[str, Any]):
    """
    Check for drug interactions and contraindications.
    
    Example request body:
    {
        "medications": ["warfarin 5mg daily", "lisinopril 10mg daily"],
        "new_medication": "ibuprofen 400mg",
        "patient_factors": {
            "age": 65,
            "kidney_function": "mild impairment"
        }
    }
    """
    try:
        current_medications = interaction_data.get("medications", [])
        new_medication = interaction_data.get("new_medication", "")
        patient_factors = interaction_data.get("patient_factors", {})
        
        # Check interactions
        interactions = check_drug_interactions(new_medication, current_medications)
        
        # Additional safety checks based on patient factors
        safety_alerts = []
        
        new_med_lower = new_medication.lower()
        age = patient_factors.get("age", 0)
        kidney_function = patient_factors.get("kidney_function", "normal")
        
        if age >= 65 and "ibuprofen" in new_med_lower:
            safety_alerts.append({
                "type": "age_related",
                "alert": "NSAIDs carry higher risk in elderly patients",
                "recommendation": "Consider acetaminophen as alternative"
            })
        
        if kidney_function != "normal" and "ibuprofen" in new_med_lower:
            safety_alerts.append({
                "type": "organ_dysfunction",
                "alert": "NSAIDs may worsen kidney function",
                "recommendation": "Avoid or use with extreme caution"
            })
        
        return {
            "new_medication": new_medication,
            "interactions": interactions,
            "safety_alerts": safety_alerts,
            "overall_risk": determine_overall_risk(interactions, safety_alerts),
            "recommendation": generate_interaction_recommendation(interactions, safety_alerts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error checking interactions: {str(e)}")

def determine_overall_risk(interactions: List[Dict], safety_alerts: List[Dict]) -> str:
    """Determine overall risk level"""
    if any(interaction.get("severity") == "high" for interaction in interactions):
        return "high"
    if safety_alerts or any(interaction.get("severity") == "moderate" for interaction in interactions):
        return "moderate"
    return "low"

def generate_interaction_recommendation(interactions: List[Dict], safety_alerts: List[Dict]) -> str:
    """Generate recommendation based on interactions and alerts"""
    if any(interaction.get("severity") == "high" for interaction in interactions):
        return "Do not prescribe - significant interaction risk"
    if safety_alerts:
        return "Use with caution - monitor closely"
    if interactions:
        return "Acceptable with monitoring"
    return "No significant interactions identified"

@router.get("/{plan_id}", summary="Get Treatment Plan")
async def get_treatment_plan(plan_id: str):
    """
    Get treatment plan by ID.
    """
    try:
        plan = treatment_plans_store.get(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Treatment plan with ID {plan_id} not found")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{plan_id}/approve", summary="Approve Treatment Plan")
async def approve_treatment_plan(plan_id: str, approval_data: Dict[str, Any]):
    """
    Approve or modify treatment plan by physician.
    
    Example request body:
    {
        "approved_by": "Dr. Smith",
        "modifications": [
            {
                "medication": "Metoprolol",
                "change": "Increase dose to 50mg twice daily",
                "reason": "Patient tolerating well, BP still elevated"
            }
        ],
        "notes": "Patient counseled on lifestyle modifications"
    }
    """
    try:
        plan = treatment_plans_store.get(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Treatment plan with ID {plan_id} not found")
        
        # Update plan with approval information
        plan["status"] = "approved"
        plan["approved_at"] = datetime.utcnow().isoformat()
        plan["approved_by"] = approval_data.get("approved_by")
        plan["modifications"] = approval_data.get("modifications", [])
        plan["approval_notes"] = approval_data.get("notes", "")
        
        return {
            "message": "Treatment plan approved successfully",
            "plan_id": plan_id,
            "approved_by": plan["approved_by"],
            "approved_at": plan["approved_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error approving treatment plan: {str(e)}")

@router.get("/patient/{patient_id}/plans", summary="Get Patient Treatment Plans")
async def get_patient_treatment_plans(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None, description="Filter by status (draft, approved, active)")
):
    """
    Get all treatment plans for a patient.
    """
    try:
        # Filter plans by patient_id
        patient_plans = []
        for plan in treatment_plans_store.values():
            if plan.get("patient_id") == patient_id:
                if status is None or plan.get("status") == status:
                    patient_plans.append(plan)
        
        # Sort by created_at (newest first)
        patient_plans.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        start_idx = skip
        end_idx = start_idx + limit
        paginated_plans = patient_plans[start_idx:end_idx]
        
        return {
            "treatment_plans": paginated_plans,
            "total": len(patient_plans),
            "patient_id": patient_id,
            "skip": skip,
            "limit": limit,
            "status_filter": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))