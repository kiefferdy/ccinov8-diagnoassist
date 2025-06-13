import React, { createContext, useContext, useState, useEffect } from 'react';
import { appDataRef } from './AppDataContext';

const PatientContext = createContext(null);

export const usePatient = () => {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within a PatientProvider');
  }
  return context;
};

export const PatientProvider = ({ children }) => {
  const [patientData, setPatientData] = useState({
    // Basic Information
    id: null,
    name: '',
    age: '',
    gender: '',
    dateOfBirth: '',
    
    // Chief Complaint
    chiefComplaint: '',
    chiefComplaintDetails: [],
    additionalClinicalNotes: '',
    clinicalNotes: '', // For free-form notes
    standardizedAssessments: {}, // For storing PHQ-9, GAD-7, etc. results
    
    // Medical History
    medicalHistory: [],
    medications: [],
    allergies: [],
    
    // Documents
    relatedDocuments: [],
    assessmentDocuments: [],
    
    // Physical Exam
    physicalExam: {
      bloodPressure: '',
      heartRate: '',
      temperature: '',
      respiratoryRate: '',
      oxygenSaturation: '',
      height: '',
      weight: '',
      bmi: '',
      additionalFindings: '',
      examDocuments: []
    },
    
    // Diagnoses
    differentialDiagnoses: [],
    selectedDiagnosis: null,
    finalDiagnosis: '',
    diagnosticNotes: '',
    
    // Tests
    recommendedTests: [],
    selectedTests: [],
    testResults: {},
    
    // Treatment
    treatmentPlan: '',
    prescriptions: []
  });
  
  const [currentStep, setCurrentStep] = useState('home');
  const [sessionId, setSessionId] = useState(null);
  const [lastSaved, setLastSaved] = useState(null);
  
  // Auto-save functionality
  useEffect(() => {
    // Only auto-save if we have a patient ID and we're in an active session
    if (patientData.id && currentStep !== 'home' && currentStep !== 'patient-list') {
      const saveTimer = setTimeout(() => {
        // Get AppData context via ref
        if (appDataRef.current) {
          if (sessionId) {
            // Update existing session
            appDataRef.current.updateSession(sessionId, patientData, currentStep);
          } else {
            // Create new session
            const newSession = appDataRef.current.createSession(patientData.id, {
              ...patientData,
              currentStep
            });
            setSessionId(newSession.id);
          }
          setLastSaved(new Date().toISOString());
        }
      }, 2000); // Auto-save after 2 seconds of inactivity
      
      return () => clearTimeout(saveTimer);
    }
  }, [patientData, currentStep, sessionId]);
  
  const updatePatientData = (field, value) => {
    setPatientData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const updatePhysicalExam = (field, value) => {
    setPatientData(prev => ({
      ...prev,
      physicalExam: {
        ...prev.physicalExam,
        [field]: value
      }
    }));
  };
  
  const resetPatient = () => {
    setPatientData({
      id: null,
      name: '',
      age: '',
      gender: '',
      dateOfBirth: '',
      chiefComplaint: '',
      chiefComplaintDetails: [],
      additionalClinicalNotes: '',
      clinicalNotes: '',
      standardizedAssessments: {},
      medicalHistory: [],
      medications: [],
      allergies: [],
      relatedDocuments: [],
      assessmentDocuments: [],
      physicalExam: {
        bloodPressure: '',
        heartRate: '',
        temperature: '',
        respiratoryRate: '',
        oxygenSaturation: '',
        height: '',
        weight: '',
        bmi: '',
        additionalFindings: '',
        examDocuments: []
      },
      differentialDiagnoses: [],
      selectedDiagnosis: null,
      finalDiagnosis: '',
      diagnosticNotes: '',
      recommendedTests: [],
      selectedTests: [],
      testResults: {},
      treatmentPlan: '',
      prescriptions: []
    });
    setCurrentStep('home');
    setSessionId(null);
  };
  
  const value = {
    patientData,
    setPatientData,
    updatePatientData,
    updatePhysicalExam,
    currentStep,
    setCurrentStep,
    sessionId,
    setSessionId,
    lastSaved,
    resetPatient
  };
  
  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};
