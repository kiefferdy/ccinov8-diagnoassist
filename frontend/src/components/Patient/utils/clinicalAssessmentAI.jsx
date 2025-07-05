import React from 'react';
import { 
  Heart, 
  Clock, 
  MapPin, 
  TrendingUp, 
  AlertCircle, 
  Activity,
  Thermometer,
  Wind,
  Brain,
  Eye,
  Pill,
  Stethoscope,
  FileQuestion,
  Microscope,
  UserCheck,
  Scale,
  Droplets,
  Moon,
  Sun
} from 'lucide-react';

// Clinical decision trees and patterns
const clinicalPatterns = {
  cardiac: {
    triggers: ['chest', 'heart', 'palpitation', 'pressure', 'tight', 'angina'],
    redFlags: [
      { pattern: ['crushing', 'radiating', 'jaw'], message: 'Possible acute coronary syndrome - consider immediate evaluation' },
      { pattern: ['shortness', 'sweating', 'nausea'], message: 'Classic cardiac presentation with associated symptoms' },
      { pattern: ['tearing', 'back'], message: 'Consider aortic dissection - requires urgent imaging' },
      { pattern: ['sudden', 'severe', 'chest'], message: 'Acute onset severe chest pain - rule out life-threatening causes' }
    ],
    initialQuestion: {
      id: 'chest_pain_description',
      text: 'Ask the patient to describe their chest discomfort in their own words. Document the location, quality, and any radiation.',
      type: 'text',
      category: 'Chief Complaint Details',
      placeholder: 'e.g., "Patient describes crushing central chest pressure radiating to left arm, started 2 hours ago while walking..."',
      helpText: 'Let the patient speak freely first, then clarify specific details. Open-ended descriptions often reveal important diagnostic clues.'
    }
  },
  respiratory: {
    triggers: ['cough', 'breathing', 'wheeze', 'chest', 'phlegm', 'shortness', 'dyspnea'],
    redFlags: [
      { pattern: ['blood', 'hemoptysis'], message: 'Hemoptysis present - requires urgent evaluation and imaging' },
      { pattern: ['sudden', 'severe', 'breathless'], message: 'Acute dyspnea - consider PE, pneumothorax, or acute heart failure' },
      { pattern: ['fever', 'productive', 'chest'], message: 'Infectious symptoms - possible pneumonia' },
      { pattern: ['stridor', 'drooling'], message: 'Upper airway obstruction - immediate intervention may be needed' }
    ],
    initialQuestion: {
      id: 'respiratory_complaint',
      text: 'Have the patient describe their breathing problem and how it affects their daily activities.',
      type: 'text',
      category: 'Chief Complaint Details',
      placeholder: 'Document onset, triggers, severity, and functional impact...',
      helpText: 'Note respiratory rate, use of accessory muscles, and ability to speak in full sentences. Observe the patient\'s breathing pattern while they speak.'
    }
  },
  neurological: {
    triggers: ['headache', 'dizzy', 'faint', 'weakness', 'numbness', 'tingling', 'confusion'],
    redFlags: [
      { pattern: ['thunderclap', 'worst', 'sudden'], message: 'Thunderclap headache - consider subarachnoid hemorrhage' },
      { pattern: ['weakness', 'speech', 'facial'], message: 'Stroke symptoms - activate stroke protocol immediately' },
      { pattern: ['fever', 'neck', 'stiff'], message: 'Meningitis signs - consider lumbar puncture' },
      { pattern: ['confusion', 'altered'], message: 'Altered mental status - broad differential, systematic approach needed' }
    ],
    initialQuestion: {
      id: 'neuro_timeline',
      text: 'Document the exact timeline and progression of the patient\'s neurological symptoms.',
      type: 'text',
      category: 'Symptom Timeline',
      placeholder: 'Include time of onset, progression, and any fluctuations...',
      helpText: 'Sudden onset suggests vascular cause; gradual onset suggests other etiologies. Time is brain - precise timing crucial for stroke management.'
    }
  },
  gastrointestinal: {
    triggers: ['stomach', 'abdomen', 'nausea', 'vomit', 'diarrhea', 'constipation', 'belly'],
    redFlags: [
      { pattern: ['blood', 'melena', 'black'], message: 'GI bleeding - assess hemodynamic stability' },
      { pattern: ['severe', 'rigid', 'rebound'], message: 'Peritoneal signs - surgical consultation needed' },
      { pattern: ['jaundice', 'yellow'], message: 'Hepatobiliary involvement - check liver function' },
      { pattern: ['distended', 'obstipation'], message: 'Possible bowel obstruction' }
    ],
    initialQuestion: {
      id: 'gi_symptoms',
      text: 'Have the patient describe their abdominal symptoms, including location, timing with meals, and bowel patterns.',
      type: 'text',
      category: 'Chief Complaint Details',
      placeholder: 'Document pain location, quality, associated symptoms, and relationship to food/bowel movements...',
      helpText: 'Use the four-quadrant approach and note any referred pain. Ask about recent travel, dietary changes, and medication use.'
    }
  },
  general: {
    triggers: [],
    redFlags: [],
    initialQuestion: {
      id: 'symptom_description',
      text: 'Have the patient describe their main concern in detail, including when it started and how it has progressed.',
      type: 'text',
      category: 'Chief Complaint Details',
      placeholder: 'Document the patient\'s narrative, timeline, and impact on daily life...',
      helpText: 'Use open-ended questions and allow the patient to tell their story. The patient\'s own words often provide valuable diagnostic information.'
    }
  }
};

