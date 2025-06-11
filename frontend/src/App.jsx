import React from 'react';
import { PatientProvider, usePatient } from './contexts/PatientContext';
import { AppDataProvider } from './contexts/AppDataContext';
import Layout from './components/Layout/Layout';
import Home from './components/Home/Home';
import PatientList from './components/PatientManagement/PatientList';
import PatientInformation from './components/Patient/PatientInformation';
import ClinicalAssessment from './components/Patient/ClinicalAssessment';
import PhysicalExam from './components/Diagnosis/PhysicalExam';
import DiagnosticAnalysis from './components/Diagnosis/DiagnosticAnalysis';
import RecommendedTests from './components/Tests/RecommendedTests';
import TestResults from './components/Tests/TestResults';
import FinalDiagnosis from './components/Treatment/FinalDiagnosis';

function AppContent() {
  const { currentStep } = usePatient();
  
  const renderStep = () => {
    // Show home if currentStep is explicitly 'home'
    if (currentStep === 'home') {
      return <Home />;
    }
    
    switch (currentStep) {
      case 'patient-list':
        return <PatientList />;
      case 'patient-info':
        return <PatientInformation />;
      case 'clinical-assessment':
        return <ClinicalAssessment />;
      case 'physical-exam':
        return <PhysicalExam />;
      case 'diagnostic-analysis':
        return <DiagnosticAnalysis />;
      case 'recommended-tests':
        return <RecommendedTests />;
      case 'test-results':
        return <TestResults />;
      case 'tests': // Legacy support
        return <RecommendedTests />;
      case 'final-diagnosis':
        return <FinalDiagnosis />;
      default:
        return <Home />;
    }
  };
  
  // Show layout with sidebar only when patient workflow is active
  const showLayout = currentStep !== 'home' && currentStep !== 'patient-list';
  
  if (showLayout) {
    return (
      <Layout>
        {renderStep()}
      </Layout>
    );
  }
  
  // For home page, show without sidebar
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        {renderStep()}
      </div>
    </div>
  );
}

function App() {
  return (
    <AppDataProvider>
      <PatientProvider>
        <AppContent />
      </PatientProvider>
    </AppDataProvider>
  );
}

export default App;
