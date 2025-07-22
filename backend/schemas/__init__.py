"""
Pydantic Schemas for DiagnoAssist API
Request/Response validation and serialization
"""

from .patient import (
    PatientBase,
    PatientCreate, 
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)

from .episode import (
    EpisodeBase,
    EpisodeCreate,
    EpisodeUpdate, 
    EpisodeResponse,
    EpisodeListResponse,
    VitalSigns,
    PhysicalExamFindings
)

from .diagnosis import (
    DiagnosisBase,
    DiagnosisCreate,
    DiagnosisUpdate,
    DiagnosisResponse, 
    DiagnosisListResponse,
    DifferentialDiagnosis,
    AIAnalysisResult
)

from .treatment import (
    TreatmentBase,
    TreatmentCreate,
    TreatmentUpdate,
    TreatmentResponse,
    TreatmentListResponse,
    MedicationTreatment,
    NonPharmacologicalTreatment
)

from .fhir_resource import (
    FHIRResourceBase,
    FHIRResourceCreate,
    FHIRResourceResponse,
    FHIRResourceListResponse
)

from .common import (
    StatusResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
    HealthCheckResponse
)

from .clinical_data import (
    # Clinical notes
    ClinicalNoteCreate,
    ClinicalNoteResponse,
    
    # Evidence and refinement
    DiagnosisEvidence,
    DiagnosisRefinement, 
    DiagnosisConfirmation,
    
    # AI analysis
    SymptomAnalysisInput,
    
    # Treatment planning
    TreatmentPlanGeneration,
    TreatmentPlanResponse,
    
    # Monitoring
    TreatmentMonitoring,
    TreatmentMonitoringResponse,
    
    # Treatment lifecycle
    TreatmentStart,
    TreatmentCompletion,
    TreatmentDiscontinuation,
    
    # Safety
    SafetyAlert
)

__all__ = [
    # Patient schemas
    "PatientBase", "PatientCreate", "PatientUpdate", "PatientResponse", "PatientListResponse",
    
    # Episode schemas  
    "EpisodeBase", "EpisodeCreate", "EpisodeUpdate", "EpisodeResponse", "EpisodeListResponse",
    "VitalSigns", "PhysicalExamFindings",
    
    # Diagnosis schemas
    "DiagnosisBase", "DiagnosisCreate", "DiagnosisUpdate", "DiagnosisResponse", 
    "DiagnosisListResponse", "DifferentialDiagnosis", "AIAnalysisResult",
    
    # Treatment schemas
    "TreatmentBase", "TreatmentCreate", "TreatmentUpdate", "TreatmentResponse",
    "TreatmentListResponse", "MedicationTreatment", "NonPharmacologicalTreatment",
    
    # FHIR schemas
    "FHIRResourceBase", "FHIRResourceCreate", "FHIRResourceResponse", "FHIRResourceListResponse",
    
    # Common schemas
    "StatusResponse", "ErrorResponse", "PaginationParams", "PaginatedResponse", "HealthCheckResponse",
    
    # Clinical data schemas
    "ClinicalNoteCreate", "ClinicalNoteResponse",
    "DiagnosisEvidence", "DiagnosisRefinement", "DiagnosisConfirmation",
    "SymptomAnalysisInput",
    "TreatmentPlanGeneration", "TreatmentPlanResponse",
    "TreatmentMonitoring", "TreatmentMonitoringResponse",
    "TreatmentStart", "TreatmentCompletion", "TreatmentDiscontinuation",
    "SafetyAlert"
]