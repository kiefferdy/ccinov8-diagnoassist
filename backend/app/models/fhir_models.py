"""
FHIR models and data structures for DiagnoAssist Backend
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class FHIRResourceStatus(str, Enum):
    """FHIR resource status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENTERED_IN_ERROR = "entered-in-error"


class FHIRPatientGender(str, Enum):
    """FHIR patient gender enum"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class FHIRContactPointSystem(str, Enum):
    """FHIR contact point system enum"""
    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    PAGER = "pager"
    URL = "url"
    SMS = "sms"
    OTHER = "other"


class FHIRContactPointUse(str, Enum):
    """FHIR contact point use enum"""
    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    MOBILE = "mobile"


class FHIRIdentifier(BaseModel):
    """FHIR identifier model"""
    use: Optional[str] = None
    type: Optional[Dict[str, Any]] = None
    system: Optional[str] = None
    value: str
    period: Optional[Dict[str, Any]] = None
    assigner: Optional[Dict[str, Any]] = None


class FHIRHumanName(BaseModel):
    """FHIR human name model"""
    use: Optional[str] = None
    text: Optional[str] = None
    family: Optional[str] = None
    given: Optional[List[str]] = None
    prefix: Optional[List[str]] = None
    suffix: Optional[List[str]] = None
    period: Optional[Dict[str, Any]] = None


class FHIRContactPoint(BaseModel):
    """FHIR contact point model"""
    system: FHIRContactPointSystem
    value: str
    use: Optional[FHIRContactPointUse] = None
    rank: Optional[int] = None
    period: Optional[Dict[str, Any]] = None


class FHIRAddress(BaseModel):
    """FHIR address model"""
    use: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None
    line: Optional[List[str]] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")
    country: Optional[str] = None
    period: Optional[Dict[str, Any]] = None


class FHIRCodeableConcept(BaseModel):
    """FHIR codeable concept model"""
    coding: Optional[List[Dict[str, Any]]] = None
    text: Optional[str] = None


class FHIRCoding(BaseModel):
    """FHIR coding model"""
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    user_selected: Optional[bool] = Field(None, alias="userSelected")


class FHIRReference(BaseModel):
    """FHIR reference model"""
    reference: Optional[str] = None
    type: Optional[str] = None
    identifier: Optional[FHIRIdentifier] = None
    display: Optional[str] = None


class FHIRQuantity(BaseModel):
    """FHIR quantity model"""
    value: Optional[float] = None
    comparator: Optional[str] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


class FHIRPatientModel(BaseModel):
    """FHIR Patient resource model"""
    resource_type: str = Field("Patient", alias="resourceType")
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicit_rules: Optional[str] = Field(None, alias="implicitRules")
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = None
    extension: Optional[List[Dict[str, Any]]] = None
    modifier_extension: Optional[List[Dict[str, Any]]] = Field(None, alias="modifierExtension")
    
    # Patient-specific fields
    identifier: Optional[List[FHIRIdentifier]] = None
    active: Optional[bool] = None
    name: Optional[List[FHIRHumanName]] = None
    telecom: Optional[List[FHIRContactPoint]] = None
    gender: Optional[FHIRPatientGender] = None
    birth_date: Optional[str] = Field(None, alias="birthDate")  # YYYY-MM-DD format
    deceased_boolean: Optional[bool] = Field(None, alias="deceasedBoolean")
    deceased_date_time: Optional[str] = Field(None, alias="deceasedDateTime")
    address: Optional[List[FHIRAddress]] = None
    marital_status: Optional[FHIRCodeableConcept] = Field(None, alias="maritalStatus")
    multiple_birth_boolean: Optional[bool] = Field(None, alias="multipleBirthBoolean")
    multiple_birth_integer: Optional[int] = Field(None, alias="multipleBirthInteger")
    photo: Optional[List[Dict[str, Any]]] = None
    contact: Optional[List[Dict[str, Any]]] = None
    communication: Optional[List[Dict[str, Any]]] = None
    general_practitioner: Optional[List[FHIRReference]] = Field(None, alias="generalPractitioner")
    managing_organization: Optional[FHIRReference] = Field(None, alias="managingOrganization")
    link: Optional[List[Dict[str, Any]]] = None


class FHIRObservationStatus(str, Enum):
    """FHIR observation status enum"""
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class FHIRObservationModel(BaseModel):
    """FHIR Observation resource model"""
    resource_type: str = Field("Observation", alias="resourceType")
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicit_rules: Optional[str] = Field(None, alias="implicitRules")
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = None
    extension: Optional[List[Dict[str, Any]]] = None
    modifier_extension: Optional[List[Dict[str, Any]]] = Field(None, alias="modifierExtension")
    
    # Observation-specific fields
    identifier: Optional[List[FHIRIdentifier]] = None
    based_on: Optional[List[FHIRReference]] = Field(None, alias="basedOn")
    part_of: Optional[List[FHIRReference]] = Field(None, alias="partOf")
    status: FHIRObservationStatus
    category: Optional[List[FHIRCodeableConcept]] = None
    code: FHIRCodeableConcept
    subject: Optional[FHIRReference] = None
    focus: Optional[List[FHIRReference]] = None
    encounter: Optional[FHIRReference] = None
    effective_date_time: Optional[str] = Field(None, alias="effectiveDateTime")
    effective_period: Optional[Dict[str, Any]] = Field(None, alias="effectivePeriod")
    effective_timing: Optional[Dict[str, Any]] = Field(None, alias="effectiveTiming")
    effective_instant: Optional[str] = Field(None, alias="effectiveInstant")
    issued: Optional[str] = None
    performer: Optional[List[FHIRReference]] = None
    value_quantity: Optional[FHIRQuantity] = Field(None, alias="valueQuantity")
    value_codeable_concept: Optional[FHIRCodeableConcept] = Field(None, alias="valueCodeableConcept")
    value_string: Optional[str] = Field(None, alias="valueString")
    value_boolean: Optional[bool] = Field(None, alias="valueBoolean")
    value_integer: Optional[int] = Field(None, alias="valueInteger")
    value_range: Optional[Dict[str, Any]] = Field(None, alias="valueRange")
    value_ratio: Optional[Dict[str, Any]] = Field(None, alias="valueRatio")
    value_sampled_data: Optional[Dict[str, Any]] = Field(None, alias="valueSampledData")
    value_time: Optional[str] = Field(None, alias="valueTime")
    value_date_time: Optional[str] = Field(None, alias="valueDateTime")
    value_period: Optional[Dict[str, Any]] = Field(None, alias="valuePeriod")
    data_absent_reason: Optional[FHIRCodeableConcept] = Field(None, alias="dataAbsentReason")
    interpretation: Optional[List[FHIRCodeableConcept]] = None
    note: Optional[List[Dict[str, Any]]] = None
    body_site: Optional[FHIRCodeableConcept] = Field(None, alias="bodySite")
    method: Optional[FHIRCodeableConcept] = None
    specimen: Optional[FHIRReference] = None
    device: Optional[FHIRReference] = None
    reference_range: Optional[List[Dict[str, Any]]] = Field(None, alias="referenceRange")
    has_member: Optional[List[FHIRReference]] = Field(None, alias="hasMember")
    derived_from: Optional[List[FHIRReference]] = Field(None, alias="derivedFrom")
    component: Optional[List[Dict[str, Any]]] = None


class FHIRConditionClinicalStatus(str, Enum):
    """FHIR condition clinical status enum"""
    ACTIVE = "active"
    RECURRENCE = "recurrence"
    RELAPSE = "relapse"
    INACTIVE = "inactive"
    REMISSION = "remission"
    RESOLVED = "resolved"


class FHIRConditionVerificationStatus(str, Enum):
    """FHIR condition verification status enum"""
    UNCONFIRMED = "unconfirmed"
    PROVISIONAL = "provisional"
    DIFFERENTIAL = "differential"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


class FHIRConditionModel(BaseModel):
    """FHIR Condition resource model"""
    resource_type: str = Field("Condition", alias="resourceType")
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicit_rules: Optional[str] = Field(None, alias="implicitRules")
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = None
    extension: Optional[List[Dict[str, Any]]] = None
    modifier_extension: Optional[List[Dict[str, Any]]] = Field(None, alias="modifierExtension")
    
    # Condition-specific fields
    identifier: Optional[List[FHIRIdentifier]] = None
    clinical_status: Optional[FHIRCodeableConcept] = Field(None, alias="clinicalStatus")
    verification_status: Optional[FHIRCodeableConcept] = Field(None, alias="verificationStatus")
    category: Optional[List[FHIRCodeableConcept]] = None
    severity: Optional[FHIRCodeableConcept] = None
    code: Optional[FHIRCodeableConcept] = None
    body_site: Optional[List[FHIRCodeableConcept]] = Field(None, alias="bodySite")
    subject: FHIRReference
    encounter: Optional[FHIRReference] = None
    onset_date_time: Optional[str] = Field(None, alias="onsetDateTime")
    onset_age: Optional[Dict[str, Any]] = Field(None, alias="onsetAge")
    onset_period: Optional[Dict[str, Any]] = Field(None, alias="onsetPeriod")
    onset_range: Optional[Dict[str, Any]] = Field(None, alias="onsetRange")
    onset_string: Optional[str] = Field(None, alias="onsetString")
    abatement_date_time: Optional[str] = Field(None, alias="abatementDateTime")
    abatement_age: Optional[Dict[str, Any]] = Field(None, alias="abatementAge")
    abatement_period: Optional[Dict[str, Any]] = Field(None, alias="abatementPeriod")
    abatement_range: Optional[Dict[str, Any]] = Field(None, alias="abatementRange")
    abatement_string: Optional[str] = Field(None, alias="abatementString")
    abatement_boolean: Optional[bool] = Field(None, alias="abatementBoolean")
    recorded_date: Optional[str] = Field(None, alias="recordedDate")
    recorder: Optional[FHIRReference] = None
    asserter: Optional[FHIRReference] = None
    stage: Optional[List[Dict[str, Any]]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    note: Optional[List[Dict[str, Any]]] = None


class FHIREncounterStatus(str, Enum):
    """FHIR encounter status enum"""
    PLANNED = "planned"
    ARRIVED = "arrived"
    TRIAGED = "triaged"
    IN_PROGRESS = "in-progress"
    ONLEAVE = "onleave"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class FHIREncounterClass(str, Enum):
    """FHIR encounter class enum"""
    AMB = "AMB"  # ambulatory
    EMER = "EMER"  # emergency
    FLD = "FLD"  # field
    HH = "HH"  # home health
    IMP = "IMP"  # inpatient encounter
    ACUTE = "ACUTE"  # inpatient acute
    NONAC = "NONAC"  # inpatient non-acute
    OBSENC = "OBSENC"  # observation encounter
    PRENC = "PRENC"  # pre-admission
    SS = "SS"  # short stay
    VR = "VR"  # virtual


class FHIREncounterModel(BaseModel):
    """FHIR Encounter resource model"""
    resource_type: str = Field("Encounter", alias="resourceType")
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicit_rules: Optional[str] = Field(None, alias="implicitRules")
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = None
    extension: Optional[List[Dict[str, Any]]] = None
    modifier_extension: Optional[List[Dict[str, Any]]] = Field(None, alias="modifierExtension")
    
    # Encounter-specific fields
    identifier: Optional[List[FHIRIdentifier]] = None
    status: FHIREncounterStatus
    status_history: Optional[List[Dict[str, Any]]] = Field(None, alias="statusHistory")
    class_: FHIRCoding = Field(alias="class")
    class_history: Optional[List[Dict[str, Any]]] = Field(None, alias="classHistory")
    type: Optional[List[FHIRCodeableConcept]] = None
    service_type: Optional[FHIRCodeableConcept] = Field(None, alias="serviceType")
    priority: Optional[FHIRCodeableConcept] = None
    subject: Optional[FHIRReference] = None
    episode_of_care: Optional[List[FHIRReference]] = Field(None, alias="episodeOfCare")
    based_on: Optional[List[FHIRReference]] = Field(None, alias="basedOn")
    participant: Optional[List[Dict[str, Any]]] = None
    appointment: Optional[List[FHIRReference]] = None
    period: Optional[Dict[str, Any]] = None
    length: Optional[FHIRQuantity] = None
    reason_code: Optional[List[FHIRCodeableConcept]] = Field(None, alias="reasonCode")
    reason_reference: Optional[List[FHIRReference]] = Field(None, alias="reasonReference")
    diagnosis: Optional[List[Dict[str, Any]]] = None
    account: Optional[List[FHIRReference]] = None
    hospitalization: Optional[Dict[str, Any]] = None
    location: Optional[List[Dict[str, Any]]] = None
    service_provider: Optional[FHIRReference] = Field(None, alias="serviceProvider")
    part_of: Optional[FHIRReference] = Field(None, alias="partOf")


class FHIRSyncStatus(BaseModel):
    """FHIR synchronization status model"""
    entity_id: str = Field(..., description="Internal entity ID")
    entity_type: str = Field(..., description="Type of entity (patient, encounter, etc.)")
    fhir_id: Optional[str] = Field(None, description="FHIR resource ID")
    last_sync: Optional[datetime] = Field(None, description="Last synchronization timestamp")
    sync_status: str = Field("pending", description="Synchronization status")
    sync_errors: Optional[List[str]] = Field(None, description="Synchronization errors")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FHIRSyncRequest(BaseModel):
    """FHIR synchronization request model"""
    entity_id: str
    entity_type: str
    operation: str = Field(..., description="CRUD operation: create, read, update, delete")
    force_sync: bool = Field(False, description="Force synchronization even if up-to-date")


class FHIRSyncResponse(BaseModel):
    """FHIR synchronization response model"""
    success: bool
    fhir_id: Optional[str] = None
    errors: Optional[List[str]] = None
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow)