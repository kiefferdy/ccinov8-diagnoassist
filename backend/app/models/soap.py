"""
SOAP Documentation Pydantic models for DiagnoAssist Backend
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class SeverityEnum(str, Enum):
    """Severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class UnitOfMeasure(str, Enum):
    """Common units of measure for vitals"""
    MMHG = "mmHg"
    BPM = "bpm"
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    PERCENT = "%"
    MG_DL = "mg/dL"
    KG = "kg"
    LBS = "lbs"
    CM = "cm"
    INCHES = "in"


# Subjective Section Models
class Symptom(BaseModel):
    """Individual symptom description"""
    name: str = Field(..., min_length=1)
    duration: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    description: Optional[str] = None
    associated_factors: List[str] = Field(default_factory=list)
    alleviating_factors: List[str] = Field(default_factory=list)
    aggravating_factors: List[str] = Field(default_factory=list)


class ReviewOfSystems(BaseModel):
    """Review of systems by body system"""
    constitutional: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    gastrointestinal: Optional[str] = None
    genitourinary: Optional[str] = None
    musculoskeletal: Optional[str] = None
    neurological: Optional[str] = None
    psychiatric: Optional[str] = None
    endocrine: Optional[str] = None
    hematologic: Optional[str] = None
    dermatologic: Optional[str] = None
    allergic_immunologic: Optional[str] = None


class SOAPSubjective(BaseModel):
    """Subjective section of SOAP note"""
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    symptoms: List[Symptom] = Field(default_factory=list)
    review_of_systems: Optional[ReviewOfSystems] = None
    social_history: Optional[str] = None
    family_history: Optional[str] = None
    past_medical_history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    last_updated: Optional[datetime] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)


# Objective Section Models
class VitalSigns(BaseModel):
    """Vital signs measurements"""
    temperature: Optional[float] = Field(None, ge=35.0, le=45.0)
    temperature_unit: UnitOfMeasure = UnitOfMeasure.CELSIUS
    systolic_bp: Optional[int] = Field(None, ge=50, le=250)
    diastolic_bp: Optional[int] = Field(None, ge=30, le=150)
    heart_rate: Optional[int] = Field(None, ge=30, le=200)
    respiratory_rate: Optional[int] = Field(None, ge=8, le=40)
    oxygen_saturation: Optional[float] = Field(None, ge=70.0, le=100.0)
    weight: Optional[float] = Field(None, ge=0.5, le=500.0)
    weight_unit: UnitOfMeasure = UnitOfMeasure.KG
    height: Optional[float] = Field(None, ge=30.0, le=250.0)
    height_unit: UnitOfMeasure = UnitOfMeasure.CM
    bmi: Optional[float] = Field(None, ge=10.0, le=60.0)
    recorded_at: Optional[datetime] = None
    
    @validator("bmi", always=True)
    def calculate_bmi(cls, v, values):
        """Auto-calculate BMI if weight and height are provided"""
        if v:  # If BMI is explicitly provided, use it
            return v
        
        weight = values.get("weight")
        height = values.get("height")
        weight_unit = values.get("weight_unit")
        height_unit = values.get("height_unit")
        
        if not (weight and height):
            return None
        
        # Convert to kg and meters for BMI calculation
        weight_kg = weight
        if weight_unit == UnitOfMeasure.LBS:
            weight_kg = weight * 0.453592
        
        height_m = height / 100  # Default cm to m
        if height_unit == UnitOfMeasure.INCHES:
            height_m = height * 0.0254
        
        if height_m > 0:
            bmi = weight_kg / (height_m ** 2)
            return round(bmi, 1)
        
        return None


class PhysicalExam(BaseModel):
    """Physical examination findings"""
    general_appearance: Optional[str] = None
    head_neck: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    abdominal: Optional[str] = None
    extremities: Optional[str] = None
    neurological: Optional[str] = None
    skin: Optional[str] = None
    other_findings: Optional[str] = None


class LabResult(BaseModel):
    """Laboratory test result"""
    test_name: str = Field(..., min_length=1)
    value: Union[str, float, int]
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal: bool = False
    ordered_date: Optional[datetime] = None
    result_date: Optional[datetime] = None
    notes: Optional[str] = None


class SOAPObjective(BaseModel):
    """Objective section of SOAP note"""
    vital_signs: Optional[VitalSigns] = None
    physical_exam: Optional[PhysicalExam] = None
    lab_results: List[LabResult] = Field(default_factory=list)
    imaging_results: Optional[str] = None
    other_tests: Optional[str] = None
    last_updated: Optional[datetime] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)


# Assessment Section Models
class Diagnosis(BaseModel):
    """Individual diagnosis"""
    condition: str = Field(..., min_length=1)
    icd10_code: Optional[str] = None
    certainty: Optional[str] = Field(None, pattern="^(confirmed|probable|possible|rule_out)$")
    severity: Optional[SeverityEnum] = None
    status: Optional[str] = Field(None, pattern="^(active|resolved|chronic|acute)$")
    notes: Optional[str] = None


class DifferentialDiagnosis(BaseModel):
    """Differential diagnosis consideration"""
    condition: str = Field(..., min_length=1)
    probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    supporting_evidence: List[str] = Field(default_factory=list)
    tests_needed: List[str] = Field(default_factory=list)


class SOAPAssessment(BaseModel):
    """Assessment section of SOAP note"""
    primary_diagnosis: Optional[Diagnosis] = None
    secondary_diagnoses: List[Diagnosis] = Field(default_factory=list)
    differential_diagnoses: List[DifferentialDiagnosis] = Field(default_factory=list)
    clinical_impression: Optional[str] = None
    prognosis: Optional[str] = None
    risk_factors: List[str] = Field(default_factory=list)
    last_updated: Optional[datetime] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)


# Plan Section Models
class Medication(BaseModel):
    """Medication prescription"""
    name: str = Field(..., min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    indication: Optional[str] = None
    instructions: Optional[str] = None


class Procedure(BaseModel):
    """Planned procedure"""
    name: str = Field(..., min_length=1)
    indication: Optional[str] = None
    urgency: Optional[str] = Field(None, pattern="^(routine|urgent|emergent)$")
    scheduled_date: Optional[datetime] = None
    provider: Optional[str] = None
    notes: Optional[str] = None


class FollowUp(BaseModel):
    """Follow-up plan"""
    timeframe: str = Field(..., min_length=1)
    purpose: Optional[str] = None
    provider: Optional[str] = None
    instructions: Optional[str] = None


class SOAPPlan(BaseModel):
    """Plan section of SOAP note"""
    medications: List[Medication] = Field(default_factory=list)
    procedures: List[Procedure] = Field(default_factory=list)
    diagnostic_tests: List[str] = Field(default_factory=list)
    follow_up: Optional[FollowUp] = None
    patient_education: Optional[str] = None
    lifestyle_modifications: List[str] = Field(default_factory=list)
    referrals: List[str] = Field(default_factory=list)
    other_interventions: Optional[str] = None
    last_updated: Optional[datetime] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)


class SOAPModel(BaseModel):
    """Complete SOAP documentation model"""
    subjective: Optional[SOAPSubjective] = None
    objective: Optional[SOAPObjective] = None
    assessment: Optional[SOAPAssessment] = None
    plan: Optional[SOAPPlan] = None
    overall_completion_percentage: int = Field(default=0, ge=0, le=100)
    last_updated: Optional[datetime] = None
    
    @validator("overall_completion_percentage", always=True)
    def calculate_overall_completion(cls, v, values):
        """Calculate overall completion percentage"""
        sections = [
            values.get("subjective"),
            values.get("objective"),
            values.get("assessment"),
            values.get("plan")
        ]
        
        completed_sections = [s for s in sections if s and s.completion_percentage > 0]
        if not completed_sections:
            return 0
        
        total_completion = sum(s.completion_percentage for s in completed_sections)
        return round(total_completion / len(sections))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# API Request/Response Models
class SOAPSectionUpdateRequest(BaseModel):
    """Request model for updating individual SOAP sections"""
    section: str = Field(..., pattern="^(subjective|objective|assessment|plan)$")
    data: Dict[str, Any]


class SOAPResponse(BaseModel):
    """Response model for SOAP data"""
    success: bool = True
    data: SOAPModel
    timestamp: datetime = Field(default_factory=datetime.utcnow)