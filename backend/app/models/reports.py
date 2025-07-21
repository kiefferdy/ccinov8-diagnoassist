"""
Reporting Models for DiagnoAssist Backend

Comprehensive reporting and analytics models for:
- Patient reports and summaries
- Episode analytics and outcomes
- Practice management metrics
- Clinical quality indicators
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class ReportType(str, Enum):
    """Types of reports available"""
    PATIENT_SUMMARY = "patient_summary"
    EPISODE_REPORT = "episode_report"
    ENCOUNTER_SUMMARY = "encounter_summary"
    PRACTICE_ANALYTICS = "practice_analytics"
    CLINICAL_QUALITY = "clinical_quality"
    FINANCIAL_SUMMARY = "financial_summary"
    UTILIZATION_REPORT = "utilization_report"
    OUTCOME_ANALYSIS = "outcome_analysis"
    DIAGNOSTIC_TRENDS = "diagnostic_trends"
    MEDICATION_ANALYSIS = "medication_analysis"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"


class ReportPeriod(str, Enum):
    """Report time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportScope(str, Enum):
    """Report scope levels"""
    PATIENT = "patient"
    PROVIDER = "provider"
    DEPARTMENT = "department"
    ORGANIZATION = "organization"
    SYSTEM = "system"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class PatientDemographics(BaseModel):
    """Patient demographics for reporting"""
    age: Optional[int] = None
    age_group: Optional[str] = None  # "pediatric", "adult", "geriatric"
    gender: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    language: Optional[str] = None
    insurance_type: Optional[str] = None
    geographic_region: Optional[str] = None


class ClinicalMetrics(BaseModel):
    """Clinical quality and outcome metrics"""
    total_encounters: int = 0
    completed_encounters: int = 0
    average_encounter_duration: Optional[float] = None  # in minutes
    patient_satisfaction_score: Optional[float] = None  # 1-5 scale
    readmission_rate: Optional[float] = None  # percentage
    medication_adherence_rate: Optional[float] = None  # percentage
    followup_compliance_rate: Optional[float] = None  # percentage
    diagnostic_accuracy_rate: Optional[float] = None  # percentage
    
    # Quality indicators
    preventive_care_completed: int = 0
    chronic_care_plans_active: int = 0
    medication_reconciliation_completed: int = 0
    care_coordination_events: int = 0


class FinancialMetrics(BaseModel):
    """Financial and billing metrics"""
    total_revenue: Optional[float] = None
    average_revenue_per_encounter: Optional[float] = None
    insurance_reimbursement_rate: Optional[float] = None
    collection_rate: Optional[float] = None
    days_in_ar: Optional[float] = None  # Days in accounts receivable
    cost_per_encounter: Optional[float] = None
    profit_margin: Optional[float] = None


class UtilizationMetrics(BaseModel):
    """Resource utilization metrics"""
    provider_productivity: Optional[float] = None  # encounters per hour
    appointment_no_show_rate: Optional[float] = None
    cancellation_rate: Optional[float] = None
    room_utilization_rate: Optional[float] = None
    equipment_utilization_rate: Optional[float] = None
    staff_efficiency_score: Optional[float] = None


class DiagnosticTrend(BaseModel):
    """Diagnostic trend data"""
    diagnosis_code: str
    diagnosis_name: str
    count: int
    percentage: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    previous_period_count: Optional[int] = None
    change_percentage: Optional[float] = None


class MedicationTrend(BaseModel):
    """Medication prescription trend data"""
    medication_name: str
    medication_class: str
    prescription_count: int
    patient_count: int
    average_dosage: Optional[str] = None
    adherence_rate: Optional[float] = None
    adverse_events: int = 0


class OutcomeMetric(BaseModel):
    """Patient outcome metric"""
    metric_name: str
    metric_value: float
    metric_unit: str
    benchmark_value: Optional[float] = None
    performance_status: str  # "above_benchmark", "at_benchmark", "below_benchmark"
    improvement_trend: str  # "improving", "stable", "declining"


