import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { appDataRef } from '../../contexts/AppDataContext';
import AutoSaveIndicator from '../common/AutoSaveIndicator';
import { 
  User, 
  ClipboardList, 
  Stethoscope, 
  TestTube, 
  FileText,
  Activity,
  Home,
  LogOut,
  FlaskConical,
  ClipboardCheck,
  X
} from 'lucide-react';

const Layout = ({ children }) => {
  const { 
    currentStep, 
    setCurrentStep, 
    patientData, 
    resetPatient, 
    sessionId,
    navigateToStep,
    highestStepReached
  } = usePatient();
  
  const steps = [
    { id: 'patient-info', label: 'Patient Information', icon: User },
    { id: 'clinical-assessment', label: 'Clinical Assessment', icon: ClipboardList },
    { id: 'physical-exam', label: 'Physical Exam', icon: Stethoscope },
    { id: 'diagnostic-analysis', label: 'Diagnostic Analysis', icon: Activity },
    { id: 'recommended-tests', label: 'Recommended Tests', icon: FlaskConical },
    { id: 'test-results', label: 'Test Results', icon: ClipboardCheck },
    { id: 'final-diagnosis', label: 'Final Diagnosis', icon: FileText }
  ];
  
  const getStepIndex = (stepId) => steps.findIndex(s => s.id === stepId);
  const currentStepIndex = getStepIndex(currentStep);
  
  const isStepAccessible = (stepId) => {
    const stepIndex = getStepIndex(stepId);
    const highestIndex = getStepIndex(highestStepReached);
    
    // Allow access to all steps up to and including the highest reached
    if (stepIndex <= highestIndex) return true;
    
    // Allow next step if current step has required data
    if (stepIndex === currentStepIndex + 1) {
      switch (currentStep) {
        case 'patient-info':
          return patientData.name && patientData.age && patientData.chiefComplaint;
        case 'clinical-assessment':
          return patientData.chiefComplaintDetails && patientData.chiefComplaintDetails.length > 0;
        case 'physical-exam':
          return patientData.physicalExam.bloodPressure || patientData.physicalExam.heartRate || 
                 patientData.physicalExam.temperature || patientData.physicalExam.respiratoryRate;
        case 'diagnostic-analysis':
          return patientData.differentialDiagnoses.length > 0;
        case 'recommended-tests':
          return patientData.selectedTests && patientData.selectedTests.length > 0;
        case 'test-results':
          return patientData.testResults && Object.values(patientData.testResults).some(r => r.status === 'completed');
        default:
          return false;
      }
    }
    return false;
  };
  
  const handleStepClick = (stepId) => {
    if (isStepAccessible(stepId)) {
      setCurrentStep(stepId);
    }
  };
  
  const handleHome = () => {
    setCurrentStep('home');
  };
  
  const handleCancelAssessment = () => {
    if (window.confirm('Are you sure you want to cancel this assessment? All unsaved changes will be lost.')) {
      // Delete the session if it exists
      if (sessionId && appDataRef.current) {
        appDataRef.current.deleteSession(sessionId);
      }
      resetPatient();
      setCurrentStep('home');
    }
  };
  
  const handleNewPatient = () => {
    if (window.confirm('Are you sure you want to start a new patient? All current data will be lost.')) {
      // Delete the session if it exists
      if (sessionId && appDataRef.current) {
        appDataRef.current.deleteSession(sessionId);
      }
      resetPatient();
      setCurrentStep('patient-selection');
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">DiagnoAssist</h1>
              <p className="text-xs text-gray-500">AI-Powered Diagnosis</p>
            </div>
          </div>
          
          {patientData.name && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-900">Current Patient</p>
              <p className="text-lg font-semibold text-blue-900">{patientData.name}</p>
              <p className="text-sm text-blue-700">{patientData.age} years • {patientData.gender}</p>
            </div>
          )}
          
          <nav className="space-y-2">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = step.id === currentStep;
              const isAccessible = isStepAccessible(step.id);
              const isCompleted = getStepIndex(step.id) < currentStepIndex;
              
              return (
                <button
                  key={step.id}
                  onClick={() => handleStepClick(step.id)}
                  disabled={!isAccessible}
                  className={`
                    w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all
                    ${isActive 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : isAccessible
                        ? 'hover:bg-gray-100 text-gray-700'
                        : 'text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  <div className="relative">
                    <Icon className="w-5 h-5" />
                    {isCompleted && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></div>
                    )}
                  </div>
                  <span className="text-sm font-medium">{step.label}</span>
                </button>
              );
            })}
          </nav>
          
          <div className="mt-8 space-y-2">
            <button
              onClick={handleHome}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 transition-all"
            >
              <Home className="w-5 h-5" />
              <span className="text-sm font-medium">Home</span>
            </button>
            <button
              onClick={handleNewPatient}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 transition-all"
            >
              <User className="w-5 h-5" />
              <span className="text-sm font-medium">New Assessment</span>
            </button>
            <button
              onClick={handleCancelAssessment}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-red-50 text-red-700 transition-all"
            >
              <X className="w-5 h-5" />
              <span className="text-sm font-medium">Cancel Assessment</span>
            </button>
            <button
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 transition-all"
            >
              <LogOut className="w-5 h-5" />
              <span className="text-sm font-medium">Sign Out</span>
            </button>
          </div>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
      
      {/* Auto-save indicator */}
      <AutoSaveIndicator />
    </div>
  );
};

export default Layout;