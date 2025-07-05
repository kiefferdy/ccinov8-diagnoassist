import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import PatientHeader from './PatientHeader';
import EpisodeCard from './EpisodeCard';
import QuickActions from './QuickActions';
import NewEpisodeModal from '../Episode/NewEpisodeModal';
import { Activity, Archive, Filter, Search } from 'lucide-react';

const PatientDashboard = () => {
  const { patientId } = useParams();
  const { getPatientById } = usePatient();
  const { getPatientEpisodes, getEpisodeStats } = useEpisode();
  const { getEpisodeEncounters } = useEncounter();
  
  const [patient, setPatient] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [showNewEpisodeModal, setShowNewEpisodeModal] = useState(false);
  const [episodeFilter, setEpisodeFilter] = useState('active'); // active, resolved, all
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Load patient and episodes
  useEffect(() => {
    const loadData = () => {
      const patientData = getPatientById(patientId);
      if (patientData) {
        setPatient(patientData);
        const patientEpisodes = getPatientEpisodes(patientId, true);
        setEpisodes(patientEpisodes);
      }
      setLoading(false);
    };
    loadData();
  }, [patientId, getPatientById, getPatientEpisodes]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-8 h-8 text-gray-400 animate-pulse mx-auto mb-2" />
          <p className="text-gray-600">Loading patient data...</p>
        </div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Patient not found</p>
        </div>
      </div>
    );
  }
  // Filter episodes
  const filteredEpisodes = episodes.filter(episode => {
    // Apply status filter
    if (episodeFilter === 'active' && episode.status === 'resolved') return false;
    if (episodeFilter === 'resolved' && episode.status !== 'resolved') return false;
    
    // Apply search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return (
        episode.chiefComplaint.toLowerCase().includes(search) ||
        episode.tags?.some(tag => tag.toLowerCase().includes(search))
      );
    }
    
    return true;
  });

  const stats = getEpisodeStats(patientId);

  const handleNewEpisode = () => {
    setShowNewEpisodeModal(true);
  };

  const handleViewAllRecords = () => {
    setEpisodeFilter('all');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Patient Header */}
        <PatientHeader patient={patient} />

        {/* Quick Actions */}
        <QuickActions 
          onNewEpisode={handleNewEpisode}
          onViewAllRecords={handleViewAllRecords}
        />

        {/* Episodes Section */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">Episodes</h2>
              <p className="text-sm text-gray-600 mt-1">
                {stats.total} total • {stats.active} active • {stats.resolved} resolved
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search episodes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              {/* Filter */}
              <select
                value={episodeFilter}
                onChange={(e) => setEpisodeFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="active">Active Episodes</option>
                <option value="resolved">Resolved Episodes</option>
                <option value="all">All Episodes</option>
              </select>
            </div>
          </div>

          {/* Episode Cards */}
          {filteredEpisodes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredEpisodes.map(episode => (
                <EpisodeCard
                  key={episode.id}
                  episode={episode}
                  encounters={getEpisodeEncounters(episode.id)}
                  patientId={patientId}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              {searchTerm || episodeFilter !== 'all' ? (
                <>
                  <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No episodes found</h3>
                  <p className="text-gray-500">Try adjusting your search or filter criteria</p>
                </>
              ) : (
                <>
                  <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No episodes yet</h3>
                  <p className="text-gray-500 mb-4">Start documenting patient visits by creating a new episode</p>
                  <button
                    onClick={handleNewEpisode}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    New Episode
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* New Episode Modal */}
      {showNewEpisodeModal && (
        <NewEpisodeModal
          patientId={patientId}
          onClose={() => setShowNewEpisodeModal(false)}
          onSuccess={(newEpisode) => {
            setShowNewEpisodeModal(false);
            // Refresh episodes list
            const updatedEpisodes = getPatientEpisodes(patientId, true);
            setEpisodes(updatedEpisodes);
          }}
        />
      )}
    </div>
  );
};

export default PatientDashboard;