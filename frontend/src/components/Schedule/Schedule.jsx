import React, { useState, useEffect } from 'react';
import { 
  Calendar, Clock, User, MapPin, Phone, Mail, 
  ChevronLeft, ChevronRight, Plus, Search, Filter,
  AlertCircle, CheckCircle, MoreHorizontal,
  Building, Edit, Trash2, Calendar as CalendarIcon,
  Activity, FileText, Pill, Heart, Brain, Zap,
  TrendingUp, BarChart3, FileCheck
} from 'lucide-react';
import DashboardLayout from '../Layout/DashboardLayout';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { StorageManager } from '../../utils/storage';
import NewAppointmentModal from './NewAppointmentModal';
import AppointmentDetailsModal from './AppointmentDetailsModal';
import WeeklyCalendar from './WeeklyCalendar';
import './schedule-animations.css';

const Schedule = () => {
  const { patients } = usePatient();
  const { episodes } = useEpisode();
  const { encounters } = useEncounter();
  const [appointments, setAppointments] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('week'); // 'day', 'week', 'month'
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  // Calculate completed encounters this week
  const getCompletedEncountersThisWeek = () => {
    const weekStart = new Date();
    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
    weekStart.setHours(0, 0, 0, 0);
    
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 7);
    
    return encounters.filter(enc => {
      const encDate = new Date(enc.date);
      return enc.status === 'completed' && encDate >= weekStart && encDate < weekEnd;
    }).length;
  };

  // Load appointments from localStorage
  useEffect(() => {
    const storedAppointments = StorageManager.getScheduledAppointments();
    if (storedAppointments.length === 0) {
      // Initialize with sample data
      const sampleAppointments = generateSampleAppointments();
      StorageManager.saveScheduledAppointments(sampleAppointments);
      setAppointments(sampleAppointments);
    } else {
      setAppointments(storedAppointments);
    }
  }, []);

  // Generate sample appointments
  const generateSampleAppointments = () => {
    if (!patients || patients.length === 0) {
      return [];
    }
    
    const statuses = ['scheduled', 'confirmed', 'completed', 'cancelled'];
    const types = ['consultation', 'follow-up', 'procedure', 'check-up'];
    const reasons = [
      'Annual physical examination',
      'Follow-up: Hypertension management',
      'Diabetes consultation',
      'Post-surgery follow-up',
      'Vaccination',
      'Lab results review',
      'Medication adjustment',
      'Symptom evaluation',
      'Routine check-up',
      'Preventive care consultation'
    ];
    const appointments = [];
    
    // Generate appointments for the next 30 days
    for (let i = 0; i < 30; i++) {
      const numAppointments = Math.floor(Math.random() * 3) + 1;
      
      for (let j = 0; j < numAppointments; j++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        date.setHours(9 + Math.floor(Math.random() * 8)); // 9 AM to 5 PM
        date.setMinutes(Math.random() > 0.5 ? 0 : 30);
        
        const patient = patients[Math.floor(Math.random() * patients.length)];
        if (!patient) continue;
        
        // Get patient's active episode if any
        const patientEpisodes = episodes.filter(ep => ep.patientId === patient.id && ep.status === 'open');
        const hasActiveEpisode = patientEpisodes.length > 0;
        
        appointments.push({
          id: `APT-${Date.now()}-${i}-${j}`,
          patientId: patient.id,
          patientName: patient.demographics.name,
          date: date.toISOString(),
          time: date.toTimeString().slice(0, 5),
          duration: 30,
          type: types[Math.floor(Math.random() * types.length)],
          status: i < 0 ? 'completed' : statuses[Math.floor(Math.random() * 2)], // Past appointments are completed
          reason: reasons[Math.floor(Math.random() * reasons.length)],
          episodeId: hasActiveEpisode ? patientEpisodes[0].id : null,
          notes: hasActiveEpisode ? `Related to ongoing episode: ${patientEpisodes[0].chiefComplaint}` : '',
          room: `Room ${Math.floor(Math.random() * 10) + 1}`,
          createdAt: new Date().toISOString()
        });
      }
    }
    
    return appointments;
  };

  // Save appointment
  const saveAppointment = (appointmentData) => {
    const newAppointment = {
      ...appointmentData,
      id: `APT-${Date.now()}`,
      createdAt: new Date().toISOString()
    };
    
    const updatedAppointments = [...appointments, newAppointment];
    setAppointments(updatedAppointments);
    StorageManager.saveScheduledAppointments(updatedAppointments);
    setShowAddModal(false);
  };

  // Update appointment
  const updateAppointment = (id, updates) => {
    const updatedAppointments = appointments.map(apt =>
      apt.id === id ? { ...apt, ...updates } : apt
    );
    setAppointments(updatedAppointments);
    StorageManager.saveScheduledAppointments(updatedAppointments);
  };

  // Delete appointment
  const deleteAppointment = (id) => {
    const updatedAppointments = appointments.filter(apt => apt.id !== id);
    setAppointments(updatedAppointments);
    StorageManager.saveScheduledAppointments(updatedAppointments);
    setShowDetailsModal(false);
  };

  // Filter appointments
  const filteredAppointments = appointments.filter(appointment => {
    const matchesSearch = appointment.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         appointment.reason.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || appointment.status === filterStatus;
    const matchesType = selectedType === 'all' || appointment.type === selectedType;
    return matchesSearch && matchesStatus && matchesType;
  });

  // Get appointments for selected date
  const getAppointmentsForDate = (date) => {
    return filteredAppointments.filter(apt => {
      const aptDate = new Date(apt.date);
      return aptDate.toDateString() === date.toDateString();
    });
  };

  // Get week dates
  const getWeekDates = () => {
    const dates = [];
    const startOfWeek = new Date(selectedDate);
    startOfWeek.setDate(selectedDate.getDate() - selectedDate.getDay());
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-700';
      case 'confirmed': return 'bg-green-100 text-green-700';
      case 'completed': return 'bg-gray-100 text-gray-700';
      case 'cancelled': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // Get appointment type icon
  const getTypeIcon = (type) => {
    switch (type) {
      case 'consultation': return <User className="w-4 h-4" />;
      case 'follow-up': return <CalendarIcon className="w-4 h-4" />;
      case 'procedure': return <Activity className="w-4 h-4" />;
      case 'check-up': return <Heart className="w-4 h-4" />;
      default: return <CalendarIcon className="w-4 h-4" />;
    }
  };

  // Process appointments to handle overlaps
  const processAppointmentsForDisplay = (appointments) => {
    if (!appointments.length) return [];
    
    // Sort appointments by start time
    const sorted = [...appointments].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    
    const processed = [];
    const columns = [];
    
    sorted.forEach(appointment => {
      const start = new Date(appointment.date).getTime();
      const end = start + appointment.duration * 60 * 1000;
      
      // Find available column
      let column = 0;
      for (let i = 0; i < columns.length; i++) {
        if (columns[i] <= start) {
          column = i;
          break;
        }
      }
      
      // If no available column, create new one
      if (column === columns.length || (columns[column] && columns[column] > start)) {
        columns.push(end);
        column = columns.length - 1;
      } else {
        columns[column] = end;
      }
      
      processed.push({
        appointment,
        column,
        totalColumns: 1 // Will be updated after all appointments are processed
      });
    });
    
    // Update total columns for each appointment
    const maxColumns = columns.length;
    processed.forEach(item => {
      item.totalColumns = maxColumns;
    });
    
    return processed;
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 animate-fadeIn">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Appointment Schedule</h1>
              <p className="text-gray-600">Manage your clinic appointments and calendar</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <Plus className="w-5 h-5" />
              <span className="font-medium">New Appointment</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-2">
              <Calendar className="w-10 h-10 text-blue-600" />
              <span className="text-3xl font-bold text-gray-900">
                {filteredAppointments.filter(apt => apt.status === 'scheduled').length}
              </span>
            </div>
            <p className="text-sm font-medium text-gray-700">Scheduled</p>
            <p className="text-xs text-gray-600 mt-1">Upcoming appointments</p>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-sm border border-green-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-2">
              <FileCheck className="w-10 h-10 text-green-600" />
              <span className="text-3xl font-bold text-gray-900">
                {getCompletedEncountersThisWeek()}
              </span>
            </div>
            <p className="text-sm font-medium text-gray-700">Completed This Week</p>
            <p className="text-xs text-gray-600 mt-1">Encounters finished</p>
          </div>
          
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl shadow-sm border border-orange-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-10 h-10 text-orange-600" />
              <span className="text-3xl font-bold text-gray-900">
                {getAppointmentsForDate(new Date()).length}
              </span>
            </div>
            <p className="text-sm font-medium text-gray-700">Today</p>
            <p className="text-xs text-gray-600 mt-1">Current day appointments</p>
          </div>
          
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-sm border border-purple-200 p-6 transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-2">
              <Activity className="w-10 h-10 text-purple-600" />
              <span className="text-3xl font-bold text-gray-900">
                {filteredAppointments.filter(apt => apt.episodeId).length}
              </span>
            </div>
            <p className="text-sm font-medium text-gray-700">Episode Related</p>
            <p className="text-xs text-gray-600 mt-1">Active episode follow-ups</p>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 mb-6 p-6 transition-all hover:shadow-xl">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Search and Filter */}
            <div className="flex flex-1 gap-3">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search patients or appointments..."
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="all">All Status</option>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="all">All Types</option>
                <option value="consultation">Consultation</option>
                <option value="follow-up">Follow-up</option>
                <option value="procedure">Procedure</option>
                <option value="check-up">Check-up</option>
              </select>
            </div>

            {/* View Mode */}
            <div className="flex items-center gap-3">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('day')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    viewMode === 'day' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Day
                </button>
                <button
                  onClick={() => setViewMode('week')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    viewMode === 'week' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Week
                </button>
                <button
                  onClick={() => setViewMode('month')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    viewMode === 'month' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Month
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Calendar Navigation */}
        {viewMode !== 'week' && (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 mb-6 p-6 transition-all hover:shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    const newDate = new Date(selectedDate);
                    if (viewMode === 'day') newDate.setDate(selectedDate.getDate() - 1);
                    else if (viewMode === 'week') newDate.setDate(selectedDate.getDate() - 7);
                    else newDate.setMonth(selectedDate.getMonth() - 1);
                    setSelectedDate(newDate);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-all calendar-nav-button"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                
                <h2 className="text-xl font-semibold text-gray-900">
                  {viewMode === 'day' && selectedDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
                {viewMode === 'week' && `Week of ${getWeekDates()[0].toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric' 
                })} - ${getWeekDates()[6].toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  year: 'numeric'
                })}`}
                {viewMode === 'month' && selectedDate.toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long' 
                })}
              </h2>
              
              <button
                onClick={() => {
                  const newDate = new Date(selectedDate);
                  if (viewMode === 'day') newDate.setDate(selectedDate.getDate() + 1);
                  else if (viewMode === 'week') newDate.setDate(selectedDate.getDate() + 7);
                  else newDate.setMonth(selectedDate.getMonth() + 1);
                  setSelectedDate(newDate);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-all calendar-nav-button"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            
            <button
              onClick={() => setSelectedDate(new Date())}
              className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-all font-medium"
            >
              Today
            </button>
          </div>

          {/* Day View */}
          {viewMode === 'day' && (
            <div className="space-y-3">
              {getAppointmentsForDate(selectedDate).length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No appointments scheduled for this day
                </div>
              ) : (
                getAppointmentsForDate(selectedDate)
                  .sort((a, b) => new Date(a.date) - new Date(b.date))
                  .map(appointment => (
                    <div
                      key={appointment.id}
                      onClick={() => {
                        setSelectedAppointment(appointment);
                        setShowDetailsModal(true);
                      }}
                      className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-all cursor-pointer"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-gray-500" />
                              <span className="font-medium">{appointment.time}</span>
                            </div>
                            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(appointment.status)}`}>
                              {appointment.status}
                            </span>
                            {appointment.episodeId && (
                              <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-700">
                                Active Episode
                              </span>
                            )}
                          </div>
                          
                          <h3 className="font-semibold text-gray-900 mb-1">
                            {appointment.patientName}
                          </h3>
                          
                          <p className="text-sm text-gray-600 mb-2">{appointment.reason}</p>
                          
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              {getTypeIcon(appointment.type)}
                              <span>{appointment.type}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Building className="w-4 h-4" />
                              <span>{appointment.room || 'Room TBA'}</span>
                            </div>
                          </div>
                          
                          {appointment.notes && (
                            <p className="text-xs text-gray-500 mt-2 italic">{appointment.notes}</p>
                          )}
                        </div>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedAppointment(appointment);
                            setShowDetailsModal(true);
                          }}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <MoreHorizontal className="w-5 h-5 text-gray-500" />
                        </button>
                      </div>
                    </div>
                  ))
              )}
            </div>
          )}

          {/* Month View */}
          {viewMode === 'month' && (
            <MonthView 
              selectedDate={selectedDate}
              appointments={filteredAppointments}
              onDateClick={(date) => {
                setSelectedDate(date);
                setViewMode('day');
              }}
              onAppointmentClick={(appointment) => {
                setSelectedAppointment(appointment);
                setShowDetailsModal(true);
              }}
            />
          )}
        </div>
        )}

        {/* Week View - Without wrapper card */}
        {viewMode === 'week' && (
          <WeeklyCalendar
            selectedDate={selectedDate}
            appointments={filteredAppointments}
            onDateChange={setSelectedDate}
            onAppointmentClick={(appointment) => {
              setSelectedAppointment(appointment);
              setShowDetailsModal(true);
            }}
            onAddAppointment={() => setShowAddModal(true)}
          />
        )}

        {/* New Appointment Modal */}
        {showAddModal && (
          <NewAppointmentModal
            patients={patients}
            episodes={episodes}
            onSave={saveAppointment}
            onClose={() => setShowAddModal(false)}
          />
        )}

        {/* Appointment Details Modal */}
        {showDetailsModal && selectedAppointment && (
          <AppointmentDetailsModal
            appointment={selectedAppointment}
            patient={patients.find(p => p.id === selectedAppointment.patientId)}
            episode={episodes.find(e => e.id === selectedAppointment.episodeId)}
            onUpdate={(updates) => {
              updateAppointment(selectedAppointment.id, updates);
              setShowDetailsModal(false);
            }}
            onDelete={() => {
              deleteAppointment(selectedAppointment.id);
              setShowDetailsModal(false);
            }}
            onClose={() => setShowDetailsModal(false)}
          />
        )}
      </div>
    </DashboardLayout>
  );
};

// Month View Component
const MonthView = ({ selectedDate, appointments, onDateClick, onAppointmentClick }) => {
  const [hoveredDate, setHoveredDate] = useState(null);
  
  const getDaysInMonth = () => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty days for alignment
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    
    return days;
  };
  
  const getAppointmentsForDate = (date) => {
    if (!date) return [];
    return appointments.filter(apt => {
      const aptDate = new Date(apt.date);
      return aptDate.toDateString() === date.toDateString();
    });
  };
  
  const days = getDaysInMonth();
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  return (
    <div className="bg-white rounded-xl p-6">
      {/* Week days header */}
      <div className="grid grid-cols-7 gap-2 mb-4">
        {weekDays.map(day => (
          <div key={day} className="text-center text-sm font-medium text-gray-600 py-2">
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {days.map((date, index) => {
          const isToday = date && date.toDateString() === new Date().toDateString();
          const isSelected = date && date.toDateString() === selectedDate.toDateString();
          const dayAppointments = date ? getAppointmentsForDate(date) : [];
          
          return (
            <div
              key={index}
              className={`min-h-[100px] p-2 border rounded-lg transition-all ${
                !date ? 'border-transparent' : 
                isToday ? 'border-blue-400 bg-blue-50' : 
                isSelected ? 'border-blue-500 bg-blue-100' :
                hoveredDate?.toDateString() === date?.toDateString() ? 'border-gray-300 bg-gray-50' :
                'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              } ${date ? 'cursor-pointer' : ''}`}
              onClick={() => date && onDateClick(date)}
              onMouseEnter={() => setHoveredDate(date)}
              onMouseLeave={() => setHoveredDate(null)}
            >
              {date && (
                <>
                  <div className={`text-sm font-medium mb-1 ${
                    isToday ? 'text-blue-700' : 
                    isSelected ? 'text-blue-800' : 
                    'text-gray-900'
                  }`}>
                    {date.getDate()}
                  </div>
                  
                  {/* Appointment indicators */}
                  <div className="space-y-1">
                    {dayAppointments.slice(0, 3).map((apt, idx) => (
                      <div
                        key={apt.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          onAppointmentClick(apt);
                        }}
                        className={`text-xs p-1 rounded truncate cursor-pointer hover:opacity-80 ${
                          apt.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                          apt.status === 'completed' ? 'bg-gray-100 text-gray-700' :
                          apt.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                          'bg-blue-100 text-blue-700'
                        }`}
                        title={`${apt.time} - ${apt.patientName}`}
                      >
                        {apt.time} {apt.patientName.split(' ')[0]}
                      </div>
                    ))}
                    {dayAppointments.length > 3 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{dayAppointments.length - 3} more
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Schedule;