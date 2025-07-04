import React, { useState } from 'react';
import { useAppData } from '../../contexts/AppDataContext';
import { usePatient } from '../../contexts/PatientContext';
import { 
  Users, 
  Search, 
  Plus, 
  Calendar,
  Phone,
  Mail,
  ChevronRight,
  FileText,
  AlertCircle,
  Clock,
  Activity,
  Home,
  Eye,
  Grid,
  List,
  Filter,
  User,
  MapPin,
  ChevronDown,
  AlertTriangle,
  Trash2,
  Play
} from 'lucide-react';

const PatientList = () => {
  const { patients, getPatientRecords, getPatientSessions, deleteSession } = useAppData();
  const { setCurrentStep, setPatientData, setSessionId } = usePatient();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [expandedPatient, setExpandedPatient] = useState(null);
  const [filterOption, setFilterOption] = useState('all'); // 'all', 'with-incomplete', 'recent'
  
  // Filter patients based on search and filter options
  let filteredPatients = patients.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone.includes(searchTerm)
  );
  
  // Apply additional filters
  if (filterOption === 'with-incomplete') {
    filteredPatients = filteredPatients.filter(patient => 
      getPatientSessions(patient.id).length > 0
    );
  } else if (filterOption === 'recent') {
    // Show patients with visits in the last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    filteredPatients = filteredPatients.filter(patient => 
      new Date(patient.lastVisit) > thirtyDaysAgo
    );
  }
  
  const handleNewPatient = () => {
    setCurrentStep('patient-selection');
  };
  
  const handleHome = () => {
    setCurrentStep('home');
  };
  
  const handleViewPatientDetails = (patient) => {
    setPatientData(prev => ({ ...prev, viewingPatientId: patient.id }));
    setCurrentStep('patient-detail');
  };
  
  const handleStartNewAssessment = (patient) => {
    const records = getPatientRecords(patient.id);
    const latestRecord = records[0];
    
    setPatientData({
      id: patient.id,
      name: patient.name,
      age: calculateAge(patient.dateOfBirth),
      gender: patient.gender,
      dateOfBirth: patient.dateOfBirth,
      chiefComplaint: '',
      chiefComplaintDuration: '',
      chiefComplaintOnset: '',
      chiefComplaintDetails: [],
      additionalClinicalNotes: '',
      historyOfPresentIllness: '',
      medicalHistory: latestRecord?.medicalHistory || [],
      medications: latestRecord?.medications || [],
      allergies: latestRecord?.allergies || [],
      relatedDocuments: [],
      assessmentDocuments: [],
      physicalExam: {
        bloodPressure: '',
        heartRate: '',
        temperature: '',
        respiratoryRate: '',
        oxygenSaturation: '',
        height: '',
        weight: '',
        bmi: '',
        additionalFindings: '',
        examDocuments: []
      },
      differentialDiagnoses: [],
      selectedDiagnosis: null,
      finalDiagnosis: '',
      diagnosticNotes: '',
      recommendedTests: [],
      selectedTests: [],
      testResults: {},
      treatmentPlan: {
        medications: [],
        procedures: [],
        referrals: [],
        followUp: '',
        patientEducation: ''
      },
      prescriptions: []
    });
    
    setCurrentStep('patient-info');
  };
  
  const handleResumeSession = (session) => {
    setPatientData(session.data);
    setSessionId(session.id);
    setCurrentStep(session.currentStep || session.lastStep);
  };
  
  const handleDeleteSession = (sessionId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this incomplete session?')) {
      deleteSession(sessionId);
    }
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const calculateAge = (dob) => {
    const today = new Date();
    const birthDate = new Date(dob);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Management</h1>
            <p className="text-gray-600">View and manage patient records and diagnostic sessions</p>
          </div>
          <button
            onClick={handleHome}
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Home className="w-5 h-5 mr-2" />
            Back to Home
          </button>
        </div>
        
        {/* Search, Filters and Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search patients by name, ID, or phone..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Filter Dropdown */}
              <div className="relative">
                <select
                  value={filterOption}
                  onChange={(e) => setFilterOption(e.target.value)}
                  className="appearance-none pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                >
                  <option value="all">All Patients</option>
                  <option value="with-incomplete">With Incomplete Sessions</option>
                  <option value="recent">Recent Visits (30 days)</option>
                </select>
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
              </div>
              
              {/* View Mode Toggle */}
              <div className="flex items-center bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
                >
                  <Grid className="w-4 h-4 text-gray-600" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
                >
                  <List className="w-4 h-4 text-gray-600" />
                </button>
              </div>
              
              <button
                onClick={handleNewPatient}
                className="flex items-center px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-5 h-5 mr-2" />
                New Patient
              </button>
            </div>
          </div>
        </div>
        
        {/* Patient Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Patients</p>
                <p className="text-2xl font-bold text-gray-900">{patients.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {patients.reduce((total, p) => total + getPatientSessions(p.id).length, 0)}
                </p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Today's Visits</p>
                <p className="text-2xl font-bold text-gray-900">
                  {patients.filter(p => 
                    new Date(p.lastVisit).toDateString() === new Date().toDateString()
                  ).length}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Records</p>
                <p className="text-2xl font-bold text-gray-900">
                  {patients.reduce((total, p) => total + getPatientRecords(p.id).length, 0)}
                </p>
              </div>
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
        
        {/* Patients Display */}
        {filteredPatients.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="text-center">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No patients found</p>
              <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPatients.map(patient => (
              <PatientCard 
                key={patient.id}
                patient={patient}
                onViewDetails={handleViewPatientDetails}
                onStartAssessment={handleStartNewAssessment}
                onResumeSession={handleResumeSession}
                onDeleteSession={handleDeleteSession}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Patient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Visit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredPatients.map(patient => (
                  <PatientRow
                    key={patient.id}
                    patient={patient}
                    expanded={expandedPatient === patient.id}
                    onToggleExpand={() => setExpandedPatient(expandedPatient === patient.id ? null : patient.id)}
                    onViewDetails={handleViewPatientDetails}
                    onStartAssessment={handleStartNewAssessment}
                    onResumeSession={handleResumeSession}
                    onDeleteSession={handleDeleteSession}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// Patient Card Component for Grid View
const PatientCard = ({ patient, onViewDetails, onStartAssessment, onResumeSession, onDeleteSession }) => {
  const { getPatientRecords, getPatientSessions } = useAppData();
  const records = getPatientRecords(patient.id);
  const sessions = getPatientSessions(patient.id);
  const latestRecord = records[0];
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow h-full flex flex-col">
      <div className="p-6 flex-1 flex flex-col">
        {/* Patient Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="font-semibold text-gray-900">{patient.name}</h3>
              <p className="text-sm text-gray-500">ID: {patient.id}</p>
            </div>
          </div>
          {sessions.length > 0 && (
            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
              {sessions.length} Incomplete
            </span>
          )}
        </div>
        
        {/* Patient Info */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="w-4 h-4 mr-2 text-gray-400" />
            {calculateAge(patient.dateOfBirth)} years • {patient.gender}
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Phone className="w-4 h-4 mr-2 text-gray-400" />
            {patient.phone}
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="w-4 h-4 mr-2 text-gray-400" />
            Last visit: {formatDate(patient.lastVisit)}
          </div>
        </div>
        
        {/* Medical Info */}
        <div className="border-t pt-4 mb-4 flex-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Past Visits</span>
            <span className="font-medium text-gray-900">{records.length}</span>
          </div>
          {latestRecord && (
            <div className="mt-2 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">{latestRecord.finalDiagnosis}</p>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Latest</span>
              </div>
              <p className="text-xs text-gray-600 mt-1">{formatDate(latestRecord.date)}</p>
            </div>
          )}
        
          {/* Latest Incomplete Session */}
          {sessions.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-900 mb-2">Latest Incomplete Session</p>
              <div className="p-2 bg-orange-50 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      {sessions[0].data?.chiefComplaint || 'No chief complaint'}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {formatDateTime(sessions[0].startedAt || sessions[0].lastUpdated)}
                    </p>
                  </div>
                  <button
                    onClick={() => onResumeSession(sessions[0])}
                    className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onViewDetails(patient)}
            className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            View Details
          </button>
          <button
            onClick={() => onStartAssessment(patient)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Assessment
          </button>
        </div>
      </div>
    </div>
  );
};

// Patient Row Component for List View
const PatientRow = ({ patient, expanded, onToggleExpand, onViewDetails, onStartAssessment, onResumeSession, onDeleteSession }) => {
  const { getPatientRecords, getPatientSessions } = useAppData();
  const records = getPatientRecords(patient.id);
  const sessions = getPatientSessions(patient.id);
  
  return (
    <>
      <tr 
        className="hover:bg-gray-50 cursor-pointer"
        onClick={onToggleExpand}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="font-medium text-gray-900">{patient.name}</p>
              <p className="text-sm text-gray-500">{patient.id} • {calculateAge(patient.dateOfBirth)} yrs • {patient.gender}</p>
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm">
            <p className="text-gray-900">{patient.phone}</p>
            <p className="text-gray-500">{patient.email}</p>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <p className="text-sm text-gray-900">{formatDate(patient.lastVisit)}</p>
          <p className="text-xs text-gray-500">{records.length} records</p>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          {sessions.length > 0 ? (
            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
              {sessions.length} Incomplete
            </span>
          ) : (
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              Up to date
            </span>
          )}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(patient);
            }}
            className="text-blue-600 hover:text-blue-900 mr-3"
          >
            View
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onStartAssessment(patient);
            }}
            className="text-blue-600 hover:text-blue-900"
          >
            New Assessment
          </button>
          <ChevronDown className={`inline-block w-4 h-4 ml-2 text-gray-400 transform transition-transform ${
            expanded ? 'rotate-180' : ''
          }`} />
        </td>
      </tr>
      
      {/* Expanded Row Content */}
      {expanded && (
        <tr>
          <td colSpan="5" className="px-6 py-4 bg-gray-50">
            <div className="grid grid-cols-2 gap-6">
              {/* Patient Details */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Patient Details</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Address:</span>
                    <span className="ml-2 text-gray-900">{patient.address}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Emergency Contact:</span>
                    <span className="ml-2 text-gray-900">{patient.emergencyContact}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Date of Birth:</span>
                    <span className="ml-2 text-gray-900">{formatDate(patient.dateOfBirth)}</span>
                  </div>
                </div>
              </div>
              
              {/* Incomplete Sessions */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Incomplete Sessions</h4>
                {sessions.length > 0 ? (
                  <div className="space-y-2">
                    {sessions.map(session => (
                      <div key={session.id} className="p-3 bg-white rounded-lg border border-orange-200">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {session.data?.chiefComplaint || 'No chief complaint'}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">
                              Started: {formatDateTime(session.startedAt || session.lastUpdated)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onResumeSession(session);
                              }}
                              className="px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700"
                            >
                              Resume
                            </button>
                            <button
                              onClick={(e) => onDeleteSession(session.id, e)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No incomplete sessions</p>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

function calculateAge(dob) {
  const today = new Date();
  const birthDate = new Date(dob);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export default PatientList;