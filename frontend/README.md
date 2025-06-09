# DiagnoAssist Frontend

An AI-powered medical diagnosis assistant that enhances doctors' workflows and helps them diagnose patients more effectively.

## Features

### 1. **Patient Information & Medical History**
- Comprehensive patient data collection
- Medical history tracking
- Medication and allergy management
- Auto-calculated BMI

### 2. **Dynamic Clinical Assessment**
- AI-powered adaptive questioning based on chief complaint
- Follow-up questions that evolve based on patient responses
- Additional clinical notes capability

### 3. **Physical Examination**
- Vital signs recording (BP, HR, Temperature, RR, O2 Sat)
- Physical measurements with automatic BMI calculation
- Additional findings documentation

### 4. **AI Diagnostic Analysis**
- Differential diagnosis generation based on clinical data
- Probability and confidence scoring
- Supporting and contradicting evidence display
- Doctor feedback integration
- Recommended tests for each diagnosis

### 5. **Laboratory Tests & Results**
- Test ordering from AI recommendations
- Custom test addition
- Result entry with interpretation
- Status tracking for each test

### 6. **Final Diagnosis & Treatment Plan**
- Refined diagnosis based on test results
- AI-generated treatment recommendations
- Prescription management
- Medical assessment note generation
- Export and print capabilities

## Tech Stack

- **React** - UI framework
- **Tailwind CSS** - Styling
- **React Router DOM** - Navigation
- **React Hook Form** - Form management
- **Lucide React** - Icons
- **Vite** - Build tool

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd /Users/kiefferdy/Desktop/ccinov8-diagnoassist/diagnoassist-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/
│   ├── Layout/          # Main layout with sidebar
│   ├── Home/           # Landing page
│   ├── Patient/        # Patient info & clinical assessment
│   ├── Diagnosis/      # Physical exam & diagnostic analysis
│   ├── Tests/          # Test management
│   └── Treatment/      # Final diagnosis & treatment
├── contexts/           # React contexts (PatientContext)
├── App.jsx            # Main app component
└── main.jsx           # Entry point
```

## Key Features

- **Responsive Design**: Works on desktop and tablet devices
- **Step-by-Step Workflow**: Guided process following clinical best practices
- **Real-time Validation**: Form validation and error handling
- **State Management**: Centralized patient data management
- **Mock AI Integration**: Simulated AI responses (ready for backend integration)

## Future Enhancements

- Backend integration with FastAPI
- Real AI model integration for diagnosis
- PDF export functionality
- Patient history database
- Multi-language support
- Voice input capabilities
- Integration with EHR systems

## Notes for Backend Integration

The frontend is designed to work with a FastAPI backend. Key API endpoints needed:

- `POST /api/patients` - Create new patient
- `POST /api/clinical-assessment/questions` - Get dynamic questions
- `POST /api/diagnosis/analyze` - Generate differential diagnoses
- `POST /api/diagnosis/refine` - Refine diagnosis with test results
- `POST /api/treatment/plan` - Generate treatment recommendations
- `GET/POST /api/patients/{id}/records` - Patient record management

## License

This project is part of the CCINOV8 initiative.
