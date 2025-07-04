import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { EditableContactSection } from './PatientDetailEdit';
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
  Edit2,
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
  CheckCircle,
  Save,
  X,
  Plus,
  Scissors,
  Info
} from 'lucide-react';

const PatientDetailView = () => {
  const { currentStep, setCurrentStep, patientData, setPatientData } = usePatient();
  const { getPatient, getPatientRecords, getPatientSessions, patients, deleteSession, updatePatient } = useAppData();
  const [selectedTab, setSelectedTab] = useState('overview');
  const [expandedRecord, setExpandedRecord] = useState(null);
  const [expandedSession, setExpandedSession] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editingSection, setEditingSection] = useState(null); // 'overview', 'medical-history', 'test-results', 'medications', 'allergies'
  const [editData, setEditData] = useState({});
  
  // Medical History Edit States
  const [editingMedicalHistory, setEditingMedicalHistory] = useState(false);
  const [medicalHistoryData, setMedicalHistoryData] = useState({
    conditions: [],
    surgicalHistory: [],
    familyHistory: '',
    socialHistory: ''
  });
  
  // Medications Edit States
  const [editingMedications, setEditingMedications] = useState(false);
  const [medicationsData, setMedicationsData] = useState([]);
  
  // Allergies Edit States
  const [editingAllergies, setEditingAllergies] = useState(false);
  const [allergiesData, setAllergiesData] = useState([]);
  
  // Test Results Edit States
  const [editingTestResults, setEditingTestResults] = useState(false);
  const [testResultsData, setTestResultsData] = useState({});
  
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
    // Use currentStep, fallback to lastStep, and if neither exists, determine based on data
    const step = session.currentStep || session.lastStep || determineStepFromData(session.data);
    setCurrentStep(step);
  };
  
  const determineStepFromData = (data) => {
    // Determine the appropriate step based on what data has been filled
    if (data.treatmentPlan && data.prescriptions) {
      return 'treatment-plan';
    } else if (data.finalDiagnosis) {
      return 'final-diagnosis';
    } else if (data.testResults && Object.keys(data.testResults).length > 0) {
      return 'test-results';
    } else if (data.selectedTests && data.selectedTests.length > 0) {
      return 'recommended-tests';
    } else if (data.doctorDiagnosis || data.diagnosticNotes) {
      return 'diagnostic-analysis';
    } else if (data.physicalExam && (data.physicalExam.bloodPressure || data.physicalExam.heartRate)) {
      return 'physical-exam';
    } else if (data.historyOfPresentIllness || data.chiefComplaint) {
      return 'clinical-assessment';
    } else {
      return 'patient-info'; // Default to patient info if no other data
    }
  };
  
  const handleDeleteSession = (sessionId) => {
    if (window.confirm('Are you sure you want to delete this incomplete session? This action cannot be undone.')) {
      deleteSession(sessionId);
    }
  };
  
  const handleSaveEdit = () => {
    if (editingSection === 'overview') {
      updatePatient(patient.id, editData);
    }
    // Add other section saves here
    setIsEditing(false);
    setEditingSection(null);
  };
  
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditingSection(null);
    setEditData({});
  };
  
  // Medical History Edit Functions
  const handleEditMedicalHistory = () => {
    setEditingMedicalHistory(true);
    // Initialize with current data
    const conditions = [...new Set(records.flatMap(r => r.medicalHistory || []))];
    const surgicalHistory = patient.surgicalHistory || [];
    const familyHistory = patient.familyHistory || '';
    const socialHistory = patient.socialHistory || '';
    
    setMedicalHistoryData({
      conditions,
      surgicalHistory,
      familyHistory,
      socialHistory
    });
  };
  
  const handleSaveMedicalHistory = () => {
    // Update patient with new medical history data
    updatePatient(patient.id, {
      ...patient,
      surgicalHistory: medicalHistoryData.surgicalHistory,
      familyHistory: medicalHistoryData.familyHistory,
      socialHistory: medicalHistoryData.socialHistory,
      // Note: conditions are stored per record, not on patient level
    });
    setEditingMedicalHistory(false);
  };
  
  const handleCancelMedicalHistory = () => {
    setEditingMedicalHistory(false);
  };
  
  // Medications Edit Functions
  const handleEditMedications = () => {
    setEditingMedications(true);
    const allMeds = [...new Set(records.flatMap(r => r.medications || []))];
    setMedicationsData(allMeds.map((med, idx) => ({ id: idx, name: med })));
  };
  
  const handleSaveMedications = () => {
    // Update the latest record with new medications
    if (records.length > 0) {
      const latestRecord = records[0];
      // This would need to be implemented in your context
      // updateRecord(latestRecord.id, { ...latestRecord, medications: medicationsData.map(m => m.name) });
    }
    setEditingMedications(false);
  };
  
  const handleCancelMedications = () => {
    setEditingMedications(false);
  };
  
  const addMedication = () => {
    setMedicationsData([...medicationsData, { id: Date.now(), name: '' }]);
  };
  
  const removeMedication = (id) => {
    setMedicationsData(medicationsData.filter(m => m.id !== id));
  };
  
  const updateMedication = (id, name) => {
    setMedicationsData(medicationsData.map(m => m.id === id ? { ...m, name } : m));
  };
  
  // Allergies Edit Functions
  const handleEditAllergies = () => {
    setEditingAllergies(true);
    const allAllergiesFromRecords = [...new Set(records.flatMap(r => r.allergies || []))];
    setAllergiesData(allAllergiesFromRecords.map((allergy, idx) => ({ id: idx, name: allergy })));
  };
  
  const handleSaveAllergies = () => {
    // Update patient with new allergies
    updatePatient(patient.id, {
      ...patient,
      allergies: allergiesData.map(a => a.name)
    });
    setEditingAllergies(false);
  };
  
  const handleCancelAllergies = () => {
    setEditingAllergies(false);
  };
  
  const addAllergy = () => {
    setAllergiesData([...allergiesData, { id: Date.now(), name: '' }]);
  };
  
  const removeAllergy = (id) => {
    setAllergiesData(allergiesData.filter(a => a.id !== id));
  };
  
  const updateAllergy = (id, name) => {
    setAllergiesData(allergiesData.map(a => a.id === id ? { ...a, name } : a));
  };
  
  // Get all medical conditions from all records
  const allMedicalConditions = [...new Set(records.flatMap(r => r.medicalHistory || []))];
  const allMedications = [...new Set(records.flatMap(r => r.medications || []))];
  const allAllergies = [...new Set(records.flatMap(r => r.allergies || []))];
  
  const tabs = [
    { id: 'overview', label: 'Patient Overview', icon: User },
    { id: 'past-visits', label: 'Past Visits', icon: FileText, count: records.length },
    { id: 'medical-history', label: 'Medical History', icon: Activity },
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
          <button 
            onClick={() => {
              setIsEditing(true);
              setEditingSection('overview');
              setSelectedTab('overview');
              setEditData({
                name: patient.name,
                dateOfBirth: patient.dateOfBirth,
                gender: patient.gender,
                phone: patient.phone,
                email: patient.email,
                address: patient.address,
                emergencyContact: patient.emergencyContact
              });
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
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
      
      {/* Critical Information Banner - Allergies */}
      {(allAllergies.length > 0 || editingAllergies) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start flex-1">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-red-900">Known Allergies</h4>
                  {!editingAllergies && (
                    <button
                      onClick={handleEditAllergies}
                      className="text-sm text-red-700 hover:text-red-800 flex items-center ml-4"
                    >
                      <Edit2 className="w-4 h-4 mr-1" />
                      Edit
                    </button>
                  )}
                  {editingAllergies && (
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={handleSaveAllergies}
                        className="px-3 py-1 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 flex items-center"
                      >
                        <Save className="w-4 h-4 mr-1" />
                        Save
                      </button>
                      <button
                        onClick={handleCancelAllergies}
                        className="px-3 py-1 border border-red-300 text-red-700 text-sm font-medium rounded-lg hover:bg-red-100"
                      >
                        Cancel
                      </button>
                    </div>
                  )}
                </div>
                {!editingAllergies ? (
                  <div className="flex flex-wrap gap-2 mt-1">
                    {allAllergies.map((allergy, index) => (
                      <span key={index} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                        {allergy}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-2 mt-3">
                    {allergiesData.map((allergy) => (
                      <div key={allergy.id} className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={allergy.name}
                          onChange={(e) => updateAllergy(allergy.id, e.target.value)}
                          className="flex-1 px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 text-sm"
                          placeholder="Enter allergy"
                        />
                        <button
                          onClick={() => removeAllergy(allergy.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded-lg"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={addAllergy}
                      className="flex items-center text-sm text-red-700 hover:text-red-800"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Allergy
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Incomplete Sessions Card */}
      {sessions.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-orange-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-medium text-orange-900 mb-3">Incomplete Sessions ({sessions.length})</h4>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div key={session.id} className="bg-white border border-orange-200 rounded-lg p-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-grow">
                        <div className="flex items-center space-x-2 mb-1">
                          <Clock className="w-4 h-4 text-orange-600" />
                          <p className="text-sm font-medium text-gray-900">
                            Started: {formatDateTime(session.startedAt || session.lastUpdated)}
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
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => handleResumeSession(session)}
                          className="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Resume
                        </button>
                        <button
                          onClick={() => handleDeleteSession(session.id)}
                          className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
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
          {/* Past Visits Tab */}
          {selectedTab === 'past-visits' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Past Visit History</h3>
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
                              {record.physicalExam.respiratoryRate && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Respiratory Rate:</span>
                                  <span className="font-medium">{record.physicalExam.respiratoryRate} breaths/min</span>
                                </div>
                              )}
                              {record.physicalExam.oxygenSaturation && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">O2 Saturation:</span>
                                  <span className="font-medium">{record.physicalExam.oxygenSaturation}</span>
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
                            {record.treatmentPlan && (
                              <div className="mb-4">
                                <p className="text-sm text-gray-600 mb-1">Treatment Summary:</p>
                                <p className="text-sm text-gray-800">{record.treatmentPlan}</p>
                              </div>
                            )}
                            {record.prescriptions && record.prescriptions.length > 0 && (
                              <div className="space-y-2">
                                <p className="text-sm text-gray-600">Prescriptions:</p>
                                {record.prescriptions.map((prescription, idx) => (
                                  <div key={idx} className="text-sm bg-white p-2 rounded border border-gray-200">
                                    <p className="font-medium text-gray-900">{prescription.medication}</p>
                                    <p className="text-gray-600">{prescription.dosage} - {prescription.frequency}</p>
                                    {prescription.duration && (
                                      <p className="text-gray-500 text-xs mt-1">Duration: {prescription.duration}</p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {/* History of Present Illness */}
                        {record.historyOfPresentIllness && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                              <Clock className="w-4 h-4 mr-2 text-indigo-600" />
                              History of Present Illness
                            </h4>
                            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200">
                              {record.historyOfPresentIllness}
                            </p>
                          </div>
                        )}
                        
                        {/* Tests and Results */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                          {/* Tests Ordered */}
                          {record.testsPerformed && record.testsPerformed.length > 0 && (
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                                <TestTube className="w-4 h-4 mr-2 text-green-600" />
                                Tests Performed
                              </h4>
                              <div className="flex flex-wrap gap-2">
                                {record.testsPerformed.map((test, idx) => (
                                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                                    {test}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Medical History at Time of Visit */}
                          {(record.medicalHistory || record.medications || record.allergies) && (
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                                <Activity className="w-4 h-4 mr-2 text-orange-600" />
                                Patient Status at Visit
                              </h4>
                              <div className="space-y-2 text-sm">
                                {record.medicalHistory && record.medicalHistory.length > 0 && (
                                  <div>
                                    <p className="text-gray-600">Conditions:</p>
                                    <div className="flex flex-wrap gap-1">
                                      {record.medicalHistory.map((condition, idx) => (
                                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                          {condition}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {record.medications && record.medications.length > 0 && (
                                  <div>
                                    <p className="text-gray-600">Medications:</p>
                                    <div className="flex flex-wrap gap-1">
                                      {record.medications.map((med, idx) => (
                                        <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                          {med}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {/* Additional Notes */}
                        {record.diagnosticNotes && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                              <FileText className="w-4 h-4 mr-2 text-gray-600" />
                              Clinical Notes
                            </h4>
                            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200">
                              {record.diagnosticNotes}
                            </p>
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
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
                  {!isEditing && editingSection !== 'overview' && (
                    <button
                      onClick={() => {
                        setIsEditing(true);
                        setEditingSection('overview');
                        setEditData({
                          name: patient.name,
                          dateOfBirth: patient.dateOfBirth,
                          gender: patient.gender,
                          phone: patient.phone,
                          email: patient.email,
                          address: patient.address,
                          emergencyContact: patient.emergencyContact
                        });
                      }}
                      className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                    >
                      <Edit2 className="w-4 h-4 mr-1" />
                      Edit
                    </button>
                  )}
                </div>
                <EditableContactSection
                  patient={patient}
                  editData={editData}
                  setEditData={setEditData}
                  isEditing={isEditing && editingSection === 'overview'}
                  onSave={handleSaveEdit}
                  onCancel={handleCancelEdit}
                />
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
          
          {/* Medical History Tab */}
          {selectedTab === 'medical-history' && (
            <div className="space-y-6">
              {/* Edit Button */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Medical History</h3>
                {!editingMedicalHistory && (
                  <button
                    onClick={handleEditMedicalHistory}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    <Edit2 className="w-4 h-4 mr-1" />
                    Edit Medical History
                  </button>
                )}
                {editingMedicalHistory && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleSaveMedicalHistory}
                      className="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 flex items-center"
                    >
                      <Save className="w-4 h-4 mr-1" />
                      Save
                    </button>
                    <button
                      onClick={handleCancelMedicalHistory}
                      className="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
              
              {/* Medical Timeline */}
              {!editingMedicalHistory && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical Timeline</h3>
                  <div className="relative">
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300"></div>
                    {records.map((record, index) => (
                      <div key={record.id} className="relative pb-8">
                        <div className="absolute left-4 w-2 h-2 bg-blue-600 rounded-full -translate-x-1/2"></div>
                        <div className="ml-12">
                          <div className="flex items-center mb-2">
                            <p className="text-sm font-medium text-gray-900">{formatDate(record.date)}</p>
                            <span className="ml-3 px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">
                              {record.icd10}
                            </span>
                          </div>
                          <p className="font-medium text-gray-900">{record.finalDiagnosis}</p>
                          <p className="text-sm text-gray-600 mt-1">Chief Complaint: {record.chiefComplaint}</p>
                          {record.treatmentPlan && (
                            <p className="text-sm text-gray-600 mt-1">Treatment: {record.treatmentPlan.substring(0, 100)}...</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Editable Sections */}
              {editingMedicalHistory && (
                <div className="space-y-6">
                  {/* Chronic Conditions */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Chronic Conditions</h4>
                    <div className="space-y-2">
                      {medicalHistoryData.conditions.map((condition, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={condition}
                            onChange={(e) => {
                              const newConditions = [...medicalHistoryData.conditions];
                              newConditions[index] = e.target.value;
                              setMedicalHistoryData({ ...medicalHistoryData, conditions: newConditions });
                            }}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter medical condition"
                          />
                          <button
                            onClick={() => {
                              const newConditions = medicalHistoryData.conditions.filter((_, i) => i !== index);
                              setMedicalHistoryData({ ...medicalHistoryData, conditions: newConditions });
                            }}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          setMedicalHistoryData({
                            ...medicalHistoryData,
                            conditions: [...medicalHistoryData.conditions, '']
                          });
                        }}
                        className="flex items-center text-sm text-blue-600 hover:text-blue-700"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Condition
                      </button>
                    </div>
                  </div>
                  
                  {/* Surgical History */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Surgical History</h4>
                    <div className="space-y-2">
                      {medicalHistoryData.surgicalHistory.map((surgery, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={surgery}
                            onChange={(e) => {
                              const newSurgeries = [...medicalHistoryData.surgicalHistory];
                              newSurgeries[index] = e.target.value;
                              setMedicalHistoryData({ ...medicalHistoryData, surgicalHistory: newSurgeries });
                            }}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter surgical procedure and date"
                          />
                          <button
                            onClick={() => {
                              const newSurgeries = medicalHistoryData.surgicalHistory.filter((_, i) => i !== index);
                              setMedicalHistoryData({ ...medicalHistoryData, surgicalHistory: newSurgeries });
                            }}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          setMedicalHistoryData({
                            ...medicalHistoryData,
                            surgicalHistory: [...medicalHistoryData.surgicalHistory, '']
                          });
                        }}
                        className="flex items-center text-sm text-blue-600 hover:text-blue-700"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Surgery
                      </button>
                    </div>
                  </div>
                  
                  {/* Family History */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Family History</h4>
                    <textarea
                      value={medicalHistoryData.familyHistory}
                      onChange={(e) => setMedicalHistoryData({ ...medicalHistoryData, familyHistory: e.target.value })}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter family medical history..."
                    />
                  </div>
                  
                  {/* Social History */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Social History</h4>
                    <textarea
                      value={medicalHistoryData.socialHistory}
                      onChange={(e) => setMedicalHistoryData({ ...medicalHistoryData, socialHistory: e.target.value })}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter social history (smoking, alcohol, occupation, etc.)..."
                    />
                  </div>
                </div>
              )}
              
              {/* Non-editable view */}
              {!editingMedicalHistory && (
                <>
                  {/* Chronic Conditions */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Chronic Conditions</h3>
                    {allMedicalConditions.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {allMedicalConditions.map((condition, index) => {
                          const firstRecordWithCondition = records.find(r => r.medicalHistory?.includes(condition));
                          return (
                            <div key={index} className="bg-white rounded-lg border border-gray-200 p-4">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h4 className="font-medium text-gray-900">{condition}</h4>
                                  {firstRecordWithCondition && (
                                    <p className="text-sm text-gray-600 mt-1">
                                      First recorded: {formatDate(firstRecordWithCondition.date)}
                                    </p>
                                  )}
                                </div>
                                <Activity className="w-5 h-5 text-blue-600" />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-6 text-center">
                        <p className="text-gray-600">No chronic conditions recorded</p>
                      </div>
                    )}
                  </div>
                  
                  {/* Surgical History */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Surgical History</h3>
                    {patient.surgicalHistory && patient.surgicalHistory.length > 0 ? (
                      <div className="space-y-3">
                        {patient.surgicalHistory.map((surgery, index) => (
                          <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                            <Scissors className="w-5 h-5 text-gray-600 mr-3" />
                            <span className="text-gray-900">{surgery}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-6 text-center">
                        <p className="text-gray-600">No surgical procedures recorded</p>
                      </div>
                    )}
                  </div>
                  
                  {/* Family History */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Family History</h3>
                    {patient.familyHistory ? (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-700 whitespace-pre-wrap">{patient.familyHistory}</p>
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-6 text-center">
                        <p className="text-gray-600">No family history recorded</p>
                      </div>
                    )}
                  </div>
                  
                  {/* Social History */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Social History</h3>
                    {patient.socialHistory ? (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-700 whitespace-pre-wrap">{patient.socialHistory}</p>
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-6 text-center">
                        <p className="text-gray-600">No social history recorded</p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
          
          {/* Test Results Tab */}
          {selectedTab === 'test-results' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Test Results History</h3>
                <button
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                  disabled
                >
                  <Info className="w-4 h-4 mr-1" />
                  Test results are read-only from past visits
                </button>
              </div>
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
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Medication History</h3>
                {!editingMedications && (
                  <button
                    onClick={handleEditMedications}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    <Edit2 className="w-4 h-4 mr-1" />
                    Edit Medications
                  </button>
                )}
                {editingMedications && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleSaveMedications}
                      className="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 flex items-center"
                    >
                      <Save className="w-4 h-4 mr-1" />
                      Save
                    </button>
                    <button
                      onClick={handleCancelMedications}
                      className="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
              
              {!editingMedications ? (
                allMedications.length > 0 ? (
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
                )
              ) : (
                <div className="space-y-3">
                  {medicationsData.map((medication) => (
                    <div key={medication.id} className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={medication.name}
                        onChange={(e) => updateMedication(medication.id, e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter medication name and dosage"
                      />
                      <button
                        onClick={() => removeMedication(medication.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={addMedication}
                    className="flex items-center text-sm text-blue-600 hover:text-blue-700"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Medication
                  </button>
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