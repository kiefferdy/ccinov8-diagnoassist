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

# @router.post("/chatbot")
# def chatbot(message: VoiceData):
#
#     print("Generating transcription...")
#
#     try:
#
#         binary_data = base64.b64decode(voice.audio_data)
#         binary_content = BinaryContent(data=binary_data, media_type="audio/wav")
#         result = transcription_agent.run_sync([binary_content])
#
#         print(result.output)
#
#         return {"success": True, "result": result.output}
#
#     except Exception as e:
#         print(f"Error! Could not transcribe audio. {e}")
#         return {"success": False}
