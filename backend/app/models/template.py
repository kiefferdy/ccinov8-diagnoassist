"""
Template Models for DiagnoAssist Backend

Comprehensive template system for SOAP documentation,
encounter workflows, and clinical decision support.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class TemplateType(str, Enum):
    """Types of templates available"""
    SOAP_COMPLETE = "soap_complete"
    SOAP_SUBJECTIVE = "soap_subjective"
    SOAP_OBJECTIVE = "soap_objective"
    SOAP_ASSESSMENT = "soap_assessment"
    SOAP_PLAN = "soap_plan"
    ENCOUNTER_WORKFLOW = "encounter_workflow"
    CLINICAL_PROTOCOL = "clinical_protocol"
    DIAGNOSTIC_CHECKLIST = "diagnostic_checklist"
    TREATMENT_PLAN = "treatment_plan"


class TemplateScope(str, Enum):
    """Template access scopes"""
    PERSONAL = "personal"        # Created by and visible to user only
    TEAM = "team"               # Shared within user's team/department
    ORGANIZATION = "organization" # Available to entire organization
    PUBLIC = "public"           # Available to all users
    SYSTEM = "system"           # Built-in system templates


class TemplateCategory(str, Enum):
    """Template categories for organization"""
    GENERAL_MEDICINE = "general_medicine"
    EMERGENCY = "emergency"
    PEDIATRICS = "pediatrics"
    INTERNAL_MEDICINE = "internal_medicine"
    SURGERY = "surgery"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    DERMATOLOGY = "dermatology"
    PSYCHIATRY = "psychiatry"
    ORTHOPEDICS = "orthopedics"
    GYNECOLOGY = "gynecology"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    ONCOLOGY = "oncology"
    INFECTIOUS_DISEASE = "infectious_disease"
    CHRONIC_CARE = "chronic_care"
    PREVENTIVE_CARE = "preventive_care"


class FieldType(str, Enum):
    """Types of template fields"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    RANGE = "range"
    VITAL_SIGNS = "vital_signs"
    MEDICATION = "medication"
    DIAGNOSIS = "diagnosis"
    PROCEDURE = "procedure"


class TemplateField(BaseModel):
    """Individual field within a template"""
    id: str = Field(..., description="Unique field identifier")
    label: str = Field(..., description="Human-readable field label")
    field_type: FieldType = Field(..., description="Type of field")
    section: str = Field(..., description="SOAP section (subjective, objective, assessment, plan)")
    required: bool = Field(False, description="Whether field is required")
    default_value: Optional[Union[str, int, float, bool, List[str]]] = Field(None, description="Default field value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    help_text: Optional[str] = Field(None, description="Help text for field")
    validation_rules: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Validation rules")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Options for select/radio fields")
    order: int = Field(0, description="Display order within section")
    width: Optional[str] = Field("full", description="Field width (full, half, third, quarter)")
    
    # Clinical-specific fields
    icd_10_codes: Optional[List[str]] = Field(None, description="Associated ICD-10 codes")
    cpt_codes: Optional[List[str]] = Field(None, description="Associated CPT codes")
    clinical_context: Optional[str] = Field(None, description="Clinical context or specialty")
    
    @validator('validation_rules')
    def validate_rules(cls, v):
        """Validate validation rules structure"""
        allowed_rules = ['min_length', 'max_length', 'min_value', 'max_value', 'pattern', 'custom']
        if v:
            for rule in v.keys():
                if rule not in allowed_rules:
                    raise ValueError(f"Invalid validation rule: {rule}")
        return v


class TemplateSection(BaseModel):
    """Template section containing multiple fields"""
    section: str = Field(..., description="SOAP section name")
    title: str = Field(..., description="Section display title")
    description: Optional[str] = Field(None, description="Section description")
    fields: List[TemplateField] = Field(default_factory=list, description="Fields in this section")
    order: int = Field(0, description="Section display order")
    collapsible: bool = Field(False, description="Whether section can be collapsed")
    expanded_by_default: bool = Field(True, description="Whether section is expanded by default")


class TemplateMetadata(BaseModel):
    """Template metadata and usage statistics"""
    usage_count: int = Field(0, description="Number of times template has been used")
    last_used: Optional[datetime] = Field(None, description="When template was last used")
    rating: Optional[float] = Field(None, description="Average user rating (1-5)")
    rating_count: int = Field(0, description="Number of ratings")
    created_by: str = Field(..., description="User ID who created template")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_by: Optional[str] = Field(None, description="User ID who last updated template")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    version: int = Field(1, description="Template version number")
    
    # Clinical metadata
    clinical_evidence_level: Optional[str] = Field(None, description="Evidence level (A, B, C, D)")
    guideline_source: Optional[str] = Field(None, description="Source of clinical guidelines")
    last_review_date: Optional[datetime] = Field(None, description="Last clinical review date")
    next_review_date: Optional[datetime] = Field(None, description="Next clinical review date")