// Question flow logic - now with more open-ended questions
const questionFlowLogic = {
  // Initial description leads to timeline
  chest_pain_description: {
    next: 'chest_timeline',
    analyzeAnswer: (answer) => {
      const lower = answer.toLowerCase();
      if (lower.includes('crushing') || lower.includes('pressure') || lower.includes('elephant')) {
        return { priority: 'high', suggestCardiac: true };
      }
      return { priority: 'medium' };
    }
  },
  respiratory_complaint: {
    next: 'respiratory_timeline',
    analyzeAnswer: (answer) => {
      const lower = answer.toLowerCase();
      if (lower.includes('sudden') || lower.includes('can\'t breathe') || lower.includes('drowning')) {
        return { priority: 'high', suggestAcute: true };
      }
      return { priority: 'medium' };
    }
  },
  neuro_timeline: {
    next: 'neuro_associated',
    analyzeAnswer: (answer) => {
      const lower = answer.toLowerCase();
      if (lower.includes('sudden') || lower.includes('seconds') || lower.includes('immediate')) {
        return { priority: 'high', suggestVascular: true };
      }
      return { priority: 'medium' };
    }
  }
};

// Enhanced question bank with more open-ended questions
const questionBank = {
  // Timeline questions
  chest_timeline: {
    id: 'chest_timeline',
    text: 'Document the exact timeline: When did the symptoms start? What was the patient doing? How have they changed?',
    type: 'text',
    category: 'Timeline & Context',
    placeholder: 'Include activity at onset, progression, and any periods of relief or worsening...',
    helpText: 'Exertional onset suggests cardiac cause; rest pain may indicate unstable angina. Document if symptoms woke patient from sleep (concerning for cardiac).'
  },
  respiratory_timeline: {
    id: 'respiratory_timeline',
    text: 'When did the breathing difficulty begin? Was it sudden or gradual? Any triggering events?',
    type: 'text',
    category: 'Timeline & Triggers',
    placeholder: 'Document onset, progression, triggers, and any interventions tried...',
    helpText: 'Sudden onset with pleuritic pain suggests PE or pneumothorax',
    templates: ['Gradual onset over days', 'Sudden onset at rest', 'Progressive worsening', 'Intermittent episodes']
  },
  
  // Associated symptoms
  associated_symptoms: {
    id: 'associated_symptoms',
    text: 'What other symptoms is the patient experiencing? Document all associated complaints.',
    type: 'text',
    category: 'Associated Symptoms',
    placeholder: 'Include constitutional symptoms (fever, weight loss), system-specific symptoms, and timing relationships...',
    helpText: 'Associated symptoms help narrow the differential and identify red flags. Ask about symptoms the patient may not think are related.'
  },
  
  // Modifying factors
  modifying_factors: {
    id: 'modifying_factors',
    text: 'What makes the symptoms better or worse? Document all modifying factors.',
    type: 'text',
    category: 'Modifying Factors',
    placeholder: 'Include positions, activities, medications, environmental factors...',
    helpText: 'Relief with antacids suggests GI cause; relief with rest suggests cardiac. Positional changes can differentiate cardiac from musculoskeletal pain.'
  },
  
  // Past medical history context
  relevant_history: {
    id: 'relevant_history',
    text: 'Document relevant past medical history, similar episodes, and current medications that may relate to these symptoms.',
    type: 'text',
    category: 'Medical History',
    placeholder: 'Include previous diagnoses, hospitalizations, procedures, and medication list...',
    helpText: 'Past history often predicts current diagnosis. Don\'t forget to ask about OTC medications and supplements.'
  },
  
  // Social history
  social_context: {
    id: 'social_context',
    text: 'Document relevant social history including occupation, exposures, travel, and lifestyle factors.',
    type: 'text',
    category: 'Social History',
    placeholder: 'Include smoking, alcohol, drugs, occupational exposures, recent travel, sick contacts...',
    helpText: 'Social history can reveal important risk factors and exposures. Be non-judgmental when asking about substance use.'
  },
  
  // Review of systems
  review_of_systems: {
    id: 'review_of_systems',
    text: 'Conduct a focused review of systems. Document pertinent positives and negatives.',
    type: 'text',
    category: 'Review of Systems',
    placeholder: 'Systematically review: Constitutional, HEENT, Cardiac, Pulmonary, GI, GU, MSK, Skin, Neuro, Psych...',
    helpText: 'ROS often uncovers symptoms the patient didn\'t think to mention. Focus on systems most relevant to the chief complaint.'
  },
  
  // Specific symptom characterization
  pain_characterization: {
    id: 'pain_characterization',
    text: 'Have the patient describe the pain in detail: quality, severity, exact location, radiation, and timing.',
    type: 'text',
    category: 'Pain Assessment',
    placeholder: 'Use OPQRST: Onset, Provocation, Quality, Radiation, Severity, Time...',
    helpText: 'Different pain qualities suggest different etiologies. Have patient point to exact location with one finger if possible.'
  },
  
  // Functional impact
  functional_impact: {
    id: 'functional_impact',
    text: 'How are these symptoms affecting the patient\'s daily life? What can\'t they do now that they could do before?',
    type: 'text',
    category: 'Functional Assessment',
    placeholder: 'Document impact on work, sleep, activities, self-care...',
    helpText: 'Functional impact helps gauge severity and urgency. Specific examples are more useful than general statements.'
  },
  
  // Patient's concerns
  patient_concerns: {
    id: 'patient_concerns',
    text: 'What is the patient most worried about? What do they think might be causing their symptoms?',
    type: 'text',
    category: 'Patient Perspective',
    placeholder: 'Document patient\'s fears, beliefs, and expectations...',
    helpText: 'Understanding patient concerns improves communication and compliance. Patients often have specific fears (e.g., cancer, heart attack) that need addressing.'
  },
  
  // Previous treatments
  tried_treatments: {
    id: 'tried_treatments',
    text: 'What has the patient already tried for these symptoms? What helped? What didn\'t help?',
    type: 'text',
    category: 'Previous Treatments',
    placeholder: 'Include medications, home remedies, lifestyle changes, and their effects...',
    helpText: 'Response to treatment provides diagnostic clues. Lack of response to typical treatments may suggest alternative diagnosis.'
  },
  
  // Sleep and constitutional symptoms
  constitutional_symptoms: {
    id: 'constitutional_symptoms',
    text: 'Document any constitutional symptoms: fever, chills, night sweats, weight changes, fatigue, appetite changes.',
    type: 'text',
    category: 'Constitutional Symptoms',
    placeholder: 'Include timing, severity, and any patterns...',
    helpText: 'Constitutional symptoms suggest systemic illness. Unintentional weight loss is always concerning.'
  },
  
  // Red flag screening
  red_flag_screen: {
    id: 'red_flag_screen',
    text: 'Screen for red flag symptoms based on the presentation. Document any concerning features.',
    type: 'text',
    category: 'Red Flag Assessment',
    placeholder: 'Systematically check for warning signs specific to this presentation...',
    helpText: 'Red flags require urgent evaluation or change in management. If red flags present, document your immediate plan.'
  }
};

