import ast
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import base64
import json
import io
from typing import Optional, Annotated, List, Dict, Any
from typing_extensions import TypedDict
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.messages import (
    ModelRequest, 
    ModelResponse, 
    UserPromptPart, 
    TextPart,
    ModelMessagesTypeAdapter
)
from datetime import datetime
from sqlalchemy.orm import Session
from config.database import SessionLocal
from repositories.patient_repository import PatientRepository
from repositories.episode_repository import EpisodeRepository
from repositories.encounter_repository import EncounterRepository

load_dotenv()

router = APIRouter()

system_prompt = """
You are a medical AI assistant designed to support doctors in a conversational, clinically relevant way. You will be provided with patient context (such as encounter notes and history), which you must treat as background knowledge. Do not mention or act on this context unless directly asked to. Only respond to the content under 'USER MESSAGE:' and do exactly what is requested—nothing more. If the message is casual or vague (e.g., "what's up"), respond casually and do not reference patient data. Never volunteer medical suggestions, summaries, or recommendations unless explicitly prompted. Keep your tone professional, friendly, and concise, as if you're chatting with a colleague who leads the interaction. Do not initiate any clinical actions or questions on your own."""

class ChatRequest(BaseModel):
    patient_id: str
    episode_id: str
    encounter_id: str
    message: str
    message_history: List[Dict]

class ChatResponse(BaseModel):
    response: str

