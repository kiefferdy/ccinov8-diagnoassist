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
    
    // Medical History
    medicalHistory: [],
    medications: [],
    allergies: [],
    
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
      additionalFindings: ''
    },
    
    // Diagnoses
    differentialDiagnoses: [],
    selectedDiagnosis: null,
    finalDiagnosis: '',
    
    // Tests
    recommendedTests: [],
    orderedTests: [],
    testResults: [],
    
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
      medicalHistory: [],
      medications: [],
      allergies: [],
      physicalExam: {
        bloodPressure: '',
        heartRate: '',
        temperature: '',
        respiratoryRate: '',
        oxygenSaturation: '',
        height: '',
        weight: '',
        bmi: '',
        additionalFindings: ''
      },
      differentialDiagnoses: [],
      selectedDiagnosis: null,
      finalDiagnosis: '',
      recommendedTests: [],
      orderedTests: [],
      testResults: [],
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
