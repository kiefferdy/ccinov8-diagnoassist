# DiagnoAssist

An AI-powered medical diagnosis assistant that enhances doctors' workflows and helps them diagnose patients more effectively.

## Getting Started

This project consists of two main components:

- **Frontend** (`frontend/`) - React-based user interface
- **Backend** (`backend/`) - FastAPI server (to be implemented)

To set up each component, refer to the respective README files in their directories:
- [Frontend Setup](./frontend/README.md)
- Backend Setup (coming soon)

## Features

- **Patient Information Management** - Comprehensive data collection with medical history tracking
- **Dynamic Clinical Assessment** - AI-powered adaptive questioning based on chief complaint
- **Physical Examination** - Vital signs recording and physical measurements
- **AI Diagnostic Analysis** - Differential diagnosis generation with probability scoring
- **Laboratory Tests & Results** - Test ordering, result entry, and interpretation
- **Final Diagnosis & Treatment** - Refined diagnosis with AI-generated treatment recommendations

## TODO

- Backend implementation
- Real AI model integration for diagnosis
- PDF export and EHR system integration
- Patient history database

## Notes for Backend Integration

The frontend is designed to work with a FastAPI backend. Key API endpoints needed:

- `POST /api/patients` - Create new patient
- `POST /api/clinical-assessment/questions` - Get dynamic questions
- `POST /api/diagnosis/analyze` - Generate differential diagnoses
- `POST /api/diagnosis/refine` - Refine diagnosis with test results
- `POST /api/treatment/plan` - Generate treatment recommendations
- `GET/POST /api/patients/{id}/records` - Patient record management
