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
  ClipboardCheck
} from 'lucide-react';

const PatientDetailView = () => {
  const { currentStep, setCurrentStep, patientData, setPatientData } = usePatient();
  const { getPatient, getPatientRecords, getPatientSessions, patients } = useAppData();
  const [selectedTab, setSelectedTab] = useState('overview');
  const [expandedRecord, setExpandedRecord] = useState(null);
  
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
  
  // Get all medical conditions from all records
  const allMedicalConditions = [...new Set(records.flatMap(r => r.medicalHistory || []))];
  const allMedications = [...new Set(records.flatMap(r => r.medications || []))];
  const allAllergies = [...new Set(records.flatMap(r => r.allergies || []))];
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'medical-history', label: 'Medical History', icon: FileText },
    { id: 'records', label: 'Visit Records', icon: ClipboardCheck },
    { id: 'test-results', label: 'Test Results', icon: TestTube },
    { id: 'medications', label: 'Medications', icon: Pill }
  ];
  
  return (
    <div className="max-w-7xl mx-auto p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div className="flex items-center">
          <button
            onClick={() => setCurrentStep('patient-list')}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">{patient.name}</h1>
            <p className="text-gray-600">Patient ID: {patient.id}</p>
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
            Start Assessment
          </button>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">{calculateAge(patient.dateOfBirth)}</span>
          </div>
          <p className="text-sm text-gray-600">Years Old</p>
          <p className="text-xs text-gray-500">{formatDate(patient.dateOfBirth)}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <FileText className="w-8 h-8 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">{records.length}</span>
          </div>
          <p className="text-sm text-gray-600">Total Visits</p>
          <p className="text-xs text-gray-500">Last: {new Date(patient.lastVisit).toLocaleDateString()}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <span className="text-2xl font-bold text-gray-900">{allAllergies.length}</span>
          </div>
          <p className="text-sm text-gray-600">Known Allergies</p>
          <p className="text-xs text-gray-500">{allAllergies[0] || 'None recorded'}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <Pill className="w-8 h-8 text-purple-600" />
            <span className="text-2xl font-bold text-gray-900">{allMedications.length}</span>
          </div>
          <p className="text-sm text-gray-600">Current Medications</p>
          <p className="text-xs text-gray-500">{sessions.length} incomplete sessions</p>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                    ${selectedTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
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
                      <p className="text-gray-900">{patient.phone}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <Mail className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Email</p>
                      <p className="text-gray-900">{patient.email}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <MapPin className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Address</p>
                      <p className="text-gray-900">{patient.address}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <User className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Emergency Contact</p>
                      <p className="text-gray-900">{patient.emergencyContact}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Recent Visits */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Visits</h3>
                <div className="space-y-3">
                  {records.slice(0, 3).map((record) => (
                    <div key={record.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{record.finalDiagnosis}</p>
                          <p className="text-sm text-gray-600">{formatDateTime(record.date)}</p>
                          <p className="text-sm text-gray-500 mt-1">Chief Complaint: {record.chiefComplaint}</p>
                        </div>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">
                          {record.icd10}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {selectedTab === 'medical-history' && (
            <div className="space-y-6">
              {/* Medical Conditions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical Conditions</h3>
                {allMedicalConditions.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {allMedicalConditions.map((condition, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {condition}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No medical conditions recorded</p>
                )}
              </div>
              
              {/* Allergies */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  Allergies
                </h3>
                {allAllergies.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {allAllergies.map((allergy, index) => (
                      <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                        {allergy}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No known allergies</p>
                )}
              </div>
              
              {/* Current Medications */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Medications</h3>
                {allMedications.length > 0 ? (
                  <div className="space-y-2">
                    {allMedications.map((medication, index) => (
                      <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                        <Pill className="w-4 h-4 text-purple-600 mr-3" />
                        <span className="text-gray-900">{medication}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No current medications</p>
                )}
              </div>
            </div>
          )}
          
          {selectedTab === 'records' && (
            <div className="space-y-4">
              {records.length > 0 ? (
                records.map((record) => (
                  <div key={record.id} className="border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedRecord(expandedRecord === record.id ? null : record.id)}
                      className="w-full p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="text-left">
                          <p className="font-medium text-gray-900">{record.finalDiagnosis}</p>
                          <p className="text-sm text-gray-600">{formatDateTime(record.date)}</p>
                          <p className="text-sm text-gray-500 mt-1">Chief Complaint: {record.chiefComplaint}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">
                            {record.icd10}
                          </span>
                          <ChevronRight className={`w-5 h-5 text-gray-400 transform transition-transform ${
                            expandedRecord === record.id ? 'rotate-90' : ''
                          }`} />
                        </div>
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
                              <div className="flex justify-between">
                                <span className="text-gray-600">Blood Pressure:</span>
                                <span className="font-medium">{record.physicalExam.bloodPressure}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Heart Rate:</span>
                                <span className="font-medium">{record.physicalExam.heartRate} bpm</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Temperature:</span>
                                <span className="font-medium">{record.physicalExam.temperature}°C</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">O2 Saturation:</span>
                                <span className="font-medium">{record.physicalExam.oxygenSaturation}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Tests & Prescriptions */}
                          <div>
                            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                              <TestTube className="w-4 h-4 mr-2 text-green-600" />
                              Tests Performed
                            </h4>
                            <div className="space-y-1 text-sm mb-4">
                              {record.testsPerformed.map((test, index) => (
                                <div key={index} className="text-gray-700">• {test}</div>
                              ))}
                            </div>
                            
                            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                              <Pill className="w-4 h-4 mr-2 text-purple-600" />
                              Prescriptions
                            </h4>
                            <div className="space-y-2 text-sm">
                              {record.prescriptions.map((rx, index) => (
                                <div key={index} className="bg-white p-2 rounded border border-gray-200">
                                  <p className="font-medium">{rx.medication} - {rx.dosage}</p>
                                  <p className="text-gray-600">{rx.frequency} for {rx.duration}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        {/* Treatment Plan */}
                        <div className="mt-4">
                          <h4 className="font-medium text-gray-900 mb-2">Treatment Plan</h4>
                          <p className="text-sm text-gray-700 whitespace-pre-wrap">{record.treatmentPlan}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 py-8">No visit records found</p>
              )}
            </div>
          )}
          
          {selectedTab === 'test-results' && (
            <div className="space-y-4">
              {records.filter(r => r.testsPerformed.length > 0).length > 0 ? (
                records.filter(r => r.testsPerformed.length > 0).map((record) => (
                  <div key={record.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="mb-3">
                      <p className="font-medium text-gray-900">{formatDateTime(record.date)}</p>
                      <p className="text-sm text-gray-600">Visit for: {record.chiefComplaint}</p>
                    </div>
                    <div className="space-y-2">
                      {record.testsPerformed.map((test, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-gray-900">{test}</span>
                          {record.testResults && record.testResults[test] && (
                            <span className="text-sm text-gray-600">
                              {record.testResults[test].value} {record.testResults[test].unit}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 py-8">No test results found</p>
              )}
            </div>
          )}
          
          {selectedTab === 'medications' && (
            <div className="space-y-6">
              {/* Current Medications */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Medications</h3>
                {allMedications.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {allMedications.map((medication, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start">
                          <Pill className="w-5 h-5 text-purple-600 mr-3 mt-0.5" />
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{medication}</p>
                            <p className="text-sm text-gray-600 mt-1">Active</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No current medications</p>
                )}
              </div>
              
              {/* Prescription History */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Prescription History</h3>
                <div className="space-y-4">
                  {records.filter(r => r.prescriptions.length > 0).map((record) => (
                    <div key={record.id} className="border border-gray-200 rounded-lg p-4">
                      <p className="font-medium text-gray-900 mb-2">{formatDateTime(record.date)}</p>
                      <div className="space-y-2">
                        {record.prescriptions.map((rx, index) => (
                          <div key={index} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900">{rx.medication} - {rx.dosage}</p>
                              <p className="text-sm text-gray-600">{rx.frequency} for {rx.duration}</p>
                            </div>
                            <span className="text-sm text-gray-500">
                              Prescribed for: {record.finalDiagnosis}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDetailView;
