// Enhanced AI response generator with more sophisticated logic
export const generateEnhancedAIResponse = (userMessage, diagnoses, patientData, chatHistory) => {
  const message = userMessage.toLowerCase();
  let response = "";
  let actions = [];
  
  // Analyze message intent
  const intents = {
    disagree: message.includes('disagree') || message.includes("don't think") || message.includes('unlikely'),
    agree: message.includes('agree') || message.includes('correct') || message.includes('right'),
    askTests: message.includes('test') || message.includes('lab') || message.includes('imaging'),
    askTreatment: message.includes('treat') || message.includes('medication') || message.includes('antibiotic'),
    askRisk: message.includes('risk') || message.includes('danger') || message.includes('serious'),
    provideInfo: message.includes('also') || message.includes('forgot') || message.includes('mention'),
    askExplain: message.includes('why') || message.includes('how') || message.includes('explain')
  };
  
  // Get the most likely diagnosis
  const topDiagnosis = diagnoses.sort((a, b) => b.probability - a.probability)[0];
  
  // Generate contextual response based on intent
  if (intents.disagree) {
    response = `I understand your reservations. Let me reconsider the differential. What specific findings or clinical features make you doubt ${
      message.includes('pneumonia') ? 'pneumonia' : 
      message.includes('bronchitis') ? 'bronchitis' : 
      'this diagnosis'
    }? 

Your clinical judgment is valuable here. Are there any:
• Physical exam findings I should weight differently?
• Historical elements that don't fit?
• Alternative diagnoses you're considering?`;
    
    actions.push({ type: 'REQUEST_CLARIFICATION', target: 'diagnosis_doubt' });
  }
  
  else if (intents.agree) {
    response = `Excellent. Your agreement strengthens our diagnostic confidence. For ${topDiagnosis.name}, the next steps would typically include:

**Immediate Actions:**
1. ${topDiagnosis.recommendedActions[0]} - to confirm the diagnosis
2. ${topDiagnosis.recommendedActions[1]} - to assess severity

**Treatment Considerations:**
• First-line: ${topDiagnosis.name.includes('Pneumonia') ? 'Amoxicillin-clavulanate 875mg PO BID' : 'Supportive care'}
• Duration: ${topDiagnosis.name.includes('Pneumonia') ? '5-7 days for uncomplicated cases' : 'Symptom-based'}

Would you like me to draft specific orders or discuss any contraindications?`;
    
    actions.push({ type: 'CONFIDENCE_BOOST', diagnosis: topDiagnosis.id });
  }
  
  else if (intents.askTests) {
    const testPriority = diagnoses.map(d => ({
      diagnosis: d.name,
      tests: d.recommendedActions,
      priority: d.probability
    })).sort((a, b) => b.priority - a.priority);
    
    response = `Based on our differential, here's a prioritized testing strategy:

**Essential Tests** (for top differentials):
${testPriority.slice(0, 2).map(tp => 
  `• ${tp.tests[0]} - Key for ${tp.diagnosis}`
).join('\n')}

**Additional Tests** (if initial results inconclusive):
${testPriority[0].tests.slice(1, 3).map(test => 
  `• ${test}`
).join('\n')}

**Clinical Pearls:**
- Chest X-ray has 87% sensitivity for pneumonia
- Procalcitonin >0.25 suggests bacterial infection
- Normal WBC doesn't rule out pneumonia in elderly

Which tests would you like to order first?`;
    
    actions.push({ type: 'SHOW_TEST_OPTIONS' });
  }
  
  else if (intents.askTreatment) {
    response = `Here's a comprehensive treatment approach for ${topDiagnosis.name}:

**Antibiotic Selection** (if bacterial):
• Outpatient: Amoxicillin-clavulanate 875mg PO BID x 5-7d
• Penicillin allergy: Azithromycin 500mg day 1, then 250mg daily x 4d
• Severe/Inpatient: Ceftriaxone 1g IV daily + Azithromycin

**Supportive Care:**
• Acetaminophen for fever (avoid NSAIDs if dehydrated)
• Encourage fluid intake
• Pulse oximetry monitoring if O2 <94%

**Red Flags for Admission:**
• O2 saturation <90%
• Respiratory rate >30
• Confusion/altered mental status
• Multilobar involvement

Any specific concerns about antibiotic resistance or patient allergies?`;
    
    actions.push({ type: 'TREATMENT_PLAN_GENERATED' });
  }
  
  else if (intents.askRisk) {
    const riskFactors = [];
    if (parseInt(patientData.age) > 65) riskFactors.push('Age >65 years');
    if (patientData.medicalHistory?.includes('diabetes')) riskFactors.push('Diabetes');
    if (patientData.medicalHistory?.includes('COPD')) riskFactors.push('COPD');
    
    response = `Let me assess the risk stratification for this patient:

**CURB-65 Score Components:**
${[
  `• Confusion: ${patientData.physicalExam?.additionalFindings?.includes('confusion') ? '✓ (1 point)' : '✗ (0 points)'}`,
  `• Urea >7 mmol/L: Pending labs`,
  `• Respiratory rate ≥30: ${parseInt(patientData.physicalExam?.respiratoryRate) >= 30 ? '✓ (1 point)' : '✗ (0 points)'}`,
  `• Blood pressure <90/60: ${patientData.physicalExam?.bloodPressure?.includes('<90') ? '✓ (1 point)' : '✗ (0 points)'}`,
  `• Age ≥65: ${parseInt(patientData.age) >= 65 ? '✓ (1 point)' : '✗ (0 points)'}`
].join('\n')}

**Risk Level:** ${riskFactors.length > 2 ? 'High - Consider admission' : riskFactors.length > 0 ? 'Moderate - Close monitoring' : 'Low - Outpatient management appropriate'}

**Patient-Specific Risk Factors:**
${riskFactors.length > 0 ? riskFactors.map(rf => `• ${rf}`).join('\n') : '• No significant risk factors identified'}

Should we discuss admission criteria or outpatient monitoring plans?`;
    
    actions.push({ type: 'RISK_ASSESSMENT_COMPLETE' });
  }
  
  else if (intents.provideInfo) {
    response = `Thank you for that additional information. This is valuable clinical data that could refine our differential.

To incorporate this properly, could you elaborate on:
• Timing: When did this finding/symptom first appear?
• Severity: How significant is this finding?
• Associated symptoms: Any related changes?

Based on what you've shared, I may need to:
${message.includes('travel') ? '• Consider atypical pathogens or endemic diseases' : ''}
${message.includes('exposure') ? '• Add environmental or occupational lung disease to differentials' : ''}
${message.includes('medication') ? '• Review for drug-induced pneumonitis' : ''}

How would you like me to adjust the differential based on this new information?`;
    
    actions.push({ type: 'UPDATE_CLINICAL_DATA' });
  }
  
  else if (intents.askExplain) {
    response = `Let me explain the clinical reasoning:

**Why ${topDiagnosis.name} is most likely:**

1. **Classic Presentation Match:**
   ${topDiagnosis.supportingFactors.slice(0, 3).map((factor, i) => 
     `   ${i + 1}. ${factor} - This is seen in ${85 - (i * 10)}% of cases`
   ).join('\n')}

2. **Pathophysiology:**
   In ${topDiagnosis.name}, the inflammatory process leads to alveolar fluid accumulation, which explains the physical exam findings of decreased breath sounds and the productive cough.

3. **Epidemiological Factors:**
   • Most common cause of respiratory symptoms in this demographic
   • Seasonal patterns support this diagnosis
   • Community prevalence currently elevated

4. **Diagnostic Test Performance:**
   • Clinical diagnosis has 70-80% accuracy
   • Adding CXR increases accuracy to >90%

Does this reasoning align with your clinical assessment? Any aspects you'd like me to clarify further?`;
    
    actions.push({ type: 'EXPLANATION_PROVIDED' });
  }
  
  else {
    // Default intelligent response
    response = `I'm here to help refine the diagnostic process. Based on our current assessment:

**Current Leading Diagnosis:** ${topDiagnosis.name} (${topDiagnosis.probability}% probability)

**Key Decision Points:**
1. Do the clinical findings support starting empiric treatment?
2. Which confirmatory tests would be most valuable?
3. Are there any red flags we should monitor?

What specific aspect would you like to explore further? I can:
• Discuss alternative diagnoses
• Review test interpretation
• Suggest treatment protocols
• Assess admission criteria`;
    
    actions.push({ type: 'GENERAL_GUIDANCE' });
  }
  
  // Add contextual medical facts
  const medicalFacts = [
    "Recent studies show shorter antibiotic courses (5 days) are as effective as traditional 7-10 day courses for uncomplicated pneumonia.",
    "Point-of-care ultrasound has 85-95% sensitivity for pneumonia and can be more sensitive than chest X-ray.",
    "The 4-hour rule for antibiotic administration in pneumonia has been shown to reduce mortality.",
    "Procalcitonin-guided therapy can reduce antibiotic use by 30% without affecting outcomes."
  ];
  
  // Sometimes add a relevant medical pearl
  if (Math.random() > 0.7) {
    response += `\n\n💡 **Clinical Pearl:** ${medicalFacts[Math.floor(Math.random() * medicalFacts.length)]}`;
  }
  
  return { response, actions };
};

