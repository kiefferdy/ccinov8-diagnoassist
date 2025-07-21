"""
FHIR R4 Metadata and CapabilityStatement endpoint
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/R4/metadata", summary="Get FHIR CapabilityStatement")
async def get_capability_statement():
    """
    Return FHIR CapabilityStatement describing server capabilities.
    This endpoint is required by the FHIR specification.
    """
    
    capability_statement = {
        "resourceType": "CapabilityStatement",
        "id": "diagnoassist-fhir-server",
        "status": "active",
        "date": datetime.utcnow().isoformat() + "Z",
        "publisher": "DiagnoAssist",
        "kind": "instance",
        "software": {
            "name": "DiagnoAssist FHIR Server",
            "version": "1.0.0"
        },
        "implementation": {
            "description": "DiagnoAssist AI-powered medical diagnosis assistant with FHIR R4 compliance",
            "url": "http://localhost:8000/fhir/R4"
        },
        "fhirVersion": "4.0.1",
        "format": [
            "json",
            "application/fhir+json"
        ],
        "rest": [
            {
                "mode": "server",
                "documentation": "DiagnoAssist FHIR R4 Server",
                "security": {
                    "cors": True,
                    "description": "Optional SMART-on-FHIR or OAuth2 authentication"
                },
                "resource": [
                    {
                        "type": "Patient",
                        "profile": "http://hl7.org/fhir/StructureDefinition/Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {
                                "name": "identifier",
                                "type": "token",
                                "documentation": "A patient identifier"
                            },
                            {
                                "name": "family",
                                "type": "string", 
                                "documentation": "A portion of the family name of the patient"
                            },
                            {
                                "name": "given",
                                "type": "string",
                                "documentation": "A portion of the given name of the patient"
                            },
                            {
                                "name": "birthdate",
                                "type": "date",
                                "documentation": "The patient's date of birth"
                            },
                            {
                                "name": "gender",
                                "type": "token",
                                "documentation": "Gender of the patient"
                            }
                        ]
                    },
                    {
                        "type": "Encounter",
                        "profile": "http://hl7.org/fhir/StructureDefinition/Encounter",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {
                                "name": "patient",
                                "type": "reference",
                                "documentation": "The patient present at the encounter"
                            },
                            {
                                "name": "date",
                                "type": "date",
                                "documentation": "A date within the period the Encounter lasted"
                            },
                            {
                                "name": "class",
                                "type": "token",
                                "documentation": "Classification of the encounter"
                            },
                            {
                                "name": "status",
                                "type": "token",
                                "documentation": "Status of the encounter"
                            }
                        ]
                    },
                    {
                        "type": "Observation",
                        "profile": "http://hl7.org/fhir/StructureDefinition/Observation",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {
                                "name": "patient",
                                "type": "reference",
                                "documentation": "The subject that the observation is about"
                            },
                            {
                                "name": "code",
                                "type": "token",
                                "documentation": "The code of the observation type"
                            },
                            {
                                "name": "date",
                                "type": "date",
                                "documentation": "Obtained date/time"
                            },
                            {
                                "name": "category",
                                "type": "token",
                                "documentation": "The classification of the type of observation"
                            }
                        ]
                    },
                    {
                        "type": "DiagnosticReport",
                        "profile": "http://hl7.org/fhir/StructureDefinition/DiagnosticReport",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {
                                "name": "patient",
                                "type": "reference",
                                "documentation": "The subject of the report"
                            },
                            {
                                "name": "date",
                                "type": "date",
                                "documentation": "The clinically relevant time of the report"
                            },
                            {
                                "name": "status",
                                "type": "token",
                                "documentation": "The status of the report"
                            }
                        ]
                    },
                    {
                        "type": "Condition",
                        "profile": "http://hl7.org/fhir/StructureDefinition/Condition",
                        "interaction": [
                            {"code": "read"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {
                                "name": "patient",
                                "type": "reference",
                                "documentation": "Who has the condition?"
                            },
                            {
                                "name": "code",
                                "type": "token",
                                "documentation": "Code for the condition"
                            },
                            {
                                "name": "clinical-status",
                                "type": "token",
                                "documentation": "The clinical status of the condition"
                            }
                        ]
                    }
                ],
                "interaction": [
                    {
                        "code": "transaction",
                        "documentation": "Submit a bundle of resources as a transaction"
                    },
                    {
                        "code": "batch",
                        "documentation": "Submit a bundle of resources as a batch"
                    }
                ]
            }
        ]
    }
    
    return capability_statement