import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { usePatient } from '../../contexts/PatientContext';
import { 
  User, 
  Calendar, 
  AlertCircle, 
  ChevronRight, 
  FileText,
  Pill,
  Activity,
  Cake
} from 'lucide-react';
import FileUpload from '../common/FileUpload';

const PatientInformation = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      name: patientData.name,
      age: patientData.age,
      gender: patientData.gender,
      dateOfBirth: patientData.dateOfBirth
    }
  });
  
  const [newCondition, setNewCondition] = useState('');
  const [newMedication, setNewMedication] = useState('');
  const [newAllergy, setNewAllergy] = useState('');
  const [relatedDocuments, setRelatedDocuments] = useState(patientData.relatedDocuments || []);
  
  const watchAge = watch('age');
  
  const onSubmit = (data) => {
    Object.keys(data).forEach(key => {
      updatePatientData(key, data[key]);
    });
    // Save related documents
    updatePatientData('relatedDocuments', relatedDocuments);
    setCurrentStep('chief-complaint');
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
  
  const handleDocumentsChange = (files) => {
    setRelatedDocuments(files);
  };  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Patient Demographics</h2>
        <p className="text-gray-600">
          {patientData.id ? `Reviewing information for ${patientData.name}` : 'Enter the patient\'s demographic information'}
        </p>
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
                Patient Name {!patientData.id && '*'}
              </label>
              <input
                type="text"
                {...register('name', { required: !patientData.id ? 'Patient name is required' : false })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:text-gray-600"
                placeholder="John Doe"
                disabled={!!patientData.id}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age {!patientData.id && '*'}
              </label>
              <input
                type="number"
                {...register('age', { 
                  required: !patientData.id ? 'Age is required' : false,
                  min: { value: 0, message: 'Age must be positive' },
                  max: { value: 150, message: 'Please enter a valid age' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:text-gray-600"
                placeholder="35"
                disabled={!!patientData.id}
              />
              {errors.age && (
                <p className="mt-1 text-sm text-red-600">{errors.age.message}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gender {!patientData.id && '*'}
              </label>
              <select
                {...register('gender', { required: !patientData.id ? 'Gender is required' : false })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:text-gray-600"
                disabled={!!patientData.id}
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              {errors.gender && (
                <p className="mt-1 text-sm text-red-600">{errors.gender.message}</p>
              )}
            </div>            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Birthday {!patientData.id && '*'}
              </label>
              <div className="relative">
                <Cake className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  {...register('dateOfBirth', { required: !patientData.id ? 'Birthday is required' : false })}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:text-gray-600"
                  disabled={!!patientData.id}
                />
                {errors.dateOfBirth && (
                  <p className="mt-1 text-sm text-red-600">{errors.dateOfBirth.message}</p>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Allergies Card - Now Prominent */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Allergies</h3>
            <span className="ml-2 text-sm text-red-600">*Critical Safety Information</span>
          </div>          
          <div>
            <div className="flex space-x-2 mb-3">
              <input
                type="text"
                value={newAllergy}
                onChange={(e) => setNewAllergy(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all"
                placeholder="Enter allergy (drug, food, environmental, etc.)"
              />
              <button
                type="button"
                onClick={addAllergy}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Add
              </button>
            </div>
            {patientData.allergies.length === 0 ? (
              <div className="p-4 bg-gray-50 rounded-lg text-center">
                <p className="text-gray-600">No known allergies (NKDA)</p>
              </div>
            ) : (
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
            )}
          </div>
        </div>
        {/* Medical History Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Activity className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Medical History</h3>
          </div>
          
          <div className="space-y-6">
            {patientData.id && (patientData.medicalHistory.length > 0 || patientData.medications.length > 0) && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Medical history has been pre-filled from previous records. You can add or remove items as needed.
                </p>
              </div>
            )}
            
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
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Type condition and press Enter"
                />
                <button
                  type="button"
                  onClick={addCondition}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>              <div className="flex flex-wrap gap-2">
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
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Type medication and press Enter"
                />
                <button
                  type="button"
                  onClick={addMedication}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>              <div className="flex flex-wrap gap-2">
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
          </div>
        </div>

        {/* Related Documents Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <FileText className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Related Documents</h3>
            <span className="ml-2 text-sm text-gray-500">(Optional)</span>
          </div>
          
          <p className="text-sm text-gray-600 mb-4">
            Upload any relevant documents such as previous test results, referral notes, or medical records.
          </p>          
          <FileUpload
            label="Upload Medical Documents"
            description="Drag and drop images, PDFs, or documents"
            acceptedFormats="image/*,.pdf,.doc,.docx,.txt"
            maxFiles={10}
            maxSizeMB={20}
            onFilesChange={handleDocumentsChange}
            existingFiles={relatedDocuments}
          />
        </div>
        
        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md"
          >
            Continue to Chief Complaint
            <ChevronRight className="ml-2 w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientInformation;