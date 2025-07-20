from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from typing import Optional, List
from datetime import datetime

class DiagnosticReportFHIRModel:
    """FHIR DiagnosticReport model helper"""
    
    @staticmethod
    def create_fhir_diagnostic_report(
        report_id: str,
        patient_id: str,
        code: str,
        encounter_id: Optional[str] = None,
        status: str = "final",
        category: str = "LAB",
        conclusion: Optional[str] = None,
        effective_date: Optional[datetime] = None,
        issued_date: Optional[datetime] = None
    ) -> FHIRDiagnosticReport:
        """Create FHIR DiagnosticReport resource"""
        
        report = FHIRDiagnosticReport()
        report.id = report_id
        report.status = status
        
        # Subject reference
        report.subject = Reference(**{
            "reference": f"Patient/{patient_id}"
        })
        
        # Encounter reference
        if encounter_id:
            report.encounter = Reference(**{
                "reference": f"Encounter/{encounter_id}"
            })
        
        # Category
        category_mapping = {
            "LAB": ("LAB", "Laboratory"),
            "RAD": ("RAD", "Radiology"),
            "PATH": ("PATH", "Pathology"),
            "AI": ("AI", "Artificial Intelligence")
        }
        
        cat_code, cat_display = category_mapping.get(category, ("LAB", "Laboratory"))
        report.category = [CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": cat_code,
                "display": cat_display
            })]
        })]
        
        # Code
        report.code = CodeableConcept(**{
            "coding": [Coding(**{
                "system": "http://loinc.org",
                "code": code,
                "display": "Diagnostic Report"
            })]
        })
        
        # Effective date
        if effective_date:
            report.effectiveDateTime = effective_date.isoformat()
        
        # Issued date
        report.issued = (issued_date or datetime.now()).isoformat()
        
        # Conclusion
        if conclusion:
            report.conclusion = conclusion
        
        return report