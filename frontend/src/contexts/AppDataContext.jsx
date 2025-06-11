import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

const AppDataContext = createContext(null);

// Export a ref that can be accessed by other contexts
export const appDataRef = { current: null };

export const useAppData = () => {
  const context = useContext(AppDataContext);
  if (!context) {
    throw new Error('useAppData must be used within an AppDataProvider');
  }
  return context;
};

export const AppDataProvider = ({ children }) => {
  // Initialize data from localStorage or use default mock data
  const [patients, setPatients] = useState(() => {
    const saved = localStorage.getItem('diagnoassist_patients');
    if (saved) {
      return JSON.parse(saved);
    }
    
    // Mock patients data
    return [
      {
        id: 'P001',
        name: 'John Smith',
        dateOfBirth: '1979-03-15',
        age: 45,
        gender: 'Male',
        phone: '(555) 123-4567',
        email: 'john.smith@email.com',
        address: '123 Main St, Anytown, USA',
        emergencyContact: 'Jane Smith - (555) 123-4568',
        createdAt: '2024-01-15T10:00:00Z',
        lastVisit: '2024-12-20T14:30:00Z'
      },
      {
        id: 'P002',
        name: 'Mary Johnson',
        dateOfBirth: '1992-07-22',
        age: 32,
        gender: 'Female',
        phone: '(555) 234-5678',
        email: 'mary.johnson@email.com',
        address: '456 Oak Ave, Anytown, USA',
        emergencyContact: 'Robert Johnson - (555) 234-5679',
        createdAt: '2024-02-10T09:00:00Z',
        lastVisit: '2024-12-18T11:00:00Z'
      },
      {
        id: 'P003',
        name: 'Robert Davis',
        dateOfBirth: '1966-11-08',
        age: 58,
        gender: 'Male',
        phone: '(555) 345-6789',
        email: 'robert.davis@email.com',
        address: '789 Pine Rd, Anytown, USA',
        emergencyContact: 'Susan Davis - (555) 345-6790',
        createdAt: '2024-03-05T13:00:00Z',
        lastVisit: '2024-12-15T16:00:00Z'
      }
    ];
  });
  
  const [patientRecords, setPatientRecords] = useState(() => {
    const saved = localStorage.getItem('diagnoassist_records');
    if (saved) {
      return JSON.parse(saved);
    }
    
    // Mock patient records
    return [
      {
        id: 'R001',
        patientId: 'P001',
        sessionId: 'S001',
        date: '2024-12-20T14:30:00Z',
        chiefComplaint: 'Persistent cough and fever',
        finalDiagnosis: 'Community-acquired Pneumonia',
        icd10: 'J18.9',
        physicalExam: {
          bloodPressure: '138/88',
          heartRate: '92',
          temperature: '38.2',
          respiratoryRate: '22',
          oxygenSaturation: '94%'
        },
        prescriptions: [
          {
            medication: 'Amoxicillin-Clavulanate',
            dosage: '875mg',
            frequency: 'Twice daily',
            duration: '7 days'
          },
          {
            medication: 'Acetaminophen',
            dosage: '500mg',
            frequency: 'Every 6 hours as needed',
            duration: 'PRN for fever'
          }
        ],
        treatmentPlan: 'Antibiotic therapy with amoxicillin-clavulanate, supportive care, follow-up in 48-72 hours',
        testsPerformed: ['Chest X-ray', 'Complete Blood Count'],
        medicalHistory: ['Hypertension', 'Type 2 Diabetes'],
        medications: ['Metformin 1000mg daily', 'Lisinopril 10mg daily'],
        allergies: ['Penicillin - mild rash']
      },
      {
        id: 'R002',
        patientId: 'P002',
        sessionId: 'S002',
        date: '2024-12-18T11:00:00Z',
        chiefComplaint: 'Severe headache and dizziness',
        finalDiagnosis: 'Migraine without aura',
        icd10: 'G43.009',
        physicalExam: {
          bloodPressure: '118/76',
          heartRate: '78',
          temperature: '36.8',
          respiratoryRate: '16',
          oxygenSaturation: '98%'
        },
        prescriptions: [
          {
            medication: 'Sumatriptan',
            dosage: '50mg',
            frequency: 'As needed for migraine',
            duration: 'PRN'
          }
        ],
        treatmentPlan: 'Migraine abortive therapy, lifestyle modifications, stress management',
        testsPerformed: [],
        medicalHistory: ['Migraine history', 'Anxiety disorder'],
        medications: ['Oral contraceptive'],
        allergies: ['None known']
      },
      {
        id: 'R003',
        patientId: 'P001',
        sessionId: 'S003',
        date: '2024-11-15T10:00:00Z',
        chiefComplaint: 'Elevated blood pressure reading at home',
        finalDiagnosis: 'Essential Hypertension',
        icd10: 'I10',
        physicalExam: {
          bloodPressure: '156/94',
          heartRate: '82',
          temperature: '36.6',
          respiratoryRate: '18',
          oxygenSaturation: '97%'
        },
        prescriptions: [
          {
            medication: 'Amlodipine',
            dosage: '5mg',
            frequency: 'Once daily',
            duration: 'Ongoing'
          }
        ],
        treatmentPlan: 'Add calcium channel blocker, continue ACE inhibitor, DASH diet, exercise program',
        testsPerformed: ['Lipid panel', 'Basic metabolic panel', 'EKG'],
        medicalHistory: ['Hypertension', 'Type 2 Diabetes', 'Hyperlipidemia'],
        medications: ['Metformin 1000mg daily', 'Lisinopril 10mg daily'],
        allergies: ['Penicillin - mild rash']
      }
    ];
  });
  
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('diagnoassist_sessions');
    if (saved) {
      return JSON.parse(saved);
    }
    
    // Mock incomplete sessions
    return [
      {
        id: 'S004',
        patientId: 'P003',
        status: 'incomplete',
        lastStep: 'recommended-tests',
        lastUpdated: '2024-12-21T09:30:00Z',
        data: {
          name: 'Robert Davis',
          age: 58,
          gender: 'Male',
          dateOfBirth: '1966-11-08',
          chiefComplaint: 'Chest pain on exertion',
          chiefComplaintDetails: ['Sharp pain', 'Occurs with physical activity', 'Relieved by rest'],
          medicalHistory: ['Hypertension', 'Hyperlipidemia', 'Former smoker'],
          medications: ['Atorvastatin 40mg daily', 'Metoprolol 50mg twice daily'],
          allergies: ['Sulfa drugs'],
          physicalExam: {
            bloodPressure: '142/88',
            heartRate: '76',
            temperature: '36.7',
            respiratoryRate: '18',
            oxygenSaturation: '96%'
          },
          differentialDiagnoses: [
            { id: 1, name: 'Stable Angina', icd10: 'I20.9', probability: 0.75, confidence: 'High' },
            { id: 2, name: 'Gastroesophageal Reflux', icd10: 'K21.9', probability: 0.15, confidence: 'Low' }
          ],
          recommendedTests: ['EKG', 'Cardiac enzymes', 'Stress test'],
          selectedTests: ['EKG', 'Cardiac enzymes']
        }
      }
    ];
  });
  
  // Save to localStorage whenever data changes
  useEffect(() => {
    localStorage.setItem('diagnoassist_patients', JSON.stringify(patients));
  }, [patients]);
  
  useEffect(() => {
    localStorage.setItem('diagnoassist_records', JSON.stringify(patientRecords));
  }, [patientRecords]);
  
  useEffect(() => {
    localStorage.setItem('diagnoassist_sessions', JSON.stringify(sessions));
  }, [sessions]);
  
  // Patient management functions
  const addPatient = (patient) => {
    const newPatient = {
      ...patient,
      id: `P${String(patients.length + 1).padStart(3, '0')}`,
      createdAt: new Date().toISOString(),
      lastVisit: new Date().toISOString()
    };
    setPatients([...patients, newPatient]);
    return newPatient;
  };
  
  const updatePatient = (patientId, updates) => {
    setPatients(patients.map(p => 
      p.id === patientId ? { ...p, ...updates } : p
    ));
  };
  
  const getPatient = (patientId) => {
    return patients.find(p => p.id === patientId);
  };
  
  const getPatientRecords = (patientId) => {
    return patientRecords.filter(r => r.patientId === patientId);
  };
  
  const getPatientLatestRecord = (patientId) => {
    const records = getPatientRecords(patientId);
    return records.sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  };
  
  // Record management functions
  const addRecord = (record) => {
    const newRecord = {
      ...record,
      id: `R${String(patientRecords.length + 1).padStart(3, '0')}`,
      date: new Date().toISOString()
    };
    setPatientRecords([...patientRecords, newRecord]);
    
    // Update patient's last visit
    updatePatient(record.patientId, { lastVisit: newRecord.date });
    
    return newRecord;
  };
  
  // Session management functions
  const createSession = (patientId, data) => {
    const newSession = {
      id: `S${String(sessions.length + 1).padStart(3, '0')}`,
      patientId,
      status: 'incomplete',
      lastStep: data.currentStep || 'patient-info',
      lastUpdated: new Date().toISOString(),
      data
    };
    setSessions([...sessions, newSession]);
    return newSession;
  };
  
  const updateSession = (sessionId, data, lastStep) => {
    setSessions(sessions.map(s => 
      s.id === sessionId 
        ? { 
            ...s, 
            data: { ...s.data, ...data },
            lastStep,
            lastUpdated: new Date().toISOString()
          } 
        : s
    ));
  };
  
  const completeSession = (sessionId) => {
    setSessions(sessions.map(s => 
      s.id === sessionId ? { ...s, status: 'complete' } : s
    ));
  };
  
  const deleteSession = (sessionId) => {
    setSessions(sessions.filter(s => s.id !== sessionId));
  };
  
  const getPatientSessions = (patientId) => {
    return sessions.filter(s => s.patientId === patientId && s.status === 'incomplete');
  };
  
  const value = {
    // Data
    patients,
    patientRecords,
    sessions,
    
    // Patient functions
    addPatient,
    updatePatient,
    getPatient,
    getPatientRecords,
    getPatientLatestRecord,
    
    // Record functions
    addRecord,
    
    // Session functions
    createSession,
    updateSession,
    completeSession,
    deleteSession,
    getPatientSessions
  };
  
  // Make the context value accessible via ref
  useEffect(() => {
    appDataRef.current = value;
  }, [value]);
  
  return (
    <AppDataContext.Provider value={value}>
      {children}
    </AppDataContext.Provider>
  );
};
