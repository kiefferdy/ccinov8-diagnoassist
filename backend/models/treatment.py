"""
Treatment Database Model - Matches Supabase schema exactly
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Treatment(Base):
    """
    Treatment model for storing treatment plans and prescriptions
    """
    __tablename__ = "treatments"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id"), nullable=False)
    diagnosis_id = Column(UUID(as_uuid=True), ForeignKey("diagnoses.id"))
    
    # Treatment details
    treatment_type = Column(String(50), default="medication")
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Medication specifics
    dosage = Column(String(100))
    frequency = Column(String(100))
    route = Column(String(50))
    duration = Column(String(100))
    instructions = Column(Text)
    
    # Clinical information
    monitoring_requirements = Column(Text, default="")
    contraindications = Column(Text, default="")
    side_effects = Column(Text, default="")
    drug_interactions = Column(Text, default="")
    
    # Treatment timing
    status = Column(String(50), default="active", nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    
    # Patient care
    lifestyle_modifications = Column(Text, default="")
    follow_up_instructions = Column(Text, default="")
    patient_education = Column(Text, default="")
    
    # Provider information
    prescriber = Column(String(100))
    approved_by = Column(String(100))
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), default="system")
    
    # Relationships
    episode = relationship("Episode", back_populates="treatments")
    diagnosis = relationship("Diagnosis", back_populates="treatments")
    
    def __repr__(self):
        return f"<Treatment(id='{self.id}', name='{self.name}', episode_id='{self.episode_id}')>"