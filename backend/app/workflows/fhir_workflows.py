"""
Advanced FHIR Workflows for DiagnoAssist Backend

This module implements sophisticated FHIR integration workflows including
bundle processing, clinical documents, questionnaires, and compliance validation.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from uuid import uuid4

from app.core.workflow_engine import (
    WorkflowStep, WorkflowDefinition, WorkflowContext, StepResult, StepStatus,
    workflow_engine, WorkflowPriority
)
from app.models.patient import PatientModel
from app.models.encounter import EncounterModel
from app.models.fhir_models import FHIRSyncResponse
from app.repositories.fhir_repository import fhir_repository
from app.services.fhir_sync_service import fhir_sync_service
from app.utils.fhir_mappers import FHIRMapper
from app.core.exceptions import ValidationException, FHIRException
import logging

logger = logging.getLogger(__name__)


class FHIRBundleCreationStep(WorkflowStep):
    """Create FHIR Bundle from multiple resources"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.bundle.create",
            name="FHIR Bundle Creation",
            description="Create FHIR Bundle from collected resources"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            resources = context.data.get("fhir_resources", [])
            bundle_type = context.data.get("bundle_type", "collection")
            
            if not resources:
                raise ValidationException("No FHIR resources provided for bundle")
            
            # Create FHIR Bundle
            bundle = {
                "resourceType": "Bundle",
                "id": str(uuid4()),
                "type": bundle_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total": len(resources),
                "entry": []
            }
            
            # Add resources to bundle
            for i, resource in enumerate(resources):
                entry = {
                    "fullUrl": f"urn:uuid:{uuid4()}",
                    "resource": resource
                }
                
                # Add request information for transaction bundles
                if bundle_type == "transaction":
                    entry["request"] = {
                        "method": "POST",
                        "url": resource["resourceType"]
                    }
                
                bundle["entry"].append(entry)
            
            # Store bundle in context
            context.data["fhir_bundle"] = bundle
            context.variables["bundle_id"] = bundle["id"]
            context.variables["bundle_size"] = len(resources)
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={
                    "bundle_id": bundle["id"],
                    "bundle_type": bundle_type,
                    "resource_count": len(resources)
                },
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class FHIRBundleValidationStep(WorkflowStep):
    """Validate FHIR Bundle against profiles and business rules"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.bundle.validate",
            name="FHIR Bundle Validation",
            description="Validate FHIR Bundle structure and content"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            bundle = context.data.get("fhir_bundle")
            if not bundle:
                raise ValidationException("FHIR Bundle is required for validation")
            
            validation_errors = []
            validation_warnings = []
            
            # Basic bundle structure validation
            required_fields = ["resourceType", "type", "entry"]
            for field in required_fields:
                if field not in bundle:
                    validation_errors.append(f"Missing required field: {field}")
            
            if bundle.get("resourceType") != "Bundle":
                validation_errors.append("Resource type must be 'Bundle'")
            
            # Validate bundle type
            valid_bundle_types = ["document", "message", "transaction", "transaction-response", 
                                 "batch", "batch-response", "history", "searchset", "collection"]
            if bundle.get("type") not in valid_bundle_types:
                validation_errors.append(f"Invalid bundle type: {bundle.get('type')}")
            
            # Validate entries
            entries = bundle.get("entry", [])
            for i, entry in enumerate(entries):
                # Check entry structure
                if "resource" not in entry:
                    validation_errors.append(f"Entry {i}: Missing resource")
                    continue
                
                resource = entry["resource"]
                
                # Basic resource validation
                if "resourceType" not in resource:
                    validation_errors.append(f"Entry {i}: Missing resourceType")
                
                # Validate resource-specific rules
                await self._validate_resource(resource, i, validation_errors, validation_warnings)
                
                # Validate references within bundle
                self._validate_bundle_references(bundle, entry, i, validation_warnings)
            
            # Store validation results
            context.variables["validation_errors"] = validation_errors
            context.variables["validation_warnings"] = validation_warnings
            context.variables["is_valid"] = len(validation_errors) == 0
            
            if validation_errors:
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.FAILED,
                    error=f"Bundle validation failed: {validation_errors}",
                    data={
                        "errors": validation_errors,
                        "warnings": validation_warnings
                    },
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={
                    "is_valid": True,
                    "warning_count": len(validation_warnings),
                    "warnings": validation_warnings
                },
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def _validate_resource(self, resource: Dict[str, Any], index: int, errors: List[str], warnings: List[str]):
        """Validate individual resource within bundle"""
        resource_type = resource.get("resourceType")
        
        if resource_type == "Patient":
            # Patient-specific validation
            if not resource.get("identifier"):
                warnings.append(f"Entry {index}: Patient missing identifier")
            
            if not resource.get("name"):
                errors.append(f"Entry {index}: Patient missing name")
        
        elif resource_type == "Encounter":
            # Encounter-specific validation
            if not resource.get("subject"):
                errors.append(f"Entry {index}: Encounter missing subject reference")
            
            if not resource.get("status"):
                errors.append(f"Entry {index}: Encounter missing status")
        
        elif resource_type == "Observation":
            # Observation-specific validation
            if not resource.get("code"):
                errors.append(f"Entry {index}: Observation missing code")
            
            if not resource.get("subject"):
                errors.append(f"Entry {index}: Observation missing subject reference")
    
    def _validate_bundle_references(self, bundle: Dict[str, Any], entry: Dict[str, Any], index: int, warnings: List[str]):
        """Validate references between resources in bundle"""
        resource = entry["resource"]
        
        # Find references in the resource
        references = self._extract_references(resource)
        
        # Check if references exist within bundle
        for ref in references:
            if ref.startswith("urn:uuid:"):
                # Internal bundle reference
                found = False
                for other_entry in bundle["entry"]:
                    if other_entry.get("fullUrl") == ref:
                        found = True
                        break
                
                if not found:
                    warnings.append(f"Entry {index}: Reference {ref} not found in bundle")
    
    def _extract_references(self, resource: Dict[str, Any]) -> List[str]:
        """Extract all references from a FHIR resource"""
        references = []
        
        def find_references(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "reference" and isinstance(value, str):
                        references.append(value)
                    else:
                        find_references(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_references(item, f"{path}[{i}]")
        
        find_references(resource)
        return references


class FHIRBundleSubmissionStep(WorkflowStep):
    """Submit FHIR Bundle to FHIR server"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.bundle.submit",
            name="FHIR Bundle Submission",
            description="Submit validated FHIR Bundle to server",
            retryable=True,
            max_retries=3
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            bundle = context.data.get("fhir_bundle")
            if not bundle:
                raise ValidationException("FHIR Bundle is required for submission")
            
            # Check if validation passed
            if not context.variables.get("is_valid", False):
                raise ValidationException("Cannot submit invalid FHIR Bundle")
            
            # Submit bundle to FHIR server
            response = await fhir_repository.submit_bundle(bundle)
            
            if response.get("resourceType") == "Bundle":
                # Process response bundle
                context.data["submission_response"] = response
                context.variables["submission_success"] = True
                
                # Extract created resource IDs
                created_resources = []
                for entry in response.get("entry", []):
                    if "response" in entry and "location" in entry["response"]:
                        created_resources.append({
                            "type": entry["response"].get("location", "").split("/")[0],
                            "id": entry["response"].get("location", "").split("/")[1] if "/" in entry["response"].get("location", "") else None,
                            "status": entry["response"].get("status")
                        })
                
                context.data["created_resources"] = created_resources
                
                return StepResult(
                    step_id=self.step_id,
                    status=StepStatus.COMPLETED,
                    data={
                        "bundle_id": response.get("id"),
                        "created_resources": len(created_resources),
                        "response_type": response.get("type")
                    },
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            else:
                raise FHIRException("Invalid response from FHIR server", "bundle_submission")
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class FHIRDocumentGenerationStep(WorkflowStep):
    """Generate FHIR Clinical Document"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.document.generate",
            name="FHIR Document Generation",
            description="Generate FHIR Clinical Document from encounter data"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            encounter = context.data.get("encounter")
            patient = context.data.get("patient")
            
            if not encounter or not patient:
                raise ValidationException("Both encounter and patient data are required")
            
            # Create document composition
            composition = {
                "resourceType": "Composition",
                "id": str(uuid4()),
                "status": "final",
                "type": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "11506-3",
                        "display": "Progress note"
                    }]
                },
                "subject": {
                    "reference": f"Patient/{patient.get('id') or 'temp-patient'}"
                },
                "encounter": {
                    "reference": f"Encounter/{encounter.get('id') or 'temp-encounter'}"
                },
                "date": datetime.utcnow().isoformat() + "Z",
                "author": [],
                "title": "Clinical Progress Note",
                "section": []
            }
            
            # Add author information
            if context.user:
                composition["author"].append({
                    "reference": f"Practitioner/{context.user.id}",
                    "display": f"{context.user.profile.first_name} {context.user.profile.last_name}"
                })
            
            # Add SOAP sections if available
            soap = encounter.get("soap")
            if soap:
                # Subjective section
                if soap.get("subjective"):
                    composition["section"].append({
                        "title": "Subjective",
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "61150-9",
                                "display": "Subjective"
                            }]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p><b>Chief Complaint:</b> {soap['subjective'].get('chief_complaint', '')}</p></div>"
                        }
                    })
                
                # Objective section
                if soap.get("objective"):
                    composition["section"].append({
                        "title": "Objective",
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "61149-1",
                                "display": "Objective"
                            }]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p><b>Physical Examination:</b> {soap['objective'].get('physical_examination', '')}</p></div>"
                        }
                    })
                
                # Assessment section
                if soap.get("assessment"):
                    composition["section"].append({
                        "title": "Assessment",
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "61146-7",
                                "display": "Assessment"
                            }]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p><b>Primary Diagnosis:</b> {soap['assessment'].get('primary_diagnosis', '')}</p></div>"
                        }
                    })
                
                # Plan section
                if soap.get("plan"):
                    composition["section"].append({
                        "title": "Plan",
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "61144-2",
                                "display": "Plan"
                            }]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p><b>Treatment Plan:</b> {soap['plan'].get('treatment_plan', '')}</p></div>"
                        }
                    })
            
            # Create document bundle
            document_bundle = {
                "resourceType": "Bundle",
                "id": str(uuid4()),
                "type": "document",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "entry": [
                    {
                        "fullUrl": f"urn:uuid:{composition['id']}",
                        "resource": composition
                    }
                ]
            }
            
            # Store document in context
            context.data["fhir_document"] = document_bundle
            context.data["composition"] = composition
            context.variables["document_id"] = document_bundle["id"]
            context.variables["composition_id"] = composition["id"]
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={
                    "document_id": document_bundle["id"],
                    "composition_id": composition["id"],
                    "section_count": len(composition["section"])
                },
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


class FHIRQuestionnaireProcessingStep(WorkflowStep):
    """Process FHIR Questionnaire responses"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.questionnaire.process",
            name="FHIR Questionnaire Processing",
            description="Process FHIR QuestionnaireResponse and extract clinical data"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            questionnaire_response = context.data.get("questionnaire_response")
            if not questionnaire_response:
                raise ValidationException("QuestionnaireResponse is required")
            
            # Extract answers from questionnaire response
            extracted_data = {
                "observations": [],
                "conditions": [],
                "medications": [],
                "allergies": []
            }
            
            # Process items recursively
            items = questionnaire_response.get("item", [])
            await self._process_questionnaire_items(items, extracted_data, context)
            
            # Create FHIR resources from extracted data
            fhir_resources = []
            
            # Create Observations
            for obs_data in extracted_data["observations"]:
                observation = {
                    "resourceType": "Observation",
                    "id": str(uuid4()),
                    "status": "final",
                    "code": obs_data.get("code", {"text": "Unknown"}),
                    "subject": {
                        "reference": f"Patient/{context.data.get('patient_id', 'unknown')}"
                    },
                    "valueString": obs_data.get("value"),
                    "effectiveDateTime": datetime.utcnow().isoformat() + "Z"
                }
                fhir_resources.append(observation)
            
            # Create Conditions
            for cond_data in extracted_data["conditions"]:
                condition = {
                    "resourceType": "Condition",
                    "id": str(uuid4()),
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }]
                    },
                    "code": cond_data.get("code", {"text": "Unknown"}),
                    "subject": {
                        "reference": f"Patient/{context.data.get('patient_id', 'unknown')}"
                    },
                    "recordedDate": datetime.utcnow().isoformat() + "Z"
                }
                fhir_resources.append(condition)
            
            # Store extracted resources
            context.data["extracted_resources"] = fhir_resources
            context.data["extraction_summary"] = {
                "observations": len(extracted_data["observations"]),
                "conditions": len(extracted_data["conditions"]),
                "medications": len(extracted_data["medications"]),
                "allergies": len(extracted_data["allergies"])
            }
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={
                    "resources_created": len(fhir_resources),
                    "extraction_summary": context.data["extraction_summary"]
                },
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def _process_questionnaire_items(self, items: List[Dict[str, Any]], extracted_data: Dict[str, List], context: WorkflowContext):
        """Process questionnaire items recursively"""
        for item in items:
            link_id = item.get("linkId", "")
            text = item.get("text", "")
            answer = item.get("answer", [])
            
            # Process answers
            for ans in answer:
                if "valueString" in ans:
                    value = ans["valueString"]
                elif "valueBoolean" in ans:
                    value = str(ans["valueBoolean"])
                elif "valueInteger" in ans:
                    value = str(ans["valueInteger"])
                elif "valueCoding" in ans:
                    value = ans["valueCoding"].get("display", ans["valueCoding"].get("code", ""))
                else:
                    value = str(ans)
                
                # Categorize based on link_id or text
                if "symptom" in link_id.lower() or "symptom" in text.lower():
                    extracted_data["observations"].append({
                        "code": {"text": text},
                        "value": value
                    })
                elif "diagnosis" in link_id.lower() or "condition" in link_id.lower():
                    extracted_data["conditions"].append({
                        "code": {"text": text},
                        "value": value
                    })
                elif "medication" in link_id.lower() or "drug" in link_id.lower():
                    extracted_data["medications"].append({
                        "code": {"text": text},
                        "value": value
                    })
                elif "allergy" in link_id.lower():
                    extracted_data["allergies"].append({
                        "code": {"text": text},
                        "value": value
                    })
                else:
                    # Default to observation
                    extracted_data["observations"].append({
                        "code": {"text": text},
                        "value": value
                    })
            
            # Process nested items
            if "item" in item:
                await self._process_questionnaire_items(item["item"], extracted_data, context)


