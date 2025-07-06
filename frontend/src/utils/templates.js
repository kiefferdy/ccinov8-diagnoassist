// Common templates for quick documentation
export const soapTemplates = {
  // Chief Complaint Templates
  chiefComplaint: {
    'upper-respiratory': {
      hpi: 'Patient presents with upper respiratory symptoms including nasal congestion, rhinorrhea, and sore throat. Symptoms began [X] days ago and have been [improving/worsening/stable]. Associated symptoms include [fever/cough/headache]. Denies shortness of breath or chest pain.',
      ros: {
        constitutional: 'Positive for mild fatigue',
        ent: 'Positive for nasal congestion, rhinorrhea, sore throat',
        respiratory: 'Negative for dyspnea, wheezing',
        cardiovascular: 'Negative for chest pain, palpitations'
      },
      physicalExam: {
        general: 'Alert and oriented, appears mildly uncomfortable',
        additionalFindings: 'HEENT: Mild pharyngeal erythema, clear nasal discharge. No lymphadenopathy. Lungs: Clear to auscultation bilaterally. Heart: Regular rate and rhythm, no murmurs.'
      },
      assessment: 'Viral upper respiratory infection',
      plan: {
        medications: [
          { name: 'Acetaminophen', dosage: '500-1000mg', frequency: 'Every 6 hours as needed', duration: 'As needed', instructions: 'For fever and pain' }
        ],
        followUp: { timeframe: '1 week if not improved', reason: 'Re-evaluate if symptoms persist' },
        patientEducation: [
          { topic: 'URI self-care', materials: 'Handout on viral URI management' }
        ]
      }
    },
    
    'hypertension-followup': {
      hpi: 'Patient returns for hypertension follow-up. Currently on [medications]. Home blood pressure readings have been [range]. Denies headache, chest pain, or shortness of breath. Medication compliance has been [good/fair/poor].',
      ros: {
        constitutional: 'Negative for fatigue, weight changes',
        cardiovascular: 'Negative for chest pain, palpitations, edema',
        neurological: 'Negative for headache, dizziness'
      },
      physicalExam: {
        general: 'Alert and oriented, appears well',
        additionalFindings: 'Cardiovascular: Regular rate and rhythm, no murmurs. No peripheral edema. Lungs: Clear bilaterally.'
      },
      assessment: 'Hypertension, [controlled/uncontrolled]',
      plan: {
        medications: [],
        followUp: { timeframe: '3 months', reason: 'Routine hypertension monitoring' },
        patientEducation: [
          { topic: 'DASH diet', materials: 'Dietary recommendations handout' },
          { topic: 'Home BP monitoring', materials: 'Instructions for proper technique' }
        ]
      }
    },
    
    'diabetes-followup': {
      hpi: 'Patient with Type 2 diabetes returns for routine follow-up. Last A1c was [X]%. Blood glucose logs show [pattern]. Currently on [medications]. Denies polyuria, polydipsia, or blurred vision. [Compliance details].',
      ros: {
        constitutional: 'Negative for weight loss, fatigue',
        endocrine: 'Negative for polyuria, polydipsia',
        neurological: 'Negative for numbness, tingling',
        eyes: 'Negative for blurred vision'
      },
      physicalExam: {
        general: 'Alert and oriented, appears well',
        additionalFindings: 'Feet: No lesions, pulses intact, monofilament testing normal. Eyes: No obvious retinopathy (recommend annual eye exam).'
      },
      assessment: 'Type 2 diabetes mellitus, [controlled/uncontrolled]',
      plan: {
        diagnosticTests: [
          { test: 'Hemoglobin A1c', urgency: 'routine' },
          { test: 'Basic metabolic panel', urgency: 'routine' },
          { test: 'Lipid panel', urgency: 'routine' }
        ],
        followUp: { timeframe: '3 months', reason: 'Diabetes management' },
        patientEducation: [
          { topic: 'Diabetes self-management', materials: 'Blood glucose monitoring log' },
          { topic: 'Foot care', materials: 'Diabetic foot care instructions' }
        ]
      }
    },
    
    'acute-back-pain': {
      hpi: 'Patient presents with acute onset low back pain that began [X] days ago after [lifting/bending/no specific trigger]. Pain is described as [sharp/dull/aching] and rated [X/10]. Pain [radiates/does not radiate] to legs. [Improves/worsens] with [movement/rest]. No bowel/bladder dysfunction.',
      ros: {
        musculoskeletal: 'Positive for back pain, negative for joint pain',
        neurological: 'Negative for numbness, weakness, bowel/bladder dysfunction'
      },
      physicalExam: {
        general: 'Alert and oriented, ambulating with antalgic gait',
        additionalFindings: 'Back: Tenderness over lumbar paraspinal muscles. No midline tenderness. Straight leg raise negative bilaterally. Strength 5/5 in lower extremities. DTRs 2+ and symmetric.'
      },
      assessment: 'Acute mechanical low back pain',
      plan: {
        medications: [
          { name: 'Ibuprofen', dosage: '600mg', frequency: 'Three times daily with food', duration: '1 week', instructions: 'Take with food' },
          { name: 'Cyclobenzaprine', dosage: '5mg', frequency: 'At bedtime', duration: '1 week', instructions: 'May cause drowsiness' }
        ],
        followUp: { timeframe: '2 weeks', reason: 'Re-evaluate if not improved' },
        patientEducation: [
          { topic: 'Back pain exercises', materials: 'Physical therapy handout' },
          { topic: 'Proper body mechanics', materials: 'Lifting techniques guide' }
        ],
        activityRestrictions: 'Avoid heavy lifting for 1 week. Gentle stretching encouraged.'
      }
    }
  },
  
  // Quick text snippets for common findings
  quickText: {
    normalVitals: {
      bloodPressure: '120/80',
      heartRate: '72',
      temperature: '98.6',
      respiratoryRate: '16',
      oxygenSaturation: '98%'
    },
    normalExam: {
      general: 'Alert and oriented x3, appears well, in no acute distress',
      cardiovascular: 'Regular rate and rhythm, no murmurs, rubs, or gallops',
      respiratory: 'Clear to auscultation bilaterally, no wheezes, rales, or rhonchi',
      abdomen: 'Soft, non-tender, non-distended, normal bowel sounds',
      neurological: 'Alert and oriented, cranial nerves II-XII intact, strength 5/5 throughout'
    }
  }
};

// Function to apply a template
export const applyTemplate = (templateKey, customValues = {}) => {
  const template = soapTemplates.chiefComplaint[templateKey];
  if (!template) return null;
  
  // Deep clone the template
  const applied = JSON.parse(JSON.stringify(template));
  
  // Apply any custom values
  Object.keys(customValues).forEach(key => {
    if (applied[key]) {
      applied[key] = customValues[key];
    }
  });
  
  return applied;
};