import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  Heart, 
  ChevronRight, 
  ChevronLeft,
  MessageSquare,
  AlertCircle,
  Clock,
  Calendar,
  User
} from 'lucide-react';

const ChiefComplaint = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [chiefComplaint, setChiefComplaint] = useState(patientData.chiefComplaint || '');
  const [duration, setDuration] = useState('');
  const [onset, setOnset] = useState('');
  const [errors, setErrors] = useState({});
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate chief complaint
    const newErrors = {};
    if (!chiefComplaint.trim()) {
      newErrors.chiefComplaint = 'Chief complaint is required';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Update patient data
    updatePatientData('chiefComplaint', chiefComplaint);
    if (duration) updatePatientData('chiefComplaintDuration', duration);
    if (onset) updatePatientData('chiefComplaintOnset', onset);
    
    // Move to next step (Subjective assessment)
    setCurrentStep('clinical-assessment');
  };
  
  const handleBack = () => {
    setCurrentStep('patient-info');
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Chief Complaint</h2>
        <p className="text-gray-600">
          What brings the patient in today? This is the starting point for the assessment.
        </p>
      </div>
      
      {/* Patient Context */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <User className="w-5 h-5 text-blue-600 mr-2" />
          <span className="font-medium text-blue-900">
            {patientData.name}, {patientData.age} years old, {patientData.gender}
          </span>
        </div>
        {patientData.allergies && patientData.allergies.length > 0 && (
          <div className="mt-2 flex items-start">
            <AlertCircle className="w-4 h-4 text-red-600 mr-2 mt-0.5" />
            <span className="text-sm text-red-800">
              Allergies: {patientData.allergies.join(', ')}
            </span>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Chief Complaint Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Heart className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Primary Concern</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chief Complaint *
              </label>
              <textarea
                value={chiefComplaint}
                onChange={(e) => {
                  setChiefComplaint(e.target.value);
                  if (errors.chiefComplaint) {
                    setErrors({ ...errors, chiefComplaint: null });
                  }
                }}
                rows={4}
                className={`w-full px-4 py-2 border ${
                  errors.chiefComplaint ? 'border-red-300' : 'border-gray-300'
                } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none`}
                placeholder="Describe the patient's main concern or symptoms in their own words..."
                autoFocus
              />
              {errors.chiefComplaint && (
                <p className="mt-1 text-sm text-red-600">{errors.chiefComplaint}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                Tip: Use the patient's own words when possible (e.g., "chest feels tight" rather than "dyspnea")
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (Optional)
                </label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="e.g., 3 days, 2 weeks"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Onset (Optional)
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={onset}
                    onChange={(e) => setOnset(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="e.g., Sudden, gradual"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Quick Tips */}
        <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <div className="flex items-start">
            <MessageSquare className="w-5 h-5 text-gray-600 mr-2 mt-0.5" />
            <div className="text-sm text-gray-600">
              <p className="font-medium mb-1">Best Practices:</p>
              <ul className="space-y-1 ml-4">
                <li>• Be specific but concise</li>
                <li>• Include timeline when relevant</li>
                <li>• Note any associated symptoms mentioned</li>
                <li>• Document exactly what the patient says</li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={handleBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
          >
            <ChevronLeft className="mr-2 w-5 h-5" />
            Back
          </button>
          
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md"
          >
            Continue to Subjective Assessment
            <ChevronRight className="ml-2 w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChiefComplaint;