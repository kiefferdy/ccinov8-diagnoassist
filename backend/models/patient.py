"""
Patient Database Model - Matches SQL Schema Exactly
"""

from sqlalchemy import Column, String, Date, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date, timezone
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Patient(Base):
    """
    Patient model - matches SQL schema exactly
    """
    __tablename__ = "patients"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Medical Record Number - unique identifier for the patient
    medical_record_number = Column(String, unique=True, nullable=False)
    
    # Demographics
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, default="unknown")
    
    # Contact information
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(Text)
    
    # Emergency contact
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    emergency_contact_relationship = Column(String)
    
    # Medical information - FIXED: Use Text instead of JSON to match SQL
    medical_history = Column(Text, default="")
    allergies = Column(Text, default="")
    current_medications = Column(Text, default="")
    
    # System fields - matches SQL exactly
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String, default="system")
    
    # Relationships
    episodes = relationship("Episode", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id='{self.id}', mrn='{self.medical_record_number}', name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient's current age"""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred this year
        if today < date(today.year, self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
            
        return age