// Dynamic question generation based on context
export const generateNextQuestion = async (chiefComplaint, questionHistory, patientData, focus = null) => {
  // Simulate brief processing
  await new Promise(resolve => setTimeout(resolve, 200));

  const complaintLower = chiefComplaint.toLowerCase();
  let category = 'general';
  let pattern = null;

  // Determine the clinical category
  for (const [cat, config] of Object.entries(clinicalPatterns)) {
    if (config.triggers.some(trigger => complaintLower.includes(trigger))) {
      category = cat;
      pattern = config;
      break;
    }
  }

  // If no questions asked yet, return initial question
  if (questionHistory.length === 0) {
    const initialQuestion = pattern ? pattern.initialQuestion : clinicalPatterns.general.initialQuestion;
    const directions = getSuggestedDirections(category, []);
    return {
      question: initialQuestion,
      suggestedDirections: directions
    };
  }

  // Check if last question was skipped with context
  const lastQuestion = questionHistory[questionHistory.length - 1];
  if (lastQuestion.skipped && lastQuestion.skipContext && focus === null) {
    // Use skip context to determine next question
    focus = `skip_context: ${lastQuestion.skipContext}`;
  }

  // Analyze the most recent answer to determine next question
  const questionFlow = questionFlowLogic[lastQuestion.id];
  
  // Get the next question based on flow logic
  let nextQuestionId = null;
  if (questionFlow && questionFlow.next) {
    nextQuestionId = questionFlow.next;
  } else {
    // Default progression based on number of questions asked
    const progressionMap = [
      'timeline', 'associated_symptoms', 'modifying_factors', 
      'relevant_history', 'social_context', 'functional_impact',
      'tried_treatments', 'constitutional_symptoms', 'review_of_systems',
      'patient_concerns', 'red_flag_screen'
    ];
    
    // Find next unanked question type
    const askedIds = questionHistory.map(q => q.id);
    for (const questionType of progressionMap) {
      const questionId = `${category}_${questionType}`;
      if (questionBank[questionId] && !askedIds.includes(questionId)) {
        nextQuestionId = questionId;
        break;
      }
      // Try generic version if specific doesn't exist
      if (questionBank[questionType] && !askedIds.includes(questionType)) {
        nextQuestionId = questionType;
        break;
      }
    }
  }

  // If we have a specific focus, override the next question
  if (focus) {
    if (focus.startsWith('skip_context:')) {
      // Parse skip context to determine appropriate question
      const skipContext = focus.replace('skip_context:', '').trim().toLowerCase();
      if (skipContext.includes('sleep')) {
        nextQuestionId = 'constitutional_symptoms';
      } else if (skipContext.includes('family') || skipContext.includes('history')) {
        nextQuestionId = 'relevant_history';
      } else if (skipContext.includes('social') || skipContext.includes('lifestyle')) {
        nextQuestionId = 'social_context';
      } else if (skipContext.includes('function') || skipContext.includes('daily')) {
        nextQuestionId = 'functional_impact';
      } else if (skipContext.includes('pain')) {
        nextQuestionId = 'pain_characterization';
      } else if (skipContext.includes('treatment') || skipContext.includes('medication')) {
        nextQuestionId = 'tried_treatments';
      }
    } else if (focus.startsWith('custom:')) {
      // Handle custom pathway
      const customFocus = focus.replace('custom:', '').trim().toLowerCase();
      if (customFocus.includes('risk') || customFocus.includes('factor')) {
        nextQuestionId = 'relevant_history';
      } else if (customFocus.includes('emergency') || customFocus.includes('urgent')) {
        nextQuestionId = 'red_flag_screen';
      } else if (customFocus.includes('detail') || customFocus.includes('specific')) {
        nextQuestionId = 'pain_characterization';
      }
    } else {
      const focusMap = {
        'cardiac_acs': 'pain_characterization',
        'respiratory_detailed': 'respiratory_timeline',
        'functional': 'functional_impact',
        'social': 'social_context',
        'red_flags': 'red_flag_screen',
        'review_systems': 'review_of_systems',
        'cardiac_risk': 'relevant_history',
        'infectious': 'constitutional_symptoms',
        'pe_assessment': 'modifying_factors'
      };
      nextQuestionId = focusMap[focus] || nextQuestionId;
    }
  }

  // Get the actual question object
  const nextQuestion = questionBank[nextQuestionId];
  
  if (nextQuestion) {
    const directions = getSuggestedDirections(category, questionHistory);
    return {
      question: nextQuestion,
      suggestedDirections: directions
    };
  }

  // If we've exhausted category-specific questions, ask general ones
  const generalQuestions = [
    'functional_impact',
    'patient_concerns', 
    'red_flag_screen',
    'review_of_systems'
  ];

  const askedIds = questionHistory.map(q => q.id);
  for (const qId of generalQuestions) {
    if (!askedIds.includes(qId) && questionBank[qId]) {
      return {
        question: questionBank[qId],
        suggestedDirections: []
      };
    }
  }

  // No more questions
  return { question: null, suggestedDirections: [] };
};