class TemplateModel(BaseModel):
    """Complete template model"""
    id: Optional[str] = Field(None, description="Template ID")
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    template_type: TemplateType = Field(..., description="Type of template")
    category: TemplateCategory = Field(..., description="Medical specialty category")
    scope: TemplateScope = Field(TemplateScope.PERSONAL, description="Template access scope")
    
    # Template structure
    sections: List[TemplateSection] = Field(..., description="Template sections")
    
    # Organizational fields
    tags: List[str] = Field(default_factory=list, description="Template tags for searching")
    keywords: List[str] = Field(default_factory=list, description="Keywords for full-text search")
    
    # Access control
    owner_id: str = Field(..., description="Owner user ID")
    shared_with_users: List[str] = Field(default_factory=list, description="User IDs with access")
    shared_with_roles: List[str] = Field(default_factory=list, description="Role IDs with access")
    
    # Template state
    is_active: bool = Field(True, description="Whether template is active")
    is_published: bool = Field(False, description="Whether template is published")
    is_system_template: bool = Field(False, description="Whether this is a system template")
    
    # Metadata
    metadata: TemplateMetadata = Field(..., description="Template metadata")
    
    # Clinical workflow integration
    encounter_types: List[str] = Field(default_factory=list, description="Applicable encounter types")
    patient_age_ranges: Optional[Dict[str, int]] = Field(None, description="Applicable age ranges")
    gender_specific: Optional[str] = Field(None, description="Gender specificity (male, female, both)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "name": "General Medicine Consultation",
                "description": "Standard template for general medicine consultations",
                "template_type": "soap_complete",
                "category": "general_medicine",
                "scope": "organization",
                "sections": [
                    {
                        "section": "subjective",
                        "title": "Subjective",
                        "description": "Patient's reported symptoms and history",
                        "fields": [
                            {
                                "id": "chief_complaint",
                                "label": "Chief Complaint",
                                "field_type": "textarea",
                                "section": "subjective",
                                "required": True,
                                "placeholder": "Primary reason for visit",
                                "order": 1
                            }
                        ],
                        "order": 1
                    }
                ],
                "tags": ["general", "consultation", "primary-care"],
                "owner_id": "user123",
                "encounter_types": ["initial", "follow-up"]
            }
        }
    
    @validator('sections')
    def validate_sections(cls, v):
        """Validate template sections"""
        if not v:
            raise ValueError("Template must have at least one section")
        
        section_names = [s.section for s in v]
        if len(section_names) != len(set(section_names)):
            raise ValueError("Section names must be unique")
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate template name"""
        if not v or not v.strip():
            raise ValueError("Template name cannot be empty")
        return v.strip()


class TemplateCreateRequest(BaseModel):
    """Request model for creating templates"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    template_type: TemplateType
    category: TemplateCategory
    scope: TemplateScope = TemplateScope.PERSONAL
    sections: List[TemplateSection]
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    shared_with_users: List[str] = Field(default_factory=list)
    shared_with_roles: List[str] = Field(default_factory=list)
    encounter_types: List[str] = Field(default_factory=list)
    patient_age_ranges: Optional[Dict[str, int]] = None
    gender_specific: Optional[str] = None


class TemplateUpdateRequest(BaseModel):
    """Request model for updating templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    template_type: Optional[TemplateType] = None
    category: Optional[TemplateCategory] = None
    scope: Optional[TemplateScope] = None
    sections: Optional[List[TemplateSection]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    shared_with_users: Optional[List[str]] = None
    shared_with_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    encounter_types: Optional[List[str]] = None
    patient_age_ranges: Optional[Dict[str, int]] = None
    gender_specific: Optional[str] = None


class TemplateSearchRequest(BaseModel):
    """Request model for searching templates"""
    query: Optional[str] = Field(None, description="Search query")
    template_type: Optional[TemplateType] = None
    category: Optional[TemplateCategory] = None
    scope: Optional[TemplateScope] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = None
    is_active: Optional[bool] = True
    is_published: Optional[bool] = None
    encounter_type: Optional[str] = None
    
    # Pagination
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc, desc)")


class TemplateApplicationRequest(BaseModel):
    """Request model for applying template to encounter"""
    template_id: str = Field(..., description="Template ID to apply")
    encounter_id: str = Field(..., description="Encounter ID to apply template to")
    merge_strategy: str = Field("replace", description="Merge strategy (replace, merge, append)")
    field_overrides: Optional[Dict[str, Any]] = Field(None, description="Field value overrides")
    apply_sections: Optional[List[str]] = Field(None, description="Specific sections to apply")


class AppliedTemplateInfo(BaseModel):
    """Information about applied template"""
    template_id: str
    template_name: str
    applied_at: datetime
    applied_by: str
    applied_sections: List[str]
    field_modifications: Optional[Dict[str, Any]] = None


class TemplateUsageStats(BaseModel):
    """Template usage statistics"""
    template_id: str
    usage_count: int
    unique_users: int
    last_used: Optional[datetime]
    avg_rating: Optional[float]
    rating_count: int
    success_rate: float  # Percentage of encounters completed when using this template
    avg_completion_time: Optional[float]  # Average time to complete encounter using template


class TemplateValidationResult(BaseModel):
    """Result of template validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    clinical_quality_score: Optional[float] = None  # 0-100 quality score