chat_agent = Agent(  
    'google-gla:gemini-2.0-flash',
    system_prompt=system_prompt,
    retries=3,
    output_type=ChatResponse
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def convert_custom_to_pydantic_ai(custom_messages: List[Dict[str, Any]]) -> List:
    pydantic_ai_messages = []
    
    for msg in custom_messages:
        try:
            timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
        except:
            timestamp = datetime.now()
        
        if msg['type'] == 'user':
            user_part = UserPromptPart(
                content=msg['content'],
                timestamp=timestamp
            )
            model_request = ModelRequest(parts=[user_part])
            pydantic_ai_messages.append(model_request)
            
        elif msg['type'] == 'ai':
            text_part = TextPart(content=msg['content'])
            model_response = ModelResponse(
                parts=[text_part],
                timestamp=timestamp,
                model_name='gpt-4o'  # Set your model name
            )
            pydantic_ai_messages.append(model_response)
    
    return pydantic_ai_messages

def extract_medical_context(patient, episode, encounter):
    """Extract essential medical context in token-efficient format"""
    
    # Calculate age (handle placeholder dates)
    try:
        from datetime import datetime
        dob = datetime.strptime(str(patient.date_of_birth), "%Y-%m-%d")
        age = datetime.now().year - dob.year
        age_str = f"{age}y"
    except:
        age_str = "Unknown age"
    
    # Parse SOAP data from encounter
    soap_subj = encounter.soap_subjective or {}
    soap_obj = encounter.soap_objective or {}
    soap_assess = encounter.soap_assessment or {}
    soap_plan = encounter.soap_plan or {}
    
    # Extract vitals
    vitals = soap_obj.get('vitals', {})
    
    medical_context = f"""PATIENT: {patient.first_name} {patient.last_name or ''} | {patient.gender} | {age_str}
MRN: {patient.medical_record_number} | Status: {patient.status}
Allergies: {patient.allergies or 'None'} | Medications: {patient.current_medications or 'None'}
Medical Hx: {patient.medical_history or 'None'}

EPISODE: {episode.chief_complaint} | {episode.encounter_type} | {episode.priority}
Status: {episode.status} | Started: {episode.start_date}
Assessment: {episode.assessment_notes or 'Pending'}

ENCOUNTER: {encounter.type} | {encounter.status} | Provider: {encounter.provider_name}
Date: {encounter.date}

SOAP:
S: CC: {soap_subj.get('chiefComplaint', episode.chief_complaint)}
   HPI: {soap_subj.get('hpi', 'Not documented')}

O: HR: {vitals.get('heartRate', 'N/A')} | Temp: {vitals.get('temperature', 'N/A')}°C
   BP: {vitals.get('bloodPressure', 'N/A')} | RR: {vitals.get('respiratoryRate', 'N/A')}

A: {soap_assess.get('clinicalImpression', episode.assessment_notes or 'Pending assessment')}
   Confidence: {soap_assess.get('workingDiagnosis', {}).get('confidence', 'N/A')}

P: {episode.plan_notes or 'Plan pending'}
"""
    
    return medical_context

def serialize_for_api(pydantic_ai_messages: List) -> str:
    return ModelMessagesTypeAdapter.dump_json(pydantic_ai_messages).decode('utf-8')

@router.post("/chat")
def post_chat(prompt: ChatRequest, db: Session = Depends(get_db)):
    patient_repo = PatientRepository(db)
    episode_repo = EpisodeRepository(db)
    encounter_repo = EncounterRepository(db)

    print(prompt.encounter_id)

    medical_context = ""
    converted_message_history = convert_custom_to_pydantic_ai(prompt.message_history)

    # fetch current chat context
    try:

        patient = patient_repo.get_by_id(prompt.patient_id)
        if not patient:
            return {"success": False, "message": "Patient not found"}

        episode = episode_repo.get_by_id(prompt.episode_id)
        if not episode:
            return {"success": False, "message": "Episode not found"}

        encounter = encounter_repo.get_by_id(prompt.encounter_id)
        if not encounter:
            return {"success": False, "message": "Encounter not found"}

        # medical_context = extract_medical_context(patient, episode, encounter)
        formatted_context = extract_medical_context(patient, episode, encounter)
        print(formatted_context)

        # print("PATIENT INFO")
        # for key, val in vars(patient).items():
        #     print(key, ": ", val)
        #     medical_context = f"{key}: {val}"
        #
        # print("\n\nEPISODE INFO")
        # for key, val in vars(episode).items():
        #     print(key, ": ", val)
        #     medical_context += f"{key}: {val}"
        #
        # print("\n\nENCOUNTER INFO")
        # for key, val in vars(encounter).items():
        #     print(key, ": ", val)
        #     medical_context += f"{key}: {val}"
        #

    except Exception as e:
        print("Error: ", e)

    try:

        user_message = formatted_context + "\n\nUSER MESSAGE:\n" + prompt.message

        print(user_message)

        result = chat_agent.run_sync(user_message, message_history=converted_message_history)
        return {"success": True, "message": result.output}

    except Exception as e:
        print(f"Error! Could not send chat message. {e}")
        return {"success": False, "message": "Error"}

class InsightsRequest(BaseModel):
    patient_id: str
    episode_id: str
    encounter_id: str
    current_section: Optional[str] = None
    chief_complaint: Optional[str] = None

class InsightsResponse(BaseModel):
    insights_json: str

insights_system_prompt = """
You are a clinical decision support AI that generates evidence-based medical insights. 

Given patient information and clinical context, provide structured clinical decision support in JSON format only. 

Your response must be valid JSON with these exact keys:
- criticalConsiderations: array of critical red flags or urgent considerations
- differentialDiagnosis: object with "Most Likely", "Can't Miss", and "Consider" keys
- diagnosticRecommendations: object with "Indicated Tests" (array) and "Avoid" (string) keys  
- treatmentConsiderations: object with treatment recommendations
- clinicalPearls: array of evidence-based clinical pearls

Base recommendations on current clinical guidelines, evidence-based medicine, and the specific patient context provided. Include likelihood ratios, sensitivity/specificity data, and validated clinical decision tools where appropriate.

Respond only with the JSON object - no additional text or formatting.
"""

insights_agent = Agent(  
    'google-gla:gemini-2.0-flash',
    system_prompt=insights_system_prompt,
    retries=3,
    output_type=InsightsResponse
)

@router.post("/insights")
def post_insights(request: InsightsRequest, db: Session = Depends(get_db)):
    patient_repo = PatientRepository(db)
    episode_repo = EpisodeRepository(db)
    encounter_repo = EncounterRepository(db)

    try:
        # Fetch medical context
        patient = patient_repo.get_by_id(request.patient_id)
        if not patient:
            return {"success": False, "message": "Patient not found"}

        episode = episode_repo.get_by_id(request.episode_id)
        if not episode:
            return {"success": False, "message": "Episode not found"}

        encounter = encounter_repo.get_by_id(request.encounter_id)
        if not encounter:
            return {"success": False, "message": "Encounter not found"}

        # Get medical context
        formatted_context = extract_medical_context(patient, episode, encounter)
        
        # Create insights-specific prompt
        insights_prompt = f"""{formatted_context}

CURRENT SECTION: {request.current_section or 'general'}

Generate comprehensive clinical decision support insights for this case. Structure your response as a JSON object with the following sections:

1. criticalConsiderations: Array of critical red flags or urgent considerations
2. differentialDiagnosis: Object with "Most Likely", "Can't Miss", and "Consider" keys
3. diagnosticRecommendations: Object with "Indicated Tests" (array) and "Avoid" (string) keys
4. treatmentConsiderations: Object with treatment recommendations by priority/type
5. clinicalPearls: Array of evidence-based clinical pearls and likelihood ratios

Focus on the chief complaint: {episode.chief_complaint}
Current documentation section: {request.current_section or 'general'}

Provide actionable, evidence-based insights appropriate for the current clinical context."""

        print("Insights prompt:", insights_prompt)

        # Use the chat agent to generate insights
        result = insights_agent.run_sync(insights_prompt)
        
        # Parse the JSON response
        try:
            insights_data = json.loads(result.output.insights_json)
            return {"success": True, "insights": insights_data}
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {"success": False, "message": "Failed to parse insights response"}

    except Exception as e:
        print(f"Error generating insights: {e}")
        return {"success": False, "message": "Failed to generate clinical insights"}

# Add these models with your other BaseModel classes
class RecommendationsRequest(BaseModel):
    patient_id: str
    episode_id: str
    encounter_id: str
    current_section: Optional[str] = None

class RecommendationItem(BaseModel):
    type: str
    title: str
    description: str
    priority: str

class RecommendationsResponse(BaseModel):
    recommendations_json: str

# Add this agent after your insights_agent
recommendations_system_prompt = """
You are a clinical documentation assistant that provides actionable recommendations for SOAP note completion.

Given patient information and the current SOAP section being documented, provide specific, actionable recommendations to help complete that section thoroughly and accurately.

Your response must be valid JSON with an array of recommendation objects. Each recommendation must have:
- type: category of recommendation (e.g., "documentation", "examination", "diagnostic", "assessment", "treatment", "screening")
- title: brief, actionable title
- description: specific guidance or template text
- priority: "high", "medium", or "low"

Tailor recommendations to:
- Current SOAP section (subjective, objective, assessment, plan)
- Chief complaint and presenting symptoms
- Patient demographics and risk factors
- What's already documented vs. what's missing

Focus on:
- Evidence-based documentation standards
- Clinical decision tools and scoring systems
- Required elements for billing/coding
- Safety considerations and red flags
- Efficiency tips for documentation

Respond only with the JSON array - no additional text.
"""

recommendations_agent = Agent(  
    'google-gla:gemini-2.0-flash',
    system_prompt=recommendations_system_prompt,
    retries=3,
    output_type=RecommendationsResponse
)

@router.post("/recommendations")
def post_recommendations(request: RecommendationsRequest, db: Session = Depends(get_db)):
    patient_repo = PatientRepository(db)
    episode_repo = EpisodeRepository(db)
    encounter_repo = EncounterRepository(db)

    try:
        # Fetch medical context
        patient = patient_repo.get_by_id(request.patient_id)
        if not patient:
            return {"success": False, "message": "Patient not found"}

        episode = episode_repo.get_by_id(request.episode_id)
        if not episode:
            return {"success": False, "message": "Episode not found"}

        encounter = encounter_repo.get_by_id(request.encounter_id)
        if not encounter:
            return {"success": False, "message": "Encounter not found"}

        # Get medical context
        formatted_context = extract_medical_context(patient, episode, encounter)
        
        # Parse SOAP data to understand what's already documented
        soap_subj = encounter.soap_subjective or {}
        soap_obj = encounter.soap_objective or {}
        soap_assess = encounter.soap_assessment or {}
        soap_plan = encounter.soap_plan or {}
        
        # Create section-specific documentation status
        section_status = {
            "subjective": {
                "chiefComplaint": bool(soap_subj.get('chiefComplaint')),
                "hpi": bool(soap_subj.get('hpi')),
                "ros": bool(soap_subj.get('reviewOfSystems')),
                "pmh": bool(soap_subj.get('pastMedicalHistory')),
                "socialHistory": bool(soap_subj.get('socialHistory'))
            },
            "objective": {
                "vitals": bool(soap_obj.get('vitals')),
                "physicalExam": bool(soap_obj.get('physicalExam')),
                "labs": bool(soap_obj.get('labResults')),
                "imaging": bool(soap_obj.get('imagingResults'))
            },
            "assessment": {
                "workingDiagnosis": bool(soap_assess.get('workingDiagnosis')),
                "differential": bool(soap_assess.get('differentialDiagnosis')),
                "clinicalImpression": bool(soap_assess.get('clinicalImpression'))
            },
            "plan": {
                "treatments": bool(soap_plan.get('treatments')),
                "medications": bool(soap_plan.get('medications')),
                "follow_up": bool(soap_plan.get('followUp')),
                "patient_education": bool(soap_plan.get('patientEducation'))
            }
        }
        
        # Create recommendations prompt
        recommendations_prompt = f"""{formatted_context}

CURRENT SECTION: {request.current_section or 'general'}
CHIEF COMPLAINT: {episode.chief_complaint}

DOCUMENTATION STATUS:
{json.dumps(section_status, indent=2)}

Generate specific, actionable recommendations for completing the {request.current_section or 'current'} section of the SOAP note. Consider:

1. What's already documented vs. what's missing
2. Section-specific requirements and best practices
3. Chief complaint-specific considerations
4. Patient safety and clinical decision making
5. Documentation efficiency and completeness

Provide 3-6 prioritized recommendations as a JSON array. Focus on practical, implementable actions the clinician can take right now to improve their documentation."""

        print("Recommendations prompt:", recommendations_prompt)

        # Use the recommendations agent
        result = recommendations_agent.run_sync(recommendations_prompt)
        
        # Parse the JSON response
        try:
            recommendations_data = json.loads(result.output.recommendations_json)
            return {"success": True, "recommendations": recommendations_data}
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"success": False, "message": "Failed to parse recommendations response"}

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return {"success": False, "message": "Failed to generate recommendations"}
