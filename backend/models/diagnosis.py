"""
Diagnosis Database Model - Matches Supabase schema exactly
"""

from sqlalchemy import Column, String, DateTime, Text, Numeric, Boolean
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

class Diagnosis(Base):
    """
    Diagnosis model for storing diagnostic information
    """
    __tablename__ = "diagnoses"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Episode reference
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id"), nullable=False)
    
    # Diagnosis details
    condition_name = Column(String(500), nullable=False)
    icd10_code = Column(String(20))
    snomed_code = Column(String(50))
    
    # AI-assisted diagnosis
    ai_probability = Column(Numeric)
    confidence_level = Column(String(20), default="low")
    ai_reasoning = Column(Text)
    
    # Physician validation
    physician_confirmed = Column(Boolean, default=False)
    physician_notes = Column(Text)
    final_diagnosis = Column(Boolean, default=False)
    
    # Clinical context
    supporting_symptoms = Column(Text, default="")
    differential_diagnoses = Column(Text, default="")
    red_flags = Column(Text, default="")
    next_steps = Column(Text, default="")
    
    # System fields
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), default="ai_system")
    
    # Relationships
    episode = relationship("Episode", back_populates="diagnoses")
    treatments = relationship("Treatment", back_populates="diagnosis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Diagnosis(id='{self.id}', condition='{self.condition_name}', episode_id='{self.episode_id}')>"