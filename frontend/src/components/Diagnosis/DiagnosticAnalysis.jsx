import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  Activity, 
  ChevronRight, 
  ChevronLeft, 
  ThumbsUp, 
  ThumbsDown,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Loader,
  RefreshCw
} from 'lucide-react';

const DiagnosticAnalysis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [diagnoses, setDiagnoses] = useState([]);
  const [expandedDiagnosis, setExpandedDiagnosis] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [doctorNotes, setDoctorNotes] = useState('');
  
  useEffect(() => {
    // Initialize with mock diagnoses if not already set
    if (patientData.differentialDiagnoses.length === 0) {
      generateMockDiagnoses();
    } else {
      setDiagnoses(patientData.differentialDiagnoses);
    }
  }, []);
  
  const generateMockDiagnoses = () => {
    // This would be replaced with actual API call
    const mockDiagnoses = [
      {
        id: 1,
        name: "Community-Acquired Pneumonia",
        icd10: "J18.9",
        probability: 0.72,
        confidence: "High",
        explanation: "Based on the patient's productive cough, fever, and physical exam findings including crackles on auscultation, community-acquired pneumonia is the most likely diagnosis.",
        supportingEvidence: [
          "Productive cough with yellow sputum",
          "Fever (38.5°C)",
          "Elevated respiratory rate (22/min)",
          "Decreased oxygen saturation (94%)",
          "Crackles heard on chest auscultation"
        ],
        contradictingEvidence: [
          "No chest pain reported",
          "Normal blood pressure"
        ],
        recommendedTests: ["Chest X-ray", "Complete Blood Count", "Sputum Culture", "Blood Culture"]
      },
      {
        id: 2,
        name: "Acute Bronchitis",
        icd10: "J20.9",
        probability: 0.18,
        confidence: "Moderate",
        explanation: "Acute bronchitis could explain the cough and respiratory symptoms, though the presence of fever and decreased O2 saturation makes pneumonia more likely.",
        supportingEvidence: [
          "Productive cough",
          "Recent onset of symptoms",
          "No significant past medical history"
        ],
        contradictingEvidence: [
          "Presence of fever",
          "Decreased oxygen saturation",
          "Crackles on auscultation"
        ],
        recommendedTests: ["Chest X-ray", "Complete Blood Count"]
      },
      {
        id: 3,
        name: "COVID-19",
        icd10: "U07.1",
        probability: 0.10,
        confidence: "Low",
        explanation: "While COVID-19 should be considered given the respiratory symptoms and fever, the typical presentation and lack of reported exposure make it less likely.",
        supportingEvidence: [
          "Fever",
          "Cough",
          "Respiratory symptoms"
        ],
        contradictingEvidence: [
          "No reported exposure",
          "No loss of taste/smell",
          "Productive rather than dry cough"
        ],
        recommendedTests: ["COVID-19 RT-PCR", "Chest X-ray"]
      }
    ];
    
    setDiagnoses(mockDiagnoses);
    updatePatientData('differentialDiagnoses', mockDiagnoses);
  };
  
  const handleFeedback = (diagnosisId, type) => {
    setFeedback(prev => ({
      ...prev,
      [diagnosisId]: type
    }));
  };
  
  const handleRefreshAnalysis = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // In real app, this would incorporate the feedback and regenerate
    // For now, just slightly modify the probabilities
    const updatedDiagnoses = diagnoses.map(d => {
      if (feedback[d.id] === 'up') {
        return { ...d, probability: Math.min(d.probability + 0.1, 1) };
      } else if (feedback[d.id] === 'down') {
        return { ...d, probability: Math.max(d.probability - 0.1, 0) };
      }
      return d;
    }).sort((a, b) => b.probability - a.probability);
    
    setDiagnoses(updatedDiagnoses);
    updatePatientData('differentialDiagnoses', updatedDiagnoses);
    setIsRefreshing(false);
    setFeedback({});
  };
  
  const handleContinue = () => {
    if (doctorNotes) {
      updatePatientData('diagnosticNotes', doctorNotes);
    }
    setCurrentStep('tests');
  };
  
  const handleBack = () => {
    setCurrentStep('physical-exam');
  };
  
  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'High': return 'text-green-600 bg-green-50';
      case 'Moderate': return 'text-yellow-600 bg-yellow-50';
      case 'Low': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };
  
  const getProbabilityColor = (probability) => {
    if (probability >= 0.7) return 'bg-green-500';
    if (probability >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">AI Diagnostic Analysis</h2>
        <p className="text-gray-600">Review the AI-generated differential diagnoses based on the clinical data</p>
      </div>
      
      {/* Analysis Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-blue-900 mb-1">Analysis Complete</p>
            <p className="text-blue-800">Generated {diagnoses.length} differential diagnoses based on clinical findings</p>
          </div>
          <button
            onClick={handleRefreshAnalysis}
            disabled={isRefreshing || Object.keys(feedback).length === 0}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300"
          >
            {isRefreshing ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Analysis
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Differential Diagnoses */}
      <div className="space-y-4 mb-6">
        {diagnoses.map((diagnosis, index) => (
          <div
            key={diagnosis.id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="text-lg font-semibold text-gray-900 mr-2">
                      {index + 1}. {diagnosis.name}
                    </span>
                    <span className="text-sm text-gray-500">ICD-10: {diagnosis.icd10}</span>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {/* Probability Bar */}
                    <div className="flex items-center flex-1 max-w-xs">
                      <span className="text-sm text-gray-600 mr-2">Probability:</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className={`h-full rounded-full ${getProbabilityColor(diagnosis.probability)}`}
                          style={{ width: `${diagnosis.probability * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {(diagnosis.probability * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    {/* Confidence Badge */}
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(diagnosis.confidence)}`}>
                      {diagnosis.confidence} Confidence
                    </span>
                  </div>
                </div>
                
                {/* Feedback Buttons */}
                <div className="flex items-center ml-4 space-x-2">
                  <button
                    onClick={() => handleFeedback(diagnosis.id, feedback[diagnosis.id] === 'up' ? null : 'up')}
                    className={`p-2 rounded-lg transition-colors ${
                      feedback[diagnosis.id] === 'up'
                        ? 'bg-green-100 text-green-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    }`}
                    title="This diagnosis seems likely"
                  >
                    <ThumbsUp className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleFeedback(diagnosis.id, feedback[diagnosis.id] === 'down' ? null : 'down')}
                    className={`p-2 rounded-lg transition-colors ${
                      feedback[diagnosis.id] === 'down'
                        ? 'bg-red-100 text-red-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    }`}
                    title="This diagnosis seems unlikely"
                  >
                    <ThumbsDown className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              {/* Explanation */}
              <p className="text-gray-700 mb-4">{diagnosis.explanation}</p>
              
              {/* Expand/Collapse Details */}
              <button
                onClick={() => setExpandedDiagnosis(expandedDiagnosis === diagnosis.id ? null : diagnosis.id)}
                className="flex items-center text-blue-600 hover:text-blue-700 font-medium"
              >
                {expandedDiagnosis === diagnosis.id ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-1" />
                    Hide Details
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-1" />
                    Show Details
                  </>
                )}
              </button>
              
              {/* Expanded Details */}
              {expandedDiagnosis === diagnosis.id && (
                <div className="mt-4 space-y-4">
                  {/* Supporting Evidence */}
                  <div>
                    <h4 className="font-medium text-green-800 mb-2">Supporting Evidence:</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {diagnosis.supportingEvidence.map((evidence, idx) => (
                        <li key={idx} className="text-sm text-gray-700">{evidence}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Contradicting Evidence */}
                  {diagnosis.contradictingEvidence.length > 0 && (
                    <div>
                      <h4 className="font-medium text-red-800 mb-2">Contradicting Evidence:</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {diagnosis.contradictingEvidence.map((evidence, idx) => (
                          <li key={idx} className="text-sm text-gray-700">{evidence}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Recommended Tests */}
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">Recommended Tests:</h4>
                    <div className="flex flex-wrap gap-2">
                      {diagnosis.recommendedTests.map((test, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                        >
                          {test}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Doctor's Notes */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center mb-4">
          <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
          <span className="ml-2 text-sm text-gray-500">(Optional)</span>
        </div>
        
        <textarea
          value={doctorNotes}
          onChange={(e) => setDoctorNotes(e.target.value)}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Add any clinical notes, disagreements with the analysis, or additional considerations..."
        />
      </div>
      
      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          Continue to Tests
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default DiagnosticAnalysis;
