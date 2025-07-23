"""
FHIR Resource Database Model - CORRECTED to match SQL schema exactly
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import json

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class FHIRResource(Base):
    """
    Generic FHIR Resource model for storing any FHIR resource as JSON
    This follows the FHIR R4 specification for resource storage
    CORRECTED to match SQL schema exactly
    """
    __tablename__ = "fhir_resources"
    
    # Primary identifier (database internal)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FHIR resource identification
    resource_type = Column(String(100), nullable=False, index=True)  # Patient, Encounter, etc.
    resource_id = Column(String(100), nullable=False, index=True)    # FHIR resource ID
    version_id = Column(String(50), default="1", nullable=False)     # FHIR version ID
    
    # FHIR resource data (stored as TEXT to match SQL schema)
    fhir_data = Column(Text, nullable=False)  # Complete FHIR resource as JSON string
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Optional fields for easier querying
    patient_reference = Column(String(100), index=True)  # Patient/[id] for quick patient filtering
    encounter_reference = Column(String(100), index=True)  # Encounter/[id] for encounter filtering
    subject_reference = Column(String(100), index=True)  # Generic subject reference
    
    # Status and flags (CORRECTED: use 'status' not 'active' to match SQL)
    status = Column(String(20), default="active", nullable=False)  # active, inactive, deleted
    source_system = Column(String(100), default="diagnoassist", nullable=False)  # System that created the resource
    
    # Create composite indexes for common queries
    __table_args__ = (
        Index('idx_resource_type_id', 'resource_type', 'resource_id'),
        Index('idx_patient_type', 'patient_reference', 'resource_type'),
        Index('idx_encounter_type', 'encounter_reference', 'resource_type'),
        Index('idx_status_resources', 'status', 'resource_type'),
    )
    
    def __repr__(self):
        return f"<FHIRResource(resource_type='{self.resource_type}', resource_id='{self.resource_id}', version='{self.version_id}')>"
    
    @property
    def fhir_data_dict(self):
        """Get FHIR data as dictionary"""
        try:
            return json.loads(self.fhir_data) if self.fhir_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @fhir_data_dict.setter
    def fhir_data_dict(self, value):
        """Set FHIR data from dictionary"""
        self.fhir_data = json.dumps(value) if value else "{}"
    
    @classmethod
    def create_from_fhir_resource(cls, fhir_resource_dict, resource_id=None):
        """
        Create FHIRResource from FHIR resource dictionary
        
        Args:
            fhir_resource_dict: Dictionary containing FHIR resource data
            resource_id: Optional resource ID (will generate if not provided)
            
        Returns:
            FHIRResource instance
        """
        resource_type = fhir_resource_dict.get("resourceType")
        if not resource_type:
            raise ValueError("FHIR resource must have resourceType")
        
        if not resource_id:
            resource_id = fhir_resource_dict.get("id", str(uuid.uuid4()))
        
        # Extract references for indexing
        patient_ref = None
        encounter_ref = None
        subject_ref = None
        
        # Extract patient reference based on resource type
        if resource_type == "Patient":
            patient_ref = f"Patient/{resource_id}"
        elif "subject" in fhir_resource_dict:
            subject_ref = fhir_resource_dict["subject"].get("reference")
            if subject_ref and subject_ref.startswith("Patient/"):
                patient_ref = subject_ref
        elif "patient" in fhir_resource_dict:
            patient_ref = fhir_resource_dict["patient"].get("reference")
        
        # Extract encounter reference
        if resource_type == "Encounter":
            encounter_ref = f"Encounter/{resource_id}"
        elif "encounter" in fhir_resource_dict:
            encounter_ref = fhir_resource_dict["encounter"].get("reference")
        elif "context" in fhir_resource_dict:
            context_ref = fhir_resource_dict["context"].get("reference", "")
            if context_ref.startswith("Encounter/"):
                encounter_ref = context_ref
        
        # Ensure the FHIR resource has proper metadata
        fhir_data = fhir_resource_dict.copy()
        fhir_data["id"] = resource_id
        
        if "meta" not in fhir_data:
            fhir_data["meta"] = {}
        
        fhir_data["meta"]["lastUpdated"] = datetime.utcnow().isoformat() + "Z"
        fhir_data["meta"]["versionId"] = "1"
        
        return cls(
            resource_type=resource_type,
            resource_id=resource_id,
            version_id="1",
            fhir_data=json.dumps(fhir_data),  # Store as JSON string
            patient_reference=patient_ref,
            encounter_reference=encounter_ref,
            subject_reference=subject_ref or patient_ref
        )
    
    def update_fhir_data(self, fhir_resource_dict):
        """
        Update the FHIR resource data and increment version
        
        Args:
            fhir_resource_dict: Updated FHIR resource dictionary
        """
        # Increment version
        current_version = int(self.version_id)
        new_version = str(current_version + 1)
        
        # Update FHIR data
        fhir_data = fhir_resource_dict.copy()
        fhir_data["id"] = self.resource_id
        
        if "meta" not in fhir_data:
            fhir_data["meta"] = {}
        
        fhir_data["meta"]["lastUpdated"] = datetime.utcnow().isoformat() + "Z"
        fhir_data["meta"]["versionId"] = new_version
        
        self.fhir_data = json.dumps(fhir_data)
        self.version_id = new_version
        self.last_updated = datetime.utcnow()
    
    def get_fhir_resource(self):
        """
        Get the FHIR resource as a dictionary
        
        Returns:
            Dictionary containing the FHIR resource
        """
        return self.fhir_data_dict
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "version_id": self.version_id,
            "fhir_data": self.fhir_data_dict,
            "patient_reference": self.patient_reference,
            "encounter_reference": self.encounter_reference,
            "subject_reference": self.subject_reference,
            "status": self.status,
            "source_system": self.source_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }