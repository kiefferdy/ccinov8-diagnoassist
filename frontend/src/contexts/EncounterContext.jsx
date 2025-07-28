import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { StorageManager, generateId } from '../utils/storage';
import apiService from '../services/apiService';

const EncounterContext = createContext(null);

// Data transformation utilities
const transformBackendToFrontend = (backendEncounter) => {
  if (!backendEncounter) return null;
  
  return {
    id: backendEncounter.id,
    episodeId: backendEncounter.episode_id,
    patientId: backendEncounter.patient_id,
    type: backendEncounter.type || 'follow-up',
    date: backendEncounter.date || new Date().toISOString(),
    status: backendEncounter.status || 'draft',
    provider: backendEncounter.provider || {
      id: backendEncounter.provider_id,
      name: backendEncounter.provider_name,
      role: backendEncounter.provider_role
    },
    soap: {
      subjective: backendEncounter.soap_subjective || {},
      objective: backendEncounter.soap_objective || {},
      assessment: backendEncounter.soap_assessment || {},
      plan: backendEncounter.soap_plan || {}
    },
    documents: backendEncounter.documents || [],
    amendments: backendEncounter.amendments || [],
    signedAt: backendEncounter.signed_at,
    signedBy: backendEncounter.signed_by,
    createdAt: backendEncounter.created_at,
    updatedAt: backendEncounter.updated_at,
    completionPercentage: backendEncounter.completion_percentage || 0,
    isSigned: backendEncounter.is_signed || false,
    chiefComplaint: backendEncounter.chief_complaint
  };
};

const transformFrontendToBackend = (frontendEncounter, isUpdate = false) => {
  if (!frontendEncounter) return null;
  
  // Helper function to clean datetime strings and objects
  const cleanObject = (obj) => {
    if (!obj || typeof obj !== 'object') return obj;
    
    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
      if (value === null || value === undefined) {
        continue; // Skip null/undefined values
      }
      
      if (Array.isArray(value)) {
        // Only include arrays that have content
        if (value.length > 0) {
          cleaned[key] = value;
        }
      } else if (typeof value === 'object') {
        const cleanedValue = cleanObject(value);
        if (Object.keys(cleanedValue).length > 0) {
          cleaned[key] = cleanedValue;
        }
      } else if (typeof value === 'string' && value.trim() === '') {
        continue; // Skip empty strings
      } else {
        cleaned[key] = value;
      }
    }
    return cleaned;
  };
  
  if (isUpdate) {
    // For updates, only send fields that can be updated
    const updateData = {};
    
    if (frontendEncounter.type) updateData.type = frontendEncounter.type;
    if (frontendEncounter.status) updateData.status = frontendEncounter.status;
    if (frontendEncounter.provider) updateData.provider = frontendEncounter.provider;
    
    // SOAP sections - check both nested and top-level formats
    const soapSubjective = frontendEncounter.soap?.subjective || frontendEncounter.soap_subjective;
    if (soapSubjective) {
      const cleanedSubjective = cleanObject(soapSubjective);
      if (Object.keys(cleanedSubjective).length > 0) {
        updateData.soap_subjective = cleanedSubjective;
      }
    }
    
    const soapObjective = frontendEncounter.soap?.objective || frontendEncounter.soap_objective;
    if (soapObjective) {
      const cleanedObjective = cleanObject(soapObjective);
      if (Object.keys(cleanedObjective).length > 0) {
        updateData.soap_objective = cleanedObjective;
      }
    }
    
    const soapAssessment = frontendEncounter.soap?.assessment || frontendEncounter.soap_assessment;
    if (soapAssessment) {
      const cleanedAssessment = cleanObject(soapAssessment);
      if (Object.keys(cleanedAssessment).length > 0) {
        updateData.soap_assessment = cleanedAssessment;
      }
    }
    
    const soapPlan = frontendEncounter.soap?.plan || frontendEncounter.soap_plan;
    if (soapPlan) {
      const cleanedPlan = cleanObject(soapPlan);
      if (Object.keys(cleanedPlan).length > 0) {
        updateData.soap_plan = cleanedPlan;
      }
    }
    
    if (frontendEncounter.documents && frontendEncounter.documents.length > 0) {
      updateData.documents = frontendEncounter.documents;
    }
    if (frontendEncounter.amendments && frontendEncounter.amendments.length > 0) {
      updateData.amendments = frontendEncounter.amendments;
    }
    
    return updateData;
  }
  
  // For creation, include all fields
  return {
    episode_id: frontendEncounter.episodeId,
    patient_id: frontendEncounter.patientId,
    type: frontendEncounter.type || 'follow-up',
    provider: frontendEncounter.provider,
    soap_subjective: frontendEncounter.soap?.subjective || {},
    soap_objective: frontendEncounter.soap?.objective || {},
    soap_assessment: frontendEncounter.soap?.assessment || {},
    soap_plan: frontendEncounter.soap?.plan || {},
    documents: frontendEncounter.documents || [],
    amendments: frontendEncounter.amendments || [],
    chief_complaint: frontendEncounter.chiefComplaint
  };
};