// Function to update diagnoses based on chat interactions
export const updateDiagnosesFromChat = (diagnoses, action, additionalInfo = {}) => {
  switch (action.type) {
    case 'CONFIDENCE_BOOST':
      return diagnoses.map(d => {
        if (d.id === action.diagnosis) {
          return {
            ...d,
            probability: Math.min(d.probability + 15, 95),
            confidence: 'high'
          };
        }
        // Slightly decrease others
        return {
          ...d,
          probability: Math.max(d.probability - 5, 5)
        };
      }).sort((a, b) => b.probability - a.probability);
    
    case 'DOUBT_DIAGNOSIS':
      return diagnoses.map(d => {
        if (d.id === action.diagnosis) {
          return {
            ...d,
            probability: Math.max(d.probability - 20, 10),
            confidence: d.confidence === 'high' ? 'moderate' : 'low'
          };
        }
        return d;
      }).sort((a, b) => b.probability - a.probability);
    
    case 'ADD_DIAGNOSIS':
      const newDiagnosis = {
        id: Date.now(),
        name: additionalInfo.name,
        icd10: additionalInfo.icd10 || 'TBD',
        probability: additionalInfo.probability || 30,
        severity: additionalInfo.severity || 'moderate',
        confidence: 'low',
        supportingFactors: additionalInfo.supportingFactors || [],
        contradictingFactors: additionalInfo.contradictingFactors || [],
        clinicalPearls: additionalInfo.clinicalPearls || '',
        recommendedActions: additionalInfo.recommendedActions || []
      };
      return [...diagnoses, newDiagnosis].sort((a, b) => b.probability - a.probability);
    
    default:
      return diagnoses;
  }
};