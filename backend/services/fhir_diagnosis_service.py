from typing import List, Optional, Dict, Any
from repositories.fhir_patient_repository import FHIRPatientRepository
from repositories.fhir_encounter_repository import FHIREncounterRepository
from services.ai_service import AIService
from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
import logging
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)

class FHIRDiagnosisService:
    """
    Service for FHIR diagnostic reports and AI diagnosis integration
    """
    
    def __init__(
        self,
        fhir_patient_repo: FHIRPatientRepository,
        fhir_encounter_repo: FHIREncounterRepository,
        ai_service: AIService
    ):
        self.fhir_patient_repo = fhir_patient_repo
        self.fhir_encounter_repo = fhir_encounter_repo
        self.ai_service = ai_service
    
    async def create_fhir_diagnostic_report(
        self, 
        report_data: Dict[str, Any]
    ) -> FHIRDiagnosticReport:
        """
        Create FHIR DiagnosticReport resource
        
        Args:
            report_data: Diagnostic report data
            
        Returns:
            Created FHIR DiagnosticReport resource
        """
        try:
            # Validate and create FHIR DiagnosticReport
            fhir_report = FHIRDiagnosticReport(**report_data)
            
            # TODO: Store in FHIR resource repository
            # For now, just return the created report
            
            logger.info(f"Created FHIR DiagnosticReport: {fhir_report.id}")
            return fhir_report
            
        except Exception as e:
            logger.error(f"Error creating FHIR DiagnosticReport: {str(e)}")
            raise
    
    async def create_ai_diagnosis_report(
        self, 
        diagnosis_data: Dict[str, Any]
    ) -> FHIRDiagnosticReport:
        """
        Create FHIR DiagnosticReport for AI diagnosis results
        
        Args:
            diagnosis_data: AI diagnosis data
            
        Returns:
            FHIR DiagnosticReport with AI diagnosis
        """
        try:
            patient_id = diagnosis_data["patient_id"]
            encounter_id = diagnosis_data.get("encounter_id")
            symptoms = diagnosis_data.get("symptoms", [])
            differential_diagnoses = diagnosis_data.get("differential_diagnoses", [])
            
            # Generate AI analysis
            clinical_data = {
                "symptoms": symptoms,
                "physical_exam": diagnosis_data.get("physical_exam", {}),
                "vital_signs": diagnosis_data.get("vital_signs", {})
            }
            
            ai_analysis = await self.ai_service.analyze_symptoms(clinical_data)
            
            # Create FHIR DiagnosticReport
            report = FHIRDiagnosticReport()
            report.id = str(uuid4())
            report.status = "final"
            
            # Set category as AI diagnosis
            report.category = [CodeableConcept(**{
                "coding": [Coding(**{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                    "code": "LAB",
                    "display": "Laboratory"
                })]
            })]
            
            # Set code as AI diagnosis
            report.code = CodeableConcept(**{
                "coding": [Coding(**{
                    "system": "https://diagnoassist.com/CodeSystem/ai-diagnosis",
                    "code": "ai-differential-diagnosis",
                    "display": "AI Differential Diagnosis"
                })]
            })
            
            # Set patient reference
            report.subject = Reference(**{
                "reference": f"Patient/{patient_id}"
            })
            
            # Set encounter reference if provided
            if encounter_id:
                report.encounter = Reference(**{
                    "reference": f"Encounter/{encounter_id}"
                })
            
            # Set effective date
            report.effectiveDateTime = datetime.utcnow().isoformat()
            
            # Set result text with AI analysis
            report.conclusion = self._format_ai_analysis_text(ai_analysis)
            
            # Add coded conclusions for each differential diagnosis
            report.conclusionCode = []
            for diag in ai_analysis.get("differential_diagnoses", []):
                if diag.get("icd10_code"):
                    conclusion_code = CodeableConcept(**{
                        "coding": [Coding(**{
                            "system": "http://hl7.org/fhir/sid/icd-10-cm",
                            "code": diag["icd10_code"],
                            "display": diag["condition"]
                        })],
                        "text": f"{diag['condition']} (Confidence: {diag.get('confidence', 0):.2f})"
                    })
                    report.conclusionCode.append(conclusion_code)
            
            logger.info(f"Created AI diagnosis report: {report.id}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating AI diagnosis report: {str(e)}")
            raise
    
    async def get_fhir_diagnostic_report(self, report_id: str) -> Optional[FHIRDiagnosticReport]:
        """
        Get FHIR DiagnosticReport by ID
        
        Args:
            report_id: DiagnosticReport resource ID
            
        Returns:
            FHIR DiagnosticReport or None
        """
        try:
            # TODO: Implement repository method
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"Error getting FHIR DiagnosticReport {report_id}: {str(e)}")
            raise
    
    async def search_diagnostic_reports(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search FHIR DiagnosticReport resources
        
        Args:
            search_params: FHIR search parameters
            
        Returns:
            FHIR Bundle with search results
        """
        try:
            # TODO: Implement search functionality
            # For now, return empty bundle
            return {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 0,
                "entry": []
            }
        except Exception as e:
            logger.error(f"Error searching FHIR DiagnosticReports: {str(e)}")
            raise
    
    def _format_ai_analysis_text(self, ai_analysis: Dict[str, Any]) -> str:
        """Format AI analysis as human-readable text"""
        text_parts = ["AI-Generated Differential Diagnosis:\n"]
        
        for i, diag in enumerate(ai_analysis.get("differential_diagnoses", []), 1):
            confidence = diag.get("confidence", 0)
            condition = diag.get("condition", "Unknown")
            evidence = diag.get("evidence", [])
            
            text_parts.append(f"{i}. {condition} (Confidence: {confidence:.2f})")
            if evidence:
                text_parts.append(f"   Evidence: {', '.join(evidence)}")
            text_parts.append("")
        
        recommendations = ai_analysis.get("recommendations", [])
        if recommendations:
            text_parts.append("Recommendations:")
            for rec in recommendations:
                text_parts.append(f"- {rec}")
        
        return "\n".join(text_parts)