// eslint-disable-next-line react-refresh/only-export-components
export const useEncounter = () => {
  const context = useContext(EncounterContext);
  if (!context) {
    throw new Error('useEncounter must be used within an EncounterProvider');
  }
  return context;
};

export const EncounterProvider = ({ children }) => {
  const [encounters, setEncounters] = useState([]);
  const [currentEncounter, setCurrentEncounter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [switchingEncounter, setSwitchingEncounter] = useState(false);
  const [error, setError] = useState(null);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [lastSaved, setLastSaved] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Load encounters from backend API with localStorage fallback
  useEffect(() => {
    const loadEncounters = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Try to load from API first
        try {
          const response = await apiService.getEncounters();
          const backendEncounters = response?.data || response || [];
          const transformedEncounters = backendEncounters.map(transformBackendToFrontend);
          console.log('EncounterContext loaded encounters:', transformedEncounters.length, transformedEncounters);
          setEncounters(transformedEncounters);
          
          // Also cache in localStorage for offline access
          StorageManager.saveEncounters(transformedEncounters);
        } catch (apiError) {
          console.warn('Failed to load encounters from API, using localStorage:', apiError);
          // Fallback to localStorage
          const storedEncounters = StorageManager.getEncounters();
          setEncounters(storedEncounters);
        }
      } catch (error) {
        console.error('Error loading encounters:', error);
        setError(error.message);
        // Final fallback
        setEncounters([]);
      } finally {
        setLoading(false);
      }
    };
    loadEncounters();
  }, []);

  // Get encounters for a specific episode
  const getEpisodeEncounters = useCallback(async (episodeId, useCache = true) => {
    if (useCache) {
      // Return cached encounters
      const cachedEncounters = encounters
        .filter(e => {
          const match = e.episodeId === episodeId;
          if (!match && encounters.length > 0) {
            console.log(`Episode ID mismatch: looking for ${episodeId} (${typeof episodeId}), found ${e.episodeId} (${typeof e.episodeId})`);
          }
          return match;
        })
        .sort((a, b) => new Date(b.date) - new Date(a.date));
      console.log(`getEpisodeEncounters(${episodeId}, cache): found ${cachedEncounters.length} encounters from ${encounters.length} total`);
      return cachedEncounters;
    }

    // Fetch fresh data from API
    try {
      const response = await apiService.getEpisodeEncounters(episodeId);
      const apiEncounters = response?.data || response || [];
      const transformedEncounters = apiEncounters.map(transformBackendToFrontend);
      
      // Update local state with fresh data - avoid duplicates
      const nonEpisodeEncounters = encounters.filter(e => e.episodeId !== episodeId);
      const deduplicatedEncounters = transformedEncounters.filter(newEnc => 
        !nonEpisodeEncounters.some(existingEnc => existingEnc.id === newEnc.id)
      );
      const updatedEncounters = [...nonEpisodeEncounters, ...deduplicatedEncounters];
      setEncounters(updatedEncounters);
      StorageManager.saveEncounters(updatedEncounters);
      
      return transformedEncounters.sort((a, b) => new Date(b.date) - new Date(a.date));
    } catch (error) {
      console.warn('Failed to fetch episode encounters from API:', error);
      // Fallback to cached data
      return encounters
        .filter(e => e.episodeId === episodeId)
        .sort((a, b) => new Date(b.date) - new Date(a.date));
    }
  }, [encounters]);

  // Create a new encounter
  const createEncounter = useCallback(async (episodeId, patientId, type = 'follow-up') => {
    try {
      // Check if we already have an encounter being created to avoid duplicates
      const existingDraftEncounter = encounters.find(e => 
        e.episodeId === episodeId && 
        e.patientId === patientId && 
        e.status === 'draft' &&
        e.type === type
      );
      
      if (existingDraftEncounter) {
        console.log('Draft encounter already exists, returning existing:', existingDraftEncounter.id);
        return existingDraftEncounter;
      }
      const encounterData = {
        episode_id: episodeId,
        patient_id: patientId,
        type,
        provider: {
          id: 'DR001', // In real app, this would come from auth context
          name: 'Dr. Current User',
          role: 'Primary Care Physician'
        },
        soap_subjective: {
          chiefComplaint: '',
          hpi: '',
          ros: {},
          pmh: '',
          medications: '',
          allergies: '',
          socialHistory: '',
          familyHistory: ''
        },
        soap_objective: {
          vitals: {
            bloodPressure: '',
            heartRate: '',
            temperature: '',
            respiratoryRate: '',
            oxygenSaturation: '',
            height: '',
            weight: '',
            bmi: ''
          },
          physicalExam: {
            general: '',
            systems: {},
            additionalFindings: ''
          }
        },
        soap_assessment: {
          clinicalImpression: '',
          differentialDiagnosis: [],
          workingDiagnosis: {
            diagnosis: '',
            icd10: '',
            confidence: 'possible'
          }
        },
        soap_plan: {
          medications: [],
          procedures: [],
          followUp: {
            timeframe: '',
            reason: '',
            instructions: ''
          },
          patientEducation: []
        }
      };

      // Try to create via API
      try {
        const response = await apiService.createEncounter(encounterData);
        const newEncounter = transformBackendToFrontend(response);
        
        // Check if encounter already exists to prevent duplicates
        const encounterExists = encounters.some(e => e.id === newEncounter.id);
        if (!encounterExists) {
          const updatedEncounters = [...encounters, newEncounter];
          setEncounters(updatedEncounters);
          StorageManager.saveEncounters(updatedEncounters);
        }
        
        return newEncounter;
      } catch (apiError) {
        console.warn('Failed to create encounter via API, creating locally:', apiError);
        
        // Fallback to local creation
        const newEncounter = {
          id: generateId('ENC'),
          episodeId,
          patientId,
          type,
          date: new Date().toISOString(),
          status: 'draft',
          provider: encounterData.provider,
          soap: {
            subjective: encounterData.soap_subjective,
            objective: encounterData.soap_objective,
            assessment: encounterData.soap_assessment,
            plan: encounterData.soap_plan
          },
          documents: [],
          amendments: [],
          signedAt: null,
          signedBy: null,
          completionPercentage: 0
        };

        // Check if encounter already exists to prevent duplicates
        const encounterExists = encounters.some(e => e.id === newEncounter.id);
        if (!encounterExists) {
          const updatedEncounters = [...encounters, newEncounter];
          setEncounters(updatedEncounters);
          StorageManager.saveEncounters(updatedEncounters);
        }
        
        return newEncounter;
      }
    } catch (error) {
      console.error('Error creating encounter:', error);
      setError(error.message);
      throw error;
    }
  }, [encounters]);
  // Update current encounter
  const updateCurrentEncounter = useCallback((updates) => {
    if (!currentEncounter) return;
    
    const updatedEncounter = { ...currentEncounter, ...updates };
    setCurrentEncounter(updatedEncounter);
    setHasUnsavedChanges(true);
  }, [currentEncounter]);

  // Update SOAP section
  const updateSOAPSection = useCallback(async (section, updates) => {
    if (!currentEncounter) return;
    
    const updatedEncounter = {
      ...currentEncounter,
      soap: {
        ...currentEncounter.soap,
        [section]: {
          ...currentEncounter.soap[section],
          ...updates,
          lastUpdated: new Date().toISOString()
        }
      }
    };
    
    setCurrentEncounter(updatedEncounter);
    setHasUnsavedChanges(true);

    // If encounter exists in backend, try to update SOAP section via API
    if (currentEncounter.id && !currentEncounter.id.startsWith('ENC')) {
      try {
        await apiService.updateSOAPSection(currentEncounter.id, {
          section,
          data: updates
        });
      } catch (apiError) {
        console.warn('Failed to update SOAP section via API:', apiError);
        // Continue with local update - will sync later
      }
    }
  }, [currentEncounter]);

  // Save current encounter
  const saveCurrentEncounter = useCallback(async () => {
    if (!currentEncounter) return false;
    
    try {
      setError(null);
      
      // Try to save via API first
      try {
        let savedEncounter;
        
        // Check if it's a new encounter (starts with 'ENC') or existing encounter
        if (currentEncounter.id.startsWith('ENC')) {
          // New local encounter - create via API
          const backendData = transformFrontendToBackend(currentEncounter, false);
          const response = await apiService.createEncounter(backendData);
          savedEncounter = transformBackendToFrontend(response);
        } else {
          // Existing encounter - update via API
          const backendData = transformFrontendToBackend(currentEncounter, true);
          const response = await apiService.updateEncounter(currentEncounter.id, backendData);
          savedEncounter = transformBackendToFrontend(response);
        }
        
        // Update local state with API response
        const updatedEncounters = encounters.map(e => 
          e.id === currentEncounter.id ? savedEncounter : e
        );
        
        if (!encounters.find(e => e.id === currentEncounter.id)) {
          updatedEncounters.push(savedEncounter);
        }
        
        setEncounters(updatedEncounters);
        setCurrentEncounter(savedEncounter);
        StorageManager.saveEncounters(updatedEncounters);
        
      } catch (apiError) {
        console.warn('Failed to save encounter via API, saving locally:', apiError);
        
        // Fallback to localStorage only
        const updatedEncounters = encounters.map(e => 
          e.id === currentEncounter.id ? currentEncounter : e
        );
        
        if (!encounters.find(e => e.id === currentEncounter.id)) {
          updatedEncounters.push(currentEncounter);
        }
        
        setEncounters(updatedEncounters);
        StorageManager.saveEncounters(updatedEncounters);
      }
      
      // Also update the related episode with clinical notes
      if (currentEncounter.episodeId) {
        const clinicalNotes = [
          `SOAP Notes (${new Date().toLocaleDateString()}):`,
          `S: ${currentEncounter.soap?.subjective?.hpi || 'No subjective data'}`,
          `O: ${currentEncounter.soap?.objective?.physicalExam?.general || 'No objective data'}`, 
          `A: ${currentEncounter.soap?.assessment?.clinicalImpression || 'No assessment'}`,
          `P: ${currentEncounter.soap?.plan?.followUp?.instructions || 'No plan'}`
        ].join('\n');
        
        try {
          await apiService.updateEpisode(currentEncounter.episodeId, {
            clinical_notes: clinicalNotes,
            assessment_notes: currentEncounter.soap?.assessment?.clinicalImpression || '',
            plan_notes: currentEncounter.soap?.plan?.followUp?.instructions || ''
          });
        } catch (apiError) {
          console.warn('Failed to sync encounter to episode:', apiError);
        }
      }
      
      setLastSaved(new Date().toISOString());
      setHasUnsavedChanges(false);
      
      return true;
    } catch (error) {
      console.error('Error saving encounter:', error);
      setError(error.message);
      return false;
    }
  }, [currentEncounter, encounters]);

  // Auto-save functionality
  useEffect(() => {
    if (!autoSaveEnabled || !currentEncounter || !hasUnsavedChanges) return;

    const saveTimer = setTimeout(() => {
      saveCurrentEncounter();
    }, 30000); // Auto-save every 30 seconds

    return () => clearTimeout(saveTimer);
  }, [currentEncounter, hasUnsavedChanges, autoSaveEnabled, saveCurrentEncounter]);

  // Sign encounter
  const signEncounter = useCallback(async (encounterId, providerName) => {
    const encounter = encounters.find(e => e.id === encounterId);
    if (!encounter || encounter.status === 'signed') return false;
    
    try {
      // Try to sign via API first
      if (!encounterId.startsWith('ENC')) {
        try {
          const response = await apiService.signEncounter(encounterId, providerName);
          const signedEncounter = transformBackendToFrontend(response);
          
          const updatedEncounters = encounters.map(e => 
            e.id === encounterId ? signedEncounter : e
          );
          
          setEncounters(updatedEncounters);
          StorageManager.saveEncounters(updatedEncounters);
          
          if (currentEncounter?.id === encounterId) {
            setCurrentEncounter(signedEncounter);
          }
          
          return true;
        } catch (apiError) {
          console.warn('Failed to sign encounter via API, signing locally:', apiError);
        }
      }
      
      // Fallback to local signing
      const signedEncounter = {
        ...encounter,
        status: 'signed',
        signedAt: new Date().toISOString(),
        signedBy: providerName,
        isSigned: true
      };
      
      const updatedEncounters = encounters.map(e => 
        e.id === encounterId ? signedEncounter : e
      );
      
      setEncounters(updatedEncounters);
      StorageManager.saveEncounters(updatedEncounters);
      
      if (currentEncounter?.id === encounterId) {
        setCurrentEncounter(signedEncounter);
      }
      
      return true;
    } catch (error) {
      console.error('Error signing encounter:', error);
      setError(error.message);
      return false;
    }
  }, [encounters, currentEncounter]);

  // Copy forward from previous encounter
  const copyForwardFromEncounter = useCallback((sourceEncounterId, sections = []) => {
    const sourceEncounter = encounters.find(e => e.id === sourceEncounterId);
    if (!sourceEncounter || !currentEncounter) return false;
    
    const updates = { ...currentEncounter };
    
    sections.forEach(section => {
      switch (section) {
        case 'vitals':
          updates.soap = {
            ...updates.soap,
            objective: {
              ...updates.soap.objective,
              vitals: { ...sourceEncounter.soap.objective.vitals }
            }
          };
          break;
        case 'medications':
          updates.soap = {
            ...updates.soap,
            subjective: {
              ...updates.soap.subjective,
              medications: sourceEncounter.soap.subjective.medications
            }
          };
          break;
        case 'allergies':
          updates.soap = {
            ...updates.soap,
            subjective: {
              ...updates.soap.subjective,
              allergies: sourceEncounter.soap.subjective.allergies
            }
          };
          break;
        case 'physicalExam':
          updates.soap = {
            ...updates.soap,
            objective: {
              ...updates.soap.objective,
              physicalExam: { ...sourceEncounter.soap.objective.physicalExam }
            }
          };
          break;
        case 'assessment':
          updates.soap = {
            ...updates.soap,
            assessment: {
              ...updates.soap.assessment,
              clinicalImpression: sourceEncounter.soap.assessment.clinicalImpression,
              workingDiagnosis: { ...sourceEncounter.soap.assessment.workingDiagnosis }
            }
          };
          break;
      }
    });
    
    setCurrentEncounter(updates);
    setHasUnsavedChanges(true);
    return true;
  }, [encounters, currentEncounter]);

  // Get encounter statistics
  const getEncounterStats = useCallback(async (episodeId, useCache = true) => {
    try {
      // Try to get stats from API first
      if (!useCache) {
        try {
          const stats = await apiService.getEpisodeEncounterStats(episodeId);
          return stats;
        } catch (apiError) {
          console.warn('Failed to get encounter stats from API:', apiError);
        }
      }
      
      // Fallback to calculating from local data
      const episodeEncounters = await getEpisodeEncounters(episodeId, useCache);
      return {
        total: episodeEncounters.length,
        draft: episodeEncounters.filter(e => e.status === 'draft').length,
        signed: episodeEncounters.filter(e => e.status === 'signed').length,
        lastVisit: episodeEncounters[0]?.date || null
      };
    } catch (error) {
      console.error('Error getting encounter stats:', error);
      return {
        total: 0,
        draft: 0,
        signed: 0,
        lastVisit: null
      };
    }
  }, [getEpisodeEncounters]);

  // Set current encounter with loading state
  const setCurrentEncounterWithLoading = useCallback(async (encounter) => {
    if (!encounter) {
      setCurrentEncounter(null);
      return;
    }
    
    setSwitchingEncounter(true);
    
    // Add a small delay to show loading state
    await new Promise(resolve => setTimeout(resolve, 200));
    
    setCurrentEncounter(encounter);
    setSwitchingEncounter(false);
  }, []);

  // Delete a specific encounter
  const deleteEncounter = useCallback(async (encounterId) => {
    try {
      // Try to delete from API first if not a local encounter
      if (!encounterId.startsWith('ENC')) {
        try {
          await apiService.deleteEncounter(encounterId);
        } catch (apiError) {
          console.warn('Failed to delete encounter from API:', apiError);
          // Continue with local deletion anyway
        }
      }
      
      // Remove from local state
      const updatedEncounters = encounters.filter(e => e.id !== encounterId);
      setEncounters(updatedEncounters);
      StorageManager.saveEncounters(updatedEncounters);
      
      // If it was the current encounter, clear it
      if (currentEncounter?.id === encounterId) {
        setCurrentEncounter(null);
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting encounter:', error);
      setError(error.message);
      return false;
    }
  }, [encounters, currentEncounter]);

  // Delete all encounters for a patient
  const deletePatientEncounters = useCallback((patientId) => {
    const updatedEncounters = encounters.filter(e => e.patientId !== patientId);
    setEncounters(updatedEncounters);
    StorageManager.saveEncounters(updatedEncounters);
  }, [encounters]);

  const value = {
    encounters,
    currentEncounter,
    setCurrentEncounter,
    setCurrentEncounterWithLoading,
    switchingEncounter,
    loading,
    error,
    autoSaveEnabled,
    setAutoSaveEnabled,
    lastSaved,
    hasUnsavedChanges,
    getEpisodeEncounters,
    createEncounter,
    updateCurrentEncounter,
    updateSOAPSection,
    saveCurrentEncounter,
    signEncounter,
    copyForwardFromEncounter,
    getEncounterStats,
    deleteEncounter,
    deletePatientEncounters
  };

  return (
    <EncounterContext.Provider value={value}>
      {children}
    </EncounterContext.Provider>
  );
};