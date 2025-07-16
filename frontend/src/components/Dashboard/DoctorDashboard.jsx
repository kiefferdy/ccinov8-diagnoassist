import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Users, Clock, ChartBar, ArrowRight, Plus, Calendar,
  Bell, TrendingUp, FileText, AlertCircle, CheckCircle, 
  Stethoscope, Heart, Brain, Sparkles, ChevronRight, Sun,
  Coffee, Moon, UserCheck, Timer, Award, Filter,
  StickyNote, X, Edit2, Trash2, Save, BarChart3, Zap,
  Target, TrendingDown, Star, Briefcase
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
  const [hoveredCard, setHoveredCard] = useState(null);
  
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
    completedToday: 5,
    rating: 4.8,
    totalPatients: 1247
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
  
  const pendingDocumentation = encounters?.filter(e => 
    e.status !== 'signed' && new Date(e.date) >= todayStart
  ).length || 0;
  
  const activeEpisodes = episodes?.filter(e => e.status === 'active').length || 0;
  
  // Calculate appointment stats
  const todaysAppointments = appointments.filter(apt => {
    const aptDate = new Date(apt.date);
    return aptDate >= todayStart && aptDate <= todayEnd;
  });
  
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
      morning: { icon: Coffee, text: 'Good morning', emoji: '☀️' },
      afternoon: { icon: Sun, text: 'Good afternoon', emoji: '🌤️' },
      evening: { icon: Moon, text: 'Good evening', emoji: '🌙' }
    };
    return greetings[timeOfDay] || greetings.morning;
  };
  
  const greeting = getGreeting();
  const GreetingIcon = greeting.icon;
  
  // Performance metrics
  const avgConsultTime = 15.3; // minutes
  const patientSatisfaction = 94; // percentage
  
  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/50 to-violet-50/50 animate-fadeIn">
        {/* Enhanced Animated Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-blue-400 to-cyan-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-br from-purple-400 to-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-400 to-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />
        </div>      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Enhanced Header Section */}
        <div className="mb-8">
          <div className="glass bg-white/80 rounded-3xl shadow-2xl p-8 border border-white/20 hover-lift">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl text-white shadow-xl animate-float">
                    <GreetingIcon className="w-10 h-10" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 text-2xl animate-bounce-subtle">{greeting.emoji}</div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                    <span className="gradient-text">{greeting.text}, {doctor.name}</span>
                    <Sparkles className="w-6 h-6 ml-3 text-yellow-500 animate-pulse" />
                  </h1>
                  <p className="text-gray-600 mt-2 flex items-center gap-4">
                    <span>{currentTime.toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}</span>
                    <span className="text-sm bg-gradient-to-r from-blue-100 to-indigo-100 px-3 py-1 rounded-full text-blue-700 font-medium">
                      {doctor.specialty} • {doctor.yearsOfExperience} years
                    </span>
                  </p>
                </div>
              </div>              
              <div className="flex items-center gap-4">
                <div className="hidden lg:flex items-center gap-6 mr-6">
                  <div className="text-center">
                    <div className="flex items-center gap-1">
                      <Star className="w-5 h-5 text-yellow-500 fill-current" />
                      <span className="text-2xl font-bold text-gray-900">{doctor.rating}</span>
                    </div>
                    <p className="text-xs text-gray-600">Rating</p>
                  </div>
                  <div className="h-12 w-px bg-gray-300" />
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{doctor.totalPatients.toLocaleString()}</p>
                    <p className="text-xs text-gray-600">Total Patients</p>
                  </div>
                </div>
                <button
                  onClick={() => navigate('/patients')}
                  className="group px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:scale-105 flex items-center space-x-2 card-hover-gradient"
                >
                  <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
                  <span className="font-medium">New Patient</span>
                </button>
              </div>
            </div>
          </div>
        </div>        
        {/* Enhanced Today's Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div 
            className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 p-6 border border-white/20 dashboard-card hover-lift group"
            onMouseEnter={() => setHoveredCard('appointments')}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Appointments Today
                </p>
                <div className="flex items-baseline space-x-2 mt-3">
                  <p className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                    {completedAppointments}
                  </p>
                  <p className="text-xl text-gray-500">/ {todaysAppointments.length}</p>
                </div>
                <div className="mt-3 bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-emerald-600 h-3 rounded-full transition-all duration-1000 shimmer"
                    style={{ width: `${todaysAppointments.length > 0 ? (completedAppointments / todaysAppointments.length) * 100 : 0}%` }}
                  />
                </div>
                {hoveredCard === 'appointments' && (
                  <p className="text-xs text-gray-500 mt-2 animate-fadeIn">
                    {todaysAppointments.length - completedAppointments} remaining today
                  </p>
                )}
              </div>
              <div className="p-4 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                <UserCheck className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>          
          <div 
            className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 p-6 border border-white/20 dashboard-card hover-lift group"
            onMouseEnter={() => setHoveredCard('documentation')}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  Pending Documentation
                </p>
                <p className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mt-3">
                  {pendingDocumentation}
                </p>
                <p className="text-xs text-gray-500 mt-2">Requires attention</p>
                {hoveredCard === 'documentation' && pendingDocumentation > 0 && (
                  <div className="mt-3 animate-fadeIn">
                    <div className="h-1 bg-orange-200 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full animate-pulse" style={{width: '60%'}} />
                    </div>
                  </div>
                )}
              </div>
              <div className="p-4 bg-gradient-to-br from-orange-100 to-red-100 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-8 h-8 text-orange-600" />
              </div>
            </div>
          </div>          
          <div 
            className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 p-6 border border-white/20 dashboard-card hover-lift group"
            onMouseEnter={() => setHoveredCard('episodes')}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Active Episodes
                </p>
                <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mt-3">
                  {activeEpisodes}
                </p>
                <p className="text-xs text-gray-500 mt-2">Ongoing care</p>
                {hoveredCard === 'episodes' && (
                  <div className="mt-3 flex items-center gap-2 animate-fadeIn">
                    <Activity className="w-3 h-3 text-blue-500 animate-pulse" />
                    <span className="text-xs text-blue-600">Active monitoring</span>
                  </div>
                )}
              </div>
              <div className="p-4 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>          
          <div 
            className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 p-6 border border-white/20 dashboard-card hover-lift group"
            onMouseEnter={() => setHoveredCard('performance')}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Timer className="w-4 h-4" />
                  Avg. Documentation Time
                </p>
                <div className="flex items-baseline gap-1 mt-3">
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    6.2
                  </p>
                  <p className="text-lg text-gray-500">min</p>
                </div>
                <p className="text-xs text-gray-500 mt-2">per encounter</p>
                {hoveredCard === 'performance' && (
                  <div className="mt-3 animate-fadeIn">
                    <div className="flex items-center gap-1 text-xs">
                      <TrendingDown className="w-3 h-3 text-green-500" />
                      <span className="text-green-600">15% faster than average</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="p-4 bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                <Timer className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </div>
        </div>        
        {/* Performance Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-3 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl p-1 shadow-xl">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6">
              <div className="flex items-center justify-between flex-wrap gap-6">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-6 h-6 text-indigo-600" />
                  <h3 className="text-lg font-bold text-gray-900">Today's Performance</h3>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-indigo-600">{avgConsultTime}</p>
                    <p className="text-xs text-gray-600">Avg. Consult (min)</p>
                  </div>
                  <div className="h-12 w-px bg-gray-300" />
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{patientSatisfaction}%</p>
                    <p className="text-xs text-gray-600">Satisfaction</p>
                  </div>
                  <div className="h-12 w-px bg-gray-300" />
                  <div className="text-center">
                    <div className="flex items-center gap-1 justify-center">
                      <Briefcase className="w-5 h-5 text-purple-600" />
                      <p className="text-2xl font-bold text-purple-600">{completedAppointments + 3}</p>
                    </div>
                    <p className="text-xs text-gray-600">Total Consultations</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Quick Actions & Upcoming Appointments */}
          <div className="lg:col-span-1 space-y-6 flex flex-col">
            {/* Enhanced Quick Actions */}
            <div className="glass bg-white/90 rounded-3xl shadow-xl p-6 border border-white/20 hover-lift">
              <h2 className="text-lg font-bold text-gray-900 mb-5 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-blue-600 animate-pulse" />
                Quick Actions
              </h2>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/patients')}
                  className="w-full p-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 flex items-center justify-between group shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white/20 rounded-xl group-hover:scale-110 transition-transform">
                      <Plus className="w-5 h-5" />
                    </div>
                    <span className="font-medium">New Patient Visit</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>                
                <button
                  onClick={() => navigate('/patients')}
                  className="w-full p-4 glass-dark bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-2xl transition-all duration-300 flex items-center justify-between group border border-gray-200 hover:border-gray-300 hover:shadow-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gray-200 rounded-xl group-hover:bg-gray-300 transition-colors">
                      <Users className="w-5 h-5 text-gray-700" />
                    </div>
                    <span className="font-medium">View All Patients</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button 
                  onClick={() => navigate('/schedule')}
                  className="w-full p-4 glass-dark bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-2xl transition-all duration-300 flex items-center justify-between group border border-gray-200 hover:border-gray-300 hover:shadow-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gray-200 rounded-xl group-hover:bg-gray-300 transition-colors">
                      <Calendar className="w-5 h-5 text-gray-700" />
                    </div>
                    <span className="font-medium">Today's Schedule</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>            
            {/* Enhanced Upcoming Appointments */}
            <div className="glass bg-white/90 rounded-3xl shadow-xl p-6 border border-white/20 hover-lift">
              <h3 className="text-lg font-bold mb-5 flex items-center justify-between">
                <span className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                  Upcoming Appointments
                </span>
                <span className="text-sm font-normal text-gray-500">Next 5</span>
              </h3>
              <div className="space-y-3 max-h-72 overflow-y-auto custom-scrollbar-light">
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
                        className="glass-dark bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-4 hover:from-blue-50 hover:to-indigo-50 transition-all cursor-pointer animate-slideInLeft border border-gray-200 hover:border-blue-300 hover:shadow-md group"
                        style={{ animationDelay: `${index * 0.1}s` }}
                        onClick={() => navigate('/schedule')}
                      >                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
                              {patient.demographics.name}
                            </p>
                            <div className="flex items-center gap-3 mt-1">
                              <p className="text-sm text-gray-600">
                                <Clock className="w-3 h-3 inline mr-1" />
                                {isToday ? 'Today' : isTomorrow ? 'Tomorrow' : aptDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} at {appointment.time}
                              </p>
                            </div>
                            <p className="text-xs text-gray-500 capitalize mt-1">{appointment.type}</p>
                          </div>
                          <div className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap ml-2 ${
                            appointment.status === 'confirmed' 
                              ? 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border border-green-200' 
                              : 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border border-blue-200'
                          }`}>
                            {appointment.status}
                          </div>
                        </div>
                      </div>
                    );
                  })}                {appointments.filter(apt => {
                  const aptDate = new Date(apt.date);
                  const now = new Date();
                  return aptDate >= now && (apt.status === 'scheduled' || apt.status === 'confirmed');
                }).length === 0 && (
                  <div className="text-center py-12">
                    <div className="relative">
                      <Calendar className="w-16 h-16 mx-auto mb-3 text-gray-300" />
                      <div className="absolute -bottom-1 -right-1/3 transform translate-x-1/2">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                          <Plus className="w-4 h-4 text-blue-600" />
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500">No upcoming appointments</p>
                    <button 
                      onClick={() => navigate('/schedule')}
                      className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Schedule appointments →
                    </button>
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
                  className="mt-4 w-full text-center text-sm text-blue-600 hover:text-blue-700 transition-colors font-medium py-2 hover:bg-blue-50 rounded-xl"
                >
                  View all appointments →
                </button>
              )}
            </div>
          </div>          
          {/* Middle & Right Columns - Enhanced Recent Patients */}
          <div className="lg:col-span-2">
            <div className="glass bg-white/90 rounded-3xl shadow-xl border border-white/20 flex flex-col hover-lift" style={{ height: '730px' }}>
              <div className="p-6 border-b border-gray-200 flex-shrink-0 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-3xl">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900 flex items-center">
                    <Users className="w-6 h-6 mr-2 text-blue-600" />
                    Recent Patients
                    {recentPatients.length > 0 && (
                      <span className="ml-3 px-3 py-1 text-sm font-normal bg-blue-100 text-blue-700 rounded-full">
                        {recentPatients.length} visits
                      </span>
                    )}
                  </h2>
                  <select
                    value={selectedStatusFilter}
                    onChange={(e) => setSelectedStatusFilter(e.target.value)}
                    className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm hover:border-gray-400 transition-colors"
                  >
                    <option value="all">All Status</option>
                    <option value="completed">✓ Completed</option>
                    <option value="in-progress">⏳ In Progress</option>
                    <option value="pending">⚡ Pending</option>
                    <option value="signed">📝 Signed</option>
                  </select>
                </div>
              </div>              
              <div className="flex-1 overflow-y-auto custom-scrollbar-light">
                <div className="divide-y divide-gray-100">
                {recentPatients.length > 0 ? (
                  recentPatients.map(({ patient, episode, encounter }, index) => (
                    <div
                      key={encounter.id}
                      className="p-6 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-indigo-50/50 transition-all cursor-pointer group animate-fadeIn"
                      style={{ animationDelay: `${index * 0.05}s` }}
                      onClick={() => navigate(`/patient/${patient.id}/episode/${episode.id}`)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="relative">
                            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:scale-110 transition-transform">
                              {patient.demographics?.name?.charAt(0).toUpperCase() || '?'}
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors text-lg">
                              {patient.demographics?.name || 'Unknown Patient'}
                            </h3>
                            <div className="flex items-center space-x-4 mt-1">
                              <span className="text-sm text-gray-600 flex items-center gap-1">
                                <Stethoscope className="w-4 h-4" />
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
                            <span className="flex items-center text-green-600 text-sm bg-green-50 px-3 py-1 rounded-full border border-green-200">
                              <CheckCircle className="w-4 h-4 mr-1.5" />
                              Completed
                            </span>
                          ) : (
                            <span className="flex items-center text-orange-600 text-sm bg-orange-50 px-3 py-1 rounded-full border border-orange-200">
                              <AlertCircle className="w-4 h-4 mr-1.5 animate-pulse" />
                              Pending
                            </span>
                          )}
                          <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-16 text-center">
                    <div className="relative inline-block">
                      <Users className="w-20 h-20 text-gray-300 mx-auto mb-4" />
                      <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Plus className="w-5 h-5 text-blue-600" />
                      </div>
                    </div>
                    <p className="text-gray-500 text-lg">
                      {selectedStatusFilter === 'all' 
                        ? 'No patient visits recorded yet' 
                        : `No patients with "${selectedStatusFilter}" status`}
                    </p>
                    <button
                      onClick={() => navigate('/patients')}
                      className="mt-4 text-blue-600 hover:text-blue-700 font-medium hover:underline"
                    >
                      Start seeing patients →
                    </button>
                  </div>
                )}
                </div>
              </div>              
              {/* Enhanced Bottom section */}
              <div className="flex-shrink-0 flex flex-col items-center justify-center p-4 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 rounded-b-3xl">
                {recentPatients.length > 0 && recentPatients.length <= 5 && (
                  <div className="text-gray-400 text-sm mb-3 flex items-center gap-2">
                    <div className="h-px w-12 bg-gray-300" />
                    <span>End of list</span>
                    <div className="h-px w-12 bg-gray-300" />
                  </div>
                )}
                {recentPatients.length > 0 && (
                  <button
                    onClick={() => navigate('/patients')}
                    className="text-blue-600 hover:text-blue-700 font-medium transition-colors hover:bg-blue-50 px-4 py-2 rounded-xl"
                  >
                    View all patients →
                  </button>
                )}
                {recentPatients.length <= 5 && selectedStatusFilter !== 'all' && (
                  <button
                    onClick={() => setSelectedStatusFilter('all')}
                    className="text-blue-600 hover:text-blue-700 text-xs mt-2 hover:underline"
                  >
                    Show all status
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>        
        {/* Enhanced Notes Section */}
        <div className="mt-8">
          <div className="bg-gradient-to-br from-yellow-50 via-orange-50 to-pink-50 rounded-3xl shadow-xl p-8 border border-yellow-200/50 hover-lift">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl shadow-lg">
                  <StickyNote className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Quick Notes</h3>
                  <p className="text-sm text-gray-600">Capture important reminders</p>
                </div>
              </div>
              <button
                onClick={() => setShowAddNote(true)}
                className="group flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform" />
                Add Note
              </button>
            </div>
            
            {/* Notes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {/* Add New Note Card */}
              {showAddNote && (
                <div className="bg-white rounded-2xl shadow-lg p-5 border-2 border-dashed border-yellow-300 animate-scaleIn">
                  <textarea
                    value={newNoteText}
                    onChange={(e) => setNewNoteText(e.target.value)}
                    placeholder="Type your note here..."
                    className="w-full h-32 p-2 text-sm resize-none border-none outline-none bg-transparent"
                    autoFocus
                  />
                  <div className="flex justify-end gap-2 mt-3">
                    <button
                      onClick={() => {
                        setShowAddNote(false);
                        setNewNoteText('');
                      }}
                      className="px-3 py-1.5 text-gray-600 hover:text-gray-800 transition-colors hover:bg-gray-100 rounded-lg"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={addNote}
                      className="px-3 py-1.5 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-all shadow-md hover:shadow-lg"
                    >
                      Save
                    </button>
                  </div>
                </div>
              )}              
              {/* Existing Notes */}
              {notes.map((note, index) => (
                <div
                  key={note.id}
                  className={`relative rounded-2xl shadow-lg p-5 transform hover:rotate-1 hover:scale-105 transition-all duration-200 sticky-note animate-fadeIn ${
                    note.color === 'yellow' ? 'note-yellow' :
                    note.color === 'blue' ? 'note-blue' :
                    note.color === 'green' ? 'note-green' :
                    note.color === 'pink' ? 'note-pink' :
                    'note-purple'
                  }`}
                  style={{ 
                    minHeight: '160px',
                    animationDelay: `${index * 0.1}s`
                  }}
                >
                  <button
                    onClick={() => deleteNote(note.id)}
                    className="absolute top-3 right-3 p-1.5 hover:bg-white/50 rounded-lg transition-colors group"
                  >
                    <X className="w-4 h-4 text-gray-600 group-hover:text-gray-800" />
                  </button>
                  <p className="text-sm text-gray-800 pr-8 whitespace-pre-wrap leading-relaxed">{note.text}</p>
                  <p className="text-xs text-gray-600 mt-4 font-medium">
                    {new Date(note.createdAt).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              ))}
              
              {/* Empty State */}
              {notes.length === 0 && !showAddNote && (
                <div className="col-span-full text-center py-16">
                  <div className="relative inline-block">
                    <StickyNote className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <Plus className="w-5 h-5 text-yellow-600" />
                    </div>
                  </div>
                  <p className="text-gray-500">No notes yet. Click "Add Note" to create one.</p>
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