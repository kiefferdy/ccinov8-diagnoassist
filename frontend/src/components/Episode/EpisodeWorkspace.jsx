import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { useNavigation } from '../../contexts/NavigationContext';
import EncounterList from '../Encounter/EncounterList';
import EncounterWorkspace from '../Encounter/EncounterWorkspace';
import EpisodeHeader from './EpisodeHeader';
import { Activity, Plus, AlertCircle } from 'lucide-react';

const EpisodeWorkspace = () => {
  const { patientId, episodeId } = useParams();
  const navigate = useNavigate();
  const { getPatientById } = usePatient();
  const { getEpisodeById } = useEpisode();
  const { getEpisodeEncounters, currentEncounter, createEncounter, setCurrentEncounter } = useEncounter();
  const { navigateTo } = useNavigation();
  
  const [patient, setPatient] = useState(null);
  const [episode, setEpisode] = useState(null);
  const [encounters, setEncounters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creatingEncounter, setCreatingEncounter] = useState(false);

  const handleCreateEncounter = useCallback(async (type = 'follow-up') => {
    if (!episode || !patient) return;
    
    try {
      const newEncounter = createEncounter(episodeId, patientId, type);
      
      // Auto-populate chief complaint from episode
      newEncounter.soap.subjective.chiefComplaint = episode.chiefComplaint;
      
      // If patient has medical background, pre-populate relevant fields
      if (patient.medicalBackground) {
        const { allergies, medications, pastMedicalHistory, socialHistory, familyHistory } = patient.medicalBackground;
        
        newEncounter.soap.subjective.allergies = allergies.map(a => 
          `${a.allergen} - ${a.reaction} (${a.severity})`
        ).join(', ');
        
        newEncounter.soap.subjective.medications = medications
          .filter(m => m.ongoing)
          .map(m => `${m.name} ${m.dosage} ${m.frequency}`)
          .join(', ');
          
        newEncounter.soap.subjective.pmh = pastMedicalHistory;
        newEncounter.soap.subjective.socialHistory = socialHistory;
        newEncounter.soap.subjective.familyHistory = familyHistory;
      }
      
      setCurrentEncounter(newEncounter);
      setEncounters(prevEncounters => [newEncounter, ...prevEncounters]);
      navigateTo('episode-workspace');
    } catch (error) {
      console.error('Failed to create encounter:', error);
    }
  }, [episode, patient, createEncounter, episodeId, patientId, setCurrentEncounter, navigateTo]);

  // Load data
  useEffect(() => {
    if (!patientId || !episodeId) return;
    
    const loadData = async () => {
      setLoading(true);
      
      const patientData = getPatientById(patientId);
      const episodeData = getEpisodeById(episodeId);
      
      if (patientData && episodeData) {
        setPatient(patientData);
        setEpisode(episodeData);
        
        const episodeEncounters = getEpisodeEncounters(episodeId);
        setEncounters(episodeEncounters);
        
        // If no encounters exist, mark that we need to create one
        if (episodeEncounters.length === 0) {
          setCreatingEncounter(true);
        } else if (episodeEncounters.length > 0) {
          // Set the most recent encounter as current
          setCurrentEncounter(episodeEncounters[0]);
        }
      }
      setLoading(false);
    };
    
    loadData();
  }, [patientId, episodeId, getPatientById, getEpisodeById, getEpisodeEncounters, setCurrentEncounter]);

  // Create initial encounter when needed
  useEffect(() => {
    if (creatingEncounter && episode && patient) {
      handleCreateEncounter('initial').then(() => {
        setCreatingEncounter(false);
      });
    }
  }, [creatingEncounter, episode, patient, handleCreateEncounter]);
  const handleSelectEncounter = (encounter) => {
    setCurrentEncounter(encounter);
  };

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
                {encounters.length} Total
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
            <EncounterList
              encounters={encounters}
              currentEncounter={currentEncounter}
              onSelectEncounter={handleSelectEncounter}
            />
          </div>
          
          {/* Quick Stats Footer */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {encounters.filter(e => e.status === 'signed').length}
                </p>
                <p className="text-xs text-gray-600">Signed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {encounters.filter(e => e.status !== 'signed').length}
                </p>
                <p className="text-xs text-gray-600">In Progress</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Main Area - SOAP Documentation */}
        <div className="flex-1">
          {currentEncounter ? (
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
  );
};

export default EpisodeWorkspace;