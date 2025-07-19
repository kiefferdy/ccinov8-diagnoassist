from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
import base64
import io
from typing import Optional, Annotated
from typing_extensions import TypedDict
from pydantic_ai import Agent, BinaryContent

load_dotenv()

router = APIRouter()

system_prompt = """
You are a clinical documentation assistant. Given a short audio transcript from a physician, extract structured information to auto-fill a SOAP note. Include the following fields: the chief complaint, a summary of the history of present illness (HPI) including symptoms, duration, and relevant exam findings, vital signs such as blood pressure, temperature, pulse, and respiratory rate, the physician’s clinical impression or diagnosis, and the planned treatments, medications, or recommendations. Focus on accuracy and clarity, capturing all essential details mentioned in the transcript. For any unknown data, input 'Unknown'.
"""

class Transcription(TypedDict):
    # Subjective
    chiefComplaint: str
    HPI: str

    # Objective - Vitals
    bloodPressure: str
    temperature: float
    pulse: int
    respiratoryRate: int

    # Assessment
    clinicalImpression: str

    # Plan
    treatments: str
    
class VoiceData(BaseModel):
    audio_data: str

transcription_agent = Agent(  
    'google-gla:gemini-2.0-flash',
    system_prompt=system_prompt,
    retries=3,
    output_type=Transcription
)

@router.post("/transcribe")
def transcribe(voice: VoiceData):

    print("Generating transcription...")

    try:

        binary_data = base64.b64decode(voice.audio_data)
        binary_content = BinaryContent(data=binary_data, media_type="audio/wav")
        result = transcription_agent.run_sync([binary_content])

        print(result.output)

        return {"success": True, "result": result.output}

    except Exception as e:
        print(f"Error! Could not transcribe audio. {e}")
        return {"success": False}
