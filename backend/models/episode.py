"""
Episode Database Model - Matches Supabase schema exactly
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime, timezone
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Episode(Base):
    """
    Episode model for storing patient encounters and visits
    """
    __tablename__ = "episodes"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Patient reference
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Episode details
    chief_complaint = Column(Text, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    encounter_type = Column(String(50), default="outpatient", nullable=False)
    priority = Column(String(50), default="routine", nullable=False)
    
    # Vital signs
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    temperature = Column(Numeric)
    respiratory_rate = Column(Integer)
    oxygen_saturation = Column(Integer)
    
    # Clinical information
    symptoms = Column(Text, default="")
    physical_exam_findings = Column(Text, default="")
    clinical_notes = Column(Text, default="")
    assessment_notes = Column(Text, default="")
    plan_notes = Column(Text, default="")
    
    # Episode timing
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_date = Column(DateTime)
    
    # Provider and location
    provider_id = Column(String(100))
    location = Column(String(200))
    
    # System fields
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(100), default="system")
    
    # Relationships
    patient = relationship("Patient", back_populates="episodes")
    encounters = relationship("Encounter", back_populates="episode", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="episode", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="episode", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Episode(id='{self.id}', patient_id='{self.patient_id}', complaint='{self.chief_complaint[:50]}...')>"