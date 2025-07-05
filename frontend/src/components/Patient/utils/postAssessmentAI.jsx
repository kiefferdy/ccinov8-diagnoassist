// Enhanced AI question generation that considers both Subjective and Objective data
export const generatePostAssessmentQuestions = (patientData) => {
  const questions = [];
  
  // Analyze chief complaint
  const chiefComplaint = patientData.chiefComplaint?.toLowerCase() || '';
  const hpi = patientData.historyOfPresentIllness?.toLowerCase() || '';
  
  // Analyze vital signs and physical exam
  const exam = patientData.physicalExam || {};
  const hasAbnormalVitals = 
    (exam.temperature && parseFloat(exam.temperature) > 37.5) ||
    (exam.heartRate && (parseInt(exam.heartRate) > 100 || parseInt(exam.heartRate) < 60)) ||
    (exam.bloodPressure && isBloodPressureAbnormal(exam.bloodPressure)) ||
    (exam.oxygenSaturation && parseInt(exam.oxygenSaturation) < 95);
  
  // Generate targeted questions based on findings
  if (chiefComplaint.includes('chest') || chiefComplaint.includes('cardiac') || 
      chiefComplaint.includes('heart') || chiefComplaint.includes('breath')) {
    
    // Cardiac risk assessment
    questions.push({
      id: 'cardiac-risk-1',
      category: 'Cardiac Risk Assessment',
      question: 'Does the patient have any of these cardiac risk factors: smoking, diabetes, hypertension, hyperlipidemia, or family history of premature CAD?',
      rationale: 'To calculate cardiac risk score and guide further workup',
      priority: 'high',
      soapRelevance: ['subjective', 'assessment']
    });
    
    questions.push({
      id: 'cardiac-risk-2',
      category: 'Symptom Characterization',
      question: 'Can you describe the exact quality of the chest discomfort? Is it pressure, sharp, burning, or tearing?',
      rationale: 'Different qualities suggest different etiologies',
      priority: 'high',
      soapRelevance: ['subjective']
    });
    
    // PE risk assessment
    questions.push({
      id: 'pe-risk-1',
      category: 'Thromboembolism Risk',
      question: 'Any recent surgery, prolonged immobilization, hormone use, or history of DVT/PE?',
      rationale: 'To assess Wells criteria for PE',
      priority: 'medium',
      soapRelevance: ['subjective', 'assessment']
    });
  }
  
  // Infectious workup questions
  if (hasAbnormalVitals && exam.temperature && parseFloat(exam.temperature) > 37.5) {
    questions.push({
      id: 'infection-1',
      category: 'Infectious Source',
      question: 'Any urinary symptoms, skin changes, or localized pain that might indicate a source of infection?',
      rationale: 'To identify potential source and guide antibiotic selection',
      priority: 'high',
      soapRelevance: ['subjective', 'plan']
    });
    
    questions.push({
      id: 'infection-2',
      category: 'Immune Status',
      question: 'Is the patient immunocompromised (diabetes, HIV, chemotherapy, chronic steroids)?',
      rationale: 'Affects differential and empiric treatment choices',
      priority: 'high',
      soapRelevance: ['subjective', 'assessment', 'plan']
    });
  }
  
  // Medication-related questions
  if (!patientData.medications || patientData.medications.length === 0) {
    questions.push({
      id: 'med-1',
      category: 'Medication History',
      question: 'Can you confirm the patient takes NO regular medications? Any OTC or herbal supplements?',
      rationale: 'Important for drug interactions and may explain symptoms',
      priority: 'medium',
      soapRelevance: ['subjective']
    });
  }
  
  // Social determinants
  questions.push({
    id: 'social-1',
    category: 'Social Factors',
    question: 'What is the patient\'s living situation and support system? Any barriers to follow-up or medication compliance?',
    rationale: 'Affects discharge planning and treatment adherence',
    priority: 'medium',
    soapRelevance: ['subjective', 'plan']
  });
  
  // Red flag screening
  if (chiefComplaint || hpi) {
    questions.push({
      id: 'red-flag-1',
      category: 'Red Flag Symptoms',
      question: 'Any unexplained weight loss, night sweats, or progressive symptoms over weeks/months?',
      rationale: 'To screen for malignancy or chronic conditions',
      priority: 'medium',
      soapRelevance: ['subjective', 'assessment']
    });
  }
  
  return questions;
};

const isBloodPressureAbnormal = (bp) => {
  if (!bp) return false;
  const [systolic, diastolic] = bp.split('/').map(num => parseInt(num));
  return systolic > 140 || systolic < 90 || diastolic > 90 || diastolic < 60;
};

// Generate follow-up questions after initial assessment
export const generateDiagnosticClarificationQuestions = (diagnosis) => {
  const questions = [];
  
  // Based on the doctor's diagnosis, generate specific clarifying questions
  const diagnosisLower = diagnosis.toLowerCase();
  
  if (diagnosisLower.includes('pneumonia')) {
    questions.push({
      category: 'Severity Assessment',
      question: 'Is the patient able to maintain oral intake? Any confusion or altered mental status?',
      rationale: 'To determine need for admission vs outpatient treatment'
    });
  }
  
  if (diagnosisLower.includes('heart') || diagnosisLower.includes('cardiac')) {
    questions.push({
      category: 'Risk Stratification',
      question: 'Has an ECG been performed? Any troponin levels available?',
      rationale: 'Essential for cardiac risk stratification'
    });
  }
  
  return questions;
};