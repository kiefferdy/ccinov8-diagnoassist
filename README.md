# DiagnoAssist - AI-Powered Diagnostic Assistant

DiagnoAssist is a modern, intuitive frontend application designed to enhance doctors' workflows and assist with patient diagnosis. Built with React and Tailwind CSS, it provides a comprehensive digital platform for medical professionals to streamline their diagnostic process.

## ✨ Features

### 🏥 Clinical Workflow Management
- **Patient Information & Clinical Assessment**: Dynamic questioning system that adapts based on patient responses
- **Physical Examination**: Comprehensive vital signs recording and system-specific examinations
- **AI Diagnostic Analysis**: Intelligent differential diagnosis generation with confidence scoring
- **Recommended Tests**: Smart test recommendations with cost estimates and urgency levels
- **Test Results Management**: Structured input for laboratory and imaging results
- **Final Diagnosis & Treatment**: Complete diagnostic conclusion with treatment planning

### 🤖 AI-Powered Features
- Dynamic follow-up question generation based on chief complaints
- Intelligent differential diagnosis with supporting/contradicting factors
- Test recommendations based on patient presentation
- Refined diagnosis analysis incorporating test results
- Treatment suggestions with dosage and duration recommendations

### 💻 Modern User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Step-by-Step Workflow**: Clear progression through diagnostic process
- **Auto-save Functionality**: Automatic saving with user notifications
- **Keyboard Shortcuts**: Efficient navigation for power users
- **Notification System**: Real-time feedback and status updates
- **Accessibility**: Full keyboard navigation and screen reader support

### 🎨 Professional Interface
- Clean, medical-focused design with intuitive icons
- Progress tracking with visual step indicators
- Real-time confidence scoring for AI recommendations
- Comprehensive data validation and error handling
- Print-friendly reports and export capabilities

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd ccinov8-diagnoassist
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:5173` to view the application

### Build for Production
```bash
npm run build
```

## 🏗️ Technical Architecture

### Frontend Stack
- **React 18**: Modern React with hooks and functional components
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Lucide React**: Beautiful, customizable icons
- **UUID**: Unique identifier generation

### State Management
- **React Context**: Global patient data management
- **useReducer**: Complex state updates with actions
- **Local Storage**: Data persistence across sessions

### Key Components

#### Context Management (`src/context/`)
- `PatientDataContext.jsx`: Global state management for patient workflow data

#### Layout Components (`src/components/Layout/`)
- `Layout.jsx`: Main application layout with navigation
- `NotificationSystem.jsx`: Toast notifications and user feedback
- `KeyboardShortcuts.jsx`: Global keyboard navigation
- `LoadingSpinner.jsx`: Loading states and transitions

#### Workflow Components (`src/components/`)
- `PatientInfo/`: Patient demographics and clinical assessment
- `PhysicalExam/`: Vital signs and physical examination findings
- `DiagnosticAnalysis/`: AI-generated differential diagnoses
- `RecommendedTests/`: Test selection and recommendations
- `TestResults/`: Laboratory and imaging results input
- `FinalDiagnosis/`: Final diagnosis and treatment planning

#### Utilities (`src/utils/`)
- `helpers.js`: Common utility functions for formatting, validation, and calculations

## 🎯 Workflow Steps

### 1. Patient Information & Clinical Assessment
- Patient demographics entry
- Chief complaint documentation
- Dynamic follow-up questions based on symptoms
- Medical history tracking
- Additional clinical observations

### 2. Physical Examination
- Comprehensive vital signs recording
- BMI calculation and categorization
- System-specific examination findings
- Normal ranges and validation

### 3. AI Diagnostic Analysis
- Intelligent differential diagnosis generation
- Confidence scoring for each diagnosis
- Supporting and contradicting factors
- Doctor feedback integration

### 4. Recommended Tests
- Smart test recommendations based on presentation
- Cost and time estimates
- Urgency categorization
- Contraindications and preparations

### 5. Test Results
- Structured input for different test types
- Laboratory values with normal ranges
- Imaging study reports
- File attachment support

### 6. Final Diagnosis & Treatment
- Refined diagnosis based on test results
- Primary and secondary diagnosis selection
- Treatment plan recommendations
- Follow-up instructions
- Medical note generation

## ⌨️ Keyboard Shortcuts

- `Ctrl/Cmd + →/←`: Navigate between steps
- `Ctrl/Cmd + 1-6`: Jump to specific workflow step
- `Ctrl/Cmd + S`: Save (auto-save is always enabled)
- `Ctrl/Cmd + /`: Show keyboard shortcuts help
- `←/→`: Navigate steps (when not in form fields)
- `Esc`: Clear focus from active element

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3b82f6) - Trust, medical professionalism
- **Secondary**: Gray (#64748b) - Balance, neutrality
- **Success**: Green (#10b981) - Positive results, completion
- **Warning**: Yellow (#f59e0b) - Caution, attention needed
- **Error**: Red (#ef4444) - Critical issues, alerts

### Typography
- **Primary Font**: Inter - Clean, readable, professional
- **Fallback**: System fonts for optimal performance

### Component Design
- **Cards**: Clean, elevated surfaces with subtle shadows
- **Forms**: Clear labels, validation states, helper text
- **Buttons**: Distinct hierarchy with clear call-to-actions
- **Icons**: Consistent Lucide React icons throughout

## 🔮 Future Enhancements

### Backend Integration
- RESTful API integration with FastAPI
- Real-time AI diagnosis processing
- Patient data persistence and retrieval
- User authentication and authorization

### Advanced Features
- Voice-to-text input for rapid documentation
- Integration with Electronic Health Records (EHR)
- Advanced analytics and reporting
- Multi-language support
- Offline functionality with data synchronization

### Clinical Tools
- Drug interaction checking
- Clinical decision support rules
- Evidence-based medicine integration
- Continuing medical education (CME) integration

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── Layout/          # Layout and infrastructure components
│   ├── PatientInfo/     # Patient information workflow
│   ├── PhysicalExam/    # Physical examination components
│   ├── DiagnosticAnalysis/ # AI diagnosis components
│   ├── RecommendedTests/   # Test recommendation components
│   ├── TestResults/     # Test results input components
│   └── FinalDiagnosis/  # Final diagnosis and treatment
├── context/             # React Context for state management
├── hooks/              # Custom React hooks
├── utils/              # Utility functions and helpers
├── App.jsx             # Main application component
├── main.jsx            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## 🤝 Contributing

This project follows modern React development practices:

1. **Component Structure**: Functional components with hooks
2. **State Management**: Context API for global state, local state for component-specific data
3. **Styling**: Tailwind CSS utility classes with custom component classes
4. **Code Organization**: Feature-based folder structure
5. **Accessibility**: WCAG 2.1 AA compliance standards
6. **Performance**: Optimized rendering and lazy loading where appropriate

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏥 Medical Disclaimer

DiagnoAssist is designed as a clinical decision support tool and should not replace professional medical judgment. All diagnostic decisions should be made by qualified healthcare professionals. The AI recommendations are suggestions only and require clinical validation.

---

Built with ❤️ for healthcare professionals to enhance patient care and diagnostic accuracy.
