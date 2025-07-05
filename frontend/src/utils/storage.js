// Storage keys for localStorage
export const StorageKeys = {
  PATIENTS: 'diagnoassist_patients_v2',
  EPISODES: 'diagnoassist_episodes_v2',
  ENCOUNTERS: 'diagnoassist_encounters_v2',
  SETTINGS: 'diagnoassist_settings_v2'
};

// Storage manager for all data operations
export const StorageManager = {
  // Patient operations
  savePatients: (patients) => {
    try {
      localStorage.setItem(StorageKeys.PATIENTS, JSON.stringify(patients));
      return true;
    } catch (error) {
      console.error('Error saving patients:', error);
      return false;
    }
  },

  getPatients: () => {
    try {
      const data = localStorage.getItem(StorageKeys.PATIENTS);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error loading patients:', error);
      return [];
    }
  },

  getPatientById: (patientId) => {
    const patients = StorageManager.getPatients();
    return patients.find(p => p.id === patientId) || null;
  },

  // Episode operations
  saveEpisodes: (episodes) => {
    try {
      localStorage.setItem(StorageKeys.EPISODES, JSON.stringify(episodes));
      return true;
    } catch (error) {
      console.error('Error saving episodes:', error);
      return false;
    }
  },
  getEpisodes: () => {
    try {
      const data = localStorage.getItem(StorageKeys.EPISODES);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error loading episodes:', error);
      return [];
    }
  },

  getPatientEpisodes: (patientId, includeResolved = true) => {
    const episodes = StorageManager.getEpisodes();
    return episodes.filter(e => {
      const matchesPatient = e.patientId === patientId;
      const matchesStatus = includeResolved || e.status !== 'resolved';
      return matchesPatient && matchesStatus;
    });
  },

  getEpisodeById: (episodeId) => {
    const episodes = StorageManager.getEpisodes();
    return episodes.find(e => e.id === episodeId) || null;
  },

  // Encounter operations
  saveEncounters: (encounters) => {
    try {
      localStorage.setItem(StorageKeys.ENCOUNTERS, JSON.stringify(encounters));
      return true;
    } catch (error) {
      console.error('Error saving encounters:', error);
      return false;
    }
  },
  getEncounters: () => {
    try {
      const data = localStorage.getItem(StorageKeys.ENCOUNTERS);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error loading encounters:', error);
      return [];
    }
  },

  getEpisodeEncounters: (episodeId) => {
    const encounters = StorageManager.getEncounters();
    return encounters
      .filter(e => e.episodeId === episodeId)
      .sort((a, b) => new Date(b.date) - new Date(a.date));
  },

  getEncounterById: (encounterId) => {
    const encounters = StorageManager.getEncounters();
    return encounters.find(e => e.id === encounterId) || null;
  },

  // Utility operations
  updatePatient: (patientId, updates) => {
    const patients = StorageManager.getPatients();
    const index = patients.findIndex(p => p.id === patientId);
    if (index !== -1) {
      patients[index] = { ...patients[index], ...updates, updatedAt: new Date().toISOString() };
      return StorageManager.savePatients(patients);
    }
    return false;
  },

  updateEpisode: (episodeId, updates) => {
    const episodes = StorageManager.getEpisodes();
    const index = episodes.findIndex(e => e.id === episodeId);
    if (index !== -1) {
      episodes[index] = { ...episodes[index], ...updates };
      return StorageManager.saveEpisodes(episodes);
    }
    return false;
  },

  updateEncounter: (encounterId, updates) => {
    const encounters = StorageManager.getEncounters();
    const index = encounters.findIndex(e => e.id === encounterId);
    if (index !== -1) {
      encounters[index] = { ...encounters[index], ...updates };
      return StorageManager.saveEncounters(encounters);
    }
    return false;
  },

  // Initialize with sample data if empty
  initializeWithSampleData: () => {
    const hasData = StorageManager.getPatients().length > 0;
    if (!hasData) {
      const sampleData = generateSampleData();
      StorageManager.savePatients(sampleData.patients);
      StorageManager.saveEpisodes(sampleData.episodes);
      StorageManager.saveEncounters(sampleData.encounters);
    }
  }
};

// ID generation utilities
export const generateId = (prefix = '') => {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 5);
  return prefix ? `${prefix}_${timestamp}_${random}` : `${timestamp}_${random}`;
};

