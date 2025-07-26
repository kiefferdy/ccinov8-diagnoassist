"""
Template Initialization for DiagnoAssist Backend

Creates system templates and initializes template service
"""
import logging
from typing import List
from datetime import datetime

from app.models.template import (
    TemplateModel, TemplateCreateRequest, TemplateSection, TemplateField,
    TemplateType, TemplateCategory, TemplateScope, FieldType, TemplateMetadata
)
from app.models.auth import UserModel, UserRole
from app.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class TemplateInitializer:
    """Initializes system templates"""
    
    def __init__(self, template_service: TemplateService):
        self.template_service = template_service
    
    async def initialize_system_templates(self) -> List[TemplateModel]:
        """
        Initialize system templates
        
        Returns:
            List of created system templates
        """
        try:
            # Create system user for templates
            system_user = UserModel(
                id="system",
                email="system@diagnoassist.com",
                name="System",
                role=UserRoleEnum.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            templates = []
            
            # Create basic SOAP templates
            templates.append(await self._create_general_medicine_template(system_user))
            templates.append(await self._create_emergency_template(system_user))
            templates.append(await self._create_pediatric_template(system_user))
            templates.append(await self._create_cardiology_template(system_user))
            templates.append(await self._create_mental_health_template(system_user))
            
            logger.info(f"Created {len(templates)} system templates")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to initialize system templates: {e}")
            raise
    
    async def _create_general_medicine_template(self, user: UserModel) -> TemplateModel:
        """Create general medicine consultation template"""
        
        sections = [
            TemplateSection(
                section="subjective",
                title="Subjective",
                description="Patient's reported symptoms and history",
                fields=[
                    TemplateField(
                        id="chief_complaint",
                        label="Chief Complaint",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        placeholder="Primary reason for visit",
                        help_text="Main symptom or concern that brought the patient in",
                        order=1,
                        width="full"
                    ),
                    TemplateField(
                        id="history_present_illness",
                        label="History of Present Illness",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        placeholder="Detailed description of current illness",
                        help_text="Onset, duration, characteristics, associated symptoms",
                        order=2,
                        width="full"
                    ),
                    TemplateField(
                        id="review_of_systems",
                        label="Review of Systems",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Systematic review of body systems",
                        order=3,
                        width="full"
                    ),
                    TemplateField(
                        id="past_medical_history",
                        label="Past Medical History",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Previous illnesses, surgeries, hospitalizations",
                        order=4,
                        width="half"
                    ),
                    TemplateField(
                        id="medications",
                        label="Current Medications",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Current prescription and OTC medications",
                        order=5,
                        width="half"
                    ),
                    TemplateField(
                        id="allergies",
                        label="Allergies",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Drug allergies and reactions",
                        order=6,
                        width="half"
                    ),
                    TemplateField(
                        id="social_history",
                        label="Social History",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Smoking, alcohol, occupation, living situation",
                        order=7,
                        width="half"
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Objective",
                description="Physical examination findings and vital signs",
                fields=[
                    TemplateField(
                        id="vital_signs",
                        label="Vital Signs",
                        field_type=FieldType.VITAL_SIGNS,
                        section="objective",
                        required=True,
                        order=1,
                        width="full"
                    ),
                    TemplateField(
                        id="general_appearance",
                        label="General Appearance",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Overall appearance, distress level, alertness",
                        order=2,
                        width="full"
                    ),
                    TemplateField(
                        id="physical_exam",
                        label="Physical Examination",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Systematic physical examination findings",
                        order=3,
                        width="full"
                    ),
                    TemplateField(
                        id="diagnostic_tests",
                        label="Diagnostic Tests",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Lab results, imaging, other diagnostic tests",
                        order=4,
                        width="full"
                    )
                ],
                order=2
            ),
            TemplateSection(
                section="assessment",
                title="Assessment",
                description="Clinical impression and differential diagnosis",
                fields=[
                    TemplateField(
                        id="primary_diagnosis",
                        label="Primary Diagnosis",
                        field_type=FieldType.DIAGNOSIS,
                        section="assessment",
                        required=True,
                        placeholder="Most likely diagnosis with ICD-10 code",
                        order=1,
                        width="full"
                    ),
                    TemplateField(
                        id="differential_diagnosis",
                        label="Differential Diagnosis",
                        field_type=FieldType.TEXTAREA,
                        section="assessment",
                        placeholder="Alternative diagnoses to consider",
                        order=2,
                        width="full"
                    ),
                    TemplateField(
                        id="clinical_impression",
                        label="Clinical Impression",
                        field_type=FieldType.TEXTAREA,
                        section="assessment",
                        placeholder="Overall clinical assessment and reasoning",
                        order=3,
                        width="full"
                    )
                ],
                order=3
            ),
            TemplateSection(
                section="plan",
                title="Plan",
                description="Treatment plan and follow-up",
                fields=[
                    TemplateField(
                        id="treatment_plan",
                        label="Treatment Plan",
                        field_type=FieldType.TEXTAREA,
                        section="plan",
                        required=True,
                        placeholder="Medications, procedures, interventions",
                        order=1,
                        width="full"
                    ),
                    TemplateField(
                        id="patient_education",
                        label="Patient Education",
                        field_type=FieldType.TEXTAREA,
                        section="plan",
                        placeholder="Instructions and education provided to patient",
                        order=2,
                        width="full"
                    ),
                    TemplateField(
                        id="follow_up",
                        label="Follow-up",
                        field_type=FieldType.TEXTAREA,
                        section="plan",
                        placeholder="Follow-up appointments and timeline",
                        order=3,
                        width="half"
                    ),
                    TemplateField(
                        id="return_precautions",
                        label="Return Precautions",
                        field_type=FieldType.TEXTAREA,
                        section="plan",
                        placeholder="When to return for care",
                        order=4,
                        width="half"
                    )
                ],
                order=4
            )
        ]
        
        template_request = TemplateCreateRequest(
            name="General Medicine Consultation",
            description="Comprehensive template for general medicine consultations and primary care visits",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.GENERAL_MEDICINE,
            scope=TemplateScope.SYSTEM,
            sections=sections,
            tags=["general", "primary-care", "consultation", "comprehensive"],
            encounter_types=["initial", "follow-up", "annual", "urgent"]
        )
        
        return await self.template_service.create_template(template_request, user)
    
    async def _create_emergency_template(self, user: UserModel) -> TemplateModel:
        """Create emergency department template"""
        
        sections = [
            TemplateSection(
                section="subjective",
                title="Chief Complaint & HPI",
                description="Emergency presentation details",
                fields=[
                    TemplateField(
                        id="chief_complaint",
                        label="Chief Complaint",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        placeholder="Primary emergency complaint",
                        order=1
                    ),
                    TemplateField(
                        id="onset_time",
                        label="Time of Onset",
                        field_type=FieldType.DATETIME,
                        section="subjective",
                        required=True,
                        order=2
                    ),
                    TemplateField(
                        id="pain_scale",
                        label="Pain Scale (0-10)",
                        field_type=FieldType.RANGE,
                        section="subjective",
                        validation_rules={"min_value": 0, "max_value": 10},
                        order=3
                    ),
                    TemplateField(
                        id="associated_symptoms",
                        label="Associated Symptoms",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Related symptoms and timeline",
                        order=4
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Emergency Assessment",
                description="Vital signs and focused examination",
                fields=[
                    TemplateField(
                        id="triage_category",
                        label="Triage Category",
                        field_type=FieldType.SELECT,
                        section="objective",
                        required=True,
                        options=[
                            {"value": "1", "label": "Resuscitation (Red)"},
                            {"value": "2", "label": "Emergent (Orange)"},
                            {"value": "3", "label": "Urgent (Yellow)"},
                            {"value": "4", "label": "Less Urgent (Green)"},
                            {"value": "5", "label": "Non-Urgent (Blue)"}
                        ],
                        order=1
                    ),
                    TemplateField(
                        id="vital_signs",
                        label="Vital Signs",
                        field_type=FieldType.VITAL_SIGNS,
                        section="objective",
                        required=True,
                        order=2
                    ),
                    TemplateField(
                        id="focused_exam",
                        label="Focused Physical Exam",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="System-specific examination",
                        order=3
                    )
                ],
                order=2
            ),
            TemplateSection(
                section="assessment",
                title="Emergency Diagnosis",
                description="Working diagnosis and severity",
                fields=[
                    TemplateField(
                        id="working_diagnosis",
                        label="Working Diagnosis",
                        field_type=FieldType.DIAGNOSIS,
                        section="assessment",
                        required=True,
                        order=1
                    ),
                    TemplateField(
                        id="severity_assessment",
                        label="Severity Assessment",
                        field_type=FieldType.SELECT,
                        section="assessment",
                        options=[
                            {"value": "critical", "label": "Critical"},
                            {"value": "severe", "label": "Severe"},
                            {"value": "moderate", "label": "Moderate"},
                            {"value": "mild", "label": "Mild"}
                        ],
                        order=2
                    )
                ],
                order=3
            ),
            TemplateSection(
                section="plan",
                title="Emergency Management",
                description="Immediate treatment and disposition",
                fields=[
                    TemplateField(
                        id="immediate_treatment",
                        label="Immediate Treatment",
                        field_type=FieldType.TEXTAREA,
                        section="plan",
                        required=True,
                        placeholder="Emergency interventions performed",
                        order=1
                    ),
                    TemplateField(
                        id="disposition",
                        label="Disposition",
                        field_type=FieldType.SELECT,
                        section="plan",
                        required=True,
                        options=[
                            {"value": "discharge", "label": "Discharge Home"},
                            {"value": "admit", "label": "Admit to Hospital"},
                            {"value": "icu", "label": "ICU Admission"},
                            {"value": "transfer", "label": "Transfer to Another Facility"},
                            {"value": "observation", "label": "Observation Unit"}
                        ],
                        order=2
                    )
                ],
                order=4
            )
        ]
        
        template_request = TemplateCreateRequest(
            name="Emergency Department Assessment",
            description="Template for emergency department evaluations and acute care",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.EMERGENCY,
            scope=TemplateScope.SYSTEM,
            sections=sections,
            tags=["emergency", "ED", "acute", "triage"],
            encounter_types=["emergency", "urgent"]
        )
        
        return await self.template_service.create_template(template_request, user)
    
    async def _create_pediatric_template(self, user: UserModel) -> TemplateModel:
        """Create pediatric consultation template"""
        
        sections = [
            TemplateSection(
                section="subjective",
                title="Pediatric History",
                description="Child-specific history and development",
                fields=[
                    TemplateField(
                        id="chief_complaint",
                        label="Chief Complaint",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        placeholder="Primary concern (from parent/guardian)",
                        order=1
                    ),
                    TemplateField(
                        id="birth_history",
                        label="Birth History",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Pregnancy, delivery, birth weight, complications",
                        order=2
                    ),
                    TemplateField(
                        id="developmental_milestones",
                        label="Developmental Milestones",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Motor, language, social development",
                        order=3
                    ),
                    TemplateField(
                        id="immunization_status",
                        label="Immunization Status",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Current vaccination status",
                        order=4
                    ),
                    TemplateField(
                        id="feeding_history",
                        label="Feeding History",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Breastfeeding, formula, solid foods",
                        order=5
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Pediatric Examination",
                description="Age-appropriate physical examination",
                fields=[
                    TemplateField(
                        id="growth_parameters",
                        label="Growth Parameters",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        required=True,
                        placeholder="Height, weight, head circumference, percentiles",
                        order=1
                    ),
                    TemplateField(
                        id="vital_signs",
                        label="Vital Signs",
                        field_type=FieldType.VITAL_SIGNS,
                        section="objective",
                        required=True,
                        order=2
                    ),
                    TemplateField(
                        id="general_appearance",
                        label="General Appearance",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Activity level, interaction, distress",
                        order=3
                    ),
                    TemplateField(
                        id="systematic_exam",
                        label="Systematic Examination",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Head-to-toe examination findings",
                        order=4
                    )
                ],
                order=2
            )
        ]
        
        template_request = TemplateCreateRequest(
            name="Pediatric Consultation",
            description="Comprehensive template for pediatric evaluations and well-child visits",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.PEDIATRICS,
            scope=TemplateScope.SYSTEM,
            sections=sections,
            tags=["pediatric", "children", "development", "well-child"],
            encounter_types=["well-child", "sick-visit", "consultation"],
            patient_age_ranges={"min_age": 0, "max_age": 18}
        )
        
        return await self.template_service.create_template(template_request, user)
    
    async def _create_cardiology_template(self, user: UserModel) -> TemplateModel:
        """Create cardiology consultation template"""
        
        sections = [
            TemplateSection(
                section="subjective",
                title="Cardiac History",
                description="Cardiovascular symptoms and risk factors",
                fields=[
                    TemplateField(
                        id="chest_pain_character",
                        label="Chest Pain Character",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Quality, location, radiation, triggers",
                        order=1
                    ),
                    TemplateField(
                        id="dyspnea_assessment",
                        label="Dyspnea Assessment",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Exertional, orthopnea, PND",
                        order=2
                    ),
                    TemplateField(
                        id="cardiac_risk_factors",
                        label="Cardiac Risk Factors",
                        field_type=FieldType.MULTISELECT,
                        section="subjective",
                        options=[
                            {"value": "diabetes", "label": "Diabetes"},
                            {"value": "hypertension", "label": "Hypertension"},
                            {"value": "smoking", "label": "Smoking"},
                            {"value": "family_history", "label": "Family History"},
                            {"value": "hyperlipidemia", "label": "Hyperlipidemia"},
                            {"value": "obesity", "label": "Obesity"}
                        ],
                        order=3
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Cardiovascular Examination",
                description="Focused cardiac assessment",
                fields=[
                    TemplateField(
                        id="blood_pressure",
                        label="Blood Pressure",
                        field_type=FieldType.TEXT,
                        section="objective",
                        required=True,
                        placeholder="Systolic/Diastolic (both arms if indicated)",
                        order=1
                    ),
                    TemplateField(
                        id="heart_rate_rhythm",
                        label="Heart Rate and Rhythm",
                        field_type=FieldType.TEXT,
                        section="objective",
                        required=True,
                        placeholder="Rate, regularity, extra sounds",
                        order=2
                    ),
                    TemplateField(
                        id="cardiac_exam",
                        label="Cardiac Examination",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Heart sounds, murmurs, gallops, rubs",
                        order=3
                    ),
                    TemplateField(
                        id="peripheral_vascular",
                        label="Peripheral Vascular",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Pulses, edema, bruits",
                        order=4
                    )
                ],
                order=2
            )
        ]
        
        template_request = TemplateCreateRequest(
            name="Cardiology Consultation",
            description="Specialized template for cardiovascular evaluations",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.CARDIOLOGY,
            scope=TemplateScope.SYSTEM,
            sections=sections,
            tags=["cardiology", "heart", "cardiovascular", "specialist"],
            encounter_types=["consultation", "follow-up"]
        )
        
        return await self.template_service.create_template(template_request, user)
    
    async def _create_mental_health_template(self, user: UserModel) -> TemplateModel:
        """Create mental health assessment template"""
        
        sections = [
            TemplateSection(
                section="subjective",
                title="Mental Health History",
                description="Psychiatric symptoms and psychosocial factors",
                fields=[
                    TemplateField(
                        id="presenting_concern",
                        label="Presenting Concern",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        required=True,
                        placeholder="Current mental health concerns",
                        order=1
                    ),
                    TemplateField(
                        id="mood_assessment",
                        label="Mood Assessment",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Mood, anxiety, sleep, appetite",
                        order=2
                    ),
                    TemplateField(
                        id="psychiatric_history",
                        label="Psychiatric History",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Previous diagnoses, hospitalizations, treatments",
                        order=3
                    ),
                    TemplateField(
                        id="substance_use",
                        label="Substance Use",
                        field_type=FieldType.TEXTAREA,
                        section="subjective",
                        placeholder="Alcohol, drugs, tobacco use patterns",
                        order=4
                    )
                ],
                order=1
            ),
            TemplateSection(
                section="objective",
                title="Mental Status Exam",
                description="Systematic mental status assessment",
                fields=[
                    TemplateField(
                        id="appearance_behavior",
                        label="Appearance & Behavior",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Appearance, psychomotor activity, cooperation",
                        order=1
                    ),
                    TemplateField(
                        id="mood_affect",
                        label="Mood & Affect",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Mood state, affect quality, appropriateness",
                        order=2
                    ),
                    TemplateField(
                        id="thought_process",
                        label="Thought Process",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Thought organization, associations",
                        order=3
                    ),
                    TemplateField(
                        id="cognitive_assessment",
                        label="Cognitive Assessment",
                        field_type=FieldType.TEXTAREA,
                        section="objective",
                        placeholder="Orientation, attention, memory",
                        order=4
                    )
                ],
                order=2
            )
        ]
        
        template_request = TemplateCreateRequest(
            name="Mental Health Assessment",
            description="Comprehensive template for psychiatric evaluations",
            template_type=TemplateType.SOAP_COMPLETE,
            category=TemplateCategory.PSYCHIATRY,
            scope=TemplateScope.SYSTEM,
            sections=sections,
            tags=["mental-health", "psychiatry", "psychology", "behavioral"],
            encounter_types=["initial", "follow-up", "crisis"]
        )
        
        return await self.template_service.create_template(template_request, user)


# Initialize template service function
async def initialize_template_service_with_dependencies():
    """Initialize template service with all dependencies"""
    try:
        from app.core.database import get_database
        from app.repositories.template_repository import TemplateRepository
        from app.services.encounter_service import encounter_service
        from app.services.template_service import TemplateService
        
        # Get database
        db = await get_database()
        
        # Create repository
        template_repository = TemplateRepository(db.templates)
        
        # Create service
        template_service_instance = TemplateService(template_repository, encounter_service)
        
        # Set global service instance
        import app.services.template_service
        app.services.template_service.template_service = template_service_instance
        
        # Initialize system templates
        initializer = TemplateInitializer(template_service_instance)
        system_templates = await initializer.initialize_system_templates()
        
        logger.info(f"Template service initialized with {len(system_templates)} system templates")
        return template_service_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize template service: {e}")
        raise