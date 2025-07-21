"""
Diagnosis Database Model
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Diagnosis(Base):
    """
    Diagnosis model for storing AI-generated and confirmed diagnoses
    """
    __tablename__ = "diagnoses"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Episode reference
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id"), nullable=False)
    
    # Diagnosis information
    condition_name = Column(String(300), nullable=False)
    icd10_code = Column(String(20))
    snomed_code = Column(String(50))
    
    # AI analysis data
    ai_probability = Column(Float)  # 0.0 to 1.0
    confidence_level = Column(String(50))  # low, moderate, high
    ai_reasoning = Column(Text)
    
    # Clinical validation
    physician_confirmed = Column(Boolean, default=False)
    physician_notes = Column(Text)
    final_diagnosis = Column(Boolean, default=False)  # Is this the final/primary diagnosis
    
    # Supporting data
    supporting_symptoms = Column(JSON, default=list)
    differential_diagnoses = Column(JSON, default=list)
    red_flags = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), default="ai_system")  # ai_system, physician, etc.
    
    # Relationships
    episode = relationship("Episode", back_populates="diagnoses")
    treatments = relationship("Treatment", back_populates="diagnosis")
    
    def __repr__(self):
        return f"<Diagnosis(id='{self.id}', condition='{self.condition_name}', probability={self.ai_probability})>"
    
    @property
    def probability_percentage(self):
        """Get probability as percentage"""
        return round(self.ai_probability * 100, 1) if self.ai_probability else None
    
    def to_dict(self):
        """Convert diagnosis to dictionary"""
        return {
            "id": str(self.id),
            "episode_id": str(self.episode_id),
            "condition_name": self.condition_name,
            "icd10_code": self.icd10_code,
            "snomed_code": self.snomed_code,
            "ai_probability": self.ai_probability,
            "probability_percentage": self.probability_percentage,
            "confidence_level": self.confidence_level,
            "ai_reasoning": self.ai_reasoning,
            "physician_confirmed": self.physician_confirmed,
            "physician_notes": self.physician_notes,
            "final_diagnosis": self.final_diagnosis,
            "supporting_symptoms": self.supporting_symptoms or [],
            "differential_diagnoses": self.differential_diagnoses or [],
            "red_flags": self.red_flags or [],
            "next_steps": self.next_steps or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }