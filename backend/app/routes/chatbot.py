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

load_dotenv()

router = APIRouter()

system_prompt = """
You are a medical assistant chatbot designed to assist doctors during patient consultations. 
You have access to relevant context, including the current encounter, previous encounters within the same episode, and the patient’s overall medical record. 
Doctors may also upload additional files to provide more context. Use all available information to answer questions clearly, accurately, and with clinical relevance. 
When unsure, indicate your uncertainty and suggest what additional information may help. 
Always prioritize patient safety, respect privacy, and support the doctor’s clinical decision-making process.
"""

class ChatRequest(BaseModel):
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

def serialize_for_api(pydantic_ai_messages: List) -> str:
    return ModelMessagesTypeAdapter.dump_json(pydantic_ai_messages).decode('utf-8')

@router.post("/chat")
def post_chat(prompt: ChatRequest):

    converted_message_history = convert_custom_to_pydantic_ai(prompt.message_history)

    try:
        result = chat_agent.run_sync(prompt.message, message_history=converted_message_history)
        return {"success": True, "message": result.output}

    except Exception as e:
        print(f"Error! Could not send chat message. {e}")
        return {"success": False, "message": "Error"}

@router.get("/chat")
def test_chat(db: Session = Depends(get_db)):
    patient_repo = PatientRepository(db)
    episode_repo = EpisodeRepository(db)  # Initialize episode repository
    
    pat_id = "f060b0cd-3a97-4d16-8e43-e46fb7bec1bd"
    episode_id = "26e74c3c-0e6e-49c0-818b-d224fdd91c5f"
    
    try:
        # Fetch patient
        patient = patient_repo.get_by_id(pat_id)
        if not patient:
            return {"success": False, "message": "Patient not found"}
        
        # Fetch episode
        episode = episode_repo.get_by_id(episode_id)
        if not episode:
            return {"success": False, "message": "Episode not found"}

        for key, value in vars(episode).items():
            print(f"{key}: {value}")
        
        # Get encounters for this episode (assuming episode has encounters relationship)
        encounters = []
        if hasattr(episode, 'encounters') and episode.encounters:
            for encounter in episode.encounters:
                encounters.append({
                    "id": str(encounter.id),
                    "encounter_type": encounter.encounter_type if hasattr(encounter, 'encounter_type') else None,
                    "status": encounter.status if hasattr(encounter, 'status') else None,
                    "start_time": encounter.start_time.isoformat() if hasattr(encounter, 'start_time') and encounter.start_time else None,
                    "end_time": encounter.end_time.isoformat() if hasattr(encounter, 'end_time') and encounter.end_time else None,
                    "chief_complaint": encounter.chief_complaint if hasattr(encounter, 'chief_complaint') else None,
                    "notes": encounter.notes if hasattr(encounter, 'notes') else None
                })
        
        return {
            "success": True,
            "patient": {
                "id": str(patient.id),
                "name": f"{patient.first_name} {patient.last_name}",
                "mrn": patient.medical_record_number,
                "status": patient.status,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender,
                "allergies": patient.allergies,
                "medical_history": patient.medical_history
            },
            "episode": {
                "id": str(episode.id),
                "episode_type": episode.episode_type if hasattr(episode, 'episode_type') else None,
                "status": episode.status if hasattr(episode, 'status') else None,
                "start_date": episode.start_date.isoformat() if hasattr(episode, 'start_date') and episode.start_date else None,
                "end_date": episode.end_date.isoformat() if hasattr(episode, 'end_date') and episode.end_date else None,
                "description": episode.description if hasattr(episode, 'description') else None,
                "priority": episode.priority if hasattr(episode, 'priority') else None
            },
            "encounters": encounters,
            "context": {
                "total_encounters": len(encounters),
                "episode_patient_match": str(episode.patient_id) == pat_id if hasattr(episode, 'patient_id') else "unknown"
            }
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}
