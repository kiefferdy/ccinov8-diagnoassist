# DiagnoAssist

An AI-powered medical diagnosis assistant that enhances doctors' workflows with episode-based care management, voice documentation, and clinical decision support.

## Architecture

```
Frontend (React) → FastAPI Backend → MongoDB + HAPI FHIR (R4)
                      ↓
                 Gemini 2.5 Pro (AI)
```

## Key Features

- **AI Voice Documentation** - Convert clinical speech to structured SOAP notes
- **Clinical Decision Support** - AI-powered differential diagnosis and treatment recommendations  
- **Episode-Based Care** - Track patient problems across multiple encounters
- **FHIR R4 Compliance** - Interoperability with Philippine healthcare standards
- **Real-time Collaboration** - Auto-save and live updates via WebSocket
- **Secure & Compliant** - JWT authentication with medical data protection

## Tech Stack

**Frontend**: React, Tailwind CSS, React Router, React Hook Form  
**Backend**: FastAPI, Python 3.11+, Pydantic, Motor (MongoDB), HTTPX  
**AI**: Google Gemini 2.5 Pro, Speech-to-text, Clinical NLP  
**Data**: MongoDB, HAPI FHIR Server, Redis (caching)  
**Infrastructure**: Docker, Docker Compose

## Quick Start

### Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

### Backend (Coming Soon)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
├── frontend/           # React application
├── backend/           # FastAPI application (in development)
├── BACKEND_DESIGN.md      # Detailed architecture design
├── BACKEND_IMPLEMENTATION.md # 8-phase implementation plan
└── README.md          # This file
```

## Documentation

- **[Backend Design](./BACKEND_DESIGN.md)** - Comprehensive architecture and design decisions
- **[Implementation Plan](./BACKEND_IMPLEMENTATION.md)** - 8-phase development roadmap
- **[Frontend Setup](./frontend/README.md)** - React application setup guide

## Development Status

- **Frontend Prototype** - Complete with demo data
- **Backend Development** - In progress (see implementation plan)
- **Database Design** - FHIR R4 + MongoDB hybrid approach
- **AI Integration** - Gemini 2.5 Pro integration planned

## Philippine Healthcare Compliance

This project follows Philippine healthcare standards:
- **FHIR R4** implementation for interoperability
- **PHCDI** (Philippine Core Data for Interoperability) compliance
- Integration with existing **CHITS** systems
- **Universal Health Care (UHC) Act** alignment
