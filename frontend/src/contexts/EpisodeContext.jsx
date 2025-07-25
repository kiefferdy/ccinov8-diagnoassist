import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { StorageManager, generateId } from '../utils/storage';
import apiService from '../services/apiService';
import { transformEpisodeToBackend, transformEpisodeFromBackend } from '../utils/dataTransformers';

const EpisodeContext = createContext(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useEpisode = () => {
  const context = useContext(EpisodeContext);
  if (!context) {
    throw new Error('useEpisode must be used within an EpisodeProvider');
  }
  return context;
};

export const EpisodeProvider = ({ children }) => {
  const [episodes, setEpisodes] = useState([]);
  const [currentEpisode, setCurrentEpisode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load episodes from API on mount
  useEffect(() => {
    const loadEpisodes = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getEpisodes();
        const backendEpisodes = response.data || response;
        const transformedEpisodes = backendEpisodes.map(transformEpisodeFromBackend);
        setEpisodes(transformedEpisodes);
        // Also save to localStorage as backup
        StorageManager.saveEpisodes(transformedEpisodes);
      } catch (error) {
        console.error('Error loading episodes from API:', error);
        setError(error.message);
        // Fallback to localStorage if API fails
        try {
          const storedEpisodes = StorageManager.getEpisodes();
          setEpisodes(storedEpisodes);
        } catch (localError) {
          console.error('Error loading episodes from storage:', localError);
        }
      } finally {
        setLoading(false);
      }
    };
    loadEpisodes();
  }, []);

  // Get episodes for a specific patient
  const getPatientEpisodes = useCallback((patientId, includeResolved = true) => {
    return episodes.filter(e => {
      const matchesPatient = e.patientId === patientId;
      const matchesStatus = includeResolved || e.status !== 'resolved';
      return matchesPatient && matchesStatus;
    });
  }, [episodes]);

  // Create a new episode
  const createEpisode = useCallback(async (patientId, episodeData) => {
    try {
      setError(null);
      const frontendEpisode = {
        patientId,
        chiefComplaint: episodeData.chiefComplaint,
        category: episodeData.category || 'acute',
        status: 'active',
        createdAt: new Date().toISOString(),
        resolvedAt: null,
        lastEncounterId: null,
        relatedEpisodeIds: episodeData.relatedEpisodeIds || [],
        tags: episodeData.tags || []
      };
      
      const backendEpisodeData = transformEpisodeToBackend(frontendEpisode, patientId);
      const backendEpisode = await apiService.createEpisode(backendEpisodeData);
      const transformedEpisode = transformEpisodeFromBackend(backendEpisode);
      
      const updatedEpisodes = [...episodes, transformedEpisode];
      setEpisodes(updatedEpisodes);
      StorageManager.saveEpisodes(updatedEpisodes);
      
      return transformedEpisode;
    } catch (error) {
      console.error('Error creating episode:', error);
      setError(error.message);
      // Fallback to localStorage creation
      const newEpisode = {
        id: generateId('E'),
        patientId,
        chiefComplaint: episodeData.chiefComplaint,
        category: episodeData.category || 'acute',
        status: 'active',
        createdAt: new Date().toISOString(),
        resolvedAt: null,
        lastEncounterId: null,
        relatedEpisodeIds: episodeData.relatedEpisodeIds || [],
        tags: episodeData.tags || []
      };

      const updatedEpisodes = [...episodes, newEpisode];
      setEpisodes(updatedEpisodes);
      StorageManager.saveEpisodes(updatedEpisodes);
      
      return newEpisode;
    }
  }, [episodes]);
  // Update an episode
  const updateEpisode = useCallback(async (episodeId, updates) => {
    try {
      setError(null);
      const episode = episodes.find(e => e.id === episodeId);
      if (!episode) throw new Error('Episode not found');
      
      const updatedEpisodeData = { ...episode, ...updates };
      const backendEpisodeData = transformEpisodeToBackend(updatedEpisodeData, episode.patientId);
      const backendEpisode = await apiService.updateEpisode(episodeId, backendEpisodeData);
      const transformedEpisode = transformEpisodeFromBackend(backendEpisode);
      
      const updatedEpisodes = episodes.map(e => 
        e.id === episodeId ? transformedEpisode : e
      );
      setEpisodes(updatedEpisodes);
      StorageManager.saveEpisodes(updatedEpisodes);
      
      // Update current episode if it's the one being updated
      if (currentEpisode?.id === episodeId) {
        setCurrentEpisode(transformedEpisode);
      }
      
      return transformedEpisode;
    } catch (error) {
      console.error('Error updating episode:', error);
      setError(error.message);
      // Fallback to localStorage update
      const updatedEpisodes = episodes.map(e => 
        e.id === episodeId ? { ...e, ...updates } : e
      );
      setEpisodes(updatedEpisodes);
      StorageManager.saveEpisodes(updatedEpisodes);
      
      if (currentEpisode?.id === episodeId) {
        setCurrentEpisode(prev => ({ ...prev, ...updates }));
      }
      
      return updatedEpisodes.find(e => e.id === episodeId);
    }
  }, [episodes, currentEpisode]);

  // Resolve an episode
  const resolveEpisode = useCallback((episodeId) => {
    return updateEpisode(episodeId, {
      status: 'resolved',
      resolvedAt: new Date().toISOString()
    });
  }, [updateEpisode]);

  // Link episodes
  const linkEpisodes = useCallback((episodeId1, episodeId2) => {
    const episode1 = episodes.find(e => e.id === episodeId1);
    const episode2 = episodes.find(e => e.id === episodeId2);
    
    if (!episode1 || !episode2) return false;
    
    // Update both episodes to include each other in relatedEpisodeIds
    const updated1 = {
      ...episode1,
      relatedEpisodeIds: [...new Set([...episode1.relatedEpisodeIds, episodeId2])]
    };
    const updated2 = {
      ...episode2,
      relatedEpisodeIds: [...new Set([...episode2.relatedEpisodeIds, episodeId1])]
    };
    
    const updatedEpisodes = episodes.map(e => {
      if (e.id === episodeId1) return updated1;
      if (e.id === episodeId2) return updated2;
      return e;
    });
    
    setEpisodes(updatedEpisodes);
    StorageManager.saveEpisodes(updatedEpisodes);
    return true;
  }, [episodes]);

  // Get episode by ID
  const getEpisodeById = useCallback((episodeId) => {
    return episodes.find(e => e.id === episodeId) || null;
  }, [episodes]);

  // Get active episodes count for a patient
  const getActiveEpisodeCount = useCallback((patientId) => {
    return episodes.filter(e => 
      e.patientId === patientId && e.status === 'active'
    ).length;
  }, [episodes]);

  // Get episode statistics
  const getEpisodeStats = useCallback((patientId) => {
    const patientEpisodes = getPatientEpisodes(patientId);
    return {
      total: patientEpisodes.length,
      active: patientEpisodes.filter(e => e.status === 'active').length,
      resolved: patientEpisodes.filter(e => e.status === 'resolved').length,
      chronic: patientEpisodes.filter(e => e.status === 'chronic-management').length
    };
  }, [getPatientEpisodes]);

  // Delete all episodes for a patient
  const deletePatientEpisodes = useCallback((patientId) => {
    const updatedEpisodes = episodes.filter(e => e.patientId !== patientId);
    setEpisodes(updatedEpisodes);
    StorageManager.saveEpisodes(updatedEpisodes);
  }, [episodes]);

  const value = {
    episodes,
    currentEpisode,
    setCurrentEpisode,
    loading,
    error,
    getPatientEpisodes,
    createEpisode,
    updateEpisode,
    resolveEpisode,
    linkEpisodes,
    getEpisodeById,
    getActiveEpisodeCount,
    getEpisodeStats,
    deletePatientEpisodes
  };

  return (
    <EpisodeContext.Provider value={value}>
      {children}
    </EpisodeContext.Provider>
  );
};