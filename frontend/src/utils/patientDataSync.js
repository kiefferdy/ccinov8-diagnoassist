// Utility function to sync patient data from encounters
export const syncPatientDataFromEncounters = (patient, episodes, getEpisodeEncounters) => {
  const allEncounters = episodes.flatMap(ep => getEpisodeEncounters(ep.id));
  
  // Extract unique conditions from encounter assessments
  const conditionsMap = new Map();
  const medicationsMap = new Map();
  
  allEncounters.forEach(encounter => {
    // Extract diagnoses/conditions
    if (encounter.soap?.assessment?.diagnoses) {
      encounter.soap.assessment.diagnoses.forEach(dx => {
        if (dx.icd10 && dx.description && !conditionsMap.has(dx.icd10)) {
          conditionsMap.set(dx.icd10, {
            id: `C${Date.now()}_${dx.icd10}`,
            condition: dx.description,
            icd10: dx.icd10,
            diagnosedDate: encounter.date,
            status: 'active',
            fromEncounter: encounter.id
          });
        }
      });
    }
    
    // Extract medications from plans
    if (encounter.soap?.plan?.medications) {
      encounter.soap.plan.medications.forEach(med => {
        const medKey = `${med.name}_${med.dosage}`;
        if (!medicationsMap.has(medKey)) {
          medicationsMap.set(medKey, {
            id: `M${Date.now()}_${medKey}`,
            name: med.name,
            dosage: med.dosage,
            frequency: med.frequency,
            startDate: encounter.date,
            ongoing: true,
            fromEncounter: encounter.id
          });
        }
      });
    }
  });
  
  // Merge with existing patient data
  const existingConditions = patient.medicalBackground?.chronicConditions || [];
  const existingMedications = patient.medicalBackground?.medications || [];
  
  // Keep manually added conditions and add auto-detected ones
  const manualConditions = existingConditions.filter(c => !c.fromEncounter);
  const autoConditions = Array.from(conditionsMap.values());
  
  // Keep manually added medications and add auto-detected ones
  const manualMedications = existingMedications.filter(m => !m.fromEncounter);
  const autoMedications = Array.from(medicationsMap.values());
  
  return {
    chronicConditions: [...manualConditions, ...autoConditions],
    medications: [...manualMedications, ...autoMedications]
  };
};