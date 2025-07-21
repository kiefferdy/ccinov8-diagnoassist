"""
Treatment Database Model
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

class Treatment(Base):
    """
    Treatment model for storing treatment plans and interventions
    """
    __tablename__ = "treatments"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id"), nullable=False)
    diagnosis_id = Column(UUID(as_uuid=True), ForeignKey("diagnoses.id"))
    
    # Treatment plan information
    treatment_type = Column(String(100))  # medication, procedure, therapy, etc.
    treatment_name = Column(String(300), nullable=False)
    description = Column(Text)
    
    # Medication-specific fields
    medication_name = Column(String(200))
    dosage = Column(String(100))
    frequency = Column(String(100))
    route = Column(String(50))  # oral, IV, IM, etc.
    duration = Column(String(100))
    
    # Instructions and monitoring
    instructions = Column(Text)
    monitoring_requirements = Column(JSON, default=list)
    contraindications = Column(JSON, default=list)
    side_effects = Column(JSON, default=list)
    drug_interactions = Column(JSON, default=list)
    
    # Status and approval
    status = Column(String(50), default="planned")  # planned, approved, active, completed, discontinued
    approved_by = Column(String(100))  # Healthcare provider who approved
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Non-pharmacological interventions
    lifestyle_modifications = Column(JSON, default=list)
    follow_up_instructions = Column(Text)
    patient_education = Column(JSON, default=list)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), default="ai_system")
    
    # Relationships
    episode = relationship("Episode", back_populates="treatments")
    diagnosis = relationship("Diagnosis", back_populates="treatments")
    
    def __repr__(self):
        return f"<Treatment(id='{self.id}', name='{self.treatment_name}', status='{self.status}')>"
    
    @property
    def is_active(self):
        """Check if treatment is currently active"""
        return self.status in ["approved", "active"]
    
    @property
    def is_medication(self):
        """Check if this is a medication treatment"""
        return self.treatment_type == "medication"
    
    def to_dict(self):
        """Convert treatment to dictionary"""
        return {
            "id": str(self.id),
            "episode_id": str(self.episode_id),
            "diagnosis_id": str(self.diagnosis_id) if self.diagnosis_id else None,
            "treatment_type": self.treatment_type,
            "treatment_name": self.treatment_name,
            "description": self.description,
            "medication_details": {
                "name": self.medication_name,
                "dosage": self.dosage,
                "frequency": self.frequency,
                "route": self.route,
                "duration": self.duration
            } if self.is_medication else None,
            "instructions": self.instructions,
            "monitoring_requirements": self.monitoring_requirements or [],
            "contraindications": self.contraindications or [],
            "side_effects": self.side_effects or [],
            "drug_interactions": self.drug_interactions or [],
            "status": self.status,
            "approved_by": self.approved_by,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "lifestyle_modifications": self.lifestyle_modifications or [],
            "follow_up_instructions": self.follow_up_instructions,
            "patient_education": self.patient_education or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }