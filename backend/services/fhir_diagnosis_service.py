from typing import List, Optional, Dict, Any
from repositories.fhir_patient_repository import FHIRPatientRepository
from repositories.fhir_encounter_repository import FHIREncounterRepository
from services.ai_service import AIService
from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport
from fhir.resources.condition import Condition as FHIRCondition
from fhir.models.diagnostic_report import DiagnosticReportFHIRModel
from fhir.models.condition import ConditionFHIRModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FHIRDiagnosisService:
    """Service for FHIR diagnosis and diagnostic reporting"""
    
    def __init__(
        self,
        fhir_patient_repo: FHIRPatientRepository,
        fhir_encounter_repo: FHIREncounterRepository,
        ai_service: AIService
    ):
        self.fhir_patient_repo = fhir_patient_repo
        self.fhir_encounter_repo = fhir_encounter_repo
        self.ai_service = ai_service
    
    async def create_fhir_diagnostic_report(self, report_data: Dict[str, Any]) -> FHIRDiagnosticReport:
        """Create FHIR DiagnosticReport resource"""
        try:
            diagnostic_report = DiagnosticReportFHIRModel.create_fhir_diagnostic_report(
                report_id=report_data.get('id'),
                patient_id=report_data.get('patient_id'),
                encounter_id=report_data.get('encounter_id'),
                status=report_data.get('status', 'final'),
                category=report_data.get('category', 'AI'),
                code=report_data.get('code', '11526-1'),
                conclusion=report_data.get('conclusion'),
                effective_date=report_data.get('effective_date'),
                issued_date=report_data.get('issued_date')
            )
            
            logger.info(f"Created FHIR DiagnosticReport: {diagnostic_report.id}")
            return diagnostic_report
            
        except Exception as e:
            logger.error(f"Error creating FHIR DiagnosticReport: {str(e)}")
            raise
    
    async def get_fhir_diagnostic_report(self, report_id: str) -> Optional[FHIRDiagnosticReport]:
        """Get FHIR DiagnosticReport resource by ID"""
        # Implementation would retrieve from repository
        pass
    
    async def create_ai_diagnosis(self, patient_id: str, encounter_id: str, symptoms: List[str]) -> FHIRDiagnosticReport:
        """Create AI-generated diagnosis as FHIR DiagnosticReport"""
        try:
            # Get AI diagnosis
            diagnosis_result = await self.ai_service.generate_diagnosis(symptoms)
            
            # Create diagnostic report
            report_id = f"ai-diagnosis-{encounter_id}-{int(datetime.now().timestamp())}"
            
            diagnostic_report = DiagnosticReportFHIRModel.create_fhir_diagnostic_report(
                report_id=report_id,
                patient_id=patient_id,
                encounter_id=encounter_id,
                status="final",
                category="AI",
                code="11526-1",  # Pathology study
                conclusion=diagnosis_result.get('conclusion'),
                effective_date=datetime.now(),
                issued_date=datetime.now()
            )
            
            return diagnostic_report
            
        except Exception as e:
            logger.error(f"Error creating AI diagnosis: {str(e)}")
            raise