export const getSuggestedDirections = (category, questionHistory) => {
  const directions = [];
  
  // Only show directions after initial questions
  if (questionHistory.length < 2) {
    return [];
  }

  // Analyze answers to suggest pathways
  const answersText = questionHistory.map(q => q.answer).join(' ').toLowerCase();

  switch (category) {
    case 'cardiac':
      if (answersText.includes('exertion') || answersText.includes('exercise')) {
        directions.push({
          label: 'Exercise tolerance',
          description: 'Detailed functional capacity assessment',
          focus: 'functional'
        });
      }
      if (answersText.includes('radiating') || answersText.includes('jaw') || answersText.includes('arm')) {
        directions.push({
          label: 'ACS protocol',
          description: 'Focus on acute coronary syndrome',
          focus: 'cardiac_acs'
        });
      }
      directions.push({
        label: 'Risk stratification',
        description: 'Assess cardiac risk factors',
        focus: 'cardiac_risk'
      });
      break;
      
    case 'respiratory':
      if (answersText.includes('fever') || answersText.includes('productive')) {
        directions.push({
          label: 'Infectious workup',
          description: 'Focus on pneumonia/bronchitis',
          focus: 'infectious'
        });
      }
      if (answersText.includes('sudden') || answersText.includes('pleuritic')) {
        directions.push({
          label: 'PE evaluation', 
          description: 'Assess for pulmonary embolism',
          focus: 'pe_assessment'
        });
      }
      break;
      
    case 'neurological':
      if (answersText.includes('worst') || answersText.includes('thunderclap')) {
        directions.push({
          label: 'Urgent evaluation',
          description: 'Focus on emergent causes',
          focus: 'red_flags'
        });
      }
      directions.push({
        label: 'Detailed neuro exam',
        description: 'Document focal findings',
        focus: 'neuro_exam'
      });
      break;

    default:
      directions.push({
        label: 'Systematic review',
        description: 'Complete review of systems',
        focus: 'review_systems'
      });
      directions.push({
        label: 'Functional assessment',
        description: 'Impact on daily activities',
        focus: 'functional'
      });
  }

  // Add social history if not yet explored
  if (!questionHistory.some(q => q.id.includes('social'))) {
    directions.push({
      label: 'Social factors',
      description: 'Explore social/environmental factors',
      focus: 'social'
    });
  }

  return directions.slice(0, 4);
};

