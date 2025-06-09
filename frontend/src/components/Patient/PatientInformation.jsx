import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { usePatient } from '../../contexts/PatientContext';
import { User, Calendar, Heart, AlertCircle, ChevronRight } from 'lucide-react';

const PatientInformation = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      name: patientData.name,
      age: patientData.age,
      gender: patientData.gender,
      dateOfBirth: patientData.dateOfBirth,
      chiefComplaint: patientData.chiefComplaint
    }
  });
  
  const [showMedicalHistory, setShowMedicalHistory] = useState(false);
  const [newCondition, setNewCondition] = useState('');
  const [newMedication, setNewMedication] = useState('');
  const [newAllergy, setNewAllergy] = useState('');
  
  const watchAge = watch('age');
  
  const onSubmit = (data) => {
    Object.keys(data).forEach(key => {
      updatePatientData(key, data[key]);
    });
    setCurrentStep('clinical-assessment');
  };
  
  const addCondition = () => {
    if (newCondition.trim()) {
      updatePatientData('medicalHistory', [...patientData.medicalHistory, newCondition]);
      setNewCondition('');
    }
  };
  
  const addMedication = () => {
    if (newMedication.trim()) {
      updatePatientData('medications', [...patientData.medications, newMedication]);
      setNewMedication('');
    }
  };
  
  const addAllergy = () => {
    if (newAllergy.trim()) {
      updatePatientData('allergies', [...patientData.allergies, newAllergy]);
      setNewAllergy('');
    }
  };
  
  const removeItem = (field, index) => {
    const newArray = [...patientData[field]];
    newArray.splice(index, 1);
    updatePatientData(field, newArray);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Patient Information</h2>
        <p className="text-gray-600">Enter the patient's basic information and chief complaint</p>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <User className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Patient Name *
              </label>
              <input
                type="text"
                {...register('name', { required: 'Patient name is required' })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="John Doe"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age *
              </label>
              <input
                type="number"
                {...register('age', { 
                  required: 'Age is required',
                  min: { value: 0, message: 'Age must be positive' },
                  max: { value: 150, message: 'Please enter a valid age' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="35"
              />
              {errors.age && (
                <p className="mt-1 text-sm text-red-600">{errors.age.message}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gender *
              </label>
              <select
                {...register('gender', { required: 'Gender is required' })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
              {errors.gender && (
                <p className="mt-1 text-sm text-red-600">{errors.gender.message}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date of Birth
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  {...register('dateOfBirth')}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>
        
        {/* Chief Complaint Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Heart className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Chief Complaint</h3>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What brings the patient in today? *
            </label>
            <textarea
              {...register('chiefComplaint', { required: 'Chief complaint is required' })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe the patient's main concern or symptoms..."
            />
            {errors.chiefComplaint && (
              <p className="mt-1 text-sm text-red-600">{errors.chiefComplaint.message}</p>
            )}
          </div>
        </div>
        
        {/* Medical History Card (Optional) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <button
            type="button"
            onClick={() => setShowMedicalHistory(!showMedicalHistory)}
            className="w-full flex items-center justify-between mb-4"
          >
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Medical History</h3>
              <span className="ml-2 text-sm text-gray-500">(Optional)</span>
            </div>
            <ChevronRight className={`w-5 h-5 text-gray-400 transform transition-transform ${showMedicalHistory ? 'rotate-90' : ''}`} />
          </button>
          
          {showMedicalHistory && (
            <div className="space-y-6">
              {/* Past Medical Conditions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Past Medical Conditions
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newCondition}
                    onChange={(e) => setNewCondition(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCondition())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Type condition and press Enter"
                  />
                  <button
                    type="button"
                    onClick={addCondition}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {patientData.medicalHistory.map((condition, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                    >
                      {condition}
                      <button
                        type="button"
                        onClick={() => removeItem('medicalHistory', index)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Current Medications */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Medications
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newMedication}
                    onChange={(e) => setNewMedication(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMedication())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Type medication and press Enter"
                  />
                  <button
                    type="button"
                    onClick={addMedication}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {patientData.medications.map((medication, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                    >
                      {medication}
                      <button
                        type="button"
                        onClick={() => removeItem('medications', index)}
                        className="ml-2 text-green-600 hover:text-green-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Allergies
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newAllergy}
                    onChange={(e) => setNewAllergy(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Type allergy and press Enter"
                  />
                  <button
                    type="button"
                    onClick={addAllergy}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {patientData.allergies.map((allergy, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800"
                    >
                      {allergy}
                      <button
                        type="button"
                        onClick={() => removeItem('allergies', index)}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            Continue to Clinical Assessment
            <ChevronRight className="ml-2 w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientInformation;
