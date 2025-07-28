"""
Encounter Pydantic Schemas - Matches frontend SOAP structure
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# SOAP Section Schemas
class SOAPSubjective(BaseModel):
    """Subjective section of SOAP notes"""
    chiefComplaint: Optional[str] = ""
    hpi: Optional[str] = ""
    ros: Optional[Dict[str, Any]] = {}
    pmh: Optional[str] = ""
    medications: Optional[str] = ""
    allergies: Optional[str] = ""
    socialHistory: Optional[str] = ""
    familyHistory: Optional[str] = ""
    lastUpdated: Optional[datetime] = None
    voiceNotes: Optional[List[Dict[str, Any]]] = []

class VitalSigns(BaseModel):
    """Vital signs data"""
    bloodPressure: Optional[str] = ""
    heartRate: Optional[str] = ""
    temperature: Optional[str] = ""
    respiratoryRate: Optional[str] = ""
    oxygenSaturation: Optional[str] = ""
    height: Optional[str] = ""
    weight: Optional[str] = ""
    bmi: Optional[str] = ""

class PhysicalExam(BaseModel):
    """Physical examination findings"""
    general: Optional[str] = ""
    systems: Optional[Dict[str, str]] = {}
    additionalFindings: Optional[str] = ""

class DiagnosticTest(BaseModel):
    """Diagnostic test information"""
    id: str
    test: str
    urgency: Optional[str] = "routine"
    status: Optional[str] = "ordered"
    orderedAt: Optional[datetime] = None
    notes: Optional[str] = ""

class TestResult(BaseModel):
    """Test result information"""
    id: str
    testId: str
    test: str
    result: str
    abnormal: Optional[bool] = False
    resultedAt: Optional[datetime] = None
    interpretation: Optional[str] = ""
    documents: Optional[List[str]] = []

class DiagnosticTests(BaseModel):
    """Diagnostic tests section"""
    ordered: Optional[List[DiagnosticTest]] = []
    results: Optional[List[TestResult]] = []

class SOAPObjective(BaseModel):
    """Objective section of SOAP notes"""
    vitals: Optional[VitalSigns] = VitalSigns()
    physicalExam: Optional[PhysicalExam] = PhysicalExam()
    diagnosticTests: Optional[DiagnosticTests] = DiagnosticTests()
    lastUpdated: Optional[datetime] = None
    voiceNotes: Optional[List[Dict[str, Any]]] = []

class DifferentialDiagnosis(BaseModel):
    """Differential diagnosis entry"""
    id: str
    diagnosis: str
    icd10: str
    probability: str  # high, moderate, low
    supportingEvidence: Optional[List[str]] = []
    contradictingEvidence: Optional[List[str]] = []

class WorkingDiagnosis(BaseModel):
    """Working diagnosis"""
    diagnosis: Optional[str] = ""
    icd10: Optional[str] = ""
    confidence: Optional[str] = "possible"  # definite, probable, possible
    clinicalReasoning: Optional[str] = ""

class AIConsultation(BaseModel):
    """AI consultation data"""
    queries: Optional[List[Dict[str, Any]]] = []
    insights: Optional[List[Dict[str, Any]]] = []

class SOAPAssessment(BaseModel):
    """Assessment section of SOAP notes"""
    clinicalImpression: Optional[str] = ""
    differentialDiagnosis: Optional[List[DifferentialDiagnosis]] = []
    workingDiagnosis: Optional[WorkingDiagnosis] = WorkingDiagnosis()
    riskAssessment: Optional[str] = ""
    lastUpdated: Optional[datetime] = None
    aiConsultation: Optional[AIConsultation] = AIConsultation()

class Medication(BaseModel):
    """Medication prescription"""
    id: str
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = ""
    prescribed: Optional[bool] = True

class Procedure(BaseModel):
    """Medical procedure"""
    id: str
    name: str
    type: str
    urgency: Optional[str] = "routine"
    status: Optional[str] = "planned"
    scheduledFor: Optional[datetime] = None
    notes: Optional[str] = ""

class Referral(BaseModel):
    """Referral to specialist"""
    id: str
    specialty: str
    provider: Optional[str] = ""
    urgency: Optional[str] = "routine"
    reason: str
    notes: Optional[str] = ""

class FollowUp(BaseModel):
    """Follow-up instructions"""
    timeframe: Optional[str] = ""
    reason: Optional[str] = ""
    instructions: Optional[str] = ""

class PatientEducation(BaseModel):
    """Patient education item"""
    topic: str
    materials: Optional[str] = ""
    discussed: Optional[bool] = False

class SOAPPlan(BaseModel):
    """Plan section of SOAP notes"""
    medications: Optional[List[Medication]] = []
    procedures: Optional[List[Procedure]] = []
    referrals: Optional[List[Referral]] = []
    followUp: Optional[FollowUp] = FollowUp()
    patientEducation: Optional[List[PatientEducation]] = []
    activityRestrictions: Optional[str] = ""
    dietRecommendations: Optional[str] = ""
    lastUpdated: Optional[datetime] = None

class Provider(BaseModel):
    """Provider information"""
    id: str
    name: str
    role: str

# Main Encounter Schemas
class EncounterBase(BaseModel):
    """Base encounter fields"""
    episode_id: UUID
    patient_id: UUID
    type: str = "initial"
    provider: Optional[Provider] = None
    soap_subjective: Optional[SOAPSubjective] = SOAPSubjective()
    soap_objective: Optional[SOAPObjective] = SOAPObjective()
    soap_assessment: Optional[SOAPAssessment] = SOAPAssessment()
    soap_plan: Optional[SOAPPlan] = SOAPPlan()
    documents: Optional[List[str]] = []
    amendments: Optional[List[Dict[str, Any]]] = []
    
    @validator('type')
    def validate_encounter_type(cls, v):
        valid_types = ['initial', 'follow-up', 'urgent', 'telemedicine', 'phone', 'lab-review']
        if v not in valid_types:
            return 'initial'
        return v

class EncounterCreate(EncounterBase):
    """Schema for creating an encounter"""
    pass

class EncounterUpdate(BaseModel):
    """Schema for updating an encounter"""
    type: Optional[str] = None
    provider: Optional[Provider] = None
    soap_subjective: Optional[SOAPSubjective] = None
    soap_objective: Optional[SOAPObjective] = None
    soap_assessment: Optional[SOAPAssessment] = None
    soap_plan: Optional[SOAPPlan] = None
    documents: Optional[List[str]] = None
    amendments: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None

class SOAPSectionUpdate(BaseModel):
    """Schema for updating individual SOAP sections"""
    section: str  # subjective, objective, assessment, plan
    data: Dict[str, Any]
    
    @validator('section')
    def validate_section(cls, v):
        valid_sections = ['subjective', 'objective', 'assessment', 'plan']
        if v not in valid_sections:
            raise ValueError(f'Section must be one of: {valid_sections}')
        return v

class EncounterResponse(EncounterBase):
    """Schema for encounter responses"""
    id: UUID
    date: datetime
    status: str
    provider_id: Optional[str] = None
    provider_name: Optional[str] = None
    provider_role: Optional[str] = None
    signed_at: Optional[datetime] = None
    signed_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = "system"
    completion_percentage: Optional[int] = 0
    is_signed: Optional[bool] = False
    chief_complaint: Optional[str] = ""
    
    class Config:
        from_attributes = True

class EncounterListResponse(BaseModel):
    """Schema for paginated encounter list"""
    data: List[EncounterResponse]
    total: int
    page: int = 1
    size: int = 20

class EncounterSignRequest(BaseModel):
    """Schema for signing an encounter"""
    provider_name: str

class EncounterStats(BaseModel):
    """Schema for encounter statistics"""
    total: int
    draft: int
    signed: int
    lastVisit: Optional[datetime] = None