export const analyzeSymptoms = (chiefComplaint, answers, patientData) => {
  const insights = [];
  const redFlags = [];
  const complaintLower = chiefComplaint.toLowerCase();

  // Convert answers object to searchable text
  const answersText = Object.values(answers).join(' ').toLowerCase();

  // Check for red flags based on patterns
  for (const [, config] of Object.entries(clinicalPatterns)) {
    if (config.triggers.some(trigger => complaintLower.includes(trigger))) {
      // Check each red flag pattern
      config.redFlags.forEach(flag => {
        const hasPattern = flag.pattern.every(keyword => answersText.includes(keyword));
        if (hasPattern) {
          redFlags.push(flag.message);
        }
      });
    }
  }

  // Generate insights based on specific findings
  
  // Timeline insights
  if (answersText.includes('sudden') || answersText.includes('acute') || answersText.includes('minutes')) {
    insights.push('Acute onset - consider emergent causes and need for rapid evaluation');
  } else if (answersText.includes('weeks') || answersText.includes('months')) {
    insights.push('Subacute/chronic presentation - systematic workup appropriate');
  }

  // Severity insights
  if (answersText.includes('severe') || answersText.includes('worst') || answersText.includes('10/10')) {
    insights.push('High severity symptoms require prompt evaluation and symptom control');
  }

  // Pattern insights
  if (answersText.includes('worse at night') || answersText.includes('wakes me')) {
    insights.push('Nocturnal symptoms - consider cardiac, pulmonary, or GERD etiology');
  }

  if (answersText.includes('with meals') || answersText.includes('after eating')) {
    insights.push('Meal-related symptoms - consider GI or cardiac (postprandial angina) causes');
  }

  // Constitutional symptoms
  if (answersText.includes('weight loss') && answersText.includes('unintentional')) {
    insights.push('Unintentional weight loss - requires thorough evaluation for malignancy or chronic disease');
    redFlags.push('Unintentional weight loss reported - consider malignancy screening');
  }

  if (answersText.includes('fever') && answersText.includes('night sweats')) {
    insights.push('B symptoms present - consider infectious, inflammatory, or malignant causes');
  }

  // Functional impact
  if (answersText.includes('cannot work') || answersText.includes('bedridden') || answersText.includes('unable to')) {
    insights.push('Significant functional impairment - expedited evaluation warranted');
  }

  // Age-specific insights
  const age = parseInt(patientData.age) || 0;
  if (age > 65) {
    if (complaintLower.includes('chest') || answersText.includes('chest')) {
      insights.push('Elderly patient with chest symptoms - higher risk for cardiac disease');
    }
    if (answersText.includes('fall') || answersText.includes('dizzy')) {
      insights.push('Fall risk in elderly patient - comprehensive assessment needed');
    }
  }

  if (age < 40 && answersText.includes('chest pain')) {
    insights.push('Young patient with chest pain - consider non-cardiac causes but don\'t miss PE or pericarditis');
  }

  // Medication-related insights
  if (answersText.includes('started new medication') || answersText.includes('recently prescribed')) {
    insights.push('Recent medication change - consider drug side effects or interactions');
  }

  // Risk factor insights
  if (answersText.includes('smoking') || answersText.includes('smoker')) {
    insights.push('Smoking history increases risk for cardiovascular and pulmonary disease');
  }

  if (answersText.includes('family history') && (answersText.includes('heart') || answersText.includes('cancer'))) {
    insights.push('Significant family history - consider genetic/hereditary conditions');
  }

  // Treatment response insights
  if (answersText.includes('no relief') || answersText.includes('nothing helps')) {
    insights.push('Poor response to initial treatments - reconsider diagnosis');
  }

  if (answersText.includes('antacid helps') || answersText.includes('better with food')) {
    insights.push('GI symptom relief pattern - consider acid-related disorders');
  }

  // Ensure we always have at least one insight
  if (insights.length === 0 && Object.keys(answers).length > 2) {
    insights.push(`${Object.keys(answers).length} clinical data points collected - pattern analysis in progress`);
  }

  return { insights, redFlags };
};

