import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { PatientProvider, usePatient } from './contexts/PatientContext';
import { AppDataProvider } from './contexts/AppDataContext';
import Layout from './components/Layout/Layout';
import Home from './components/Home/Home';
import PatientList from './components/PatientManagement/PatientList';
import PatientDetailView from './components/PatientManagement/PatientDetailView';
import PatientSelection from './components/Patient/PatientSelection';
import PatientInformation from './components/Patient/PatientInformation';
import ClinicalAssessment from './components/Patient/ClinicalAssessment';
import PhysicalExam from './components/Diagnosis/PhysicalExam';
import DiagnosticAnalysis from './components/Diagnosis/DiagnosticAnalysis';
import RecommendedTests from './components/Tests/RecommendedTests';
import TestResults from './components/Tests/TestResults';
import FinalDiagnosis from './components/FinalDiagnosis/FinalDiagnosis';
import TreatmentPlan from './components/TreatmentPlan/TreatmentPlan';
import ClinicalSummary from './components/ClinicalSummary/ClinicalSummary';
import LandingPage from './components/LandingPage/LandingPage';

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
      case 'patient-detail':
        return <PatientDetailView />;
      case 'patient-selection':
        return <PatientSelection />;
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
      case 'treatment-plan':
        return <TreatmentPlan />;
      case 'clinical-summary':
        return <ClinicalSummary />;
      default:
        return <Home />;
    }
  };
  
  // Show layout with sidebar only when patient workflow is active
  const showLayout = currentStep !== 'home' && 
                    currentStep !== 'patient-list' && 
                    currentStep !== 'patient-detail' && 
                    currentStep !== 'patient-selection';
  
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
    <Router>
      <Routes>
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/*" element={
          <AppDataProvider>
            <PatientProvider>
              <AppContent />
            </PatientProvider>
          </AppDataProvider>
        } />
      </Routes>
    </Router>
  );
}

export default App;
