import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { StorageManager, generateId } from '../utils/storage';
import apiService from '../services/apiService';
import { transformPatientToBackend, transformPatientFromBackend } from '../utils/dataTransformers';
import patientExtensionsStorage from '../utils/patientExtensions';

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
  const [error, setError] = useState(null);

  // Load patients from API on mount
  useEffect(() => {
    const loadPatients = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getPatients();
        const backendPatients = response.data || response;
        const transformedPatients = backendPatients.map(patient => {
          const transformed = transformPatientFromBackend(patient);
          // Enrich with SQLite extensions
          return patientExtensionsStorage.enrichPatient(transformed);
        });
        setPatients(transformedPatients);
        // Also save to localStorage as backup
        StorageManager.savePatients(transformedPatients);
      } catch (error) {
        console.error('Error loading patients from API:', error);
        setError(error.message);
        // Fallback to localStorage if API fails
        try {
          const storedPatients = StorageManager.getPatients();
          setPatients(storedPatients);
        } catch (localError) {
          console.error('Error loading patients from storage:', localError);
        }
      } finally {
        setLoading(false);
      }
    };
    loadPatients();
  }, []);
  // Initialize with sample data if needed (only as fallback)
  useEffect(() => {
    if (!loading && patients.length === 0 && error) {
      StorageManager.initializeWithSampleData();
      const storedPatients = StorageManager.getPatients();
      setPatients(storedPatients);
    }
  }, [loading, patients.length, error]);

  // Create a new patient
  const createPatient = useCallback(async (patientData) => {
    try {
      setError(null);
      const backendPatientData = transformPatientToBackend(patientData);
      const backendPatient = await apiService.createPatient(backendPatientData);
      const transformedPatient = transformPatientFromBackend(backendPatient);
      
      // Store extensions in SQLite-like storage
      const extensions = patientExtensionsStorage.extractExtensions({ demographics: patientData });
      patientExtensionsStorage.setPatientExtensions(transformedPatient.id, extensions);
      
      // Enrich with extensions
      const enrichedPatient = patientExtensionsStorage.enrichPatient(transformedPatient);
      
      const updatedPatients = [...patients, enrichedPatient];
      setPatients(updatedPatients);
      // Also save to localStorage as backup
      StorageManager.savePatients(updatedPatients);
      return enrichedPatient;
    } catch (error) {
      console.error('Error creating patient:', error);
      setError(error.message);
      // Fallback to localStorage creation
      const newPatient = {
        id: generateId('P'),
        demographics: {
          name: patientData.name,
          dateOfBirth: patientData.dateOfBirth,
          gender: patientData.gender,
          phone: patientData.phone || '',
          email: patientData.email || '',
          address: patientData.address || '',
          maritalStatus: patientData.maritalStatus || '',
          occupation: patientData.occupation || '',
          emergencyContact: patientData.emergencyContact || '',
          emergencyContactPhone: patientData.emergencyContactPhone || '',
          emergencyContactRelation: patientData.emergencyContactRelation || '',
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
      // Also store extensions for fallback creation
      const extensions = patientExtensionsStorage.extractExtensions(newPatient);
      patientExtensionsStorage.setPatientExtensions(newPatient.id, extensions);
      
      const updatedPatients = [...patients, newPatient];
      setPatients(updatedPatients);
      StorageManager.savePatients(updatedPatients);
      return newPatient;
    }
  }, [patients]);

  // Update patient demographics
  const updatePatientDemographics = useCallback(async (patientId, updates) => {
    try {
      setError(null);
      const patient = patients.find(p => p.id === patientId);
      if (!patient) throw new Error('Patient not found');
      
      const updatedPatientData = {
        ...patient,
        demographics: { ...patient.demographics, ...updates },
        updatedAt: new Date().toISOString()
      };
      
      // Update extensions in SQLite-like storage
      const extensions = patientExtensionsStorage.extractExtensions(updatedPatientData);
      patientExtensionsStorage.setPatientExtensions(patientId, extensions);
      
      const backendPatientData = transformPatientToBackend(updatedPatientData);
      const backendPatient = await apiService.updatePatient(patient.id, backendPatientData);
      const transformedPatient = transformPatientFromBackend(backendPatient);
      
      // Enrich with extensions
      const enrichedPatient = patientExtensionsStorage.enrichPatient(transformedPatient);
      
      const updatedPatients = patients.map(p => 
        p.id === patientId ? enrichedPatient : p
      );
      
      setPatients(updatedPatients);
      StorageManager.savePatients(updatedPatients);
      
      // Update current patient if it's the one being updated
      if (currentPatient?.id === patientId) {
        setCurrentPatient(enrichedPatient);
      }
    } catch (error) {
      console.error('Error updating patient demographics:', error);
      setError(error.message);
      // Fallback to localStorage update
      const updatedPatients = patients.map(p => 
        p.id === patientId 
          ? { 
              ...p, 
              demographics: { ...p.demographics, ...updates },
              updatedAt: new Date().toISOString()
            } 
          : p
      );
      
      // Update extensions in fallback too
      const extensions = patientExtensionsStorage.extractExtensions({
        demographics: { ...patients.find(p => p.id === patientId)?.demographics, ...updates }
      });
      patientExtensionsStorage.setPatientExtensions(patientId, extensions);
      
      setPatients(updatedPatients);
      StorageManager.savePatients(updatedPatients);
      
      if (currentPatient?.id === patientId) {
        const updatedCurrent = {
          ...currentPatient,
          demographics: { ...currentPatient.demographics, ...updates },
          updatedAt: new Date().toISOString()
        };
        setCurrentPatient(updatedCurrent);
      }
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

  // Delete patient
  const deletePatient = useCallback(async (patientId) => {
    try {
      setError(null);
      await apiService.deletePatient(patientId);
      
      // Clean up extensions in SQLite-like storage
      patientExtensionsStorage.deletePatientExtensions(patientId);
      
      const updatedPatients = patients.filter(p => p.id !== patientId);
      setPatients(updatedPatients);
      StorageManager.savePatients(updatedPatients);
      
      // Clear current patient if it's the one being deleted
      if (currentPatient?.id === patientId) {
        setCurrentPatient(null);
      }
    } catch (error) {
      console.error('Error deleting patient:', error);
      setError(error.message);
      // Fallback to localStorage deletion
      patientExtensionsStorage.deletePatientExtensions(patientId);
      
      const updatedPatients = patients.filter(p => p.id !== patientId);
      setPatients(updatedPatients);
      StorageManager.savePatients(updatedPatients);
      
      if (currentPatient?.id === patientId) {
        setCurrentPatient(null);
      }
    }
  }, [patients, currentPatient]);

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
    error,
    createPatient,
    updatePatient,
    updatePatientDemographics,
    updatePatientMedicalBackground,
    deletePatient,
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