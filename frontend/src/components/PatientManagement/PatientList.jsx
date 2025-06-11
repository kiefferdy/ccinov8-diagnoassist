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
  Activity
} from 'lucide-react';

const PatientList = () => {
  const { patients, getPatientRecords, getPatientSessions } = useAppData();
  const { setCurrentStep } = usePatient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  
  // Filter patients based on search
  const filteredPatients = patients.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone.includes(searchTerm)
  );
  
  const handleNewPatient = () => {
    setCurrentStep('patient-info');
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
    <div className="max-w-7xl mx-auto p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Management</h1>
        <p className="text-gray-600">View and manage patient records and diagnostic sessions</p>
      </div>
      
      {/* Search and Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
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
          <button
            onClick={handleNewPatient}
            className="ml-4 flex items-center px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            New Patient
          </button>
        </div>
      </div>
      
      {/* Patients List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <Users className="w-5 h-5 mr-2 text-blue-600" />
                Patients ({filteredPatients.length})
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {filteredPatients.length === 0 ? (
                <div className="p-12 text-center">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No patients found</p>
                </div>
              ) : (
                filteredPatients.map(patient => {
                  const records = getPatientRecords(patient.id);
                  const sessions = getPatientSessions(patient.id);
                  const isSelected = selectedPatient?.id === patient.id;
                  
                  return (
                    <div
                      key={patient.id}
                      onClick={() => setSelectedPatient(patient)}
                      className={`p-6 cursor-pointer transition-all ${
                        isSelected ? 'bg-blue-50 border-l-4 border-blue-600' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <h3 className="text-lg font-medium text-gray-900">{patient.name}</h3>
                            <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                              {patient.id}
                            </span>
                            {sessions.length > 0 && (
                              <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded flex items-center">
                                <Clock className="w-3 h-3 mr-1" />
                                {sessions.length} Incomplete
                              </span>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-2">
                            <span>{calculateAge(patient.dateOfBirth)} years • {patient.gender}</span>
                            <span className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              Last visit: {formatDate(patient.lastVisit)}
                            </span>
                          </div>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span className="flex items-center">
                              <Phone className="w-4 h-4 mr-1" />
                              {patient.phone}
                            </span>
                            <span className="flex items-center">
                              <Mail className="w-4 h-4 mr-1" />
                              {patient.email}
                            </span>
                          </div>
                          
                          <div className="mt-3 flex items-center text-sm">
                            <FileText className="w-4 h-4 mr-1 text-gray-400" />
                            <span className="text-gray-600">{records.length} medical records</span>
                          </div>
                        </div>
                        
                        <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
                          isSelected ? 'transform rotate-90' : ''
                        }`} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
        
        {/* Patient Details Panel */}
        <div className="lg:col-span-1">
          {selectedPatient ? (
            <PatientDetails patient={selectedPatient} />
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Select a patient to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const PatientDetails = ({ patient }) => {
  const { getPatientRecords, getPatientSessions } = useAppData();
  const { setCurrentStep, setPatientData, setSessionId } = usePatient();
  const records = getPatientRecords(patient.id);
  const sessions = getPatientSessions(patient.id);
  
  const handleNewSession = () => {
    // Pre-fill patient data from latest record
    const latestRecord = records[0]; // Already sorted by date
    
    setPatientData({
      id: patient.id,
      name: patient.name,
      age: patient.age,
      gender: patient.gender,
      dateOfBirth: patient.dateOfBirth,
      chiefComplaint: '',
      chiefComplaintDetails: [],
      additionalClinicalNotes: '',
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
      treatmentPlan: '',
      prescriptions: []
    });
    
    setCurrentStep('clinical-assessment');
  };
  
  const handleResumeSession = (session) => {
    // Load session data
    setPatientData(session.data);
    setSessionId(session.id);
    setCurrentStep(session.lastStep);
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
  
  return (
    <div className="space-y-6">
      {/* Patient Info Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Patient Information</h3>
        
        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-500">Full Name</label>
            <p className="font-medium text-gray-900">{patient.name}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-gray-500">Date of Birth</label>
              <p className="font-medium text-gray-900">{new Date(patient.dateOfBirth).toLocaleDateString()}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Gender</label>
              <p className="font-medium text-gray-900">{patient.gender}</p>
            </div>
          </div>
          
          <div>
            <label className="text-sm text-gray-500">Phone</label>
            <p className="font-medium text-gray-900">{patient.phone}</p>
          </div>
          
          <div>
            <label className="text-sm text-gray-500">Email</label>
            <p className="font-medium text-gray-900">{patient.email}</p>
          </div>
          
          <div>
            <label className="text-sm text-gray-500">Address</label>
            <p className="font-medium text-gray-900">{patient.address}</p>
          </div>
          
          <div>
            <label className="text-sm text-gray-500">Emergency Contact</label>
            <p className="font-medium text-gray-900">{patient.emergencyContact}</p>
          </div>
        </div>
        
        <button
          onClick={handleNewSession}
          className="w-full mt-6 flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Activity className="w-5 h-5 mr-2" />
          Start New Diagnostic Session
        </button>
      </div>
      
      {/* Incomplete Sessions */}
      {sessions.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-yellow-600" />
            Incomplete Sessions ({sessions.length})
          </h3>
          
          <div className="space-y-3">
            {sessions.map(session => (
              <div key={session.id} className="bg-white rounded-lg p-4 border border-yellow-200">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-medium text-gray-900">{session.data.chiefComplaint || 'No chief complaint'}</p>
                    <p className="text-sm text-gray-600">
                      Last updated: {formatDateTime(session.lastUpdated)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    Progress: {session.lastStep}
                  </span>
                  <button
                    onClick={() => handleResumeSession(session)}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Resume →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Recent Records */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical Records</h3>
        
        {records.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No medical records found</p>
        ) : (
          <div className="space-y-3">
            {records.slice(0, 5).map(record => (
              <div key={record.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{record.finalDiagnosis}</p>
                    <p className="text-sm text-gray-600">{formatDateTime(record.date)}</p>
                  </div>
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                    {record.icd10}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-2">
                  Chief Complaint: {record.chiefComplaint}
                </p>
                
                {record.prescriptions.length > 0 && (
                  <div className="text-sm text-gray-500">
                    Prescriptions: {record.prescriptions.map(p => p.medication).join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientList;
