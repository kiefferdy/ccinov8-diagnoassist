import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { usePatient } from '../../contexts/PatientContext';
import { 
  Heart, 
  Thermometer, 
  Activity, 
  Wind, 
  Droplet,
  Ruler,
  Weight,
  ChevronRight,
  ChevronLeft,
  AlertCircle,
  FileText,
  ChevronDown,
  Info
} from 'lucide-react';
import FileUpload from '../common/FileUpload';

const PhysicalExam = () => {
  const { patientData, updatePhysicalExam, setCurrentStep } = usePatient();
  const [bmiCalculated, setBmiCalculated] = useState(false);
  const [showAdditionalFindings, setShowAdditionalFindings] = useState(false);
  const [examDocuments, setExamDocuments] = useState(patientData.physicalExam.examDocuments || []);
  
  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm({
    defaultValues: {
      ...patientData.physicalExam
    }
  });
  
  const watchHeight = watch('height');
  const watchWeight = watch('weight');
  
  // Calculate BMI when height and weight change
  useEffect(() => {
    if (watchHeight && watchWeight) {
      const heightInMeters = parseFloat(watchHeight) / 100;
      const weightInKg = parseFloat(watchWeight);
      
      if (heightInMeters > 0 && weightInKg > 0) {
        const bmi = (weightInKg / (heightInMeters * heightInMeters)).toFixed(1);
        setValue('bmi', bmi);
        setBmiCalculated(true);
      }
    }
  }, [watchHeight, watchWeight, setValue]);
  
  const onSubmit = async (data) => {
    // Update all physical exam data including documents
    Object.keys(data).forEach(key => {
      updatePhysicalExam(key, data[key]);
    });
    updatePhysicalExam('examDocuments', examDocuments);
    
    // In a real app, this would call an API to analyze the data
    // For now, we'll generate mock differential diagnoses
    await generateInitialDiagnosis(data);
    
    setCurrentStep('diagnostic-analysis');
  };
  
  const generateInitialDiagnosis = async (examData) => {
    // Mock function - replace with actual API call
    const mockDiagnoses = [
      {
        id: 1,
        name: "Hypertension",
        probability: 0.75,
        explanation: "Elevated blood pressure reading combined with patient's age and symptoms suggest primary hypertension.",
        supportingEvidence: ["Blood pressure: " + examData.bloodPressure, "Patient age", "Chief complaint"]
      },
      {
        id: 2,
        name: "Anxiety Disorder",
        probability: 0.45,
        explanation: "Elevated heart rate and blood pressure could be related to anxiety, especially given the patient's reported symptoms.",
        supportingEvidence: ["Elevated heart rate: " + examData.heartRate, "Blood pressure elevation", "Symptom pattern"]
      },
      {
        id: 3,
        name: "Thyroid Disorder",
        probability: 0.30,
        explanation: "Vital sign abnormalities could indicate hyperthyroidism. Further testing recommended.",
        supportingEvidence: ["Heart rate elevation", "Patient symptoms", "Physical exam findings"]
      }
    ];
    
    updatePhysicalExam('differentialDiagnoses', mockDiagnoses);
  };
  
  const handleBack = () => {
    setCurrentStep('clinical-assessment');
  };
  
  const getBMICategory = (bmi) => {
    const bmiValue = parseFloat(bmi);
    if (bmiValue < 18.5) return { category: 'Underweight', color: 'text-yellow-600' };
    if (bmiValue < 25) return { category: 'Normal', color: 'text-green-600' };
    if (bmiValue < 30) return { category: 'Overweight', color: 'text-orange-600' };
    return { category: 'Obese', color: 'text-red-600' };
  };
  
  const handleDocumentsChange = (files) => {
    setExamDocuments(files);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Physical Examination</h2>
        <p className="text-gray-600">Record the patient's vital signs and physical exam findings</p>
      </div>
      
      {/* Optional Fields Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-start">
          <Info className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-blue-800 text-sm">
            All fields in this section are optional. Fill in only the measurements and observations that are available or relevant to the patient's condition.
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Vital Signs Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Activity className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Vital Signs</h3>
            <span className="ml-2 text-sm text-gray-500">(Optional)</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Blood Pressure */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Heart className="w-4 h-4 mr-1 text-red-500" />
                  Blood Pressure (mmHg)
                </div>
              </label>
              <input
                type="text"
                {...register('bloodPressure', { 
                  pattern: {
                    value: /^\d{2,3}\/\d{2,3}$/,
                    message: 'Format: 120/80'
                  }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="120/80"
              />
              {errors.bloodPressure && (
                <p className="mt-1 text-sm text-red-600">{errors.bloodPressure.message}</p>
              )}
            </div>
            
            {/* Heart Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Activity className="w-4 h-4 mr-1 text-red-500" />
                  Heart Rate (bpm)
                </div>
              </label>
              <input
                type="number"
                {...register('heartRate', { 
                  min: { value: 30, message: 'Heart rate seems too low' },
                  max: { value: 250, message: 'Heart rate seems too high' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="72"
              />
              {errors.heartRate && (
                <p className="mt-1 text-sm text-red-600">{errors.heartRate.message}</p>
              )}
            </div>
            
            {/* Temperature */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Thermometer className="w-4 h-4 mr-1 text-orange-500" />
                  Temperature (°C)
                </div>
              </label>
              <input
                type="number"
                step="0.1"
                {...register('temperature', {
                  min: { value: 35, message: 'Temperature seems too low' },
                  max: { value: 42, message: 'Temperature seems too high' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="36.5"
              />
              {errors.temperature && (
                <p className="mt-1 text-sm text-red-600">{errors.temperature.message}</p>
              )}
            </div>
            
            {/* Respiratory Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Wind className="w-4 h-4 mr-1 text-blue-500" />
                  Respiratory Rate (breaths/min)
                </div>
              </label>
              <input
                type="number"
                {...register('respiratoryRate', {
                  min: { value: 8, message: 'Respiratory rate seems too low' },
                  max: { value: 40, message: 'Respiratory rate seems too high' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="16"
              />
              {errors.respiratoryRate && (
                <p className="mt-1 text-sm text-red-600">{errors.respiratoryRate.message}</p>
              )}
            </div>
            
            {/* Oxygen Saturation */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Droplet className="w-4 h-4 mr-1 text-blue-500" />
                  Oxygen Saturation (%)
                </div>
              </label>
              <input
                type="number"
                {...register('oxygenSaturation', {
                  min: { value: 70, message: 'O2 saturation seems too low' },
                  max: { value: 100, message: 'O2 saturation cannot exceed 100%' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="98"
              />
              {errors.oxygenSaturation && (
                <p className="mt-1 text-sm text-red-600">{errors.oxygenSaturation.message}</p>
              )}
            </div>
          </div>
        </div>
        
        {/* Physical Measurements Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Ruler className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Physical Measurements</h3>
            <span className="ml-2 text-sm text-gray-500">(Optional)</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Height */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Ruler className="w-4 h-4 mr-1 text-gray-500" />
                  Height (cm)
                </div>
              </label>
              <input
                type="number"
                {...register('height', {
                  min: { value: 50, message: 'Height seems too low' },
                  max: { value: 250, message: 'Height seems too high' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="170"
              />
              {errors.height && (
                <p className="mt-1 text-sm text-red-600">{errors.height.message}</p>
              )}
            </div>
            
            {/* Weight */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center">
                  <Weight className="w-4 h-4 mr-1 text-gray-500" />
                  Weight (kg)
                </div>
              </label>
              <input
                type="number"
                step="0.1"
                {...register('weight', {
                  min: { value: 10, message: 'Weight seems too low' },
                  max: { value: 300, message: 'Weight seems too high' }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="70"
              />
              {errors.weight && (
                <p className="mt-1 text-sm text-red-600">{errors.weight.message}</p>
              )}
            </div>
            
            {/* BMI */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                BMI (Auto-calculated)
              </label>
              <div className="relative">
                <input
                  type="text"
                  {...register('bmi')}
                  readOnly
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  placeholder="Auto-calculated"
                />
                {bmiCalculated && watch('bmi') && (
                  <div className={`mt-1 text-sm font-medium ${getBMICategory(watch('bmi')).color}`}>
                    {getBMICategory(watch('bmi')).category}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Additional Findings Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <button
            type="button"
            onClick={() => setShowAdditionalFindings(!showAdditionalFindings)}
            className="w-full flex items-center justify-between mb-4"
          >
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Additional Physical Exam Findings</h3>
              <span className="ml-2 text-sm text-gray-500">(Optional)</span>
            </div>
            <ChevronDown className={`w-5 h-5 text-gray-400 transform transition-transform ${showAdditionalFindings ? 'rotate-180' : ''}`} />
          </button>
          
          {showAdditionalFindings && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clinical Observations
                </label>
                <textarea
                  {...register('additionalFindings')}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Note any additional physical exam findings, abnormalities, or observations..."
                />
              </div>
              
              <div>
                <FileUpload
                  label="Attach Exam Documentation"
                  description="Upload photos of physical findings, exam notes, or diagnostic images"
                  acceptedFormats="image/*,.pdf,.doc,.docx"
                  maxFiles={8}
                  maxSizeMB={15}
                  onFilesChange={handleDocumentsChange}
                  existingFiles={examDocuments}
                />
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Common Physical Exam Documentation:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Photos of skin lesions, rashes, or visible symptoms</li>
                  <li>• ECG strips or rhythm strips</li>
                  <li>• Dermatoscopy images</li>
                  <li>• Otoscopy or ophthalmoscopy findings</li>
                  <li>• Hand-drawn diagrams of physical findings</li>
                </ul>
              </div>
            </div>
          )}
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
            Generate Diagnostic Analysis
            <ChevronRight className="ml-2 w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default PhysicalExam;