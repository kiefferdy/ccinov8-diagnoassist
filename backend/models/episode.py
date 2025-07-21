"""
Episode Database Model
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Episode(Base):
    """
    Episode model for storing medical encounters/episodes of care
    """
    __tablename__ = "episodes"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Patient reference
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Episode details
    chief_complaint = Column(String(500), nullable=False)
    status = Column(String(50), default="in-progress")  # in-progress, completed, cancelled
    encounter_type = Column(String(50), default="outpatient")  # outpatient, inpatient, emergency
    priority = Column(String(50), default="routine")  # routine, urgent, emergent
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    
    # Provider and location
    provider_id = Column(String(100))  # Healthcare provider identifier
    location = Column(String(200))
    
    # Clinical data
    vital_signs = Column(JSON, default=dict)
    symptoms = Column(JSON, default=list)
    physical_exam_findings = Column(JSON, default=dict)
    
    # Notes and assessments
    clinical_notes = Column(Text)
    assessment_notes = Column(Text)
    plan_notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="episodes")
    diagnoses = relationship("Diagnosis", back_populates="episode", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="episode", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Episode(id='{self.id}', patient_id='{self.patient_id}', complaint='{self.chief_complaint}')>"
    
    @property
    def duration(self):
        """Calculate episode duration"""
        if not self.end_time:
            return None
        return self.end_time - self.start_time
    
    @property
    def is_active(self):
        """Check if episode is currently active"""
        return self.status == "in-progress"
    
    def to_dict(self):
        """Convert episode to dictionary"""
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "chief_complaint": self.chief_complaint,
            "status": self.status,
            "encounter_type": self.encounter_type,
            "priority": self.priority,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "provider_id": self.provider_id,
            "location": self.location,
            "vital_signs": self.vital_signs or {},
            "symptoms": self.symptoms or [],
            "physical_exam_findings": self.physical_exam_findings or {},
            "clinical_notes": self.clinical_notes,
            "assessment_notes": self.assessment_notes,
            "plan_notes": self.plan_notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }