import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { StorageManager, generateId } from '../utils/storage';

const PatientContext = createContext(null);

// eslint-disable-next-line react-refresh/only-export-components
export const usePatient = () => {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within a PatientProvider');
  }
  return context;
};

export const PatientProvider = ({ children }) => {
  const [patients, setPatients] = useState([]);
  const [currentPatient, setCurrentPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load patients from storage on mount
  useEffect(() => {
    const loadPatients = () => {
      try {
        const storedPatients = StorageManager.getPatients();
        setPatients(storedPatients);
        setLoading(false);
      } catch (error) {
        console.error('Error loading patients:', error);
        setLoading(false);
      }
    };
    loadPatients();
  }, []);
  // Initialize with sample data if needed
  useEffect(() => {
    if (!loading && patients.length === 0) {
      StorageManager.initializeWithSampleData();
      const storedPatients = StorageManager.getPatients();
      setPatients(storedPatients);
    }
  }, [loading, patients.length]);

  // Create a new patient
  const createPatient = useCallback((patientData) => {
    const newPatient = {
      id: generateId('P'),
      demographics: {
        name: patientData.name,
        dateOfBirth: patientData.dateOfBirth,
        gender: patientData.gender,
        phone: patientData.phone || '',
        email: patientData.email || '',
        address: patientData.address || '',
        emergencyContact: patientData.emergencyContact || '',
        insuranceInfo: patientData.insuranceInfo || {}
      },
      medicalBackground: {
        allergies: patientData.allergies || [],
        medications: patientData.medications || [],
        chronicConditions: patientData.chronicConditions || [],
        pastMedicalHistory: patientData.pastMedicalHistory || '',
        pastSurgicalHistory: patientData.pastSurgicalHistory || '',
        familyHistory: patientData.familyHistory || '',
        socialHistory: patientData.socialHistory || ''
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const updatedPatients = [...patients, newPatient];
    setPatients(updatedPatients);
    StorageManager.savePatients(updatedPatients);
    
    return newPatient;
  }, [patients]);

  // Update patient demographics
  const updatePatientDemographics = useCallback((patientId, updates) => {
    const updatedPatients = patients.map(p => 
      p.id === patientId 
        ? { 
            ...p, 
            demographics: { ...p.demographics, ...updates },
            updatedAt: new Date().toISOString()
          } 
        : p
    );
    
    setPatients(updatedPatients);
    StorageManager.savePatients(updatedPatients);
    
    // Update current patient if it's the one being updated
    if (currentPatient?.id === patientId) {
      setCurrentPatient(prev => ({
        ...prev,
        demographics: { ...prev.demographics, ...updates },
        updatedAt: new Date().toISOString()
      }));
    }
  }, [patients, currentPatient]);

  // Update patient medical background
  const updatePatientMedicalBackground = useCallback((patientId, updates) => {
    const updatedPatients = patients.map(p => 
      p.id === patientId 
        ? { 
            ...p, 
            medicalBackground: { ...p.medicalBackground, ...updates },
            updatedAt: new Date().toISOString()
          } 
        : p
    );
    
    setPatients(updatedPatients);
    StorageManager.savePatients(updatedPatients);
    
    // Update current patient if it's the one being updated
    if (currentPatient?.id === patientId) {
      setCurrentPatient(prev => ({
        ...prev,
        medicalBackground: { ...prev.medicalBackground, ...updates },
        updatedAt: new Date().toISOString()
      }));
    }
  }, [patients, currentPatient]);

  // Add allergy
  const addAllergy = useCallback((patientId, allergy) => {
    const patient = patients.find(p => p.id === patientId);
    if (!patient) return;

    const newAllergy = {
      id: generateId('A'),
      ...allergy,
      addedDate: new Date().toISOString()
    };

    const updatedAllergies = [...patient.medicalBackground.allergies, newAllergy];
    updatePatientMedicalBackground(patientId, { allergies: updatedAllergies });
  }, [patients, updatePatientMedicalBackground]);

  // Add medication
  const addMedication = useCallback((patientId, medication) => {
    const patient = patients.find(p => p.id === patientId);
    if (!patient) return;

    const newMedication = {
      id: generateId('M'),
      ...medication,
      startDate: medication.startDate || new Date().toISOString(),
      ongoing: medication.ongoing !== false
    };

    const updatedMedications = [...patient.medicalBackground.medications, newMedication];
    updatePatientMedicalBackground(patientId, { medications: updatedMedications });
  }, [patients, updatePatientMedicalBackground]);

  // Add chronic condition
  const addChronicCondition = useCallback((patientId, condition) => {
    const patient = patients.find(p => p.id === patientId);
    if (!patient) return;

    const newCondition = {
      id: generateId('C'),
      ...condition,
      diagnosedDate: condition.diagnosedDate || new Date().toISOString(),
      status: condition.status || 'active'
    };

    const updatedConditions = [...patient.medicalBackground.chronicConditions, newCondition];
    updatePatientMedicalBackground(patientId, { chronicConditions: updatedConditions });
  }, [patients, updatePatientMedicalBackground]);

  // Get patient by ID
  const getPatientById = useCallback((patientId) => {
    return patients.find(p => p.id === patientId) || null;
  }, [patients]);

  // Search patients
  const searchPatients = useCallback((query) => {
    const lowerQuery = query.toLowerCase();
    return patients.filter(p => 
      p.demographics.name.toLowerCase().includes(lowerQuery) ||
      p.demographics.phone.includes(query) ||
      p.demographics.email.toLowerCase().includes(lowerQuery) ||
      p.id.toLowerCase().includes(lowerQuery)
    );
  }, [patients]);

  // Calculate age from date of birth
  const calculateAge = useCallback((dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  }, []);

  // Update entire patient data
  const updatePatient = useCallback((patientId, updates) => {
    const updatedPatients = patients.map(p => 
      p.id === patientId 
        ? { 
            ...p, 
            ...updates,
            updatedAt: new Date().toISOString()
          } 
        : p
    );
    
    setPatients(updatedPatients);
    StorageManager.savePatients(updatedPatients);
    
    // Update current patient if it's the one being updated
    if (currentPatient?.id === patientId) {
      setCurrentPatient(prev => ({
        ...prev,
        ...updates,
        updatedAt: new Date().toISOString()
      }));
    }
  }, [patients, currentPatient]);

  const value = {
    patients,
    currentPatient,
    setCurrentPatient,
    loading,
    createPatient,
    updatePatient,
    updatePatientDemographics,
    updatePatientMedicalBackground,
    addAllergy,
    addMedication,
    addChronicCondition,
    getPatientById,
    searchPatients,
    calculateAge
  };

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};