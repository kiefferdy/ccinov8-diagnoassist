import { createContext, useContext, useReducer } from 'react'

const PatientDataContext = createContext()

const initialState = {
  currentStep: 1,
  patient: {
    id: null,
    name: '',
    age: '',
    gender: '',
    medicalRecordNumber: '',
  },
  chiefComplaint: '',
  presentIllness: '',
  medicalHistory: [],
  dynamicQuestions: [],
  dynamicAnswers: {},
  additionalObservations: '',
  physicalExam: {
    vitalSigns: {
      bloodPressure: '',
      heartRate: '',
      temperature: '',
      respiratoryRate: '',
      oxygenSaturation: '',
      height: '',
      weight: '',
      bmi: ''
    },
    generalAppearance: '',
    cardiovascular: '',
    respiratory: '',
    gastrointestinal: '',
    neurological: '',
    musculoskeletal: '',
    skin: '',
    other: ''
  },
  initialDiagnosis: {
    differentialDiagnoses: [],
    reasoning: '',
    confidence: null
  },
  recommendedTests: [],
  selectedTests: [],
  testResults: {},
  refinedDiagnosis: {
    differentialDiagnoses: [],
    reasoning: '',
    confidence: null,
    changes: []
  },
  finalDiagnosis: {
    primaryDiagnosis: '',
    secondaryDiagnoses: [],
    treatmentPlan: '',
    followUpInstructions: '',
    notes: ''
  }
}

function patientDataReducer(state, action) {
  switch (action.type) {
    case 'SET_CURRENT_STEP':
      return { ...state, currentStep: action.payload }
    case 'UPDATE_PATIENT_INFO':
      return { ...state, patient: { ...state.patient, ...action.payload } }
    case 'SET_CHIEF_COMPLAINT':
      return { ...state, chiefComplaint: action.payload }
    case 'SET_PRESENT_ILLNESS':
      return { ...state, presentIllness: action.payload }
    case 'ADD_MEDICAL_HISTORY':
      return { ...state, medicalHistory: [...state.medicalHistory, action.payload] }
    case 'SET_MEDICAL_HISTORY':
      return { ...state, medicalHistory: action.payload }
    case 'ADD_DYNAMIC_QUESTION':
      return { ...state, dynamicQuestions: [...state.dynamicQuestions, action.payload] }
    case 'UPDATE_DYNAMIC_ANSWER':
      return { 
        ...state, 
        dynamicAnswers: { ...state.dynamicAnswers, [action.payload.questionId]: action.payload.answer }
      }
    case 'SET_ADDITIONAL_OBSERVATIONS':
      return { ...state, additionalObservations: action.payload }
    case 'UPDATE_PHYSICAL_EXAM':
      return { 
        ...state, 
        physicalExam: { ...state.physicalExam, ...action.payload }
      }
    case 'UPDATE_VITAL_SIGNS':
      return {
        ...state,
        physicalExam: {
          ...state.physicalExam,
          vitalSigns: { ...state.physicalExam.vitalSigns, ...action.payload }
        }
      }
    case 'SET_INITIAL_DIAGNOSIS':
      return { ...state, initialDiagnosis: action.payload }
    case 'SET_RECOMMENDED_TESTS':
      return { ...state, recommendedTests: action.payload }
    case 'SET_SELECTED_TESTS':
      return { ...state, selectedTests: action.payload }
    case 'UPDATE_TEST_RESULT':
      return {
        ...state,
        testResults: { ...state.testResults, [action.payload.testId]: action.payload.result }
      }
    case 'SET_REFINED_DIAGNOSIS':
      return { ...state, refinedDiagnosis: action.payload }
    case 'UPDATE_FINAL_DIAGNOSIS':
      return { ...state, finalDiagnosis: { ...state.finalDiagnosis, ...action.payload } }
    case 'RESET_PATIENT_DATA':
      return initialState
    default:
      return state
  }
}

export function PatientDataProvider({ children }) {
  const [state, dispatch] = useReducer(patientDataReducer, initialState)

  const value = {
    ...state,
    dispatch,
    // Helper functions
    nextStep: () => dispatch({ type: 'SET_CURRENT_STEP', payload: state.currentStep + 1 }),
    prevStep: () => dispatch({ type: 'SET_CURRENT_STEP', payload: Math.max(1, state.currentStep - 1) }),
    goToStep: (step) => dispatch({ type: 'SET_CURRENT_STEP', payload: step }),
    updatePatient: (data) => dispatch({ type: 'UPDATE_PATIENT_INFO', payload: data }),
    setChiefComplaint: (complaint) => dispatch({ type: 'SET_CHIEF_COMPLAINT', payload: complaint }),
    setPresentIllness: (illness) => dispatch({ type: 'SET_PRESENT_ILLNESS', payload: illness }),
    addMedicalHistory: (history) => dispatch({ type: 'ADD_MEDICAL_HISTORY', payload: history }),
    addDynamicQuestion: (question) => dispatch({ type: 'ADD_DYNAMIC_QUESTION', payload: question }),
    updateDynamicAnswer: (questionId, answer) => dispatch({ 
      type: 'UPDATE_DYNAMIC_ANSWER', 
      payload: { questionId, answer } 
    }),
    setAdditionalObservations: (observations) => dispatch({ type: 'SET_ADDITIONAL_OBSERVATIONS', payload: observations }),
    updatePhysicalExam: (data) => dispatch({ type: 'UPDATE_PHYSICAL_EXAM', payload: data }),
    updateVitalSigns: (vitals) => dispatch({ type: 'UPDATE_VITAL_SIGNS', payload: vitals }),
    setInitialDiagnosis: (diagnosis) => dispatch({ type: 'SET_INITIAL_DIAGNOSIS', payload: diagnosis }),
    setRecommendedTests: (tests) => dispatch({ type: 'SET_RECOMMENDED_TESTS', payload: tests }),
    setSelectedTests: (tests) => dispatch({ type: 'SET_SELECTED_TESTS', payload: tests }),
    updateTestResult: (testId, result) => dispatch({ 
      type: 'UPDATE_TEST_RESULT', 
      payload: { testId, result } 
    }),
    setRefinedDiagnosis: (diagnosis) => dispatch({ type: 'SET_REFINED_DIAGNOSIS', payload: diagnosis }),
    updateFinalDiagnosis: (data) => dispatch({ type: 'UPDATE_FINAL_DIAGNOSIS', payload: data }),
    resetData: () => dispatch({ type: 'RESET_PATIENT_DATA' })
  }

  return (
    <PatientDataContext.Provider value={value}>
      {children}
    </PatientDataContext.Provider>
  )
}

export function usePatientData() {
  const context = useContext(PatientDataContext)
  if (!context) {
    throw new Error('usePatientData must be used within a PatientDataProvider')
  }
  return context
}