export const getStandardizedTools = (chiefComplaint) => {
  const tools = [];
  const complaintLower = chiefComplaint.toLowerCase();

  // Core tools always available
  const coreTools = {
    depression: {
      id: 'phq9',
      name: 'PHQ-9',
      description: 'Depression screening',
      questions: [
        'Little interest or pleasure in doing things',
        'Feeling down, depressed, or hopeless',
        'Trouble falling asleep, staying asleep, or sleeping too much',
        'Feeling tired or having little energy',
        'Poor appetite or overeating',
        'Feeling bad about yourself',
        'Trouble concentrating',
        'Moving or speaking slowly or being restless',
        'Thoughts of self-harm'
      ]
    },
    anxiety: {
      id: 'gad7',
      name: 'GAD-7',
      description: 'Anxiety screening',
      questions: [
        'Feeling nervous, anxious, or on edge',
        'Not being able to stop or control worrying',
        'Worrying too much about different things',
        'Trouble relaxing',
        'Being so restless that it\'s hard to sit still',
        'Becoming easily annoyed or irritable',
        'Feeling afraid as if something awful might happen'
      ]
    }
  };

  // Condition-specific tools
  const specificTools = {
    pain: {
      id: 'brief-pain',
      name: 'Brief Pain Inventory',
      description: 'Comprehensive pain assessment',
      conditions: ['pain', 'ache', 'hurt', 'sore']
    },
    wells_pe: {
      id: 'wells-pe',
      name: 'Wells\' Criteria for PE',
      description: 'PE risk stratification',
      conditions: ['chest', 'breath', 'dyspnea', 'clot']
    },
    cage: {
      id: 'cage',
      name: 'CAGE Questionnaire',
      description: 'Alcohol screening',
      conditions: ['alcohol', 'drinking', 'substance']
    },
    mmse: {
      id: 'mmse',
      name: 'Mini-Mental State Exam',
      description: 'Cognitive assessment',
      conditions: ['memory', 'confusion', 'dementia', 'cognitive']
    }
  };

  // Add condition-specific tools
  Object.values(specificTools).forEach(tool => {
    if (tool.conditions.some(condition => complaintLower.includes(condition))) {
      tools.push(tool);
    }
  });

  // Always include depression and anxiety screening
  tools.push(coreTools.depression);
  tools.push(coreTools.anxiety);

  // Remove duplicates
  const uniqueTools = tools.filter((tool, index, self) =>
    index === self.findIndex((t) => t.id === tool.id)
  );

  return uniqueTools;
};