class ReportFilter(BaseModel):
    """Filters for report generation"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    patient_ids: Optional[List[str]] = None
    episode_ids: Optional[List[str]] = None
    encounter_ids: Optional[List[str]] = None
    provider_ids: Optional[List[str]] = None
    department_ids: Optional[List[str]] = None
    diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    age_range: Optional[Dict[str, int]] = None  # {"min": 18, "max": 65}
    gender: Optional[str] = None
    insurance_types: Optional[List[str]] = None
    encounter_types: Optional[List[str]] = None
    patient_status: Optional[str] = None  # "active", "inactive", "all"


class ReportSection(BaseModel):
    """Individual report section"""
    section_id: str
    title: str
    description: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    order: int = 0


class PatientSummaryReport(BaseModel):
    """Comprehensive patient summary report"""
    patient_id: str
    patient_name: str
    demographics: PatientDemographics
    medical_history_summary: str
    active_conditions: List[Dict[str, Any]] = Field(default_factory=list)
    current_medications: List[Dict[str, Any]] = Field(default_factory=list)
    recent_encounters: List[Dict[str, Any]] = Field(default_factory=list)
    upcoming_appointments: List[Dict[str, Any]] = Field(default_factory=list)
    care_plans: List[Dict[str, Any]] = Field(default_factory=list)
    lab_results_summary: List[Dict[str, Any]] = Field(default_factory=list)
    vital_signs_trends: List[Dict[str, Any]] = Field(default_factory=list)
    clinical_alerts: List[Dict[str, Any]] = Field(default_factory=list)
    care_team: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Quality metrics
    preventive_care_status: Dict[str, Any] = Field(default_factory=dict)
    chronic_care_management: Dict[str, Any] = Field(default_factory=dict)
    medication_adherence: Optional[float] = None
    
    # Report metadata
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    report_period: Optional[str] = None
    generated_by: str


class EpisodeReport(BaseModel):
    """Episode-based care report"""
    episode_id: str
    patient_id: str
    episode_title: str
    start_date: date
    end_date: Optional[date] = None
    status: str
    category: str
    
    # Episode summary
    chief_complaint: str
    final_diagnosis: Optional[str] = None
    treatment_summary: str
    outcome_description: Optional[str] = None
    
    # Encounter details
    total_encounters: int
    encounter_types_breakdown: Dict[str, int] = Field(default_factory=dict)
    encounters: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Clinical data
    procedures_performed: List[Dict[str, Any]] = Field(default_factory=list)
    medications_prescribed: List[Dict[str, Any]] = Field(default_factory=list)
    lab_tests_ordered: List[Dict[str, Any]] = Field(default_factory=list)
    imaging_studies: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Quality metrics
    episode_duration_days: Optional[int] = None
    follow_up_compliance: Optional[float] = None
    patient_satisfaction: Optional[float] = None
    clinical_outcomes_achieved: List[str] = Field(default_factory=list)
    
    # Financial
    total_cost: Optional[float] = None
    insurance_coverage: Optional[float] = None
    
    # Report metadata
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str


class PracticeAnalyticsReport(BaseModel):
    """Practice-wide analytics report"""
    practice_name: str
    report_period: str
    period_start: date
    period_end: date
    
    # Volume metrics
    total_patients: int
    new_patients: int
    total_encounters: int
    encounters_by_type: Dict[str, int] = Field(default_factory=dict)
    
    # Demographics breakdown
    patient_demographics: PatientDemographics
    age_distribution: Dict[str, int] = Field(default_factory=dict)
    gender_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Clinical metrics
    clinical_metrics: ClinicalMetrics
    top_diagnoses: List[DiagnosticTrend] = Field(default_factory=list)
    top_procedures: List[Dict[str, Any]] = Field(default_factory=list)
    medication_trends: List[MedicationTrend] = Field(default_factory=list)
    
    # Quality indicators
    quality_measures: List[OutcomeMetric] = Field(default_factory=list)
    patient_safety_indicators: List[Dict[str, Any]] = Field(default_factory=list)
    clinical_outcomes: List[OutcomeMetric] = Field(default_factory=list)
    
    # Financial metrics
    financial_metrics: FinancialMetrics
    
    # Utilization metrics
    utilization_metrics: UtilizationMetrics
    
    # Provider performance
    provider_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Trends and insights
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    comparative_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Report metadata
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str


class ReportRequest(BaseModel):
    """Request for report generation"""
    report_type: ReportType
    report_format: ReportFormat = ReportFormat.JSON
    scope: ReportScope = ReportScope.PROVIDER
    filters: ReportFilter = Field(default_factory=ReportFilter)
    include_charts: bool = True
    include_raw_data: bool = False
    email_delivery: bool = False
    email_recipients: List[str] = Field(default_factory=list)
    
    # Scheduling (for recurring reports)
    is_scheduled: bool = False
    schedule_frequency: Optional[ReportPeriod] = None
    schedule_day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    schedule_day_of_month: Optional[int] = None  # 1-31
    
    @validator('email_recipients')
    def validate_emails(cls, v):
        """Validate email addresses"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f"Invalid email address: {email}")
        return v


