import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  ChevronRight, 
  ChevronLeft,
  Brain,
  AlertCircle,
  CheckCircle,
  Activity,
  Lightbulb,
  FileText,
  User,
  Save,
  Bot,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react';
import ClinicalInsightsPanel from './components/ClinicalInsightsPanel';

const DiagnosticAnalysis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [doctorDiagnosis, setDoctorDiagnosis] = useState(patientData.doctorDiagnosis || '');
  const [diagnosticNotes, setDiagnosticNotes] = useState(patientData.diagnosticNotes || '');
  const [showInsights, setShowInsights] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errors, setErrors] = useState({});
  
  const handleSaveDiagnosis = () => {
    // Validate doctor's diagnosis
    const newErrors = {};
    if (!doctorDiagnosis.trim()) {
      newErrors.doctorDiagnosis = 'Please enter your diagnosis';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Save doctor's diagnosis
    updatePatientData('doctorDiagnosis', doctorDiagnosis);
    updatePatientData('diagnosticNotes', diagnosticNotes);
    
    // Show success
    setErrors({});
  };
  
  const handleToggleInsights = () => {
    if (!showInsights && !patientData.hasViewedInsights) {
      setIsAnalyzing(true);
      setTimeout(() => {
        setIsAnalyzing(false);
        updatePatientData('hasViewedInsights', true);
      }, 1000);
    }
    setShowInsights(!showInsights);
  };
  
  const handleRefreshInsights = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 1500);
  };
  
  const handleContinue = () => {
    if (!doctorDiagnosis.trim()) {
      setErrors({ doctorDiagnosis: 'Please enter your diagnosis before continuing' });
      return;
    }
    
    // Save final data
    updatePatientData('doctorDiagnosis', doctorDiagnosis);
    updatePatientData('diagnosticNotes', diagnosticNotes);
    
    setCurrentStep('recommended-tests');
  };
  
  const handleBack = () => {
    setCurrentStep('physical-exam');
  };  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Assessment (A)</h2>
        <p className="text-gray-600">Document your clinical diagnosis based on the subjective and objective findings</p>
      </div>
      
      {/* Patient Context */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-blue-900 mb-1">Chief Complaint:</p>
            <p className="text-lg text-blue-800">{patientData.chiefComplaint}</p>
          </div>
          <div className="flex items-center text-sm text-blue-700">
            <User className="w-4 h-4 mr-1" />
            {patientData.name}, {patientData.age} {patientData.gender}
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Doctor's Diagnosis Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">Clinical Diagnosis</h3>
              </div>
              <button
                onClick={handleToggleInsights}
                className={`text-sm px-3 py-1 rounded-lg transition-colors flex items-center
                  ${showInsights 
                    ? 'bg-purple-100 text-purple-700 hover:bg-purple-200' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
              >
                {showInsights ? (
                  <>
                    <EyeOff className="w-4 h-4 mr-1" />
                    Hide Insights
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4 mr-1" />
                    Show Insights
                  </>
                )}
              </button>
            </div>            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Diagnosis *
                </label>
                <input
                  type="text"
                  value={doctorDiagnosis}
                  onChange={(e) => {
                    setDoctorDiagnosis(e.target.value);
                    if (errors.doctorDiagnosis) {
                      setErrors({ ...errors, doctorDiagnosis: null });
                    }
                  }}
                  className={`w-full px-4 py-2 border ${
                    errors.doctorDiagnosis ? 'border-red-300' : 'border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all`}
                  placeholder="Enter your primary diagnosis (e.g., Community-acquired pneumonia)"
                />
                {errors.doctorDiagnosis && (
                  <p className="mt-1 text-sm text-red-600">{errors.doctorDiagnosis}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clinical Reasoning & Notes (Optional)
                </label>
                <textarea
                  value={diagnosticNotes}
                  onChange={(e) => setDiagnosticNotes(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                  placeholder="Document your clinical reasoning, differential considerations, severity assessment, or any factors that influenced your diagnosis..."
                />
              </div>
              
              <div className="pt-4">
                <button
                  onClick={handleSaveDiagnosis}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Diagnosis
                </button>
              </div>
            </div>
          </div>
          
          {/* Clinical Insights Panel - Only shown when toggled */}
          {showInsights && (
            <ClinicalInsightsPanel 
              patientData={patientData}
              isAnalyzing={isAnalyzing}
              onRefresh={handleRefreshInsights}
            />
          )}
        </div>        
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          {/* Quick Summary */}
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Assessment Summary
            </h4>
            <div className="space-y-2 text-sm">
              <div>
                <p className="text-gray-600">Subjective findings:</p>
                <p className="text-gray-900">
                  {patientData.chiefComplaintDetails?.length || 0} clinical details documented
                </p>
              </div>
              <div>
                <p className="text-gray-600">Objective findings:</p>
                <p className="text-gray-900">
                  Vitals and physical exam completed
                </p>
              </div>
              {doctorDiagnosis && (
                <div className="pt-2 border-t">
                  <p className="text-gray-600">Your diagnosis:</p>
                  <p className="text-gray-900 font-medium">{doctorDiagnosis}</p>
                </div>
              )}
            </div>
          </div>
          
          {/* Quick Tips */}
          <div className="bg-blue-50 rounded-xl p-4">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2" />
              Assessment Tips
            </h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• Synthesize subjective and objective findings</li>
              <li>• Consider the most likely diagnosis first</li>
              <li>• Document your clinical reasoning</li>
              <li>• Think about what to rule out</li>
              <li>• Clinical insights are optional aids only</li>
            </ul>
          </div>
          
          {/* Info about Insights */}
          {!showInsights && (
            <div className="bg-purple-50 rounded-xl p-4">
              <h4 className="font-semibold text-purple-900 mb-2 flex items-center">
                <Brain className="w-4 h-4 mr-2" />
                AI Clinical Insights
              </h4>
              <p className="text-sm text-purple-800 mb-3">
                Optional AI-powered insights can help you:
              </p>
              <ul className="space-y-1 text-sm text-purple-700">
                <li>• Identify red flags</li>
                <li>• Consider differentials</li>
                <li>• Review diagnostic approaches</li>
                <li>• Access clinical pearls</li>
              </ul>
              <button
                onClick={handleToggleInsights}
                className="mt-3 w-full px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
              >
                Show Clinical Insights
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md"
        >
          Continue to Plan
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default DiagnosticAnalysis;