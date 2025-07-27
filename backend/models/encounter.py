"""
Encounter Database Model - Matches frontend SOAP structure
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean
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

class Encounter(Base):
    """
    Encounter model for storing individual patient visits with SOAP documentation
    """
    __tablename__ = "encounters"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key relationships
    episode_id = Column(UUID(as_uuid=True), ForeignKey("episodes.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Encounter metadata
    type = Column(String(50), default="follow-up", nullable=False)  # initial, follow-up, urgent, telemedicine, phone, lab-review
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(20), default="draft", nullable=False)  # draft, signed
    
    # Provider information
    provider_id = Column(String(100))
    provider_name = Column(String(200))
    provider_role = Column(String(100))
    
    # SOAP Documentation - stored as JSON for flexibility
    # Subjective section
    soap_subjective = Column(JSON)  # {chiefComplaint, hpi, ros, pmh, medications, allergies, socialHistory, familyHistory, voiceNotes, lastUpdated}
    
    # Objective section  
    soap_objective = Column(JSON)   # {vitals, physicalExam, diagnosticTests, voiceNotes, lastUpdated}
    
    # Assessment section
    soap_assessment = Column(JSON)  # {clinicalImpression, differentialDiagnosis, workingDiagnosis, riskAssessment, aiConsultation, lastUpdated}
    
    # Plan section
    soap_plan = Column(JSON)        # {medications, procedures, referrals, followUp, patientEducation, activityRestrictions, dietRecommendations, lastUpdated}
    
    # Additional encounter data
    documents = Column(JSON)        # Array of document references
    amendments = Column(JSON)       # Array of amendments to the encounter
    
    # Signing information
    signed_at = Column(DateTime)
    signed_by = Column(String(200))
    
    # System fields
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(100), default="system")
    
    # Relationships
    episode = relationship("Episode", back_populates="encounters")
    patient = relationship("Patient", back_populates="encounters")
    
    def __repr__(self):
        return f"<Encounter(id='{self.id}', episode_id='{self.episode_id}', type='{self.type}', status='{self.status}')>"
    
    @property
    def is_signed(self):
        """Check if encounter is signed"""
        return self.status == "signed"
    
    @property
    def chief_complaint(self):
        """Extract chief complaint from SOAP subjective data"""
        if self.soap_subjective:
            return self.soap_subjective.get('chiefComplaint', '')
        return ''
    
    @property
    def completion_percentage(self):
        """Calculate documentation completion percentage"""
        completed = 0
        total = 4
        
        # Check Subjective
        if self.soap_subjective and (self.soap_subjective.get('hpi') or self.soap_subjective.get('ros')):
            completed += 1
            
        # Check Objective  
        if self.soap_objective:
            vitals = self.soap_objective.get('vitals', {})
            physical_exam = self.soap_objective.get('physicalExam', {})
            if any(vitals.values()) or physical_exam.get('general'):
                completed += 1
                
        # Check Assessment
        if self.soap_assessment and self.soap_assessment.get('clinicalImpression'):
            completed += 1
            
        # Check Plan
        if self.soap_plan:
            plan_data = self.soap_plan
            if (plan_data.get('medications') or 
                plan_data.get('procedures') or 
                plan_data.get('followUp', {}).get('timeframe')):
                completed += 1
                
        return round((completed / total) * 100)