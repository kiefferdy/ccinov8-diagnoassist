import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Users, Clock, ChartBar, ArrowRight, Plus, Calendar,
  Bell, TrendingUp, FileText, AlertCircle, CheckCircle, 
  Stethoscope, Heart, Brain, Sparkles, ChevronRight, Sun,
  Coffee, Moon, UserCheck, Timer, Award, Filter,
  StickyNote, X, Edit2, Trash2, Save
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { StorageManager } from '../../utils/storage';
import DashboardLayout from '../Layout/DashboardLayout';
import './dashboard-animations.css';

const DoctorDashboard = () => {
  const navigate = useNavigate();
  const { patients } = usePatient();
  const { episodes } = useEpisode();
  const { encounters } = useEncounter();
  
  const [timeOfDay, setTimeOfDay] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('all');
  const [appointments, setAppointments] = useState([]);
  const [notes, setNotes] = useState([]);
  const [newNoteText, setNewNoteText] = useState('');
  const [showAddNote, setShowAddNote] = useState(false);
  
  // Load appointments and notes
  useEffect(() => {
    const storedAppointments = StorageManager.getScheduledAppointments();
    setAppointments(storedAppointments);
    
    // Load notes from localStorage
    const storedNotes = localStorage.getItem('doctor_notes');
    if (storedNotes) {
      setNotes(JSON.parse(storedNotes));
    }
  }, []);
  
  // Mock doctor data - in real app would come from auth context
  const doctor = {
    name: 'Dr. Sarah Chen',
    specialty: 'Internal Medicine',
    yearsOfExperience: 12,
    patientsToday: 8,
    completedToday: 5
  };
  
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now);
      
      const hour = now.getHours();
      if (hour < 12) setTimeOfDay('morning');
      else if (hour < 17) setTimeOfDay('afternoon');
      else setTimeOfDay('evening');
    };
    
    updateTime();
    const interval = setInterval(updateTime, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, []);
  
  // Calculate stats
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  const todayEnd = new Date();
  todayEnd.setHours(23, 59, 59, 999);
  
  const todaysEncounters = encounters?.filter(e => 
    new Date(e.date) >= todayStart
  ) || [];
  
  const pendingDocumentation = encounters?.filter(e => 
    e.status !== 'signed' && new Date(e.date) >= todayStart
  ).length || 0;
  
  const activeEpisodes = episodes?.filter(e => e.status === 'active').length || 0;
  
  // Calculate appointment stats
  const todaysAppointments = appointments.filter(apt => {
    const aptDate = new Date(apt.date);
    return aptDate >= todayStart && aptDate <= todayEnd;
  });
  
  const scheduledAppointments = todaysAppointments.filter(apt => 
    apt.status === 'scheduled' || apt.status === 'confirmed'
  ).length;
  
  const completedAppointments = todaysAppointments.filter(apt => 
    apt.status === 'completed'
  ).length;
  
  // Note management functions
  const addNote = () => {
    if (newNoteText.trim()) {
      const newNote = {
        id: Date.now(),
        text: newNoteText.trim(),
        color: ['yellow', 'blue', 'green', 'pink', 'purple'][Math.floor(Math.random() * 5)],
        createdAt: new Date().toISOString()
      };
      const updatedNotes = [...notes, newNote];
      setNotes(updatedNotes);
      localStorage.setItem('doctor_notes', JSON.stringify(updatedNotes));
      setNewNoteText('');
      setShowAddNote(false);
    }
  };

  const deleteNote = (id) => {
    const updatedNotes = notes.filter(note => note.id !== id);
    setNotes(updatedNotes);
    localStorage.setItem('doctor_notes', JSON.stringify(updatedNotes));
  };

  const updateNote = (id, newText) => {
    const updatedNotes = notes.map(note => 
      note.id === id ? { ...note, text: newText } : note
    );
    setNotes(updatedNotes);
    localStorage.setItem('doctor_notes', JSON.stringify(updatedNotes));
  };
  
  // Get recent patients with filtering
  const recentPatients = (encounters || [])
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .map(encounter => {
      const episode = episodes?.find(e => e.id === encounter.episodeId);
      const patient = patients?.find(p => p.id === (encounter.patientId || episode?.patientId));
      return { encounter, episode, patient };
    })
    .filter(item => {
      if (!item.patient || !item.episode) return false;
      if (selectedStatusFilter === 'all') return true;
      return item.encounter.status === selectedStatusFilter;
    })
    .slice(0, 10); // Show up to 10 patients  
  const getGreeting = () => {
    const greetings = {
      morning: { icon: Coffee, text: 'Good morning' },
      afternoon: { icon: Sun, text: 'Good afternoon' },
      evening: { icon: Moon, text: 'Good evening' }
    };
    return greetings[timeOfDay] || greetings.morning;
  };
  
  const greeting = getGreeting();
  const GreetingIcon = greeting.icon;
  
  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 animate-fadeIn">
        {/* Animated Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />
        </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl text-white">
                  <GreetingIcon className="w-8 h-8" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                    {greeting.text}, {doctor.name}
                    <Sparkles className="w-5 h-5 ml-2 text-yellow-500" />
                  </h1>
                  <p className="text-gray-600 mt-1">
                    {currentTime.toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </p>
                </div>
              </div>
              
              <button
                onClick={() => navigate('/patients')}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span className="font-medium">New Patient</span>
              </button>
            </div>
          </div>
        </div>        
        {/* Today's Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Appointments Today</p>
                <div className="flex items-baseline space-x-2 mt-2">
                  <p className="text-3xl font-bold text-gray-900">{completedAppointments}</p>
                  <p className="text-lg text-gray-500">/ {todaysAppointments.length}</p>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${todaysAppointments.length > 0 ? (completedAppointments / todaysAppointments.length) * 100 : 0}%` }}
                  />
                </div>
              </div>
              <div className="p-3 bg-green-100 rounded-xl">
                <UserCheck className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Documentation</p>
                <p className="text-3xl font-bold text-orange-600 mt-2">{pendingDocumentation}</p>
                <p className="text-xs text-gray-500 mt-1">Requires attention</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-xl">
                <FileText className="w-8 h-8 text-orange-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Episodes</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{activeEpisodes}</p>
                <p className="text-xs text-gray-500 mt-1">Ongoing care</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-xl">
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Documentation Time</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">6.2</p>
                <p className="text-xs text-gray-500 mt-1">minutes per encounter</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-xl">
                <Timer className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </div>
        </div>        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Quick Actions & Upcoming Appointments */}
          <div className="lg:col-span-1 space-y-6 flex flex-col">
            {/* Quick Actions */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                Quick Actions
              </h2>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/patients')}
                  className="w-full p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 flex items-center justify-between group"
                >
                  <div className="flex items-center space-x-3">
                    <Plus className="w-5 h-5" />
                    <span className="font-medium">New Patient Visit</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button
                  onClick={() => navigate('/patients')}
                  className="w-full p-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-300 flex items-center justify-between group"
                >
                  <div className="flex items-center space-x-3">
                    <Users className="w-5 h-5" />
                    <span className="font-medium">View All Patients</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button 
                  onClick={() => navigate('/schedule')}
                  className="w-full p-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-300 flex items-center justify-between group">
                  <div className="flex items-center space-x-3">
                    <Calendar className="w-5 h-5" />
                    <span className="font-medium">Today's Schedule</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
            
            {/* Upcoming Appointments */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                Upcoming Appointments
              </h3>
              <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar-light">
                {appointments
                  .filter(apt => {
                    const aptDate = new Date(apt.date);
                    const now = new Date();
                    return aptDate >= now && (apt.status === 'scheduled' || apt.status === 'confirmed');
                  })
                  .sort((a, b) => new Date(a.date) - new Date(b.date))
                  .slice(0, 5)
                  .map((appointment, index) => {
                    const patient = patients?.find(p => p.id === appointment.patientId);
                    if (!patient) return null;
                    const aptDate = new Date(appointment.date);
                    const isToday = aptDate.toDateString() === new Date().toDateString();
                    const isTomorrow = aptDate.toDateString() === new Date(Date.now() + 86400000).toDateString();
                    
                    return (
                      <div 
                        key={appointment.id}
                        className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors cursor-pointer animate-slideInLeft border border-gray-200"
                        style={{ animationDelay: `${index * 0.1}s` }}
                        onClick={() => navigate('/schedule')}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-sm text-gray-900">{patient.demographics.name}</p>
                            <p className="text-xs text-gray-600">
                              {isToday ? 'Today' : isTomorrow ? 'Tomorrow' : aptDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} at {appointment.time}
                            </p>
                            <p className="text-xs text-gray-500 capitalize">{appointment.type}</p>
                          </div>
                          <div className={`px-2 py-1 rounded-full text-xs whitespace-nowrap ml-2 ${
                            appointment.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {appointment.status}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                {appointments.filter(apt => {
                  const aptDate = new Date(apt.date);
                  const now = new Date();
                  return aptDate >= now && (apt.status === 'scheduled' || apt.status === 'confirmed');
                }).length === 0 && (
                  <div className="text-center py-8">
                    <Calendar className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm text-gray-500">No upcoming appointments</p>
                  </div>
                )}
              </div>
              {appointments.filter(apt => {
                const aptDate = new Date(apt.date);
                const now = new Date();
                return aptDate >= now && (apt.status === 'scheduled' || apt.status === 'confirmed');
              }).length > 5 && (
                <button 
                  onClick={() => navigate('/schedule')}
                  className="mt-4 w-full text-center text-sm text-blue-600 hover:text-blue-700 transition-colors font-medium"
                >
                  View all appointments →
                </button>
              )}
            </div>
          </div>          
          {/* Middle & Right Columns - Recent Patients */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 h-full flex flex-col">
              <div className="p-6 border-b border-gray-100 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-gray-900 flex items-center">
                    <Users className="w-5 h-5 mr-2 text-blue-600" />
                    Recent Patients
                    {recentPatients.length > 0 && (
                      <span className="ml-2 text-sm font-normal text-gray-500">
                        ({recentPatients.length})
                      </span>
                    )}
                  </h2>
                  <select
                    value={selectedStatusFilter}
                    onChange={(e) => setSelectedStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Status</option>
                    <option value="completed">Completed</option>
                    <option value="in-progress">In Progress</option>
                    <option value="pending">Pending</option>
                    <option value="signed">Signed</option>
                  </select>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto custom-scrollbar-light" style={{ maxHeight: '420px' }}>
                <div className="divide-y divide-gray-100">
                {recentPatients.length > 0 ? (
                  <>
                    {recentPatients.map(({ patient, episode, encounter }) => (
                    <div
                      key={encounter.id}
                      className="p-6 hover:bg-gray-50 transition-colors cursor-pointer group"
                      onClick={() => navigate(`/patient/${patient.id}/episode/${episode.id}`)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                            {patient.demographics?.name?.charAt(0).toUpperCase() || '?'}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                              {patient.demographics?.name || 'Unknown Patient'}
                            </h3>
                            <div className="flex items-center space-x-4 mt-1">
                              <span className="text-sm text-gray-600">
                                {episode.chiefComplaint}
                              </span>
                              <span className="text-xs text-gray-400">
                                {new Date(encounter.date).toLocaleTimeString('en-US', {
                                  hour: 'numeric',
                                  minute: '2-digit',
                                  hour12: true
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          {encounter.status === 'signed' ? (
                            <span className="flex items-center text-green-600 text-sm">
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Completed
                            </span>
                          ) : (
                            <span className="flex items-center text-orange-600 text-sm">
                              <AlertCircle className="w-4 h-4 mr-1" />
                              Pending
                            </span>
                          )}
                          <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
                        </div>
                      </div>
                    </div>
                  ))}
                    {/* Empty space filler when there are few patients */}
                    {recentPatients.length <= 5 && (
                      <div className="p-6 text-center border-t border-gray-100">
                        <div className="text-gray-400 text-sm">
                          <p className="mb-2">— End of list —</p>
                          {selectedStatusFilter !== 'all' && (
                            <button
                              onClick={() => setSelectedStatusFilter('all')}
                              className="text-blue-600 hover:text-blue-700 text-xs"
                            >
                              Show all status
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-12 text-center">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">
                      {selectedStatusFilter === 'all' 
                        ? 'No patient visits recorded yet' 
                        : `No patients with "${selectedStatusFilter}" status`}
                    </p>
                    <button
                      onClick={() => navigate('/patients')}
                      className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Start seeing patients →
                    </button>
                  </div>
                )}
                </div>
              </div>
              
              {recentPatients.length > 0 && (
                <div className="p-4 border-t border-gray-100 flex-shrink-0">
                  <button
                    onClick={() => navigate('/patients')}
                    className="w-full text-center text-blue-600 hover:text-blue-700 font-medium transition-colors"
                  >
                    View all patients →
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>        
        {/* Notes Section */}
        <div className="mt-8">
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-6 border border-yellow-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-yellow-100 rounded-xl">
                  <StickyNote className="w-6 h-6 text-yellow-700" />
                </div>
                <h3 className="font-bold text-gray-900">Quick Notes</h3>
              </div>
              <button
                onClick={() => setShowAddNote(true)}
                className="flex items-center gap-2 px-3 py-1.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-all text-sm font-medium"
              >
                <Plus className="w-4 h-4" />
                Add Note
              </button>
            </div>
            
            {/* Notes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Add New Note Card */}
              {showAddNote && (
                <div className="bg-white rounded-lg shadow-md p-4 border-2 border-dashed border-yellow-300">
                  <textarea
                    value={newNoteText}
                    onChange={(e) => setNewNoteText(e.target.value)}
                    placeholder="Type your note here..."
                    className="w-full h-32 p-2 text-sm resize-none border-none outline-none"
                    autoFocus
                  />
                  <div className="flex justify-end gap-2 mt-2">
                    <button
                      onClick={() => {
                        setShowAddNote(false);
                        setNewNoteText('');
                      }}
                      className="px-3 py-1 text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={addNote}
                      className="px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                    >
                      Save
                    </button>
                  </div>
                </div>
              )}
              
              {/* Existing Notes */}
              {notes.map((note) => (
                <div
                  key={note.id}
                  className={`relative rounded-lg shadow-md p-4 transform hover:rotate-1 transition-all duration-200 sticky-note ${
                    note.color === 'yellow' ? 'note-yellow' :
                    note.color === 'blue' ? 'note-blue' :
                    note.color === 'green' ? 'note-green' :
                    note.color === 'pink' ? 'note-pink' :
                    'note-purple'
                  }`}
                  style={{ minHeight: '150px' }}
                >
                  <button
                    onClick={() => deleteNote(note.id)}
                    className="absolute top-2 right-2 p-1 hover:bg-white/50 rounded transition-colors"
                  >
                    <X className="w-4 h-4 text-gray-600" />
                  </button>
                  <p className="text-sm text-gray-800 pr-6 whitespace-pre-wrap">{note.text}</p>
                  <p className="text-xs text-gray-500 mt-3">
                    {new Date(note.createdAt).toLocaleDateString()}
                  </p>
                </div>
              ))}
              
              {/* Empty State */}
              {notes.length === 0 && !showAddNote && (
                <div className="col-span-full text-center py-8 text-gray-500">
                  <StickyNote className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No notes yet. Click "Add Note" to create one.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      </div>
    </DashboardLayout>
  );
};

export default DoctorDashboard;