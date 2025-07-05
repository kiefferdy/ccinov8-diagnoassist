import React from 'react';
import { AlertCircle, Phone, Mail, Calendar, User, Shield, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PatientHeader = ({ patient }) => {
  const navigate = useNavigate();
  const age = React.useMemo(() => {
    const today = new Date();
    const birthDate = new Date(patient.demographics.dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  }, [patient.demographics.dateOfBirth]);

  const handleBack = () => {
    navigate('/patients');
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start">
          <button
            onClick={handleBack}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4">
            <User className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{patient.demographics.name}</h1>
            <div className="flex items-center text-sm text-gray-600 mt-1">
              <span>{age} years old</span>
              <span className="mx-2">•</span>
              <span>{patient.demographics.gender}</span>
              <span className="mx-2">•</span>
              <span>ID: {patient.id}</span>
            </div>
          </div>
        </div>
      </div>
      {/* Allergies Alert */}
      {patient.medicalBackground.allergies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <span className="font-medium text-red-900">Allergies:</span>
            <div className="ml-2 flex flex-wrap gap-2">
              {patient.medicalBackground.allergies.map((allergy, index) => (
                <span key={allergy.id} className="text-red-700">
                  {allergy.allergen} ({allergy.reaction})
                  {index < patient.medicalBackground.allergies.length - 1 && ', '}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Contact Information */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Contact Information</h3>
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <Phone className="w-4 h-4 mr-2" />
              {patient.demographics.phone}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Mail className="w-4 h-4 mr-2" />
              {patient.demographics.email}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="w-4 h-4 mr-2" />
              DOB: {new Date(patient.demographics.dateOfBirth).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* Current Medications */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Current Medications</h3>
          {patient.medicalBackground.medications.filter(m => m.ongoing).length > 0 ? (
            <ul className="space-y-1">
              {patient.medicalBackground.medications
                .filter(m => m.ongoing)
                .slice(0, 3)
                .map(med => (
                  <li key={med.id} className="text-sm text-gray-600">
                    • {med.name} {med.dosage} - {med.frequency}
                  </li>
                ))}
              {patient.medicalBackground.medications.filter(m => m.ongoing).length > 3 && (
                <li className="text-sm text-blue-600 cursor-pointer">
                  + {patient.medicalBackground.medications.filter(m => m.ongoing).length - 3} more
                </li>
              )}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No current medications</p>
          )}
        </div>

        {/* Chronic Conditions */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Chronic Conditions</h3>
          {patient.medicalBackground.chronicConditions.filter(c => c.status === 'active').length > 0 ? (
            <ul className="space-y-1">
              {patient.medicalBackground.chronicConditions
                .filter(c => c.status === 'active')
                .map(condition => (
                  <li key={condition.id} className="text-sm text-gray-600">
                    • {condition.condition} (ICD-10: {condition.icd10})
                  </li>
                ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No chronic conditions</p>
          )}
        </div>
      </div>

      {/* Insurance Info */}
      {patient.demographics.insuranceInfo?.provider && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center text-sm text-gray-600">
            <Shield className="w-4 h-4 mr-2" />
            <span>
              {patient.demographics.insuranceInfo.provider} - 
              Member ID: {patient.demographics.insuranceInfo.memberId}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientHeader;