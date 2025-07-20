from fhir.resources.capabilitystatement import CapabilityStatement
from fhir.resources.capabilitystatementrest import CapabilityStatementRest
from fhir.resources.capabilitystatementrestresource import CapabilityStatementRestResource
from fhir.resources.capabilitystatementrestinteraction import CapabilityStatementRestInteraction
from fhir.resources.capabilitystatementrestsearchparam import CapabilityStatementRestSearchParam
from fhir.resources.capabilitystatementrestoperation import CapabilityStatementRestOperation
from fhir.resources.capabilitystatementrestresourceoperation import CapabilityStatementRestResourceOperation
from datetime import datetime
from .settings import get_settings

settings = get_settings()

def create_capability_statement() -> CapabilityStatement:
    """
    Create FHIR CapabilityStatement describing server capabilities
    """
    
    capability = CapabilityStatement()
    
    # Basic server information
    capability.id = "diagnoassist-capability"
    capability.url = f"{settings.fhir_base_url}/metadata"
    capability.version = settings.app_version
    capability.name = "DiagnoAssistCapabilityStatement"
    capability.title = "DiagnoAssist FHIR Capability Statement"
    capability.status = "active"
    capability.experimental = False
    capability.date = datetime.utcnow().isoformat()
    capability.publisher = settings.fhir_publisher
    capability.contact = [{
        "name": "DiagnoAssist Support",
        "telecom": [{
            "system": "email",
            "value": settings.fhir_contact_email
        }]
    }]
    
    capability.description = (
        "DiagnoAssist FHIR R4 server providing AI-powered medical diagnosis "
        "assistance with full healthcare interoperability support."
    )
    
    # Server capabilities
    capability.kind = "instance"
    capability.software = {
        "name": "DiagnoAssist FHIR Server",
        "version": settings.app_version,
        "releaseDate": "2025-07-20"
    }
    capability.implementation = {
        "description": "DiagnoAssist AI Medical Diagnosis Platform",
        "url": settings.fhir_base_url
    }
    capability.fhirVersion = settings.fhir_version
    capability.format = ["json", "xml"]
    capability.patchFormat = ["application/json-patch+json"]
    
    # REST capabilities
    rest = CapabilityStatementRest()
    rest.mode = "server"
    rest.documentation = "DiagnoAssist FHIR R4 REST API"
    
    # Security (SMART on FHIR)
    rest.security = {
        "cors": True,
        "service": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/restful-security-service",
                "code": "SMART-on-FHIR",
                "display": "SMART on FHIR"
            }]
        }],
        "description": "Uses SMART on FHIR authorization",
        "extension": [{
            "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris",
            "extension": [
                {
                    "url": "token",
                    "valueUri": "https://diagnoassist.com/auth/token"
                },
                {
                    "url": "authorize", 
                    "valueUri": "https://diagnoassist.com/auth/authorize"
                }
            ]
        }]
    }
    
    # Supported resources
    rest.resource = []
    
    # Patient Resource
    patient_resource = CapabilityStatementRestResource()
    patient_resource.type = "Patient"
    patient_resource.profile = "http://hl7.org/fhir/StructureDefinition/Patient"
    patient_resource.documentation = "Patient demographics and identification"
    
    patient_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="delete"),
        CapabilityStatementRestInteraction(code="search-type"),
        CapabilityStatementRestInteraction(code="vread"),
        CapabilityStatementRestInteraction(code="history-instance")
    ]
    
    patient_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="name", type="string", documentation="Search by name"),
        CapabilityStatementRestSearchParam(name="given", type="string", documentation="Search by given name"),
        CapabilityStatementRestSearchParam(name="family", type="string", documentation="Search by family name"),
        CapabilityStatementRestSearchParam(name="birthdate", type="date", documentation="Search by birth date"),
        CapabilityStatementRestSearchParam(name="gender", type="token", documentation="Search by gender"),
        CapabilityStatementRestSearchParam(name="identifier", type="token", documentation="Search by identifier"),
        CapabilityStatementRestSearchParam(name="active", type="token", documentation="Search by active status")
    ]
    
    patient_resource.operation = [
        CapabilityStatementRestResourceOperation(
            name="everything",
            definition="http://hl7.org/fhir/OperationDefinition/Patient-everything",
            documentation="Fetch all patient data"
        )
    ]
    
    rest.resource.append(patient_resource)
    
    # Encounter Resource
    encounter_resource = CapabilityStatementRestResource()
    encounter_resource.type = "Encounter"
    encounter_resource.profile = "http://hl7.org/fhir/StructureDefinition/Encounter"
    encounter_resource.documentation = "Medical encounters and episodes of care"
    
    encounter_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="search-type"),
        CapabilityStatementRestInteraction(code="vread")
    ]
    
    encounter_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="patient", type="reference", documentation="Patient reference"),
        CapabilityStatementRestSearchParam(name="date", type="date", documentation="Encounter date"),
        CapabilityStatementRestSearchParam(name="class", type="token", documentation="Encounter class"),
        CapabilityStatementRestSearchParam(name="status", type="token", documentation="Encounter status"),
        CapabilityStatementRestSearchParam(name="type", type="token", documentation="Encounter type")
    ]
    
    rest.resource.append(encounter_resource)
    
    # Observation Resource
    observation_resource = CapabilityStatementRestResource()
    observation_resource.type = "Observation"
    observation_resource.profile = "http://hl7.org/fhir/StructureDefinition/Observation"
    observation_resource.documentation = "Vital signs, lab results, and clinical observations"
    
    observation_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="search-type"),
        CapabilityStatementRestInteraction(code="vread")
    ]
    
    observation_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="patient", type="reference", documentation="Patient reference"),
        CapabilityStatementRestSearchParam(name="encounter", type="reference", documentation="Encounter reference"),
        CapabilityStatementRestSearchParam(name="category", type="token", documentation="Observation category"),
        CapabilityStatementRestSearchParam(name="code", type="token", documentation="Observation code"),
        CapabilityStatementRestSearchParam(name="date", type="date", documentation="Observation date"),
        CapabilityStatementRestSearchParam(name="value-quantity", type="quantity", documentation="Observation value"),
        CapabilityStatementRestSearchParam(name="component-code", type="token", documentation="Component code")
    ]
    
    rest.resource.append(observation_resource)
    
    # DiagnosticReport Resource
    diagnostic_resource = CapabilityStatementRestResource()
    diagnostic_resource.type = "DiagnosticReport"
    diagnostic_resource.profile = "http://hl7.org/fhir/StructureDefinition/DiagnosticReport"
    diagnostic_resource.documentation = "AI diagnosis reports and clinical assessments"
    
    diagnostic_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="search-type"),
        CapabilityStatementRestInteraction(code="vread")
    ]
    
    diagnostic_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="patient", type="reference", documentation="Patient reference"),
        CapabilityStatementRestSearchParam(name="encounter", type="reference", documentation="Encounter reference"),
        CapabilityStatementRestSearchParam(name="category", type="token", documentation="Report category"),
        CapabilityStatementRestSearchParam(name="code", type="token", documentation="Report code"),
        CapabilityStatementRestSearchParam(name="date", type="date", documentation="Report date"),
        CapabilityStatementRestSearchParam(name="status", type="token", documentation="Report status")
    ]
    
    rest.resource.append(diagnostic_resource)
    
    # Condition Resource
    condition_resource = CapabilityStatementRestResource()
    condition_resource.type = "Condition"
    condition_resource.profile = "http://hl7.org/fhir/StructureDefinition/Condition"
    condition_resource.documentation = "Patient conditions and diagnoses"
    
    condition_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="search-type"),
        CapabilityStatementRestInteraction(code="vread")
    ]
    
    condition_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="patient", type="reference", documentation="Patient reference"),
        CapabilityStatementRestSearchParam(name="encounter", type="reference", documentation="Encounter reference"),
        CapabilityStatementRestSearchParam(name="category", type="token", documentation="Condition category"),
        CapabilityStatementRestSearchParam(name="code", type="token", documentation="Condition code"),
        CapabilityStatementRestSearchParam(name="clinical-status", type="token", documentation="Clinical status")
    ]
    
    rest.resource.append(condition_resource)
    
    # CarePlan Resource (for treatment plans)
    careplan_resource = CapabilityStatementRestResource()
    careplan_resource.type = "CarePlan"
    careplan_resource.profile = "http://hl7.org/fhir/StructureDefinition/CarePlan"
    careplan_resource.documentation = "AI-generated treatment and care plans"
    
    careplan_resource.interaction = [
        CapabilityStatementRestInteraction(code="read"),
        CapabilityStatementRestInteraction(code="create"),
        CapabilityStatementRestInteraction(code="update"),
        CapabilityStatementRestInteraction(code="search-type")
    ]
    
    careplan_resource.searchParam = [
        CapabilityStatementRestSearchParam(name="patient", type="reference", documentation="Patient reference"),
        CapabilityStatementRestSearchParam(name="encounter", type="reference", documentation="Encounter reference"),
        CapabilityStatementRestSearchParam(name="category", type="token", documentation="Care plan category"),
        CapabilityStatementRestSearchParam(name="status", type="token", documentation="Care plan status"),
        CapabilityStatementRestSearchParam(name="date", type="date", documentation="Care plan date")
    ]
    
    rest.resource.append(careplan_resource)
    
    # Bundle operations
    rest.operation = [
        CapabilityStatementRestOperation(
            name="validate",
            definition="http://hl7.org/fhir/OperationDefinition/Resource-validate",
            documentation="Validate a resource"
        ),
        CapabilityStatementRestOperation(
            name="batch",
            definition="http://hl7.org/fhir/OperationDefinition/Bundle-batch",
            documentation="Process a batch bundle"
        ),
        CapabilityStatementRestOperation(
            name="transaction",
            definition="http://hl7.org/fhir/OperationDefinition/Bundle-transaction", 
            documentation="Process a transaction bundle"
        )
    ]
    
    capability.rest = [rest]
    
    return capability
