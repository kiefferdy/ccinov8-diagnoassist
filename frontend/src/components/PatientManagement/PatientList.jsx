import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import DashboardLayout from '../Layout/DashboardLayout';
import NewPatientModal from './NewPatientModal';
import { 
  Users, Search, Plus, Calendar, Phone, Mail,
  ChevronRight, Activity, Grid, List, Filter,
  User, AlertCircle, Heart, Stethoscope, Clock,
  FileText, TrendingUp, CheckCircle
} from 'lucide-react';
import './patient-animations.css';

const PatientList = () => {
  const navigate = useNavigate();
  const { patients, searchPatients, calculateAge } = usePatient();
  const { getPatientEpisodes, getActiveEpisodeCount } = useEpisode();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filterOption, setFilterOption] = useState('all'); // 'all', 'active', 'recent'
  const [showNewPatientModal, setShowNewPatientModal] = useState(false);
  
  // Filter patients
  const filteredPatients = searchTerm 
    ? searchPatients(searchTerm)
    : patients;
  
  // Apply additional filters
  const displayPatients = filteredPatients.filter(patient => {
    if (filterOption === 'active') {
      return getActiveEpisodeCount(patient.id) > 0;
    }
    return true;
  });
  
  const handlePatientSelect = (patient) => {
    navigate(`/patient/${patient.id}`);
  };
  
  const handleNewPatient = () => {
    setShowNewPatientModal(true);
  };

  // Calculate statistics
  const stats = {
    totalPatients: patients.length,
    activePatients: patients.filter(p => getActiveEpisodeCount(p.id) > 0).length,
    newThisMonth: patients.filter(p => {
      const createdDate = new Date(p.createdAt || Date.now());
      const monthAgo = new Date();
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      return createdDate > monthAgo;
    }).length,
    withAllergies: patients.filter(p => p.medicalBackground?.allergies?.length > 0).length
  };
  const PatientCard = ({ patient }) => {
    const episodes = getPatientEpisodes(patient.id);
    const activeEpisodes = episodes.filter(e => e.status === 'active');
    const age = calculateAge(patient.demographics.dateOfBirth);
    
    return (
      <div 
        className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105 patient-card"
        onClick={() => handlePatientSelect(patient)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-md">
              <User className="w-6 h-6 text-white" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">{patient.demographics.name}</h3>
              <p className="text-sm text-gray-500">ID: {patient.id} • {age} years • {patient.demographics.gender}</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-gray-600">
            <Phone className="w-4 h-4 mr-2 text-gray-400" />
            {patient.demographics.phone}
          </div>
          <div className="flex items-center text-gray-600">
            <Mail className="w-4 h-4 mr-2 text-gray-400" />
            {patient.demographics.email}
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Activity className="w-4 h-4 text-blue-500 mr-2" />
              <span className="text-sm font-medium text-gray-700">
                {activeEpisodes.length} active episode{activeEpisodes.length !== 1 ? 's' : ''}
              </span>
            </div>
            {patient.medicalBackground?.allergies?.length > 0 && (
              <div className="flex items-center bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
                <AlertCircle className="w-3 h-3 mr-1" />
                <span className="text-xs font-medium">Allergies</span>
              </div>
            )}
          </div>
          
          {activeEpisodes.length > 0 && (
            <div className="mt-3">
              <div className="text-xs text-gray-500 mb-1">Current Episode:</div>
              <div className="text-sm text-gray-700 font-medium truncate">
                {activeEpisodes[0].chiefComplaint}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const PatientRow = ({ patient }) => {
    const episodes = getPatientEpisodes(patient.id);
    const activeEpisodes = episodes.filter(e => e.status === 'active');
    const age = calculateAge(patient.demographics.dateOfBirth);
    
    return (
      <tr 
        className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 cursor-pointer transition-all duration-200"
        onClick={() => handlePatientSelect(patient)}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-md">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-900">{patient.demographics.name}</div>
              <div className="text-sm text-gray-500">ID: {patient.id}</div>
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
          {age} years / {patient.demographics.gender}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
          {patient.demographics.phone}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
          {patient.demographics.email}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          {activeEpisodes.length > 0 ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {activeEpisodes.length} active
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
              No active
            </span>
          )}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          {patient.medicalBackground?.allergies?.length > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
              <AlertCircle className="w-3 h-3 mr-1" />
              Allergies
            </span>
          )}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <ChevronRight className="w-5 h-5 text-gray-400 ml-auto" />
        </td>
      </tr>
    );
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 animate-fadeIn">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Management</h1>
                <p className="text-gray-600">Manage and view all clinic patients</p>
              </div>
              <button
                onClick={handleNewPatient}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg flex items-center hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <Plus className="w-5 h-5 mr-2" />
                <span className="font-medium">New Patient</span>
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-200 p-6 transition-all hover:shadow-md stat-card">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-10 h-10 text-blue-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.totalPatients}</span>
              </div>
              <p className="text-sm font-medium text-gray-700">Total Patients</p>
              <p className="text-xs text-gray-600 mt-1">Registered in system</p>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-sm border border-green-200 p-6 transition-all hover:shadow-md stat-card">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-10 h-10 text-green-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.activePatients}</span>
              </div>
              <p className="text-sm font-medium text-gray-700">Active Patients</p>
              <p className="text-xs text-gray-600 mt-1">With ongoing episodes</p>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-sm border border-purple-200 p-6 transition-all hover:shadow-md stat-card">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-10 h-10 text-purple-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.newThisMonth}</span>
              </div>
              <p className="text-sm font-medium text-gray-700">New This Month</p>
              <p className="text-xs text-gray-600 mt-1">Recently registered</p>
            </div>
            
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl shadow-sm border border-orange-200 p-6 transition-all hover:shadow-md stat-card">
              <div className="flex items-center justify-between mb-2">
                <AlertCircle className="w-10 h-10 text-orange-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.withAllergies}</span>
              </div>
              <p className="text-sm font-medium text-gray-700">With Allergies</p>
              <p className="text-xs text-gray-600 mt-1">Require special attention</p>
            </div>
          </div>
          
          {/* Search and Filters */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6 transition-all hover:shadow-xl">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search patients by name, ID, or phone..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              
              <div className="flex gap-3">
                <select
                  value={filterOption}
                  onChange={(e) => setFilterOption(e.target.value)}
                  className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="all">All Patients</option>
                  <option value="active">With Active Episodes</option>
                </select>
                
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded-md transition-all ${
                      viewMode === 'grid' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Grid className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded-md transition-all ${
                      viewMode === 'list' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <List className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Patient Count */}
            <div className="mt-4 text-sm text-gray-600">
              Showing <span className="font-medium text-gray-900">{displayPatients.length}</span> of{' '}
              <span className="font-medium text-gray-900">{patients.length}</span> patients
            </div>
          </div>
          
          {/* Patients Display */}
          {displayPatients.length === 0 ? (
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
              <p className="text-gray-600">
                {searchTerm ? 'Try adjusting your search criteria' : 'Add your first patient to get started'}
              </p>
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayPatients.map(patient => (
                <PatientCard key={patient.id} patient={patient} />
              ))}
            </div>
          ) : (
            <div className="bg-white shadow-lg rounded-xl overflow-hidden border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Patient
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Age / Gender
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Phone
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Episodes
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                      Alerts
                    </th>
                    <th className="relative px-6 py-4">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {displayPatients.map(patient => (
                    <PatientRow key={patient.id} patient={patient} />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      
      {/* New Patient Modal */}
      {showNewPatientModal && (
        <NewPatientModal
          onClose={() => setShowNewPatientModal(false)}
          onSuccess={(newPatient) => {
            setShowNewPatientModal(false);
            navigate(`/patient/${newPatient.id}`);
          }}
        />
      )}
    </DashboardLayout>
  );
};

export default PatientList;