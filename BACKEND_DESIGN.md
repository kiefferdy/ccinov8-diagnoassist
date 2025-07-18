# DiagnoAssist Backend Design

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Data Architecture](#data-architecture)
5. [API Design](#api-design)
6. [AI Integration](#ai-integration)
7. [Security & Authentication](#security--authentication)
8. [Real-time Features](#real-time-features)
9. [Project Structure](#project-structure)
10. [Database Design](#database-design)
11. [FHIR Integration](#fhir-integration)
12. [Performance & Scalability](#performance--scalability)

## Overview

DiagnoAssist backend is a FastAPI-based medical diagnosis assistant that integrates AI-powered clinical decision support with standardized healthcare data management. The system uses a hybrid FHIR R4 + MongoDB architecture to balance interoperability with application-specific innovation.

### Key Features
- **AI-Powered Voice Documentation**: Gemini 2.5 Pro integration for voice-to-SOAP conversion
- **Clinical Decision Support**: AI-generated differential diagnoses and treatment recommendations
- **Episode-Based Care Model**: Granular patient care tracking beyond traditional encounters
- **Real-time Collaboration**: WebSocket-based auto-save and live updates
- **FHIR R4 Compliance**: Interoperability with Philippine healthcare standards
- **Comprehensive SOAP Documentation**: Structured clinical documentation workflow

## Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                       │
├─────────────────────────────────────────────────────────────────┤
│                    API Gateway / Load Balancer                  │
├─────────────────────────────────────────────────────────────────┤
│                       FastAPI Backend                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Routes    │  │  Services   │  │ Repositories│             │
│  │   Layer     │  │    Layer    │  │    Layer    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                     External Services                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Gemini    │  │ HAPI FHIR   │  │   MongoDB   │             │
│  │ 2.5 Pro API │  │   Server    │  │   Database  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Layered Architecture Pattern
- **Routes Layer**: HTTP endpoint handling, request/response validation
- **Services Layer**: Business logic, workflow orchestration, AI integration
- **Repositories Layer**: Data access abstraction for FHIR and MongoDB
- **Models Layer**: Pydantic schemas for validation and serialization

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Python 3.11+**: Latest Python with type hints and async support
- **Pydantic**: Data validation and serialization using Python type annotations
- **Uvicorn**: ASGI server for high-performance async applications

### Data Layer
- **MongoDB**: Primary database for application-specific data
- **Motor**: Async MongoDB driver for Python
- **HAPI FHIR Server**: Standards-compliant FHIR R4 server
- **HTTPX**: Async HTTP client for FHIR API communication

### AI Integration
- **Google Cloud AI Platform**: Gemini 2.5 Pro API integration
- **OpenAI SDK**: Alternative AI provider support
- **Langchain**: AI workflow orchestration (if needed)

### Authentication & Security
- **JWT (JSON Web Tokens)**: Stateless authentication
- **Passlib**: Password hashing with bcrypt
- **OAuth2**: Third-party authentication support
- **CORS**: Cross-origin resource sharing

### Real-time Features
- **WebSockets**: Real-time communication
- **Redis**: Session management and caching
- **Celery**: Background task processing

### Development & Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Linting

## Data Architecture

### Hybrid FHIR + MongoDB Approach

#### FHIR R4 Data (HAPI FHIR Server)
```python
# Standards-compliant medical data
- Patient demographics and identifiers
- Medical history (conditions, allergies, medications)
- Signed encounters and observations
- Vital signs and lab results
- Appointments and scheduling
- Medication requests and prescriptions
```

#### MongoDB Data (Application-Specific)
```python
# Workflow and innovation data
- Episode-based care model
- SOAP documentation drafts
- AI consultation history
- Voice recordings and transcripts
- Workflow states (draft, in-progress, signed)
- Auto-save and versioning data
- Template system
- Amendment tracking
```

### Data Synchronization Strategy
```python
# Data Flow Pattern
Draft State    → MongoDB Only
In-Progress    → MongoDB + Background FHIR Prep
Signed         → MongoDB + FHIR Sync
Query          → Aggregate from Both Sources
```

## API Design

### RESTful API Structure
```
/api/v1/
├── /auth/
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh
│   └── GET /profile
├── /patients/
│   ├── GET /patients
│   ├── POST /patients
│   ├── GET /patients/{id}
│   ├── PUT /patients/{id}
│   └── DELETE /patients/{id}
├── /episodes/
│   ├── GET /episodes
│   ├── POST /episodes
│   ├── GET /episodes/{id}
│   ├── PUT /episodes/{id}
│   └── GET /patients/{patient_id}/episodes
├── /encounters/
│   ├── GET /encounters
│   ├── POST /encounters
│   ├── GET /encounters/{id}
│   ├── PUT /encounters/{id}
│   ├── POST /encounters/{id}/sign
│   └── GET /episodes/{episode_id}/encounters
├── /soap/
│   ├── PUT /encounters/{id}/soap/subjective
│   ├── PUT /encounters/{id}/soap/objective
│   ├── PUT /encounters/{id}/soap/assessment
│   └── PUT /encounters/{id}/soap/plan
├── /ai/
│   ├── POST /ai/voice/process
│   ├── POST /ai/chat/query
│   ├── GET /ai/insights/{encounter_id}
│   └── GET /ai/recommendations/{encounter_id}
├── /fhir/
│   ├── GET /fhir/patients/{id}
│   ├── POST /fhir/sync/patient/{id}
│   ├── POST /fhir/sync/encounter/{id}
│   └── GET /fhir/observations/{patient_id}
└── /ws/
    ├── /ws/encounter/{id}
    └── /ws/chat/{encounter_id}
```

### Response Format Standards
```python
# Success Response
{
    "success": true,
    "data": {...},
    "timestamp": "2024-01-15T10:30:00Z"
}

# Error Response
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request data",
        "details": [...],
        "timestamp": "2024-01-15T10:30:00Z"
    }
}

# Paginated Response
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "has_next": true,
        "has_prev": false
    }
}
```

## AI Integration

### Gemini 2.5 Pro Integration
```python
class AIService:
    async def process_voice_to_soap(
        self, 
        audio_blob: bytes, 
        patient_context: PatientContext
    ) -> SOAPExtraction:
        """Process voice recording into structured SOAP data"""
        
        # Prepare multimodal input
        context = self._build_patient_context(patient_context)
        
        # Call Gemini 2.5 Pro
        response = await self.gemini_client.generate_content([
            {"text": f"Context: {context}"},
            {"audio": audio_blob},
            {"text": "Extract and organize this clinical information into SOAP format"}
        ])
        
        # Validate and return structured data
        return SOAPExtraction.parse_obj(response.candidates[0].content)
    
    async def generate_clinical_insights(
        self, 
        encounter_data: EncounterData
    ) -> ClinicalInsights:
        """Generate AI-powered clinical insights"""
        
        prompt = self._build_clinical_prompt(encounter_data)
        
        response = await self.gemini_client.generate_content(prompt)
        
        return ClinicalInsights.parse_obj(response.candidates[0].content)
```

### AI-Powered Features
- **Voice-to-SOAP Conversion**: Convert clinical speech to structured documentation
- **Differential Diagnosis**: Generate AI-assisted diagnostic suggestions
- **Clinical Decision Support**: Evidence-based treatment recommendations
- **Risk Assessment**: Automated red flag identification
- **Documentation Templates**: Context-aware template suggestions

## Security & Authentication

### Authentication Flow
```python
# JWT-based authentication
1. User login → Validate credentials
2. Generate JWT token (access + refresh)
3. Include token in Authorization header
4. Validate token on each request
5. Refresh token before expiry
```

### Security Measures
- **HTTPS Only**: All communication encrypted
- **JWT Tokens**: Stateless authentication with expiry
- **Password Security**: bcrypt hashing with salt
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Restricted cross-origin access
- **Audit Logging**: All actions logged with user context

### Data Privacy
- **HIPAA Compliance**: Patient data protection
- **Data Encryption**: At rest and in transit
- **Access Control**: Role-based permissions
- **Data Retention**: Configurable retention policies
- **Audit Trail**: Complete action history

## Real-time Features

### WebSocket Implementation
```python
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, encounter_id: str):
        """Connect to encounter workspace"""
        await websocket.accept()
        self.active_connections[encounter_id] = websocket
    
    async def broadcast_update(self, encounter_id: str, update: dict):
        """Broadcast real-time updates"""
        if encounter_id in self.active_connections:
            await self.active_connections[encounter_id].send_json(update)
```

### Real-time Features
- **Auto-save**: Automatic draft saving every 30 seconds
- **Live Updates**: Real-time SOAP section updates
- **Collaboration**: Multi-user encounter editing
- **Status Notifications**: Workflow state changes
- **AI Chat**: Real-time clinical assistant chat

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   ├── episode.py
│   │   ├── encounter.py
│   │   ├── soap.py
│   │   ├── fhir_models.py
│   │   └── auth.py
│   │
│   ├── schemas/                # API request/response schemas
│   │   ├── __init__.py
│   │   ├── patient_schemas.py
│   │   ├── episode_schemas.py
│   │   ├── encounter_schemas.py
│   │   ├── soap_schemas.py
│   │   └── ai_schemas.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── patient_repository.py
│   │   ├── episode_repository.py
│   │   ├── encounter_repository.py
│   │   └── fhir_repository.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── episode_service.py
│   │   ├── encounter_service.py
│   │   ├── soap_service.py
│   │   ├── ai_service.py
│   │   ├── fhir_service.py
│   │   └── auth_service.py
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── patients.py
│   │   │   ├── episodes.py
│   │   │   ├── encounters.py
│   │   │   ├── soap.py
│   │   │   ├── ai.py
│   │   │   ├── fhir.py
│   │   │   └── websocket.py
│   │   └── api.py
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── fhir_client.py
│   │   ├── ai_client.py
│   │   └── websocket_manager.py
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── fhir_mappers.py
│   │   ├── validation.py
│   │   ├── datetime_utils.py
│   │   └── file_utils.py
│   │
│   └── middleware/             # Custom middleware
│       ├── __init__.py
│       ├── auth_middleware.py
│       ├── cors_middleware.py
│       └── logging_middleware.py
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models/
│   ├── test_repositories/
│   ├── test_services/
│   └── test_api/
│
├── migrations/                 # Database migrations
│   ├── __init__.py
│   └── versions/
│
├── docker/                     # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── scripts/                    # Utility scripts
│   ├── init_db.py
│   ├── seed_data.py
│   └── fhir_sync.py
│
├── requirements/               # Python dependencies
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── .env.example               # Environment variables template
├── .gitignore
├── README.md
└── pyproject.toml             # Python project configuration
```

## Database Design

### MongoDB Collections

#### Patients Collection
```python
{
    "_id": ObjectId("..."),
    "id": "P001",
    "demographics": {
        "name": "John Smith",
        "date_of_birth": "1979-03-15",
        "gender": "male",
        "phone": "+1234567890",
        "email": "john@example.com",
        "address": {...}
    },
    "medical_background": {
        "allergies": [...],
        "medications": [...],
        "chronic_conditions": [...],
        "past_medical_history": "...",
        "family_history": "..."
    },
    "fhir_patient_id": "fhir-patient-123",
    "created_at": ISODate("..."),
    "updated_at": ISODate("...")
}
```

#### Episodes Collection
```python
{
    "_id": ObjectId("..."),
    "id": "E001",
    "patient_id": "P001",
    "chief_complaint": "Persistent cough and fever",
    "category": "acute",
    "status": "active",
    "related_episode_ids": ["E002"],
    "tags": ["respiratory", "infectious"],
    "last_encounter_id": "ENC001",
    "created_at": ISODate("..."),
    "resolved_at": null
}
```

#### Encounters Collection
```python
{
    "_id": ObjectId("..."),
    "id": "ENC001",
    "episode_id": "E001",
    "patient_id": "P001",
    "type": "initial",
    "status": "draft",
    "provider": {
        "id": "DR001",
        "name": "Dr. Smith",
        "role": "Primary Care Physician"
    },
    "soap": {
        "subjective": {...},
        "objective": {...},
        "assessment": {...},
        "plan": {...}
    },
    "ai_consultation": {
        "voice_processing": [...],
        "chat_history": [...],
        "insights": [...]
    },
    "workflow": {
        "auto_save_enabled": true,
        "last_saved": ISODate("..."),
        "amendments": [...]
    },
    "fhir_encounter_id": null,
    "created_at": ISODate("..."),
    "updated_at": ISODate("..."),
    "signed_at": null,
    "signed_by": null
}
```

### MongoDB Indexes
```python
# Performance optimization indexes
db.patients.createIndex({"id": 1}, {"unique": True})
db.patients.createIndex({"demographics.email": 1})
db.patients.createIndex({"fhir_patient_id": 1})

db.episodes.createIndex({"id": 1}, {"unique": True})
db.episodes.createIndex({"patient_id": 1, "status": 1})
db.episodes.createIndex({"created_at": -1})

db.encounters.createIndex({"id": 1}, {"unique": True})
db.encounters.createIndex({"episode_id": 1})
db.encounters.createIndex({"patient_id": 1, "status": 1})
db.encounters.createIndex({"created_at": -1})
```

## FHIR Integration

### FHIR Resource Mapping

#### Patient Resource
```python
class FHIRPatientMapper:
    @staticmethod
    def to_fhir(patient: PatientModel) -> FHIRPatient:
        return FHIRPatient(
            resourceType="Patient",
            name=[{
                "family": patient.demographics.name.split()[-1],
                "given": patient.demographics.name.split()[:-1]
            }],
            birthDate=patient.demographics.date_of_birth,
            gender=patient.demographics.gender,
            telecom=[
                {"system": "phone", "value": patient.demographics.phone},
                {"system": "email", "value": patient.demographics.email}
            ]
        )
```

#### Observation Resources (Vital Signs)
```python
class VitalSignsMapper:
    @staticmethod
    def to_fhir_observations(
        vitals: VitalSigns, 
        patient_id: str
    ) -> List[FHIRObservation]:
        observations = []
        
        if vitals.blood_pressure:
            observations.append(FHIRObservation(
                resourceType="Observation",
                status="final",
                code={"coding": [{
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel"
                }]},
                subject={"reference": f"Patient/{patient_id}"},
                component=[
                    {
                        "code": {"coding": [{
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }]},
                        "valueQuantity": {
                            "value": vitals.systolic_bp,
                            "unit": "mmHg"
                        }
                    }
                ]
            ))
        
        return observations
```

### FHIR Synchronization Strategy
```python
class FHIRSyncService:
    async def sync_signed_encounter(self, encounter_id: str) -> bool:
        """Sync signed encounter to FHIR server"""
        
        # 1. Get encounter data
        encounter = await self.encounter_repo.get_by_id(encounter_id)
        
        if encounter.status != "signed":
            return False
        
        # 2. Convert to FHIR resources
        fhir_encounter = self.mapper.to_fhir_encounter(encounter)
        fhir_observations = self.mapper.to_fhir_observations(encounter.soap.objective.vitals)
        fhir_conditions = self.mapper.to_fhir_conditions(encounter.soap.assessment)
        
        # 3. Save to FHIR server
        try:
            encounter_ref = await self.fhir_client.create_encounter(fhir_encounter)
            
            for obs in fhir_observations:
                obs.encounter = {"reference": encounter_ref}
                await self.fhir_client.create_observation(obs)
            
            for condition in fhir_conditions:
                condition.encounter = {"reference": encounter_ref}
                await self.fhir_client.create_condition(condition)
            
            # 4. Update MongoDB with FHIR references
            await self.encounter_repo.update_fhir_references(
                encounter_id, 
                encounter_ref
            )
            
            return True
            
        except FHIRException as e:
            logger.error(f"FHIR sync failed: {e}")
            return False
```

## Performance & Scalability

### Caching Strategy
```python
# Redis caching for frequently accessed data
- Patient demographics (5 min TTL)
- Episode summaries (10 min TTL)
- AI insights (1 hour TTL)
- FHIR resources (15 min TTL)
```

### Database Optimization
```python
# MongoDB optimization
- Compound indexes for common queries
- Aggregation pipelines for complex queries
- Connection pooling
- Read replicas for scaling
```

### API Performance
```python
# FastAPI optimization
- Async/await throughout
- Response caching
- Request compression
- Connection pooling
- Background tasks for heavy operations
```

### Monitoring & Observability
```python
# Monitoring stack
- Prometheus metrics
- Grafana dashboards
- ELK stack for logging
- Health check endpoints
- Performance monitoring
```

## Error Handling

### Exception Hierarchy
```python
class DiagnoAssistException(Exception):
    """Base exception for DiagnoAssist"""
    pass

class ValidationException(DiagnoAssistException):
    """Data validation errors"""
    pass

class FHIRException(DiagnoAssistException):
    """FHIR integration errors"""
    pass

class AIServiceException(DiagnoAssistException):
    """AI service errors"""
    pass

class DatabaseException(DiagnoAssistException):
    """Database operation errors"""
    pass
```

### Error Response Format
```python
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid encounter data",
        "details": {
            "field": "soap.objective.vitals.heart_rate",
            "issue": "Value must be between 30 and 200"
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456"
    }
}
```

## Configuration Management

### Environment Variables
```python
# .env file structure
DATABASE_URL=mongodb://localhost:27017/diagnoassist
FHIR_SERVER_URL=http://localhost:8080/fhir
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_jwt_secret
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

### Configuration Classes
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    fhir_server_url: str
    gemini_api_key: str
    jwt_secret_key: str
    redis_url: str
    cors_origins: List[str]
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

This comprehensive backend design document provides the foundation for building a robust, scalable, and maintainable medical diagnosis assistant that integrates modern AI capabilities with established healthcare standards.