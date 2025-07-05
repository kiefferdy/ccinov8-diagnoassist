import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { StorageManager, generateId } from '../utils/storage';

const EncounterContext = createContext(null);

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
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [lastSaved, setLastSaved] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Load encounters from storage on mount
  useEffect(() => {
    const loadEncounters = () => {
      try {
        const storedEncounters = StorageManager.getEncounters();
        setEncounters(storedEncounters);
        setLoading(false);
      } catch (error) {
        console.error('Error loading encounters:', error);
        setLoading(false);
      }
    };
    loadEncounters();
  }, []);
  // Auto-save functionality
  useEffect(() => {
    if (!autoSaveEnabled || !currentEncounter || !hasUnsavedChanges) return;

    const saveTimer = setTimeout(() => {
      saveCurrentEncounter();
    }, 30000); // Auto-save every 30 seconds

    return () => clearTimeout(saveTimer);
  }, [currentEncounter, hasUnsavedChanges, autoSaveEnabled]);

  // Get encounters for a specific episode
  const getEpisodeEncounters = useCallback((episodeId) => {
    return encounters
      .filter(e => e.episodeId === episodeId)
      .sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [encounters]);

  // Create a new encounter
  const createEncounter = useCallback((episodeId, patientId, type = 'follow-up') => {
    const newEncounter = {
      id: generateId('ENC'),
      episodeId,
      patientId,
      type,
      date: new Date().toISOString(),
      status: 'draft',
      provider: {
        id: 'DR001', // In real app, this would come from auth context
        name: 'Dr. Current User',
        role: 'Primary Care Physician'
      },
      soap: {
        subjective: {
          chiefComplaint: '', // Will be populated from episode
          hpi: '',
          ros: {},
          pmh: '',
          medications: '',
          allergies: '',
          socialHistory: '',
          familyHistory: '',
          lastUpdated: new Date().toISOString(),
          voiceNotes: []
        },
        objective: {
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
          },
          diagnosticTests: {
            ordered: [],
            results: []
          },
          lastUpdated: new Date().toISOString(),
          voiceNotes: []
        },
        assessment: {
          clinicalImpression: '',
          differentialDiagnosis: [],
          workingDiagnosis: {
            diagnosis: '',
            icd10: '',
            confidence: 'possible',
            clinicalReasoning: ''
          },
          riskAssessment: '',
          lastUpdated: new Date().toISOString(),
          aiConsultation: {
            queries: [],
            insights: []
          }
        },
        plan: {
          medications: [],
          procedures: [],
          referrals: [],
          followUp: {
            timeframe: '',
            reason: '',
            instructions: ''
          },
          patientEducation: [],
          activityRestrictions: '',
          dietRecommendations: '',
          lastUpdated: new Date().toISOString()
        }
      },
      documents: [],
      amendments: [],
      signedAt: null,
      signedBy: null
    };

    const updatedEncounters = [...encounters, newEncounter];
    setEncounters(updatedEncounters);
    StorageManager.saveEncounters(updatedEncounters);
    
    // Update episode's lastEncounterId
    StorageManager.updateEpisode(episodeId, { lastEncounterId: newEncounter.id });
    
    return newEncounter;
  }, [encounters]);
  // Update current encounter
  const updateCurrentEncounter = useCallback((updates) => {
    if (!currentEncounter) return;
    
    const updatedEncounter = { ...currentEncounter, ...updates };
    setCurrentEncounter(updatedEncounter);
    setHasUnsavedChanges(true);
  }, [currentEncounter]);

  // Update SOAP section
  const updateSOAPSection = useCallback((section, updates) => {
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
  }, [currentEncounter]);

  // Save current encounter
  const saveCurrentEncounter = useCallback(() => {
    if (!currentEncounter) return false;
    
    const updatedEncounters = encounters.map(e => 
      e.id === currentEncounter.id ? currentEncounter : e
    );
    
    // If it's a new encounter not yet in the list
    if (!encounters.find(e => e.id === currentEncounter.id)) {
      updatedEncounters.push(currentEncounter);
    }
    
    setEncounters(updatedEncounters);
    StorageManager.saveEncounters(updatedEncounters);
    setLastSaved(new Date().toISOString());
    setHasUnsavedChanges(false);
    
    return true;
  }, [currentEncounter, encounters]);

  // Sign encounter
  const signEncounter = useCallback((encounterId, providerName) => {
    const encounter = encounters.find(e => e.id === encounterId);
    if (!encounter || encounter.status === 'signed') return false;
    
    const signedEncounter = {
      ...encounter,
      status: 'signed',
      signedAt: new Date().toISOString(),
      signedBy: providerName
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
  }, [encounters, currentEncounter]);

  // Copy forward from previous encounter
  const copyForwardFromEncounter = useCallback((sourceEncounterId, sections = []) => {
    const sourceEncounter = encounters.find(e => e.id === sourceEncounterId);
    if (!sourceEncounter || !currentEncounter) return false;
    
    const updates = {};
    
    sections.forEach(section => {
      switch (section) {
        case 'vitals':
          updates.soap = {
            ...currentEncounter.soap,
            objective: {
              ...currentEncounter.soap.objective,
              vitals: { ...sourceEncounter.soap.objective.vitals }
            }
          };
          break;
        case 'medications':
          updates.soap = {
            ...currentEncounter.soap,
            subjective: {
              ...currentEncounter.soap.subjective,
              medications: sourceEncounter.soap.subjective.medications
            }
          };
          break;
        case 'allergies':
          updates.soap = {
            ...currentEncounter.soap,
            subjective: {
              ...currentEncounter.soap.subjective,
              allergies: sourceEncounter.soap.subjective.allergies
            }
          };
          break;
        // Add more sections as needed
      }
    });
    
    updateCurrentEncounter(updates);
    return true;
  }, [encounters, currentEncounter, updateCurrentEncounter]);

  // Get encounter statistics
  const getEncounterStats = useCallback((episodeId) => {
    const episodeEncounters = getEpisodeEncounters(episodeId);
    return {
      total: episodeEncounters.length,
      draft: episodeEncounters.filter(e => e.status === 'draft').length,
      signed: episodeEncounters.filter(e => e.status === 'signed').length,
      lastVisit: episodeEncounters[0]?.date || null
    };
  }, [getEpisodeEncounters]);

  const value = {
    encounters,
    currentEncounter,
    setCurrentEncounter,
    loading,
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
    getEncounterStats
  };

  return (
    <EncounterContext.Provider value={value}>
      {children}
    </EncounterContext.Provider>
  );
};