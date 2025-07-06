import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Phone, Mail, AlertCircle, Calendar, ChevronLeft } from 'lucide-react';

const PatientHeader = ({ patient }) => {
  const navigate = useNavigate();
  
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
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
            <User className="w-8 h-8 text-blue-600" />
          </div>
          
          <div className="ml-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">{patient.demographics.name}</h1>
              <span className="ml-3 text-sm text-gray-500">ID: {patient.id}</span>
            </div>
            
            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              <div className="flex items-center text-gray-600">
                <Calendar className="w-4 h-4 mr-2 flex-shrink-0" />
                {age} years old • {patient.demographics.gender} • DOB: {new Date(patient.demographics.dateOfBirth).toLocaleDateString()}
              </div>
              <div className="flex items-center text-gray-600">
                <Phone className="w-4 h-4 mr-2 flex-shrink-0" />
                {patient.demographics.phone}
              </div>
              <div className="flex items-center text-gray-600">
                <Mail className="w-4 h-4 mr-2 flex-shrink-0" />
                {patient.demographics.email}
              </div>
              {patient.demographics.address && (
                <div className="text-gray-600">
                  {patient.demographics.address}
                </div>
              )}
            </div>
            
            {/* Medical Alerts */}
            <div className="mt-3 flex flex-wrap gap-2">
              {patient.medicalBackground?.allergies?.length > 0 && (
                <div className="flex items-center bg-red-50 text-red-700 px-3 py-1 rounded-full text-sm">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  Allergies: {patient.medicalBackground.allergies.map(a => a.allergen).join(', ')}
                </div>
              )}
              
              {patient.medicalBackground?.chronicConditions?.length > 0 && (
                <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm">
                  Chronic: {patient.medicalBackground.chronicConditions.map(c => c.condition).join(', ')}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <button
          onClick={() => navigate('/patients')}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back to Patients
        </button>
      </div>
    </div>
  );
};

export default PatientHeader;