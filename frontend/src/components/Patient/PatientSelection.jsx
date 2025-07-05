import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  Users, 
  Search, 
  UserPlus,
  ChevronRight,
  Calendar,
  Phone,
  Mail,
  Clock,
  Activity,
  Home
} from 'lucide-react';

const PatientSelection = () => {
  const { setPatientData, setCurrentStep } = usePatient();
  const { patients } = useAppData();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showNewPatient, setShowNewPatient] = useState(false);
  
  // Filter patients based on search
  const filteredPatients = patients.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone.includes(searchTerm)
  );
  
  const handleSelectPatient = (patient) => {
    // Store the patient ID being viewed
    setPatientData({
      viewingPatientId: patient.id
    });
    
    // Navigate to patient detail view (Visit Records tab)
    setCurrentStep('patient-detail');
  };
  
  const handleNewPatient = () => {
    // Reset patient data for new patient
    setPatientData({
      id: null,
      name: '',
      age: '',
      gender: '',
      dateOfBirth: '',
      chiefComplaint: '',
      chiefComplaintDetails: [],
      additionalClinicalNotes: '',
      medicalHistory: [],
      medications: [],
      allergies: [],
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
    
    setCurrentStep('patient-info');
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
    <div className="max-w-4xl mx-auto">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Start Patient Assessment</h2>
          <p className="text-gray-600">Select an existing patient or create a new patient record</p>
        </div>
        <button
          onClick={() => setCurrentStep('home')}
          className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Home className="w-5 h-5 mr-2" />
          Back to Home
        </button>
      </div>
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => setShowNewPatient(false)}
            className={`p-6 rounded-lg border-2 transition-all ${
              !showNewPatient 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Users className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Existing Patient</h3>
            <p className="text-sm text-gray-600">Select from registered patients</p>
          </button>
          
          <button
            onClick={() => setShowNewPatient(true)}
            className={`p-6 rounded-lg border-2 transition-all ${
              showNewPatient 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <UserPlus className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-1">New Patient</h3>
            <p className="text-sm text-gray-600">Create a new patient record</p>
          </button>
        </div>
      </div>
      
      {!showNewPatient ? (
        <>
          {/* Search Bar */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search patients by name, ID, or phone..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Patient List */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Select Patient ({filteredPatients.length})
              </h3>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {filteredPatients.length === 0 ? (
                <div className="p-12 text-center">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No patients found</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {filteredPatients.map(patient => (
                    <div
                      key={patient.id}
                      onClick={() => setSelectedPatient(patient)}
                      className={`p-6 cursor-pointer transition-all hover:bg-gray-50 ${
                        selectedPatient?.id === patient.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <h4 className="text-lg font-medium text-gray-900">{patient.name}</h4>
                            <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                              {patient.id}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-2">
                            <span>{calculateAge(patient.dateOfBirth)} years • {patient.gender}</span>
                            <span className="flex items-center">
                              <Clock className="w-4 h-4 mr-1" />
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
                        </div>
                        
                        {selectedPatient?.id === patient.id && (
                          <ChevronRight className="w-5 h-5 text-blue-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {selectedPatient && (
              <div className="p-6 border-t border-gray-200 bg-gray-50">
                <button
                  onClick={() => handleSelectPatient(selectedPatient)}
                  className="w-full flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Activity className="w-5 h-5 mr-2" />
                  Start Assessment for {selectedPatient.name}
                </button>
              </div>
            )}
          </div>
        </>
      ) : (
        /* New Patient */
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <UserPlus className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Create New Patient</h3>
            <p className="text-gray-600 mb-6">You'll enter patient details in the next step</p>
            <button
              onClick={handleNewPatient}
              className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
            >
              Continue to Patient Information
              <ChevronRight className="ml-2 w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientSelection;
