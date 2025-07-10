import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Users, Clock, ChartBar, ArrowRight, Plus, Calendar,
  Bell, TrendingUp, FileText, AlertCircle, CheckCircle, 
  Stethoscope, Heart, Brain, Sparkles, ChevronRight, Sun,
  Coffee, Moon, UserCheck, Timer, Target, Award, Filter
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import DashboardLayout from '../Layout/DashboardLayout';
import './dashboard-animations.css';

const DoctorDashboard = () => {
  const navigate = useNavigate();
  const { patients } = usePatient();
  const { episodes } = useEpisode();
  const { encounters } = useEncounter();
  
  const [timeOfDay, setTimeOfDay] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedTimeFilter, setSelectedTimeFilter] = useState('today');
  
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
  
  const todaysEncounters = encounters?.filter(e => 
    new Date(e.date) >= todayStart
  ) || [];
  
  const pendingDocumentation = encounters?.filter(e => 
    e.status !== 'signed' && new Date(e.date) >= todayStart
  ).length || 0;
  
  const activeEpisodes = episodes?.filter(e => e.status === 'active').length || 0;
  
  // Get recent patients (last 5 encounters)
  const recentPatients = (encounters || [])
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
    .map(encounter => {
      const episode = episodes?.find(e => e.id === encounter.episodeId);
      const patient = patients?.find(p => p.id === (encounter.patientId || episode?.patientId));
      return { encounter, episode, patient };
    })
    .filter(item => item.patient && item.episode);  
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
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
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
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Patients Today</p>
                <div className="flex items-baseline space-x-2 mt-2">
                  <p className="text-3xl font-bold text-gray-900">{doctor.completedToday}</p>
                  <p className="text-lg text-gray-500">/ {doctor.patientsToday}</p>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(doctor.completedToday / doctor.patientsToday) * 100}%` }}
                  />
                </div>
              </div>
              <div className="p-3 bg-green-100 rounded-xl">
                <UserCheck className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
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
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
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
          
          <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
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
          {/* Left Column - Quick Actions & Schedule */}
          <div className="lg:col-span-1 space-y-6">
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
                
                <button className="w-full p-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-300 flex items-center justify-between group">
                  <div className="flex items-center space-x-3">
                    <Calendar className="w-5 h-5" />
                    <span className="font-medium">Today's Schedule</span>
                  </div>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
            
            {/* Today's Progress */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg p-6 text-white">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Today's Progress
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Patients Seen</span>
                    <span className="text-sm font-bold">{doctor.completedToday}/{doctor.patientsToday}</span>
                  </div>
                  <div className="bg-white/20 rounded-full h-2">
                    <div 
                      className="bg-white h-2 rounded-full transition-all duration-500"
                      style={{ width: `${(doctor.completedToday / doctor.patientsToday) * 100}%` }}
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Documentation</span>
                    <span className="text-sm font-bold">
                      {todaysEncounters.length > 0 
                        ? `${((todaysEncounters.length - pendingDocumentation) / todaysEncounters.length * 100).toFixed(0)}%`
                        : '100%'
                      }
                    </span>
                  </div>
                  <div className="bg-white/20 rounded-full h-2">
                    <div 
                      className="bg-white h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: todaysEncounters.length > 0 
                          ? `${((todaysEncounters.length - pendingDocumentation) / todaysEncounters.length * 100)}%`
                          : '100%'
                      }}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-white/20">
                <div className="flex items-center justify-center">
                  <Award className="w-8 h-8 mr-2" />
                  <span className="font-bold">Great work today!</span>
                </div>
              </div>
            </div>
          </div>          
          {/* Middle & Right Columns - Recent Patients */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-gray-900 flex items-center">
                    <Clock className="w-5 h-5 mr-2 text-blue-600" />
                    Recent Patients
                  </h2>
                  <select
                    value={selectedTimeFilter}
                    onChange={(e) => setSelectedTimeFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                  </select>
                </div>
              </div>
              
              <div className="divide-y divide-gray-100">
                {recentPatients.length > 0 ? (
                  recentPatients.map(({ patient, episode, encounter }) => (
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
                  ))
                ) : (
                  <div className="p-12 text-center">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">No patient visits yet today</p>
                    <button
                      onClick={() => navigate('/patients')}
                      className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Start seeing patients →
                    </button>
                  </div>
                )}
              </div>
              
              {recentPatients.length > 0 && (
                <div className="p-4 border-t border-gray-100">
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
        {/* Notifications/Alerts Section */}
        <div className="mt-8">
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-6 border border-yellow-200">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-yellow-100 rounded-xl">
                <Bell className="w-6 h-6 text-yellow-700" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-gray-900 mb-2">Important Reminders</h3>
                <div className="space-y-2">
                  {pendingDocumentation > 0 && (
                    <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                      <div className="flex items-center space-x-3">
                        <AlertCircle className="w-5 h-5 text-orange-600" />
                        <span className="text-sm text-gray-700">
                          You have {pendingDocumentation} unsigned encounters that need documentation
                        </span>
                      </div>
                      <button 
                        onClick={() => navigate('/patients')}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Review
                      </button>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="w-5 h-5 text-blue-600" />
                      <span className="text-sm text-gray-700">
                        {activeEpisodes} active episodes require follow-up
                      </span>
                    </div>
                    <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                      View
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </DashboardLayout>
  );
};

export default DoctorDashboard;