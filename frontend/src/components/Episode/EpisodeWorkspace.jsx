import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
// Removed useNavigation import since we don't navigate within episode workspace
import EncounterList from '../Encounter/EncounterList';
import EncounterWorkspace from '../Encounter/EncounterWorkspace';
import EpisodeHeader from './EpisodeHeader';
import DashboardLayout from '../Layout/DashboardLayout';
import { Activity, Plus, AlertCircle } from 'lucide-react';

const EpisodeWorkspace = () => {
  const { patientId, episodeId } = useParams();
  const navigate = useNavigate();
  const { getPatientById, loading: patientsLoading } = usePatient();
  const { getEpisodeById, loading: episodesLoading } = useEpisode();
  const { getEpisodeEncounters, currentEncounter, createEncounter, setCurrentEncounterWithLoading, switchingEncounter } = useEncounter();
  // Removed navigateTo since we don't navigate within episode workspace
  
  const [patient, setPatient] = useState(null);
  const [episode, setEpisode] = useState(null);
  const [encounters, setEncounters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creatingEncounter, setCreatingEncounter] = useState(false);
  const [encountersLoading, setEncountersLoading] = useState(false);

  const handleCreateEncounter = useCallback(async (type = 'follow-up') => {
    if (!episode || !patient) return;
    
    try {
      console.log(`🏥 EpisodeWorkspace.handleCreateEncounter called for episode: ${episodeId}, type: ${type}`);
      const newEncounter = await createEncounter(episodeId, patientId, type);
      
      // Auto-populate chief complaint from episode
      newEncounter.soap.subjective.chiefComplaint = episode.chiefComplaint;
      
      // If patient has medical background, pre-populate relevant fields
      if (patient.medicalBackground) {
        const { allergies, medications, pastMedicalHistory, pastSurgicalHistory, socialHistory, familyHistory, chronicConditions } = patient.medicalBackground;
        
        // Format allergies
        if (allergies && allergies.length > 0) {
          newEncounter.soap.subjective.allergies = allergies.map(a => 
            `${a.allergen} - ${a.reaction} (${a.severity})`
          ).join(', ');
        }
        
        // Format current medications
        if (medications && medications.length > 0) {
          newEncounter.soap.subjective.medications = medications
            .filter(m => m.ongoing)
            .map(m => `${m.name} ${m.dosage} ${m.frequency}`)
            .join(', ');
        }
        
        // Combine past medical and surgical history
        let pmhText = '';
        if (pastMedicalHistory) {
          pmhText = pastMedicalHistory;
        }
        if (pastSurgicalHistory) {
          pmhText = pmhText ? `${pmhText}\n\nPast Surgical History:\n${pastSurgicalHistory}` : `Past Surgical History:\n${pastSurgicalHistory}`;
        }
        
        // Add chronic conditions to PMH
        if (chronicConditions && chronicConditions.length > 0) {
          const conditionsList = chronicConditions.map(c => `- ${c.condition} (${c.icd10})`).join('\n');
          pmhText = pmhText ? `${pmhText}\n\nChronic Conditions:\n${conditionsList}` : `Chronic Conditions:\n${conditionsList}`;
        }
        
        newEncounter.soap.subjective.pmh = pmhText;
        newEncounter.soap.subjective.socialHistory = socialHistory || '';
        newEncounter.soap.subjective.familyHistory = familyHistory || '';
      }
      
      await setCurrentEncounterWithLoading(newEncounter);
      
      // Refresh encounters list to show the new encounter
      try {
        const episodeEncounters = await getEpisodeEncounters(episodeId, false); // Force fresh data
        setEncounters(episodeEncounters);
        setCreatingEncounter(false);
      } catch (refreshError) {
        console.warn('Failed to refresh encounters after creation:', refreshError);
        // Fallback: manually add to list if refresh fails
        setEncounters(prev => [newEncounter, ...prev.filter(e => e.id !== newEncounter.id)]);
        setCreatingEncounter(false);
      }
    } catch (error) {
      console.error('Failed to create encounter:', error);
    }
  }, [episode, patient, createEncounter, episodeId, patientId, setCurrentEncounterWithLoading, getEpisodeEncounters]);

  const handleSelectEncounter = useCallback(async (encounter) => {
    await setCurrentEncounterWithLoading(encounter);
    // Don't navigate - we're already on episode-workspace
  }, [setCurrentEncounterWithLoading]);

  const handleEncounterDeleted = useCallback(async () => {
    // Refresh encounters after deletion
    try {
      setEncountersLoading(true);
      const episodeEncounters = await getEpisodeEncounters(episodeId, false); // Force fresh data
      setEncounters(episodeEncounters);
      
      // If current encounter was deleted, clear it or select the most recent one
      if (episodeEncounters.length > 0) {
        await setCurrentEncounterWithLoading(episodeEncounters[0]);
      } else {
        // When all encounters are deleted, don't auto-create a new one
        // Show empty state and let user decide
        await setCurrentEncounterWithLoading(null);
        setCreatingEncounter(false);
      }
    } catch (error) {
      console.error('Error refreshing encounters after deletion:', error);
    } finally {
      setEncountersLoading(false);
    }
  }, [episodeId, getEpisodeEncounters, setCurrentEncounterWithLoading]);

  // Load data - wait for contexts to finish loading first
  useEffect(() => {
    if (!patientId || !episodeId) return;
    
    // Don't try to load data while contexts are still loading
    if (patientsLoading || episodesLoading) {
      setLoading(true);
      return;
    }
    
    // Skip if we already have the correct patient and episode loaded
    if (patient?.id === patientId && episode?.id === episodeId && !loading) {
      return;
    }
    
    const loadData = async () => {
      setLoading(true);
      
      try {
        const patientData = getPatientById(patientId);
        const episodeData = getEpisodeById(episodeId);
        
        if (!patientData) {
          console.error(`Patient not found: ${patientId}`);
          setLoading(false);
          return;
        }
        
        if (!episodeData) {
          console.warn(`Episode not found: ${episodeId}, retrying in 1 second...`);
          // Retry after a short delay in case the episode was just created
          setTimeout(async () => {
            const retryEpisodeData = getEpisodeById(episodeId);
            if (retryEpisodeData) {
              setEpisode(retryEpisodeData);
              
              // Continue with loading encounters
              setEncountersLoading(true);
              try {
                const episodeEncounters = await getEpisodeEncounters(episodeId, false);
                setEncounters(episodeEncounters);
                
                if (episodeEncounters.length > 0) {
                  await setCurrentEncounterWithLoading(episodeEncounters[0]);
                  setCreatingEncounter(false);
                } else {
                  await setCurrentEncounterWithLoading(null);
                  setCreatingEncounter(false); // Don't auto-create for retried episodes either
                }
              } catch (encounterError) {
                console.warn('Failed to load encounters on retry:', encounterError);
                setEncounters([]);
                await setCurrentEncounterWithLoading(null);
                setCreatingEncounter(false); // Don't auto-create on retry error either
              } finally {
                setEncountersLoading(false);
                setLoading(false);
              }
            } else {
              console.error(`Episode still not found after retry: ${episodeId}`);
              setLoading(false);
            }
          }, 1000);
          return;
        }
        
        setPatient(patientData);
        setEpisode(episodeData);
        
        // Load encounters asynchronously
        setEncountersLoading(true);
        try {
          const episodeEncounters = await getEpisodeEncounters(episodeId, false); // Always fetch fresh data to avoid duplicates
          setEncounters(episodeEncounters);
          
          if (episodeEncounters.length > 0) {
            // Set the most recent encounter as current
            await setCurrentEncounterWithLoading(episodeEncounters[0]);
            setCreatingEncounter(false); // Ensure we don't auto-create if encounters exist
          } else {
            // For empty episodes, DON'T auto-create encounters
            // Let the user decide when to create the first encounter
            console.log(`📭 Episode ${episodeId} has no encounters - leaving empty for user to decide`);
            await setCurrentEncounterWithLoading(null);
            setCreatingEncounter(false); // Changed from true to false
          }
        } catch (encounterError) {
          console.warn('Failed to load encounters, using empty array:', encounterError);
          setEncounters([]);
          await setCurrentEncounterWithLoading(null);
          setCreatingEncounter(false); // Don't auto-create on error either
        } finally {
          setEncountersLoading(false);
        }
      } catch (error) {
        console.error('Error loading episode data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [patientId, episodeId, getPatientById, getEpisodeById, getEpisodeEncounters, setCurrentEncounterWithLoading, patientsLoading, episodesLoading]);

  // Note: Auto-creation is now DISABLED
  // Episodes start empty and users must manually create encounters
  // This useEffect is kept for backwards compatibility but should not trigger
  useEffect(() => {
    if (creatingEncounter && episode && patient && encounters.length === 0 && !loading) {
      console.log(`⚠️ Auto-creation triggered (this should not happen anymore) for episode ${episode.id}`);
      
      let isMounted = true;
      
      handleCreateEncounter('initial').then(() => {
        if (isMounted) {
          setCreatingEncounter(false);
        }
      }).catch(error => {
        console.error('Failed to create initial encounter:', error);
        if (isMounted) {
          setCreatingEncounter(false);
        }
      });
      
      return () => {
        isMounted = false;
      };
    }
  }, [creatingEncounter, episode?.id, patient?.id, encounters.length, loading, handleCreateEncounter]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-8 h-8 text-gray-400 animate-pulse mx-auto mb-2" />
          <p className="text-gray-600">Loading episode data...</p>
        </div>
      </div>
    );
  }

  if (!patient || !episode) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">Episode or patient not found</p>
          <button
            onClick={() => navigate('/patients')}
            className="text-blue-600 hover:text-blue-700"
          >
            Return to patient list
          </button>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout hideTopNav>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Episode Header */}
        <EpisodeHeader episode={episode} patient={patient} />
      
      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Modern Sidebar - Encounter List */}
        <div className="w-80 bg-white shadow-xl border-r border-gray-200 flex flex-col overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 text-white">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-bold flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Encounters
              </h3>
              <span className="bg-white/20 px-2 py-1 rounded-full text-xs font-medium">
                {encountersLoading ? (
                  <div className="w-8 h-3 bg-white/30 rounded animate-pulse"></div>
                ) : (
                  `${(encounters || []).length} Total`
                )}
              </span>
            </div>
            <button
              onClick={() => handleCreateEncounter('follow-up')}
              className="w-full mt-3 px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 group"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">New Encounter</span>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto bg-gray-50">
            {encountersLoading ? (
              <div className="p-4 space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded mb-2"></div>
                      <div className="h-3 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EncounterList
                encounters={encounters || []}
                currentEncounter={currentEncounter}
                onSelectEncounter={handleSelectEncounter}
                onEncounterDeleted={handleEncounterDeleted}
              />
            )}
          </div>
          
          {/* Quick Stats Footer */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                {encountersLoading ? (
                  <div className="w-8 h-8 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded animate-pulse mx-auto mb-1"></div>
                ) : (
                  <p className="text-2xl font-bold text-gray-900">
                    {(encounters || []).filter(e => e.status === 'signed' || e.isSigned).length}
                  </p>
                )}
                <p className="text-xs text-gray-600">Signed</p>
              </div>
              <div>
                {encountersLoading ? (
                  <div className="w-8 h-8 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded animate-pulse mx-auto mb-1"></div>
                ) : (
                  <p className="text-2xl font-bold text-blue-600">
                    {(encounters || []).filter(e => e.status !== 'signed' && !e.isSigned).length}
                  </p>
                )}
                <p className="text-xs text-gray-600">In Progress</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Main Area - SOAP Documentation */}
        <div className="flex-1">
          {encountersLoading ? (
            <div className="flex items-center justify-center h-full bg-white">
              <div className="text-center max-w-md">
                <div className="relative">
                  <Activity className="w-16 h-16 text-blue-500 animate-pulse mx-auto mb-4" />
                  <div className="absolute inset-0 w-16 h-16 bg-blue-200 rounded-full animate-ping opacity-20" />
                </div>
                <p className="text-gray-700 font-medium text-lg mb-2">Loading encounters...</p>
                <p className="text-gray-500 text-sm">Please wait while we fetch the encounter data for this episode.</p>
              </div>
            </div>
          ) : switchingEncounter ? (
            <div className="flex items-center justify-center h-full bg-white">
              <div className="text-center max-w-md">
                <div className="relative">
                  <Activity className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
                  <div className="absolute inset-0 w-12 h-12 bg-blue-200 rounded-full animate-pulse opacity-30" />
                </div>
                <p className="text-gray-700 font-medium mb-2">Loading encounter...</p>
                <p className="text-gray-500 text-sm">Preparing SOAP documentation interface...</p>
              </div>  
            </div>
          ) : currentEncounter ? (
            <EncounterWorkspace
              encounter={currentEncounter}
              episode={episode}
              patient={patient}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No encounter selected</p>
                <button
                  onClick={() => handleCreateEncounter('initial')}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create First Encounter
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      </div>
    </DashboardLayout>
  );
};

export default EpisodeWorkspace;