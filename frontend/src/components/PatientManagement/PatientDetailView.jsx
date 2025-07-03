import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  User, 
  Calendar,
  Phone,
  Mail,
  MapPin,
  AlertCircle,
  FileText,
  Clock,
  Pill,
  Activity,
  Home,
  Edit,
  ChevronLeft,
  ChevronRight,
  Download,
  Printer,
  Heart,
  Stethoscope,
  TestTube,
  ClipboardCheck,
  Trash2,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const PatientDetailView = () => {
  const { currentStep, setCurrentStep, patientData, setPatientData } = usePatient();
  const { getPatient, getPatientRecords, getPatientSessions, patients, deleteSession } = useAppData();
  const [selectedTab, setSelectedTab] = useState('incomplete-sessions');
  const [expandedRecord, setExpandedRecord] = useState(null);
  const [expandedSession, setExpandedSession] = useState(null);
  
  // Get patient ID from patientData or URL params
  const patientId = patientData.viewingPatientId;
  const patient = getPatient(patientId);
  const records = getPatientRecords(patientId);
  const sessions = getPatientSessions(patientId);
  
  if (!patient) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="text-center py-12">
          <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Patient not found</p>
          <button
            onClick={() => setCurrentStep('patient-list')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Back to Patient List
          </button>
        </div>
      </div>
    );
  }
  
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
  
  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  const handleStartAssessment = () => {
    // Get the latest record for pre-filling medical history
    const latestRecord = records[0];
    
    // Set patient data with pre-filled information
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
      reviewOfSystems: '',
      pastMedicalHistory: latestRecord?.pastMedicalHistory || '',
      socialHistory: latestRecord?.socialHistory || '',
      familyHistory: latestRecord?.familyHistory || '',
      medicalHistory: latestRecord?.medicalHistory || [],
      medications: latestRecord?.medications || [],
      allergies: latestRecord?.allergies || [],
      surgicalHistory: latestRecord?.surgicalHistory || [],
      relatedDocuments: [],
      assessmentDocuments: [],
      differentialDiagnoses: [],
      selectedDiagnosis: null,
      finalDiagnosis: '',
      icdCode: '',
      additionalDiagnoses: [],
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
      postAssessmentQAs: [],
      clarifyingQuestions: [],
      redFlags: [],
      selectedTests: [],
      testResults: {},
      treatmentPlan: {
        medications: [],
        procedures: [],
        referrals: [],
        followUp: '',
        patientEducation: ''
      },
      prescriptions: [],
      followUpRecommendations: '',
      clinicalSummary: '',
      assessmentNote: [],
      previousVisitId: latestRecord?.id // Track which visit this is a follow-up to
    });
    
    setCurrentStep('patient-info');
  };
  
  const handleResumeSession = (session) => {
    // Load the session data
    setPatientData(session.data);
    setCurrentStep(session.currentStep);
  };
  
  const handleDeleteSession = (sessionId) => {
    if (window.confirm('Are you sure you want to delete this incomplete session? This action cannot be undone.')) {
      deleteSession(sessionId);
    }
  };
  
  // Get all medical conditions from all records
  const allMedicalConditions = [...new Set(records.flatMap(r => r.medicalHistory || []))];
  const allMedications = [...new Set(records.flatMap(r => r.medications || []))];
  const allAllergies = [...new Set(records.flatMap(r => r.allergies || []))];
  
  const tabs = [
    { id: 'incomplete-sessions', label: 'Incomplete Sessions', icon: AlertTriangle, count: sessions.length },
    { id: 'medical-records', label: 'Medical Records', icon: FileText, count: records.length },
    { id: 'overview', label: 'Patient Overview', icon: User },
    { id: 'test-results', label: 'Test Results', icon: TestTube },
    { id: 'medications', label: 'Medications', icon: Pill, count: allMedications.length }
  ];
  
  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center">
          <button
            onClick={() => setCurrentStep('patient-list')}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">{patient.name}</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>ID: {patient.id}</span>
              <span>•</span>
              <span>{calculateAge(patient.dateOfBirth)} years old</span>
              <span>•</span>
              <span>{patient.gender}</span>
              <span>•</span>
              <span>DOB: {formatDate(patient.dateOfBirth)}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Printer className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Edit className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={handleStartAssessment}
            className="flex items-center px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Activity className="w-5 h-5 mr-2" />
            New Assessment
          </button>
        </div>
      </div>
      
      {/* Critical Information Banner */}
      {allAllergies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-red-900">Known Allergies</h4>
              <div className="flex flex-wrap gap-2 mt-1">
                {allAllergies.map((allergy, index) => (
                  <span key={index} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                    {allergy}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-6 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = selectedTab === tab.id;
              const hasIncomplete = tab.id === 'incomplete-sessions' && sessions.length > 0;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                    ${isActive
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className={`w-4 h-4 ${hasIncomplete ? 'text-orange-500' : ''}`} />
                  <span>{tab.label}</span>
                  {tab.count !== undefined && tab.count > 0 && (
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      hasIncomplete 
                        ? 'bg-orange-100 text-orange-700' 
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* Incomplete Sessions Tab */}
          {selectedTab === 'incomplete-sessions' && (
            <div className="space-y-4">
              {sessions.length > 0 ? (
                <>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Incomplete Assessment Sessions</h3>
                    <p className="text-sm text-gray-600">{sessions.length} session{sessions.length > 1 ? 's' : ''} in progress</p>
                  </div>
                  
                  {sessions.map((session) => (
                    <div key={session.id} className="border border-orange-200 bg-orange-50 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-grow">
                          <div className="flex items-center space-x-2 mb-2">
                            <Clock className="w-4 h-4 text-orange-600" />
                            <p className="font-medium text-gray-900">
                              Started: {formatDateTime(session.startedAt)}
                            </p>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Chief Complaint: </span>
                              <span className="text-gray-900">
                                {session.data?.chiefComplaint || 'Not yet recorded'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Current Step: </span>
                              <span className="font-medium text-gray-900">
                                {session.currentStep ? session.currentStep.split('-').map(word => 
                                  word.charAt(0).toUpperCase() + word.slice(1)
                                ).join(' ') : 'Unknown'}
                              </span>
                            </div>
                          </div>
                          
                          {session.data && session.data.historyOfPresentIllness && (
                            <div className="mt-2 text-sm">
                              <span className="text-gray-600">History Preview: </span>
                              <span className="text-gray-700">
                                {session.data.historyOfPresentIllness.substring(0, 100)}...
                              </span>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => handleResumeSession(session)}
                            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Resume
                          </button>
                          <button
                            onClick={() => handleDeleteSession(session.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <div className="text-center py-12">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <p className="text-gray-600">No incomplete sessions</p>
                  <p className="text-sm text-gray-500 mt-1">All assessments have been completed</p>
                </div>
              )}
            </div>
          )}
          
          {/* Medical Records Tab */}
          {selectedTab === 'medical-records' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Medical Record History</h3>
                <p className="text-sm text-gray-600">{records.length} visit{records.length !== 1 ? 's' : ''} on record</p>
              </div>
              
              {records.length > 0 ? (
                records.map((record) => (
                  <div key={record.id} className="border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-colors">
                    <button
                      onClick={() => setExpandedRecord(expandedRecord === record.id ? null : record.id)}
                      className="w-full p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="text-left">
                          <div className="flex items-center space-x-3">
                            <p className="font-medium text-gray-900">{record.finalDiagnosis}</p>
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">
                              {record.icd10}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{formatDateTime(record.date)}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            <span className="font-medium">Chief Complaint:</span> {record.chiefComplaint}
                          </p>
                        </div>
                        <ChevronRight className={`w-5 h-5 text-gray-400 transform transition-transform flex-shrink-0 ${
                          expandedRecord === record.id ? 'rotate-90' : ''
                        }`} />
                      </div>
                    </button>
                    
                    {expandedRecord === record.id && (
                      <div className="border-t border-gray-200 p-4 bg-gray-50">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Physical Exam */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                              <Stethoscope className="w-4 h-4 mr-2 text-blue-600" />
                              Physical Examination
                            </h4>
                            <div className="space-y-2 text-sm">
                              {record.physicalExam.bloodPressure && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Blood Pressure:</span>
                                  <span className="font-medium">{record.physicalExam.bloodPressure}</span>
                                </div>
                              )}
                              {record.physicalExam.heartRate && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Heart Rate:</span>
                                  <span className="font-medium">{record.physicalExam.heartRate} bpm</span>
                                </div>
                              )}
                              {record.physicalExam.temperature && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Temperature:</span>
                                  <span className="font-medium">{record.physicalExam.temperature}°C</span>
                                </div>
                              )}
                              {record.physicalExam.additionalFindings && (
                                <div className="mt-2">
                                  <p className="text-gray-600">Additional Findings:</p>
                                  <p className="text-gray-800 mt-1">{record.physicalExam.additionalFindings}</p>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Treatment */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                              <Heart className="w-4 h-4 mr-2 text-purple-600" />
                              Treatment Plan
                            </h4>
                            {record.prescriptions && record.prescriptions.length > 0 && (
                              <div className="space-y-2">
                                <p className="text-sm text-gray-600">Prescriptions:</p>
                                {record.prescriptions.map((prescription, idx) => (
                                  <div key={idx} className="text-sm bg-white p-2 rounded border border-gray-200">
                                    <p className="font-medium text-gray-900">{prescription.medication}</p>
                                    <p className="text-gray-600">{prescription.dosage} - {prescription.frequency}</p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {/* Tests Ordered */}
                        {record.selectedTests && record.selectedTests.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                              <TestTube className="w-4 h-4 mr-2 text-green-600" />
                              Tests Ordered
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {record.selectedTests.map((test, idx) => (
                                <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                                  {test.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">No medical records found</p>
                  <p className="text-sm text-gray-500 mt-1">Start a new assessment to create the first record</p>
                </div>
              )}
            </div>
          )}
          
          {/* Patient Overview Tab */}
          {selectedTab === 'overview' && (
            <div className="space-y-6">
              {/* Contact Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start">
                    <Phone className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Phone</p>
                      <p className="text-gray-900">{patient.phone || 'Not provided'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <Mail className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Email</p>
                      <p className="text-gray-900">{patient.email || 'Not provided'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <MapPin className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Address</p>
                      <p className="text-gray-900">{patient.address || 'Not provided'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <User className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Emergency Contact</p>
                      <p className="text-gray-900">{patient.emergencyContact || 'Not provided'}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Medical History Summary */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical History Summary</h3>
                
                {/* Medical Conditions */}
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Medical Conditions</h4>
                  {allMedicalConditions.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {allMedicalConditions.map((condition, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {condition}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No medical conditions recorded</p>
                  )}
                </div>
                
                {/* Current Medications */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Current Medications</h4>
                  {allMedications.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {allMedications.map((medication, index) => (
                        <div key={index} className="flex items-center p-2 bg-purple-50 rounded-lg">
                          <Pill className="w-4 h-4 text-purple-600 mr-2 flex-shrink-0" />
                          <span className="text-sm text-gray-900">{medication}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No current medications</p>
                  )}
                </div>
              </div>
              
              {/* Visit Statistics */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Visit Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-2xl font-bold text-gray-900">{records.length}</p>
                    <p className="text-sm text-gray-600">Total Visits</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-2xl font-bold text-gray-900">
                      {records.length > 0 ? formatDate(records[0].date) : 'N/A'}
                    </p>
                    <p className="text-sm text-gray-600">Last Visit</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-2xl font-bold text-gray-900">{sessions.length}</p>
                    <p className="text-sm text-gray-600">Incomplete Sessions</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Test Results Tab */}
          {selectedTab === 'test-results' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Results History</h3>
              {records.some(r => r.testResults && Object.keys(r.testResults).length > 0) ? (
                records.filter(r => r.testResults && Object.keys(r.testResults).length > 0).map((record) => (
                  <div key={record.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <p className="font-medium text-gray-900">{formatDate(record.date)}</p>
                      <p className="text-sm text-gray-600">{record.finalDiagnosis}</p>
                    </div>
                    <div className="space-y-2">
                      {Object.entries(record.testResults).map(([testName, result]) => (
                        <div key={testName} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium text-gray-900">{testName}</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            result.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {result.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <TestTube className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">No test results found</p>
                </div>
              )}
            </div>
          )}
          
          {/* Medications Tab */}
          {selectedTab === 'medications' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Medication History</h3>
              {allMedications.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {allMedications.map((medication, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start">
                        <Pill className="w-5 h-5 text-purple-600 mr-3 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-900">{medication}</p>
                          <p className="text-sm text-gray-600 mt-1">
                            Last prescribed: {records.find(r => r.medications?.includes(medication))?.date 
                              ? formatDate(records.find(r => r.medications?.includes(medication)).date)
                              : 'Unknown'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Pill className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">No medications recorded</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDetailView;