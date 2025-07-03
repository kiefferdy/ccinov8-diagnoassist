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
    chiefComplaintDuration: '',
    chiefComplaintOnset: '',
    chiefComplaintDetails: [],
    additionalClinicalNotes: '',
    clinicalNotes: '', // For free-form notes
    standardizedAssessments: {}, // For storing PHQ-9, GAD-7, etc. results
    
    // SOAP Documentation
    historyOfPresentIllness: '',
    reviewOfSystems: '',
    pastMedicalHistory: '',
    socialHistory: '',
    familyHistory: '',
    
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
    doctorDiagnosis: '',
    finalDiagnosis: '',
    diagnosticNotes: '',
    hasViewedInsights: false,
    
    // Tests
    recommendedTests: [],
    selectedTests: [],
    testResults: {},
    
    // Treatment
    therapeuticPlan: {
      medications: [],
      procedures: [],
      referrals: [],
      followUp: '',
      patientEducation: ''
    },
    treatmentPlan: '',
    prescriptions: [],
    followUpRecommendations: '',
    patientEducation: '',
    clinicalSummary: '',
    assessmentNote: '',
    
    // AI Assistance
    clarifyingQuestions: [],
    redFlags: []
  });
  
  const [currentStep, setCurrentStep] = useState('home');
  const [sessionId, setSessionId] = useState(null);
  const [lastSaved, setLastSaved] = useState(null);
  const [savedData, setSavedData] = useState(null); // Track last saved state
  const [dataByStep, setDataByStep] = useState({}); // Track data saved at each step
  const [stepSnapshot, setStepSnapshot] = useState(null); // Snapshot when entering a step
  const [highestStepReached, setHighestStepReached] = useState('home'); // Track progression
  
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
          setSavedData(JSON.parse(JSON.stringify(patientData))); // Deep copy
          setDataByStep(prev => ({
            ...prev,
            [currentStep]: JSON.parse(JSON.stringify(patientData))
          }));
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
      chiefComplaintDuration: '',
      chiefComplaintOnset: '',
      chiefComplaintDetails: [],
      additionalClinicalNotes: '',
      clinicalNotes: '',
      standardizedAssessments: {},
      historyOfPresentIllness: '',
      reviewOfSystems: '',
      pastMedicalHistory: '',
      socialHistory: '',
      familyHistory: '',
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
      doctorDiagnosis: '',
      finalDiagnosis: '',
      diagnosticNotes: '',
      hasViewedInsights: false,
      recommendedTests: [],
      selectedTests: [],
      testResults: {},
      therapeuticPlan: {
        medications: [],
        procedures: [],
        referrals: [],
        followUp: '',
        patientEducation: ''
      },
      treatmentPlan: '',
      prescriptions: [],
      followUpRecommendations: '',
      patientEducation: '',
      clinicalSummary: '',
      assessmentNote: '',
      clarifyingQuestions: [],
      redFlags: []
    });
    setCurrentStep('home');
    setSessionId(null);
    setSavedData(null);
    setDataByStep({});
    setStepSnapshot(null);
    setHighestStepReached('home');
  };
  
  // Check if current data has unsaved changes
  const hasUnsavedChanges = () => {
    if (!savedData) return false;
    return JSON.stringify(patientData) !== JSON.stringify(savedData);
  };
  
  // Get data relevant to a specific step
  const getStepRelevantData = (step) => {
    switch (step) {
      case 'patient-info':
        return {
          name: patientData.name,
          age: patientData.age,
          gender: patientData.gender,
          dateOfBirth: patientData.dateOfBirth,
          medicalHistory: patientData.medicalHistory,
          medications: patientData.medications,
          allergies: patientData.allergies
        };
      case 'chief-complaint':
        return {
          chiefComplaint: patientData.chiefComplaint,
          chiefComplaintDuration: patientData.chiefComplaintDuration,
          chiefComplaintOnset: patientData.chiefComplaintOnset
        };
      case 'clinical-assessment':
        return {
          chiefComplaintDetails: patientData.chiefComplaintDetails,
          additionalClinicalNotes: patientData.additionalClinicalNotes,
          clinicalNotes: patientData.clinicalNotes,
          standardizedAssessments: patientData.standardizedAssessments,
          assessmentDocuments: patientData.assessmentDocuments,
          historyOfPresentIllness: patientData.historyOfPresentIllness,
          reviewOfSystems: patientData.reviewOfSystems,
          pastMedicalHistory: patientData.pastMedicalHistory,
          socialHistory: patientData.socialHistory,
          familyHistory: patientData.familyHistory
        };
      case 'physical-exam':
        return {
          physicalExam: patientData.physicalExam
        };
      case 'diagnostic-analysis':
        return {
          differentialDiagnoses: patientData.differentialDiagnoses,
          diagnosticNotes: patientData.diagnosticNotes,
          doctorDiagnosis: patientData.doctorDiagnosis,
          hasViewedInsights: patientData.hasViewedInsights
        };
      case 'recommended-tests':
        return {
          recommendedTests: patientData.recommendedTests,
          selectedTests: patientData.selectedTests,
          therapeuticPlan: patientData.therapeuticPlan
        };
      case 'test-results':
        return {
          testResults: patientData.testResults
        };
      case 'final-diagnosis':
        return {
          selectedDiagnosis: patientData.selectedDiagnosis,
          finalDiagnosis: patientData.finalDiagnosis
        };
      case 'treatment-plan':
        return {
          treatmentPlan: patientData.treatmentPlan,
          prescriptions: patientData.prescriptions,
          followUpRecommendations: patientData.followUpRecommendations,
          patientEducation: patientData.patientEducation
        };
      case 'clinical-summary':
        return {
          clinicalSummary: patientData.clinicalSummary,
          assessmentNote: patientData.assessmentNote
        };
      default:
        return {};
    }
  };
  
  // Check if data for a specific step has changed from what was saved
  const hasStepDataChanged = (step) => {
    const savedStepData = dataByStep[step];
    if (!savedStepData) return false;
    
    const currentStepData = getStepRelevantData(step);
    const savedRelevantData = {};
    
    // Extract relevant data from saved step data
    Object.keys(currentStepData).forEach(key => {
      savedRelevantData[key] = savedStepData[key];
    });
    
    return JSON.stringify(currentStepData) !== JSON.stringify(savedRelevantData);
  };
  
  // Check if changes to a step would affect subsequent steps
  const wouldChangesAffectSubsequentSteps = (step) => {
    const steps = ['patient-info', 'clinical-assessment', 'physical-exam', 
                  'diagnostic-analysis', 'recommended-tests', 'test-results', 
                  'final-diagnosis', 'treatment-plan', 'clinical-summary'];
    const stepIndex = steps.indexOf(step);
    
    // Check if any subsequent steps have data
    for (let i = stepIndex + 1; i < steps.length; i++) {
      const futureStep = steps[i];
      const futureData = getStepRelevantData(futureStep);
      
      // Check if future step has meaningful data
      if (futureStep === 'diagnostic-analysis' && patientData.differentialDiagnoses.length > 0) return true;
      if (futureStep === 'recommended-tests' && patientData.recommendedTests.length > 0) return true;
      if (futureStep === 'test-results' && Object.keys(patientData.testResults).length > 0) return true;
      if (futureStep === 'final-diagnosis' && (patientData.selectedDiagnosis || patientData.finalDiagnosis)) return true;
      if (futureStep === 'treatment-plan' && (patientData.treatmentPlan || patientData.prescriptions.length > 0)) return true;
      if (futureStep === 'clinical-summary' && patientData.clinicalSummary) return true;
    }
    
    return false;
  };
  
  // Enhanced navigation with proper step tracking
  const setCurrentStepAndTrack = (newStep) => {
    const steps = ['patient-info', 'clinical-assessment', 'physical-exam', 
                  'diagnostic-analysis', 'recommended-tests', 'test-results', 
                  'final-diagnosis', 'treatment-plan', 'clinical-summary'];
    const newStepIndex = steps.indexOf(newStep);
    const highestIndex = steps.indexOf(highestStepReached);
    
    // Update highest step reached if moving forward
    if (newStepIndex > highestIndex) {
      setHighestStepReached(newStep);
    }
    
    setCurrentStep(newStep);
  };
  
  // Check if current step data has changed from snapshot
  const hasChangedSinceNavigation = () => {
    if (!stepSnapshot) return false;
    const currentData = getStepRelevantData(currentStep);
    return JSON.stringify(currentData) !== JSON.stringify(stepSnapshot);
  };
  
  const value = {
    patientData,
    setPatientData,
    updatePatientData,
    updatePhysicalExam,
    currentStep,
    setCurrentStep: setCurrentStepAndTrack,
    sessionId,
    setSessionId,
    lastSaved,
    resetPatient,
    hasUnsavedChanges,
    hasStepDataChanged,
    navigateToStep: setCurrentStepAndTrack,
    wouldChangesAffectSubsequentSteps,
    hasChangedSinceNavigation,
    highestStepReached
  };
  
  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};
