"""
Clinical Data Pydantic Schemas
Schemas for clinical notes, evidence, monitoring, and other clinical data types
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

# =============================================================================
# Clinical Notes Schemas
# =============================================================================

class ClinicalNoteCreate(BaseModel):
    """Schema for creating clinical notes"""
    note_type: str = Field(..., regex="^(progress|assessment|plan|discharge|consultation)$")
    content: str = Field(..., min_length=1, max_length=5000)
    author_id: str = Field(..., max_length=100)
    is_private: bool = False
    tags: Optional[List[str]] = Field(default_factory=list)


class ClinicalNoteResponse(ClinicalNoteCreate):
    """Schema for clinical note response"""
    id: UUID
    episode_id: UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Evidence and Refinement Schemas
# =============================================================================

class DiagnosisEvidence(BaseModel):
    """Schema for diagnosis supporting evidence"""
    evidence_type: str = Field(..., regex="^(symptom|sign|test_result|imaging|lab|clinical_reasoning)$")
    description: str = Field(..., min_length=1, max_length=1000)
    supporting_strength: str = Field(..., regex="^(weak|moderate|strong)$")
    source: Optional[str] = Field(None, max_length=200)
    date_observed: Optional[datetime] = None


class DiagnosisRefinement(BaseModel):
    """Schema for refining diagnosis with additional evidence"""
    new_evidence: List[DiagnosisEvidence]
    updated_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    updated_reasoning: Optional[str] = None
    physician_notes: Optional[str] = None


class DiagnosisConfirmation(BaseModel):
    """Schema for confirming final diagnosis"""
    confirmed: bool = True
    confirmation_method: str = Field(..., regex="^(clinical_assessment|test_results|specialist_consult|imaging|response_to_treatment)$")
    confirming_physician: str = Field(..., max_length=200)
    confirmation_notes: Optional[str] = None
    certainty_level: str = Field(..., regex="^(probable|likely|definite)$")


# =============================================================================
# AI Analysis Input Schemas
# =============================================================================

class SymptomAnalysisInput(BaseModel):
    """Schema for AI symptom analysis input"""
    patient_id: UUID
    episode_id: Optional[UUID] = None
    chief_complaint: str = Field(..., min_length=1, max_length=500)
    symptoms: List[str] = Field(..., min_items=1)
    duration: Optional[str] = None
    severity: Optional[str] = Field(None, regex="^(mild|moderate|severe)$")
    patient_demographics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    medical_history: Optional[List[str]] = Field(default_factory=list)
    current_medications: Optional[List[str]] = Field(default_factory=list)
    vital_signs: Optional[Dict[str, Any]] = Field(default_factory=dict)


# =============================================================================
# Treatment Planning Schemas
# =============================================================================

class TreatmentPlanGeneration(BaseModel):
    """Schema for generating treatment plans"""
    patient_id: UUID
    episode_id: UUID
    diagnosis_id: UUID
    patient_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    contraindications: Optional[List[str]] = Field(default_factory=list)
    current_medications: Optional[List[str]] = Field(default_factory=list)
    severity: str = Field(..., regex="^(mild|moderate|severe)$")
    goals: Optional[List[str]] = Field(default_factory=list)


class TreatmentPlanResponse(BaseModel):
    """Schema for treatment plan response"""
    plan_id: UUID
    primary_treatment: Dict[str, Any]
    alternative_treatments: List[Dict[str, Any]]
    monitoring_plan: Dict[str, Any]
    follow_up_schedule: List[Dict[str, Any]]
    patient_education: List[str]
    warning_signs: List[str]
    generated_at: datetime
    confidence_score: float = Field(..., ge=0.0, le=1.0)


# =============================================================================
# Monitoring Schemas
# =============================================================================

class TreatmentMonitoring(BaseModel):
    """Schema for treatment monitoring data"""
    monitoring_type: str = Field(..., regex="^(symptoms|vitals|lab_values|side_effects|compliance|response)$")
    measurement_value: Optional[str] = None
    measurement_unit: Optional[str] = None
    normal_range: Optional[str] = None
    status: str = Field(..., regex="^(normal|abnormal|critical)$")
    notes: Optional[str] = None
    recorded_by: str = Field(..., max_length=200)
    recorded_at: datetime


class TreatmentMonitoringResponse(TreatmentMonitoring):
    """Schema for monitoring response"""
    id: UUID
    treatment_id: UUID
    alert_generated: bool = False
    alert_level: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")


# =============================================================================
# Treatment Lifecycle Schemas
# =============================================================================

class TreatmentStart(BaseModel):
    """Schema for starting treatment"""
    start_date: datetime
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    special_instructions: Optional[str] = None
    patient_consent: bool = True


class TreatmentCompletion(BaseModel):
    """Schema for completing treatment"""
    completion_date: datetime
    completion_reason: str = Field(..., regex="^(completed_course|patient_improved|side_effects|patient_request|ineffective)$")
    outcome_assessment: str = Field(..., regex="^(excellent|good|fair|poor)$")
    patient_response: Optional[str] = None
    follow_up_needed: bool = False


class TreatmentDiscontinuation(BaseModel):
    """Schema for discontinuing treatment"""
    discontinuation_date: datetime
    reason: str = Field(..., regex="^(side_effects|ineffective|patient_request|contraindication|completed)$")
    notes: Optional[str] = None
    alternative_recommended: Optional[str] = None


# =============================================================================
# Safety and Alert Schemas
# =============================================================================

class SafetyAlert(BaseModel):
    """Schema for safety alerts"""
    alert_type: str = Field(..., regex="^(drug_interaction|allergy|contraindication|dose_limit|monitoring_required)$")
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    message: str = Field(..., min_length=1, max_length=500)
    recommendation: Optional[str] = None
    requires_action: bool = False
    auto_generated: bool = True
    generated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Differential Diagnosis and AI Analysis Result Schemas
# =============================================================================

class DifferentialDiagnosis(BaseModel):
    """Schema for differential diagnosis"""
    condition_name: str
    icd10_code: Optional[str] = None
    probability: float = Field(..., ge=0.0, le=1.0)
    supporting_factors: List[str]
    opposing_factors: List[str]
    recommended_tests: Optional[List[str]] = Field(default_factory=list)


class AIAnalysisResult(BaseModel):
    """Schema for AI analysis results"""
    primary_diagnosis: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    differential_diagnoses: List[DifferentialDiagnosis]
    reasoning: str
    recommended_next_steps: List[str]
    red_flags: Optional[List[str]] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Physical Exam Findings Schema (for episode compatibility)
# =============================================================================

class PhysicalExamFindings(BaseModel):
    """Schema for physical examination findings"""
    general_appearance: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    neurological: Optional[str] = None
    gastrointestinal: Optional[str] = None
    musculoskeletal: Optional[str] = None
    skin: Optional[str] = None
    other_findings: Optional[str] = None