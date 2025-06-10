import React, { createContext, useContext, useState } from 'react';

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
    resetPatient
  };
  
  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};