// Sample data generator
const generateSampleData = () => {
  const patients = [
    {
      id: 'P001',
      demographics: {
        name: 'John Smith',
        dateOfBirth: '1979-03-15',
        gender: 'Male',
        phone: '(555) 123-4567',
        email: 'john.smith@email.com',
        address: '123 Main St, Anytown, USA',
        emergencyContact: 'Jane Smith - (555) 123-4568',
        insuranceInfo: {
          provider: 'Blue Cross Blue Shield',
          memberId: 'BC123456789',
          group: 'GRP001'
        }
      },
      medicalBackground: {
        allergies: [
          { id: 'A001', allergen: 'Penicillin', reaction: 'Rash', severity: 'moderate' }
        ],
        medications: [
          { id: 'M001', name: 'Metformin', dosage: '500mg', frequency: 'Twice daily', startDate: '2023-01-15', ongoing: true },
          { id: 'M002', name: 'Lisinopril', dosage: '10mg', frequency: 'Once daily', startDate: '2023-06-20', ongoing: true }
        ],
        chronicConditions: [
          { id: 'C001', condition: 'Type 2 Diabetes', icd10: 'E11.9', diagnosedDate: '2023-01-15', status: 'active' },
          { id: 'C002', condition: 'Hypertension', icd10: 'I10', diagnosedDate: '2023-06-20', status: 'active' }
        ],
        pastMedicalHistory: 'Appendectomy in 2005. No other significant medical history.',
        pastSurgicalHistory: 'Appendectomy 2005',
        familyHistory: 'Father: Type 2 Diabetes, Hypertension. Mother: Breast cancer.',
        socialHistory: 'Non-smoker, occasional alcohol use, exercises 3x per week'
      },
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-12-20T14:30:00Z'
    },
    {
      id: 'P002',
      demographics: {
        name: 'Mary Johnson',
        dateOfBirth: '1992-07-22',
        gender: 'Female',
        phone: '(555) 234-5678',
        email: 'mary.johnson@email.com',
        address: '456 Oak Ave, Anytown, USA',
        emergencyContact: 'Robert Johnson - (555) 234-5679',
        insuranceInfo: {
          provider: 'Aetna',
          memberId: 'AET987654321',
          group: 'GRP002'
        }
      },
      medicalBackground: {
        allergies: [],
        medications: [
          { id: 'M003', name: 'Birth Control Pills', dosage: 'Standard', frequency: 'Once daily', startDate: '2020-03-01', ongoing: true }
        ],
        chronicConditions: [],
        pastMedicalHistory: 'Generally healthy. Seasonal allergies.',
        pastSurgicalHistory: 'None',
        familyHistory: 'No significant family history',
        socialHistory: 'Non-smoker, social drinker, yoga instructor'
      },
      createdAt: '2024-02-10T09:00:00Z',
      updatedAt: '2024-12-18T11:00:00Z'
    }
  ];

  const episodes = [
    {
      id: 'E001',
      patientId: 'P001',
      chiefComplaint: 'Persistent cough and fever',
      category: 'acute',
      status: 'active',
      createdAt: '2024-12-15T10:00:00Z',
      resolvedAt: null,
      lastEncounterId: 'ENC002',
      relatedEpisodeIds: [],
      tags: ['respiratory', 'infectious']
    },
    {
      id: 'E002',
      patientId: 'P001',
      chiefComplaint: 'Diabetes management',
      category: 'chronic',
      status: 'chronic-management',
      createdAt: '2024-01-15T10:00:00Z',
      resolvedAt: null,
      lastEncounterId: 'ENC003',
      relatedEpisodeIds: [],
      tags: ['diabetes', 'endocrine']
    },
    {
      id: 'E003',
      patientId: 'P002',
      chiefComplaint: 'Annual physical exam',
      category: 'preventive',
      status: 'resolved',
      createdAt: '2024-12-01T09:00:00Z',
      resolvedAt: '2024-12-01T10:00:00Z',
      lastEncounterId: 'ENC004',
      relatedEpisodeIds: [],
      tags: ['preventive', 'wellness']
    }
  ];

  const encounters = [
    {
      id: 'ENC001',
      episodeId: 'E001',
      patientId: 'P001',
      type: 'initial',
      date: '2024-12-15T10:00:00Z',
      status: 'signed',
      provider: {
        id: 'DR001',
        name: 'Dr. Smith',
        role: 'Primary Care Physician'
      },
      soap: {
        subjective: {
          chiefComplaint: 'Persistent cough and fever',
          hpi: 'Patient presents with 5-day history of productive cough with yellow sputum and fever up to 101°F. Associated with fatigue and mild chest discomfort.',
          ros: {
            constitutional: 'Positive for fever and fatigue',
            respiratory: 'Positive for cough with sputum production',
            cardiovascular: 'Negative for chest pain or palpitations'
          },
          pmh: 'Type 2 Diabetes, Hypertension',
          medications: 'Metformin 500mg BID, Lisinopril 10mg daily',
          allergies: 'Penicillin - rash',
          socialHistory: 'Non-smoker, exercises regularly',
          familyHistory: 'As documented',
          lastUpdated: '2024-12-15T10:30:00Z',
          voiceNotes: []
        },
        objective: {
          vitals: {
            bloodPressure: '138/88',
            heartRate: '92',
            temperature: '38.2',
            respiratoryRate: '22',
            oxygenSaturation: '94%',
            height: '5\'10"',
            weight: '180 lbs',
            bmi: '25.8'
          },
          physicalExam: {
            general: 'Alert and oriented, appears mildly ill',
            systems: {
              respiratory: 'Bilateral rhonchi, no wheezing',
              cardiovascular: 'Regular rate and rhythm, no murmurs'
            },
            additionalFindings: 'Throat mildly erythematous'
          },
          diagnosticTests: {
            ordered: [
              {
                id: 'T001',
                test: 'Chest X-ray',
                urgency: 'urgent',
                status: 'resulted',
                orderedAt: '2024-12-15T11:00:00Z',
                notes: 'Rule out pneumonia'
              }
            ],
            results: [
              {
                id: 'R001',
                testId: 'T001',
                test: 'Chest X-ray',
                result: 'No acute infiltrates, normal cardiac silhouette',
                abnormal: false,
                resultedAt: '2024-12-15T14:00:00Z',
                interpretation: 'No evidence of pneumonia',
                documents: []
              }
            ]
          },
          lastUpdated: '2024-12-15T14:30:00Z',
          voiceNotes: []
        },
        assessment: {
          clinicalImpression: 'Acute bronchitis likely viral in nature. No evidence of bacterial pneumonia on imaging.',
          differentialDiagnosis: [
            {
              id: 'D001',
              diagnosis: 'Acute bronchitis',
              icd10: 'J20.9',
              probability: 'high',
              supportingEvidence: ['Productive cough', 'Fever', 'Rhonchi on exam'],
              contradictingEvidence: ['Normal chest X-ray']
            },
            {
              id: 'D002',
              diagnosis: 'Community-acquired pneumonia',
              icd10: 'J18.9',
              probability: 'low',
              supportingEvidence: ['Fever', 'Productive cough'],
              contradictingEvidence: ['Normal chest X-ray', 'O2 sat 94%']
            }
          ],
          workingDiagnosis: {
            diagnosis: 'Acute bronchitis',
            icd10: 'J20.9',
            confidence: 'probable',
            clinicalReasoning: 'Clinical presentation consistent with acute bronchitis. Chest X-ray negative for pneumonia.'
          },
          riskAssessment: 'Low risk for complications. Monitor for worsening symptoms.',
          lastUpdated: '2024-12-15T15:00:00Z',
          aiConsultation: {
            queries: [],
            insights: []
          }
        },
        plan: {
          medications: [
            {
              id: 'RX001',
              name: 'Guaifenesin',
              dosage: '400mg',
              frequency: 'Every 4 hours as needed',
              duration: '7 days',
              instructions: 'For cough',
              prescribed: true
            },
            {
              id: 'RX002',
              name: 'Acetaminophen',
              dosage: '500mg',
              frequency: 'Every 6 hours as needed',
              duration: 'As needed',
              instructions: 'For fever',
              prescribed: true
            }
          ],
          procedures: [],
          referrals: [],
          followUp: {
            timeframe: '1 week',
            reason: 'Re-evaluate if symptoms persist',
            instructions: 'Return sooner if symptoms worsen or shortness of breath develops'
          },
          patientEducation: [
            {
              topic: 'Bronchitis care',
              materials: 'Handout provided on bronchitis self-care',
              discussed: true
            }
          ],
          activityRestrictions: 'Rest as needed, avoid strenuous activity until fever resolves',
          dietRecommendations: 'Increase fluid intake',
          lastUpdated: '2024-12-15T15:30:00Z'
        }
      },
      documents: [],
      amendments: [],
      signedAt: '2024-12-15T16:00:00Z',
      signedBy: 'Dr. Smith'
    }
  ];

  return { patients, episodes, encounters };
};