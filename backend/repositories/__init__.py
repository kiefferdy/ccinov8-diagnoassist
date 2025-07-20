"""
Repository layer for DiagnoAssist
Handles all data access operations with clean abstractions
"""

from .base import BaseRepository
from .patient_repository import PatientRepository
from .episode_repository import EpisodeRepository
from .diagnosis_repository import DiagnosisRepository
from .treatment_repository import TreatmentRepository
from .fhir_patient_repository import FHIRPatientRepository
from .fhir_encounter_repository import FHIREncounterRepository
from .fhir_observation_repository import FHIRObservationRepository
from .audit_repository import AuditRepository

__all__ = [
    "BaseRepository",
    "PatientRepository", 
    "EpisodeRepository",
    "DiagnosisRepository",
    "TreatmentRepository",
    "FHIRPatientRepository",
    "FHIREncounterRepository", 
    "FHIRObservationRepository",
    "AuditRepository"
]