import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import PatientHeader from './PatientHeader';
import EpisodeCard from './EpisodeCard';
import QuickActions from './QuickActions';
import NewEpisodeModal from '../Episode/NewEpisodeModal';
import AllRecordsView from '../AllRecords/AllRecordsView';
import QuickNoteModal from '../QuickNote/QuickNoteModal';
import QuickNotesView from '../QuickNote/QuickNotesView';
import DashboardLayout from '../Layout/DashboardLayout';
import './animations.css'; // Import animations
import { 
  Activity, Archive, Filter, Search, Plus, Calendar, Clock, 
  TrendingUp, AlertCircle, FileText, Heart, Brain, Pill,
  ChevronRight, BarChart3, Zap
} from 'lucide-react';

const PatientDashboard = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const { getPatientById, patients, loading: patientsLoading } = usePatient();
  const { getPatientEpisodes, getEpisodeStats, loading: episodesLoading } = useEpisode();
  const { getEpisodeEncounters } = useEncounter();
  
  const [patient, setPatient] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [showNewEpisodeModal, setShowNewEpisodeModal] = useState(false);
  const [showAllRecordsModal, setShowAllRecordsModal] = useState(false);
  const [showQuickNoteModal, setShowQuickNoteModal] = useState(false);
  const [showQuickNotesView, setShowQuickNotesView] = useState(false);
  const [episodeFilter, setEpisodeFilter] = useState('active');
  const [episodeTypeFilter, setEpisodeTypeFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('all'); // all, month, year
  const [quickNotesCount, setQuickNotesCount] = useState(0);
  const [recentEncounters, setRecentEncounters] = useState([]);
  const [episodeEncounters, setEpisodeEncounters] = useState({});

  // Load patient and episodes - wait for contexts to finish loading first
  useEffect(() => {
    if (!patientId) return;
    
    // Don't try to load data while contexts are still loading
    if (patientsLoading || episodesLoading) {
      setLoading(true);
      return;
    }
    
    const loadData = () => {
      try {
        const patientData = getPatientById(patientId);
        if (patientData) {
          setPatient(patientData);
          const patientEpisodes = getPatientEpisodes(patientId, true);
          setEpisodes(patientEpisodes);
        } else {
          console.error(`Patient not found: ${patientId}`);
        }
      } catch (error) {
        console.error('Error loading patient data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [patientId, getPatientById, getPatientEpisodes, patients, patientsLoading, episodesLoading]);

  // Calculate quick notes count
  useEffect(() => {
    if (patient) {
      const allNotes = JSON.parse(localStorage.getItem('quickNotes') || '[]');
      const patientNotes = allNotes.filter(note => note.patientId === patient.id);
      setQuickNotesCount(patientNotes.length);
    }
  }, [patient]);

  // Load encounters for all episodes asynchronously
  useEffect(() => {
    const loadEncounters = async () => {
      if (episodes.length === 0) {
        setRecentEncounters([]);
        setEpisodeEncounters({});
        return;
      }

      try {
        const allEncounters = [];
        const encountersByEpisode = {};
        
        // Load encounters for each episode
        for (const episode of episodes) {
          try {
            const encounters = await getEpisodeEncounters(episode.id, true); // Use cache
            encountersByEpisode[episode.id] = encounters;
            allEncounters.push(...encounters);
          } catch (error) {
            console.warn(`Failed to load encounters for episode ${episode.id}:`, error);
            encountersByEpisode[episode.id] = []; // Set empty array as fallback
          }
        }

        // Sort by date and take the 5 most recent for the recent encounters section
        const sortedEncounters = allEncounters
          .sort((a, b) => new Date(b.date || b.createdAt) - new Date(a.date || a.createdAt))
          .slice(0, 5);

        setRecentEncounters(sortedEncounters);
        setEpisodeEncounters(encountersByEpisode);
      } catch (error) {
        console.error('Error loading encounters:', error);
        setRecentEncounters([]);
        setEpisodeEncounters({});
      }
    };

    loadEncounters();
  }, [episodes, getEpisodeEncounters]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <Activity className="w-16 h-16 text-blue-600 animate-pulse mx-auto mb-4" />
            <div className="absolute inset-0 w-16 h-16 bg-blue-400 rounded-full animate-ping opacity-20" />
          </div>
          <p className="text-gray-600 font-medium">Loading patient data...</p>
        </div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center bg-white rounded-2xl shadow-xl p-8">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-gray-800 font-semibold text-lg">Patient not found</p>
          <p className="text-gray-600 mt-2">Please check the patient ID and try again.</p>
        </div>
      </div>
    );
  }

  // Filter episodes
  const filteredEpisodes = episodes.filter(episode => {
    // Apply status filter
    if (episodeFilter === 'active' && (episode.status === 'resolved' || episode.status === 'archived')) return false;
    if (episodeFilter === 'resolved' && episode.status !== 'resolved') return false;
    if (episodeFilter === 'archived' && episode.status !== 'archived') return false;
    
    // Apply type filter
    if (episodeTypeFilter !== 'all' && episode.type !== episodeTypeFilter) return false;
    
    // Apply time range filter
    if (selectedTimeRange !== 'all') {
      const episodeDate = new Date(episode.createdAt);
      const now = new Date();
      
      if (selectedTimeRange === 'month') {
        const oneMonthAgo = new Date(now.setMonth(now.getMonth() - 1));
        if (episodeDate < oneMonthAgo) return false;
      } else if (selectedTimeRange === 'year') {
        const oneYearAgo = new Date(now.setFullYear(now.getFullYear() - 1));
        if (episodeDate < oneYearAgo) return false;
      }
    }
    
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

  const urgentEpisodes = episodes.filter(ep => 
    ep.status === 'active' && ep.tags?.includes('urgent')
  ).length;

  const chronicConditions = patient.medicalBackground?.chronicConditions?.length || 0;

  const handleNewEpisode = () => {
    setShowNewEpisodeModal(true);
  };

  const handleViewAllRecords = () => {
    setShowAllRecordsModal(true);
  };

  const handleContinueCare = () => {
    // Find the most recent active episode
    const activeEpisodes = episodes.filter(ep => ep.status === 'active');
    if (activeEpisodes.length > 0) {
      // Sort by most recent activity using loaded encounter data
      const mostRecentEpisode = activeEpisodes.sort((a, b) => {
        const aEncounters = episodeEncounters[a.id] || [];
        const bEncounters = episodeEncounters[b.id] || [];
        const aLastDate = aEncounters.length > 0 
          ? new Date(aEncounters[aEncounters.length - 1].date || aEncounters[aEncounters.length - 1].createdAt)
          : new Date(a.createdAt);
        const bLastDate = bEncounters.length > 0
          ? new Date(bEncounters[bEncounters.length - 1].date || bEncounters[bEncounters.length - 1].createdAt)
          : new Date(b.createdAt);
        return bLastDate - aLastDate;
      })[0];
      
      // Navigate to episode workspace
      navigate(`/patient/${patientId}/episode/${mostRecentEpisode.id}`);
    } else {
      // No active episodes, show new episode modal
      setShowNewEpisodeModal(true);
    }
  };

  const handleQuickNote = () => {
    setShowQuickNoteModal(true);
  };

  const handleSaveQuickNote = (note) => {
    // Save to localStorage
    const existingNotes = JSON.parse(localStorage.getItem('quickNotes') || '[]');
    const updatedNotes = [...existingNotes, note];
    localStorage.setItem('quickNotes', JSON.stringify(updatedNotes));
    
    // Update count
    const patientNotes = updatedNotes.filter(n => n.patientId === patient.id);
    setQuickNotesCount(patientNotes.length);
    
    // Show success message
    if (window.showNotification) {
      window.showNotification('Quick note saved successfully', 'success');
    }
    
    // In a real app, this would also save to the backend
    console.log('Quick note saved:', note);
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        {/* Animated Background Pattern */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Patient Header with enhanced design */}
        <div className="mb-8">
          <PatientHeader 
            patient={patient} 
            key={patient.updatedAt} // Force re-render when patient is updated
          />
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Episodes</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.active}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {urgentEpisodes > 0 && `${urgentEpisodes} urgent`}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-xl">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Episodes</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.resolved} resolved
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-xl">
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Chronic Conditions</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{chronicConditions}</p>
                <p className="text-xs text-gray-500 mt-1">Active management</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-xl">
                <Heart className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Visit</p>
                <p className="text-lg font-bold text-gray-900 mt-2">
                  {patient.lastVisit ? new Date(patient.lastVisit).toLocaleDateString() : 'N/A'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {patient.lastVisit && 
                    `${Math.floor((new Date() - new Date(patient.lastVisit)) / (1000 * 60 * 60 * 24))} days ago`
                  }
                </p>
              </div>
              <div className="p-3 bg-indigo-100 rounded-xl">
                <Calendar className="w-8 h-8 text-indigo-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions with better design */}
        <div className="mb-8">
          <QuickActions 
            onNewEpisode={handleNewEpisode}
            onViewAllRecords={handleViewAllRecords}
            onContinueCare={handleContinueCare}
            onQuickNote={handleQuickNote}
            stats={stats}
            quickNotesCount={quickNotesCount}
          />
        </div>

        {/* Episodes Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Activity className="w-7 h-7 mr-2 text-blue-600" />
                Clinical Episodes
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage and track patient care episodes
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
              {/* Search */}
              <div className="relative flex-1 sm:flex-initial">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search episodes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full sm:w-64 pl-9 pr-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              
              {/* Time Range Filter */}
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="all">All Time</option>
                <option value="month">Last Month</option>
                <option value="year">Last Year</option>
              </select>
              
              {/* Status Filter */}
              <select
                value={episodeFilter}
                onChange={(e) => setEpisodeFilter(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="active">Active Episodes</option>
                <option value="resolved">Resolved Episodes</option>
                <option value="archived">Archived Episodes</option>
                <option value="all">All Episodes</option>
              </select>
              
              {/* Type Filter */}
              <select
                value={episodeTypeFilter}
                onChange={(e) => setEpisodeTypeFilter(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="all">All Types</option>
                <option value="acute">Acute</option>
                <option value="chronic">Chronic</option>
                <option value="preventive">Preventive</option>
                <option value="follow-up">Follow-up</option>
              </select>
            </div>
          </div>

          {/* Episode Cards */}
          {filteredEpisodes.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredEpisodes.map(episode => (
                <EpisodeCard
                  key={episode.id}
                  episode={episode}
                  encounters={episodeEncounters[episode.id] || []}
                  patientId={patientId}
                />
              ))}
            </div>
          ) : (
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border-2 border-dashed border-gray-300 p-12 text-center">
              {searchTerm || episodeFilter !== 'all' || selectedTimeRange !== 'all' ? (
                <>
                  <Archive className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No episodes found</h3>
                  <p className="text-gray-600 max-w-md mx-auto">
                    Try adjusting your search criteria or filters to see more results
                  </p>
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setEpisodeFilter('all');
                      setSelectedTimeRange('all');
                    }}
                    className="mt-4 text-blue-600 hover:text-blue-700 font-medium text-sm"
                  >
                    Clear all filters
                  </button>
                </>
              ) : (
                <>
                  <div className="relative">
                    <Activity className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                    <Plus className="w-6 h-6 text-blue-600 absolute bottom-0 right-1/2 transform translate-x-8 bg-white rounded-full p-1" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Start documenting care</h3>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto">
                    Create your first episode to begin tracking this patient's clinical journey
                  </p>
                  <button
                    onClick={handleNewEpisode}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Create First Episode
                  </button>
                </>
              )}
            </div>
          )}
        </div>

        {/* Recent Activity Timeline */}
        {recentEncounters.length > 0 && (
          <div className="mt-8 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-blue-600" />
              Recent Activity
            </h3>
            <div className="space-y-3">
              {recentEncounters.slice(0, 3).map((encounter) => (
                <div key={encounter.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      encounter.status === 'signed' ? 'bg-green-500' : 'bg-yellow-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {encounter.type ? 
                          (encounter.type.charAt(0).toUpperCase() + encounter.type.slice(1)) : 
                          'Unknown'
                        } Visit
                      </p>
                      <p className="text-xs text-gray-600">
                        {new Date(encounter.date || encounter.createdAt).toLocaleDateString()} - {encounter.status || 'draft'}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Notes Section */}
        {quickNotesCount > 0 && (
          <div className="mt-8 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-orange-600" />
                Quick Notes
              </h3>
              <button
                onClick={() => setShowQuickNotesView(true)}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View All ({quickNotesCount})
                <ChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>
            <p className="text-sm text-gray-600">
              {quickNotesCount} clinical note{quickNotesCount !== 1 ? 's' : ''} recorded for this patient
            </p>
          </div>
        )}
      </div>

      {/* New Episode Modal */}
      {showNewEpisodeModal && (
        <NewEpisodeModal
          patientId={patientId}
          onClose={() => setShowNewEpisodeModal(false)}
          onSuccess={() => {
            setShowNewEpisodeModal(false);
            // Refresh episodes list
            const updatedEpisodes = getPatientEpisodes(patientId, true);
            setEpisodes(updatedEpisodes);
          }}
        />
      )}
      
      {/* All Records Modal */}
      {showAllRecordsModal && (
        <AllRecordsView
          patient={patient}
          onClose={() => setShowAllRecordsModal(false)}
        />
      )}
      
      {/* Quick Note Modal */}
      {showQuickNoteModal && (
        <QuickNoteModal
          patient={patient}
          onClose={() => setShowQuickNoteModal(false)}
          onSave={handleSaveQuickNote}
        />
      )}
      
      {/* Quick Notes View */}
      {showQuickNotesView && (
        <QuickNotesView
          patient={patient}
          onClose={() => setShowQuickNotesView(false)}
        />
      )}
      </div>
    </DashboardLayout>
  );
};

export default PatientDashboard;