export const generateAssessmentSummary = (chiefComplaint, answers, patientData) => {
  const summary = {
    summary: '',
    insights: []
  };

  // Count answered questions
  const answeredCount = Object.keys(answers).length;
  if (answeredCount === 0) return summary;

  // Build narrative summary
  const age = parseInt(patientData.age) || 0;
  const gender = patientData.gender || 'patient';
  
  // Start with patient demographics and chief complaint
  summary.summary = `${age}-year-old ${gender} presenting with ${chiefComplaint.toLowerCase()}. `;

  // Add key findings from answers
  const categories = {
    timeline: [],
    symptoms: [],
    modifiers: [],
    history: [],
    functional: []
  };

  // Categorize answers
  Object.entries(answers).forEach(([questionId, data]) => {
    const answer = data.answer.toLowerCase();
    const category = data.category?.toLowerCase() || '';
    
    if (category.includes('timeline') || questionId.includes('timeline') || questionId.includes('duration')) {
      categories.timeline.push(answer);
    } else if (category.includes('symptom') || category.includes('associated')) {
      categories.symptoms.push(answer);
    } else if (category.includes('modif') || answer.includes('worse') || answer.includes('better')) {
      categories.modifiers.push(answer);
    } else if (category.includes('history') || category.includes('medical')) {
      categories.history.push(answer);
    } else if (category.includes('function') || category.includes('impact')) {
      categories.functional.push(answer);
    }
  });

  // Build timeline summary
  if (categories.timeline.length > 0) {
    const timelineText = categories.timeline[0];
    if (timelineText.includes('hour')) {
      summary.summary += 'Acute onset. ';
    } else if (timelineText.includes('day')) {
      summary.summary += 'Subacute presentation. ';
    } else if (timelineText.includes('week') || timelineText.includes('month')) {
      summary.summary += 'Chronic symptoms. ';
    }
  }

  // Add symptom characterization
  if (categories.symptoms.length > 0) {
    summary.summary += `Associated with ${categories.symptoms.slice(0, 2).join(', ')}. `;
  }

  // Add functional impact if significant
  if (categories.functional.length > 0) {
    const functionalText = categories.functional[0];
    if (functionalText.includes('severe') || functionalText.includes('unable')) {
      summary.summary += 'Significant functional impairment noted. ';
    }
  }

  // Generate clinical insights based on patterns
  const answersText = Object.values(answers).map(a => a.answer).join(' ').toLowerCase();

  // Pattern-based insights
  if (answersText.includes('worse') && answersText.includes('night')) {
    summary.insights.push('Nocturnal symptom exacerbation - consider cardiac, pulmonary, or GERD causes');
  }

  if (answersText.includes('sudden') && answersText.includes('severe')) {
    summary.insights.push('Acute severe presentation requires expedited evaluation');
  }

  if (answersText.includes('progressive') || answersText.includes('worsening')) {
    summary.insights.push('Progressive symptoms warrant close monitoring and follow-up');
  }

  if (answersText.includes('fever') || answersText.includes('chills')) {
    summary.insights.push('Constitutional symptoms suggest infectious or inflammatory process');
  }

  if (answersText.includes('weight loss')) {
    summary.insights.push('Weight loss requires investigation for systemic disease');
  }

  // Age-specific insights
  if (age > 65 && answersText.includes('fall')) {
    summary.insights.push('Fall risk assessment needed in elderly patient');
  }

  if (age < 50 && answersText.includes('chest')) {
    summary.insights.push('Consider both cardiac and non-cardiac causes in younger patient');
  }

  // Treatment response insights
  if (answersText.includes('no relief') || answersText.includes('failed')) {
    summary.insights.push('Poor response to initial treatments - consider alternative diagnoses');
  }

  // Add summary of assessment completeness
  if (answeredCount < 5) {
    summary.insights.push(`Initial assessment phase - ${answeredCount} areas explored`);
  } else if (answeredCount < 10) {
    summary.insights.push(`Comprehensive assessment in progress - ${answeredCount} clinical areas documented`);
  } else {
    summary.insights.push(`Thorough assessment completed - ${answeredCount} clinical findings documented`);
  }

  // Chief complaint specific insights
  const complaintLower = chiefComplaint.toLowerCase();
  if (complaintLower.includes('chest') && answersText.includes('exertion')) {
    summary.insights.push('Exertional symptoms - cardiac etiology should be ruled out');
  }

  if (complaintLower.includes('headache') && answersText.includes('worst')) {
    summary.insights.push('Red flag headache features present - urgent evaluation indicated');
  }

  return summary;
};