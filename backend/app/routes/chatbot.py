from dotenv import load_dotenv
from fastapi import APIRouter
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



