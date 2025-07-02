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
  RefreshCw
} from 'lucide-react';
import { generateEnhancedAIResponse, updateDiagnosesFromChat } from './components/AIResponseGenerator';

const DiagnosticAnalysis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [doctorDiagnosis, setDoctorDiagnosis] = useState(patientData.doctorDiagnosis || '');
  const [diagnosticNotes, setDiagnosticNotes] = useState(patientData.diagnosticNotes || '');
  const [diagnoses, setDiagnoses] = useState(patientData.differentialDiagnoses || []);
  const [showAI, setShowAI] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAskedAI, setHasAskedAI] = useState(false);
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
    updatePatientData('differentialDiagnoses', []);
    
    // Show success
    setErrors({});
  };
  
  const handleAskAI = async () => {
    if (!doctorDiagnosis.trim()) {
      setErrors({ doctorDiagnosis: 'Please enter your diagnosis first' });
      return;
    }
    
    setIsAnalyzing(true);
    setShowAI(true);
    
    // Simulate AI analysis
    await new Promise(resolve => setTimeout(resolve, 2000));    
    // Generate AI differential diagnoses based on doctor's input
    const generatedDiagnoses = [
      {
        id: 1,
        name: "Community-Acquired Pneumonia",
        icd10: "J18.9",
        probability: 0.75,
        severity: "moderate",
        confidence: "high",
        supportingFactors: [
          "Productive cough with fever",
          "Elevated heart rate (102 bpm)",
          "Decreased breath sounds in lower right lobe",
          "Patient appears acutely ill"
        ],
        contradictingFactors: [
          "No significant dyspnea reported",
          "Oxygen saturation normal (98%)"
        ],
        clinicalPearls: "Consider atypical pathogens if patient doesn't respond to initial antibiotics",
        recommendedActions: ["Chest X-ray", "CBC with differential", "Procalcitonin", "Blood cultures if severe"]
      },
      {
        id: 2,
        name: "Acute Bronchitis",
        icd10: "J20.9",
        probability: 0.65,
        severity: "mild",
        confidence: "moderate",
        supportingFactors: [
          "Productive cough",
          "Fever present",
          "Recent URI symptoms"
        ],
        contradictingFactors: [
          "Physical exam suggests consolidation",
          "Patient appears more acutely ill than typical bronchitis"
        ],
        clinicalPearls: "Bronchitis typically doesn't cause focal lung findings on exam",
        recommendedActions: ["Chest X-ray to rule out pneumonia", "Supportive care"]
      }
    ];    
    setDiagnoses(generatedDiagnoses);
    updatePatientData('differentialDiagnoses', generatedDiagnoses);
    setIsAnalyzing(false);
    setHasAskedAI(true);
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
            <div className="flex items-center mb-6">
              <Activity className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Clinical Diagnosis</h3>
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
                  Diagnostic Notes (Optional)
                </label>
                <textarea
                  value={diagnosticNotes}
                  onChange={(e) => setDiagnosticNotes(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                  placeholder="Additional notes about your diagnosis, severity assessment, or clinical reasoning..."
                />
              </div>              
              <div className="flex items-center justify-between pt-4 border-t">
                <button
                  onClick={handleSaveDiagnosis}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Diagnosis
                </button>
                
                {doctorDiagnosis && (
                  <button
                    onClick={handleAskAI}
                    disabled={isAnalyzing}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center disabled:bg-gray-400"
                  >
                    {isAnalyzing ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Ask AI
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
          
          {/* AI Differential Diagnoses */}
          {showAI && diagnoses.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center mb-6">
                <Bot className="w-5 h-5 text-purple-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">AI Differential Diagnoses</h3>
                <span className="ml-2 text-sm text-gray-500">For consideration only</span>
              </div>              
              <div className="space-y-4">
                {diagnoses.map((diagnosis) => (
                  <div key={diagnosis.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{diagnosis.name}</h4>
                        <p className="text-sm text-gray-600">ICD-10: {diagnosis.icd10}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue-600">{Math.round(diagnosis.probability * 100)}%</div>
                        <p className="text-xs text-gray-500">Confidence: {diagnosis.confidence}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm font-medium text-green-700 mb-1">Supporting Factors:</p>
                        <ul className="text-sm text-gray-600 ml-4">
                          {diagnosis.supportingFactors.map((factor, idx) => (
                            <li key={idx}>• {factor}</li>
                          ))}
                        </ul>
                      </div>
                      
                      {diagnosis.contradictingFactors.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-red-700 mb-1">Contradicting Factors:</p>
                          <ul className="text-sm text-gray-600 ml-4">
                            {diagnosis.contradictingFactors.map((factor, idx) => (
                              <li key={idx}>• {factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {diagnosis.clinicalPearls && (
                        <div className="mt-3 p-3 bg-yellow-50 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            <Lightbulb className="w-4 h-4 inline mr-1" />
                            {diagnosis.clinicalPearls}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
          
          {/* Clinical Tips */}
          <div className="bg-blue-50 rounded-xl p-4">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2" />
              Clinical Tips
            </h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• Consider the most common diagnoses first</li>
              <li>• Don't forget to rule out serious conditions</li>
              <li>• Document your clinical reasoning</li>
              <li>• AI suggestions are for reference only</li>
            </ul>
          </div>
          
          {/* Red Flags */}
          {patientData.redFlags && patientData.redFlags.length > 0 && (
            <div className="bg-red-50 rounded-xl p-4">
              <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                <AlertCircle className="w-4 h-4 mr-2" />
                Clinical Red Flags
              </h4>
              <ul className="space-y-1 text-sm text-red-800">
                {patientData.redFlags.map((flag, idx) => (
                  <li key={idx}>• {flag}</li>
                ))}
              </ul>
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