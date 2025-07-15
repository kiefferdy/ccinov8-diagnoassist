import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, Phone, Mail, AlertCircle, Calendar, ChevronLeft,
  MapPin, Heart, Pill, Activity, Edit, Shield, Info,
  FileText, Clock, Star, AlertTriangle, Droplets, 
  Stethoscope, CreditCard, UserCheck, Home, ChevronDown, ChevronUp
} from 'lucide-react';
import EditPatientModal from '../PatientManagement/EditPatientModal';

const PatientHeader = ({ patient }) => {
  const navigate = useNavigate();
  const [showFullInfo, setShowFullInfo] = useState(false);
  const [activeInfoTab, setActiveInfoTab] = useState('overview');
  const [showEditModal, setShowEditModal] = useState(false);
  
  const calculateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };
  
  const age = calculateAge(patient.demographics.dateOfBirth);
  
  // Get initials for avatar
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
  
  // Count active medications
  const activeMedications = patient.medicalBackground?.medications?.filter(m => m.ongoing).length || 0;
  
  // Risk indicators
  const riskFactors = [];
  if (patient.medicalBackground?.allergies?.some(a => a.severity === 'severe')) {
    riskFactors.push({ type: 'allergy', severity: 'high' });
  }
  if (age > 65) {
    riskFactors.push({ type: 'age', severity: 'medium' });
  }
  if (patient.medicalBackground?.chronicConditions?.length > 2) {
    riskFactors.push({ type: 'comorbidity', severity: 'medium' });
  }
  
  const infoTabs = [
    { id: 'overview', label: 'Overview', icon: Info },
    { id: 'medical', label: 'Medical', icon: Heart },
    { id: 'contact', label: 'Contact', icon: Phone },
    { id: 'insurance', label: 'Insurance', icon: CreditCard }
  ];
  
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Main Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            {/* Enhanced Avatar */}
            <div className="relative">
              <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border-2 border-white/30">
                <span className="text-2xl font-bold text-white">
                  {getInitials(patient.demographics.name)}
                </span>
              </div>
              {riskFactors.length > 0 && (
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center border-2 border-white">
                  <AlertTriangle className="w-3 h-3 text-white" />
                </div>
              )}
            </div>
            
            {/* Patient Info */}
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold">{patient.demographics.name}</h1>
                <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium">
                  ID: {patient.id}
                </span>
                {patient.vip && (
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                )}
              </div>
              
              <div className="mt-2 flex flex-wrap items-center gap-4 text-blue-100">
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  <span>{age} years • {patient.demographics.gender}</span>
                </div>
                <div className="flex items-center">
                  <Phone className="w-4 h-4 mr-1" />
                  <span>{patient.demographics.phone}</span>
                </div>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 mr-1" />
                  <span>{patient.demographics.email}</span>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="mt-4 flex flex-wrap gap-3">
                <div className="px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">Last Visit: {patient.lastVisit ? new Date(patient.lastVisit).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div className="px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg flex items-center">
                  <Pill className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">{activeMedications} Active Medications</span>
                </div>
                <div className="px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg flex items-center">
                  <Heart className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">{patient.medicalBackground?.chronicConditions?.length || 0} Chronic Conditions</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowEditModal(true)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              title="Edit patient information"
            >
              <Edit className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/patients')}
              className="flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-lg hover:bg-white/30 transition-colors"
            >
              <ChevronLeft className="w-5 h-5 mr-1" />
              Back
            </button>
          </div>
        </div>
      </div>
      
      {/* Critical Alerts Bar */}
      {patient.medicalBackground?.allergies?.length > 0 && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0" />
            <div className="flex-1">
              <span className="font-semibold text-red-800">Allergies: </span>
              <span className="text-red-700">
                {patient.medicalBackground.allergies.map(a => 
                  `${a.allergen} (${a.reaction}${a.severity === 'severe' ? ' - SEVERE' : ''})`
                ).join(' • ')}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Expandable Info Section */}
      <div className="border-t border-gray-100">
        <button
          onClick={() => setShowFullInfo(!showFullInfo)}
          className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <span className="text-sm font-medium text-gray-700">
            {showFullInfo ? 'Hide' : 'Show'} Complete Patient Information
          </span>
          {showFullInfo ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>
        
        {showFullInfo && (
          <div className="border-t border-gray-100">
            {/* Tab Navigation */}
            <div className="flex border-b border-gray-200 px-6">
              {infoTabs.map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveInfoTab(tab.id)}
                    className={`
                      flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors
                      ${activeInfoTab === tab.id
                        ? 'text-blue-600 border-blue-600'
                        : 'text-gray-500 border-transparent hover:text-gray-700'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
            
            {/* Tab Content */}
            <div className="p-6">
              {activeInfoTab === 'overview' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-sm font-medium text-gray-700">Date of Birth</span>
                    </div>
                    <p className="text-gray-900">{new Date(patient.demographics.dateOfBirth).toLocaleDateString()}</p>
                    <p className="text-sm text-gray-500">{age} years old</p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <UserCheck className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-sm font-medium text-gray-700">Patient Since</span>
                    </div>
                    <p className="text-gray-900">{new Date(patient.createdAt).toLocaleDateString()}</p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <Clock className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-sm font-medium text-gray-700">Last Updated</span>
                    </div>
                    <p className="text-gray-900">{new Date(patient.updatedAt).toLocaleDateString()}</p>
                  </div>
                </div>
              )}
              
              {activeInfoTab === 'medical' && (
                <div className="space-y-4">
                  {/* Chronic Conditions */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Heart className="w-4 h-4 mr-2 text-red-500" />
                      Chronic Conditions
                    </h4>
                    {patient.medicalBackground?.chronicConditions?.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {patient.medicalBackground.chronicConditions.map((condition, idx) => (
                          <div key={idx} className="bg-red-50 rounded-lg p-3 border border-red-200">
                            <p className="font-medium text-gray-900">{condition.condition}</p>
                            <p className="text-sm text-gray-600">ICD-10: {condition.icd10} • Since {new Date(condition.diagnosedDate).getFullYear()}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No chronic conditions documented</p>
                    )}
                  </div>
                  
                  {/* Current Medications */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Pill className="w-4 h-4 mr-2 text-blue-500" />
                      Current Medications
                    </h4>
                    {patient.medicalBackground?.medications?.filter(m => m.ongoing).length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {patient.medicalBackground.medications.filter(m => m.ongoing).map((med, idx) => (
                          <div key={idx} className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                            <p className="font-medium text-gray-900">{med.name}</p>
                            <p className="text-sm text-gray-600">{med.dosage} • {med.frequency}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No active medications</p>
                    )}
                  </div>
                  
                  {/* Medical History */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">Past Medical History</h5>
                      <p className="text-sm text-gray-600">
                        {patient.medicalBackground?.pastMedicalHistory || 'Not documented'}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">Family History</h5>
                      <p className="text-sm text-gray-600">
                        {patient.medicalBackground?.familyHistory || 'Not documented'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {activeInfoTab === 'contact' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-start">
                      <Phone className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Phone</p>
                        <p className="text-gray-900">{patient.demographics.phone}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start">
                      <Mail className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Email</p>
                        <p className="text-gray-900">{patient.demographics.email}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start">
                      <Home className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Address</p>
                        <p className="text-gray-900">{patient.demographics.address || 'Not provided'}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-start">
                      <UserCheck className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">Emergency Contact</p>
                        <p className="text-gray-900">{patient.demographics.emergencyContact || 'Not provided'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {activeInfoTab === 'insurance' && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center text-gray-500">
                    <CreditCard className="w-5 h-5 mr-2" />
                    <p className="text-sm">Insurance information not available in demo</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Edit Patient Modal */}
      {showEditModal && (
        <EditPatientModal
          patient={patient}
          onClose={() => setShowEditModal(false)}
        />
      )}
    </div>
  );
};

export default PatientHeader;