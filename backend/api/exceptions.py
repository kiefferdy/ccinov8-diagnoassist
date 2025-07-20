from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class DiagnoAssistException(HTTPException):
    """Base exception for DiagnoAssist"""
    pass

class PatientNotFoundException(DiagnoAssistException):
    def __init__(self, patient_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

class EpisodeNotFoundException(DiagnoAssistException):
    def __init__(self, episode_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with ID {episode_id} not found"
        )

class FHIRValidationException(DiagnoAssistException):
    def __init__(self, message: str, resource_type: Optional[str] = None):
        detail = f"FHIR validation error: {message}"
        if resource_type:
            detail = f"FHIR {resource_type} validation error: {message}"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class AIServiceException(DiagnoAssistException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {message}"
        )

class InsufficientDataException(DiagnoAssistException):
    def __init__(self, required_fields: list):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient data. Required fields: {', '.join(required_fields)}"
        )