class FHIRComplianceValidationStep(WorkflowStep):
    """Validate FHIR resources for compliance with profiles and regulations"""
    
    def __init__(self):
        super().__init__(
            step_id="fhir.compliance.validate",
            name="FHIR Compliance Validation",
            description="Validate FHIR resources for regulatory compliance"
        )
    
    async def execute(self, context: WorkflowContext) -> StepResult:
        start_time = datetime.utcnow()
        
        try:
            resources = context.data.get("fhir_resources", [])
            compliance_profile = context.data.get("compliance_profile", "US-Core")
            
            if not resources:
                raise ValidationException("No FHIR resources provided for compliance validation")
            
            compliance_results = {
                "total_resources": len(resources),
                "compliant_resources": 0,
                "non_compliant_resources": 0,
                "violations": [],
                "warnings": []
            }
            
            for i, resource in enumerate(resources):
                resource_type = resource.get("resourceType", "Unknown")
                resource_violations = []
                resource_warnings = []
                
                # US Core compliance checks
                if compliance_profile == "US-Core":
                    await self._validate_us_core_compliance(resource, resource_violations, resource_warnings)
                
                # HIPAA compliance checks
                await self._validate_hipaa_compliance(resource, resource_violations, resource_warnings)
                
                # General FHIR compliance
                await self._validate_general_fhir_compliance(resource, resource_violations, resource_warnings)
                
                if resource_violations:
                    compliance_results["non_compliant_resources"] += 1
                    compliance_results["violations"].extend([
                        f"Resource {i} ({resource_type}): {violation}" 
                        for violation in resource_violations
                    ])
                else:
                    compliance_results["compliant_resources"] += 1
                
                if resource_warnings:
                    compliance_results["warnings"].extend([
                        f"Resource {i} ({resource_type}): {warning}"
                        for warning in resource_warnings
                    ])
            
            # Calculate compliance rate
            compliance_rate = (compliance_results["compliant_resources"] / 
                             compliance_results["total_resources"]) * 100 if compliance_results["total_resources"] > 0 else 0
            
            compliance_results["compliance_rate"] = compliance_rate
            
            # Store results
            context.data["compliance_results"] = compliance_results
            context.variables["is_compliant"] = compliance_results["non_compliant_resources"] == 0
            context.variables["compliance_rate"] = compliance_rate
            
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.COMPLETED,
                data={
                    "compliance_rate": compliance_rate,
                    "compliant_resources": compliance_results["compliant_resources"],
                    "violation_count": len(compliance_results["violations"]),
                    "warning_count": len(compliance_results["warnings"])
                },
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return StepResult(
                step_id=self.step_id,
                status=StepStatus.FAILED,
                error=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def _validate_us_core_compliance(self, resource: Dict[str, Any], violations: List[str], warnings: List[str]):
        """Validate US Core compliance"""
        resource_type = resource.get("resourceType")
        
        if resource_type == "Patient":
            # US Core Patient requirements
            if not resource.get("identifier"):
                violations.append("Missing required identifier")
            
            if not resource.get("name"):
                violations.append("Missing required name")
            
            if not resource.get("gender"):
                warnings.append("Missing recommended gender")
                
        elif resource_type == "Observation":
            # US Core Observation requirements
            if not resource.get("status"):
                violations.append("Missing required status")
            
            if not resource.get("code"):
                violations.append("Missing required code")
            
            if not resource.get("subject"):
                violations.append("Missing required subject reference")
    
    async def _validate_hipaa_compliance(self, resource: Dict[str, Any], violations: List[str], warnings: List[str]):
        """Validate HIPAA compliance"""
        # Check for potentially sensitive information in text fields
        sensitive_patterns = ["ssn", "social security", "credit card", "bank account"]
        
        def check_text_fields(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and any(pattern in value.lower() for pattern in sensitive_patterns):
                        warnings.append(f"Potentially sensitive information found in {path}.{key}")
                    else:
                        check_text_fields(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_text_fields(item, f"{path}[{i}]")
        
        check_text_fields(resource)
    
    async def _validate_general_fhir_compliance(self, resource: Dict[str, Any], violations: List[str], warnings: List[str]):
        """Validate general FHIR compliance"""
        # Check required fields
        if not resource.get("resourceType"):
            violations.append("Missing resourceType")
        
        # Check for valid resource type
        valid_resource_types = [
            "Patient", "Practitioner", "Organization", "Encounter", "Observation",
            "Condition", "Medication", "MedicationRequest", "DiagnosticReport",
            "Bundle", "Composition", "Questionnaire", "QuestionnaireResponse"
        ]
        
        if resource.get("resourceType") not in valid_resource_types:
            warnings.append(f"Unusual resource type: {resource.get('resourceType')}")


def register_fhir_workflows():
    """Register all FHIR-specific workflows"""
    
    # Register workflow steps
    workflow_engine.register_step(FHIRBundleCreationStep())
    workflow_engine.register_step(FHIRBundleValidationStep())
    workflow_engine.register_step(FHIRBundleSubmissionStep())
    workflow_engine.register_step(FHIRDocumentGenerationStep())
    workflow_engine.register_step(FHIRQuestionnaireProcessingStep())
    workflow_engine.register_step(FHIRComplianceValidationStep())
    
    # FHIR Bundle Processing Workflow
    fhir_bundle_workflow = WorkflowDefinition(
        workflow_id="fhir.bundle.processing",
        name="FHIR Bundle Processing Workflow",
        description="Create, validate, and submit FHIR bundles",
        version="1.0",
        steps=[
            "fhir.bundle.create",
            "fhir.bundle.validate",
            "fhir.compliance.validate",
            "fhir.bundle.submit"
        ],
        dependencies={
            "fhir.bundle.validate": ["fhir.bundle.create"],
            "fhir.compliance.validate": ["fhir.bundle.validate"],
            "fhir.bundle.submit": ["fhir.compliance.validate"]
        },
        timeout_seconds=600,  # 10 minutes
        default_priority=WorkflowPriority.HIGH
    )
    
    workflow_engine.register_workflow(fhir_bundle_workflow)
    
    # FHIR Clinical Document Workflow
    fhir_document_workflow = WorkflowDefinition(
        workflow_id="fhir.clinical.document",
        name="FHIR Clinical Document Workflow",
        description="Generate and process FHIR clinical documents",
        version="1.0",
        steps=[
            "fhir.document.generate",
            "fhir.compliance.validate",
            "fhir.bundle.submit"
        ],
        dependencies={
            "fhir.compliance.validate": ["fhir.document.generate"],
            "fhir.bundle.submit": ["fhir.compliance.validate"]
        },
        timeout_seconds=300,  # 5 minutes
        default_priority=WorkflowPriority.NORMAL
    )
    
    workflow_engine.register_workflow(fhir_document_workflow)
    
    # FHIR Questionnaire Processing Workflow
    fhir_questionnaire_workflow = WorkflowDefinition(
        workflow_id="fhir.questionnaire.processing",
        name="FHIR Questionnaire Processing Workflow",
        description="Process questionnaire responses and extract clinical data",
        version="1.0",
        steps=[
            "fhir.questionnaire.process",
            "fhir.bundle.create",
            "fhir.compliance.validate",
            "fhir.bundle.submit"
        ],
        dependencies={
            "fhir.bundle.create": ["fhir.questionnaire.process"],
            "fhir.compliance.validate": ["fhir.bundle.create"],
            "fhir.bundle.submit": ["fhir.compliance.validate"]
        },
        timeout_seconds=400,  # 6-7 minutes
        default_priority=WorkflowPriority.NORMAL
    )
    
    workflow_engine.register_workflow(fhir_questionnaire_workflow)
    
    logger.info("Registered FHIR workflows successfully")


# Initialize FHIR workflows on module import
register_fhir_workflows()