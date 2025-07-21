"""
Patient Database Model
"""

from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

try:
    from config.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class Patient(Base):
    """
    Patient model for storing patient demographic and basic information
    """
    __tablename__ = "patients"
    
    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Medical Record Number - unique identifier for the patient
    medical_record_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))  # male, female, other, unknown
    
    # Contact information
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    address = Column(Text)
    
    # Emergency contact
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    
    # Medical information
    medical_history = Column(JSON, default=list)  # List of conditions
    allergies = Column(JSON, default=list)  # List of allergies
    current_medications = Column(JSON, default=list)  # List of medications
    
    # System fields
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    episodes = relationship("Episode", back_populates="patient", cascade="all, delete-orphan")
    
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