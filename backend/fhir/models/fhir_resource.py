from sqlalchemy import Column, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from config.database import Base

class FHIRResource(Base):
    """Model for storing FHIR resources"""
    
    __tablename__ = "fhir_resources"
    
    id = Column(String, primary_key=True, index=True)
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(String, nullable=False, index=True)
    version_id = Column(String, nullable=True)
    fhir_data = Column(JSON, nullable=False)
    internal_id = Column(String, nullable=True, index=True)  # Link to internal tables
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())