class ReportModel(BaseModel):
    """Generated report model"""
    id: Optional[str] = None
    report_type: ReportType
    title: str
    description: Optional[str] = None
    
    # Request details
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    filters_applied: ReportFilter
    
    # Generation details
    status: ReportStatus = ReportStatus.PENDING
    generated_at: Optional[datetime] = None
    generation_time_seconds: Optional[float] = None
    
    # Report content
    sections: List[ReportSection] = Field(default_factory=list)
    summary: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Export details
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    download_count: int = 0
    expires_at: Optional[datetime] = None
    
    # Sharing
    shared_with: List[str] = Field(default_factory=list)
    is_public: bool = False
    
    # Error handling
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            ObjectId: str
        }


class ReportTemplate(BaseModel):
    """Report template for standardized reporting"""
    id: Optional[str] = None
    name: str
    description: str
    report_type: ReportType
    
    # Template structure
    sections: List[ReportSection] = Field(default_factory=list)
    default_filters: ReportFilter = Field(default_factory=ReportFilter)
    
    # Configuration
    is_active: bool = True
    is_system_template: bool = False
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    id: str
    title: str
    widget_type: str  # "chart", "metric", "table", "list"
    size: str  # "small", "medium", "large", "full"
    position: Dict[str, int]  # {"row": 1, "col": 1}
    
    # Data configuration
    data_source: str
    refresh_interval: int = 300  # seconds
    filters: Dict[str, Any] = Field(default_factory=dict)
    
    # Visualization
    chart_config: Optional[Dict[str, Any]] = None
    display_options: Dict[str, Any] = Field(default_factory=dict)
    
    # Permissions
    visible_to: List[str] = Field(default_factory=list)
    editable_by: List[str] = Field(default_factory=list)


class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    # Layout
    widgets: List[DashboardWidget] = Field(default_factory=list)
    layout_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Access control
    owner_id: str
    shared_with: List[str] = Field(default_factory=list)
    is_default: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_viewed: Optional[datetime] = None


class AnalyticsQuery(BaseModel):
    """Analytics query for custom reporting"""
    query_name: str
    description: Optional[str] = None
    
    # Query parameters
    aggregations: List[Dict[str, Any]] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    grouping: List[str] = Field(default_factory=list)
    sorting: List[Dict[str, str]] = Field(default_factory=list)
    
    # Output configuration
    limit: Optional[int] = None
    include_totals: bool = True
    
    # Caching
    cache_duration: int = 3600  # seconds
    
    # Permissions
    created_by: str
    allowed_users: List[str] = Field(default_factory=list)


class ReportSchedule(BaseModel):
    """Scheduled report configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    # Report configuration
    report_request: ReportRequest
    
    # Schedule settings
    frequency: ReportPeriod
    start_date: date
    end_date: Optional[date] = None
    
    # Timing
    execution_time: str  # "HH:MM" format
    timezone: str = "UTC"
    
    # Status
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    
    # Error handling
    max_retries: int = 3
    retry_interval: int = 300  # seconds
    last_error: Optional[str] = None
    
    # Notifications
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notification_emails: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)