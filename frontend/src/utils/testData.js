// Sample data for testing and demonstration purposes
export const sampleSOAPData = {
  assessment: {
    diagnoses: [
      {
        icd10: 'E11.9',
        description: 'Type 2 diabetes mellitus without complications',
        isPrimary: true
      },
      {
        icd10: 'I10',
        description: 'Essential (primary) hypertension',
        isPrimary: false
      }
    ]
  },
  plan: {
    medications: [
      {
        name: 'Metformin',
        dosage: '500mg',
        frequency: 'Twice daily',
        duration: 'Ongoing',
        instructions: 'Take with meals'
      },
      {
        name: 'Lisinopril',
        dosage: '10mg',
        frequency: 'Once daily',
        duration: 'Ongoing',
        instructions: 'Take in the morning'
      }
    ]
  }
};

// Function to add test encounter data
export const addTestEncounterData = (patientId, episodeId, createEncounter) => {
  const testEncounter = createEncounter(episodeId, patientId, 'follow-up');
  
  // Add diagnoses to assessment
  testEncounter.soap.assessment.diagnoses = sampleSOAPData.assessment.diagnoses;
  
  // Add medications to plan
  testEncounter.soap.plan.medications = sampleSOAPData.plan.medications;
  
  // Mark as signed
  testEncounter.status = 'signed';
  testEncounter.signedAt = new Date().toISOString();
  testEncounter.signedBy = 'Dr. Demo';
  
  // Save to localStorage
  const encounters = JSON.parse(localStorage.getItem('encounters') || '[]');
  const updatedEncounters = encounters.map(e => 
    e.id === testEncounter.id ? testEncounter : e
  );
  localStorage.setItem('encounters', JSON.stringify(updatedEncounters));
  
  return testEncounter;
};