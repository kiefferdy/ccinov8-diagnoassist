import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { 
  Users, 
  Search, 
  Plus, 
  Calendar,
  Phone,
  Mail,
  ChevronRight,
  Activity,
  Home,
  Grid,
  List,
  Filter,
  User,
  AlertCircle
} from 'lucide-react';

const PatientList = () => {
  const navigate = useNavigate();
  const { patients, searchPatients, calculateAge } = usePatient();
  const { getPatientEpisodes, getActiveEpisodeCount } = useEpisode();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filterOption, setFilterOption] = useState('all'); // 'all', 'active', 'recent'
  
  // Filter patients
  const filteredPatients = searchTerm 
    ? searchPatients(searchTerm)
    : patients;
  
  // Apply additional filters
  const displayPatients = filteredPatients.filter(patient => {
    if (filterOption === 'active') {
      return getActiveEpisodeCount(patient.id) > 0;
    }
    // Add more filters as needed
    return true;
  });
  
  const handlePatientSelect = (patient) => {
    navigate(`/patient/${patient.id}`);
  };
  
  const handleNewPatient = () => {
    // TODO: Implement new patient modal
    console.log('New patient creation - to be implemented');
  };
  
  const handleHomeClick = () => {
    navigate('/');
  };
  const PatientCard = ({ patient }) => {
    const episodes = getPatientEpisodes(patient.id);
    const activeEpisodes = episodes.filter(e => e.status === 'active');
    const age = calculateAge(patient.demographics.dateOfBirth);
    
    return (
      <div 
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => handlePatientSelect(patient)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">{patient.demographics.name}</h3>
              <p className="text-sm text-gray-500">ID: {patient.id} • {age} years • {patient.demographics.gender}</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-gray-600">
            <Phone className="w-4 h-4 mr-2" />
            {patient.demographics.phone}
          </div>
          <div className="flex items-center text-gray-600">
            <Mail className="w-4 h-4 mr-2" />
            {patient.demographics.email}
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center">
            <Activity className="w-4 h-4 text-gray-400 mr-2" />
            <span className="text-sm text-gray-600">
              {activeEpisodes.length} active episode{activeEpisodes.length !== 1 ? 's' : ''}
            </span>
          </div>
          {patient.medicalBackground.allergies.length > 0 && (
            <div className="flex items-center text-orange-600">
              <AlertCircle className="w-4 h-4 mr-1" />
              <span className="text-xs font-medium">Allergies</span>
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
        className="hover:bg-gray-50 cursor-pointer"
        onClick={() => handlePatientSelect(patient)}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-900">{patient.demographics.name}</div>
              <div className="text-sm text-gray-500">ID: {patient.id}</div>
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {age} years / {patient.demographics.gender}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {patient.demographics.phone}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {patient.demographics.email}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {activeEpisodes.length} active
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </td>
      </tr>
    );
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <button
                onClick={handleHomeClick}
                className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Home className="w-5 h-5 text-gray-600" />
              </button>
              <h1 className="text-3xl font-bold text-gray-900">Patients</h1>
            </div>
            <button
              onClick={handleNewPatient}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Patient
            </button>
          </div>
          
          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search patients by name, ID, or phone..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterOption}
                onChange={(e) => setFilterOption(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Patients</option>
                <option value="active">With Active Episodes</option>
              </select>
              
              <div className="flex bg-white border border-gray-300 rounded-lg">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100' : ''} rounded-l-lg`}
                >
                  <Grid className="w-5 h-5 text-gray-600" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 ${viewMode === 'list' ? 'bg-gray-100' : ''} rounded-r-lg`}
                >
                  <List className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Patient Count */}
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            Showing {displayPatients.length} of {patients.length} patients
          </p>
        </div>
        
        {/* Patients Display */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayPatients.map(patient => (
              <PatientCard key={patient.id} patient={patient} />
            ))}
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Patient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Age / Gender
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Episodes
                  </th>
                  <th className="relative px-6 py-3">
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
        
        {/* Empty State */}
        {displayPatients.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Try adjusting your search criteria' : 'Start by adding a new patient'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientList;