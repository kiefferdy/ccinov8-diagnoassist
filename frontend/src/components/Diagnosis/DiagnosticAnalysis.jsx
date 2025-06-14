import React, { useState, useEffect, useRef } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  ChevronRight, 
  ChevronLeft,
  Send,
  Bot,
  User,
  Sparkles,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Brain,
  MessageSquare,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  Activity,
  BarChart3,
  FileText
} from 'lucide-react';
import DifferentialDiagnosisCard from './components/DifferentialDiagnosisCard';
import AIChat from './components/AIChat';
import DiagnosisInsightsPanel from './components/DiagnosisInsightsPanel';
import { generateEnhancedAIResponse, updateDiagnosesFromChat } from './components/AIResponseGenerator';

const DiagnosticAnalysis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [diagnoses, setDiagnoses] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedView, setSelectedView] = useState('diagnoses'); // 'diagnoses', 'chat', or 'insights'
  
  useEffect(() => {
    if (patientData.differentialDiagnoses.length === 0) {
      performInitialAnalysis();
    } else {
      setDiagnoses(patientData.differentialDiagnoses);
    }
    
    // Initialize chat with welcome message
    if (chatMessages.length === 0) {
      setChatMessages([
        {
          id: 1,
          sender: 'ai',
          message: "I've analyzed the patient's clinical data and generated differential diagnoses. Would you like to discuss any specific aspects or provide additional information that might refine the diagnosis?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, []);
  
  const performInitialAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate API call with sophisticated diagnoses
    await new Promise(resolve => setTimeout(resolve, 2000));
    
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
      },
      {
        id: 3,
        name: "Pulmonary Embolism",
        icd10: "I26.9",
        probability: 0.25,
        severity: "high",
        confidence: "low",
        supportingFactors: [
          "Elevated heart rate",
          "Acute onset of symptoms"
        ],
        contradictingFactors: [
          "No chest pain or dyspnea",
          "No risk factors mentioned",
          "Productive cough more suggestive of infection"
        ],
        clinicalPearls: "PE should always be considered in the differential of acute respiratory symptoms",
        recommendedActions: ["Calculate Wells' score", "D-dimer if low probability", "CTA if high suspicion"]
      },
      {
        id: 4,
        name: "Atypical Pneumonia",
        icd10: "J15.9",
        probability: 0.20,
        severity: "moderate",
        confidence: "low",
        supportingFactors: [
          "Gradual onset of symptoms",
          "Constitutional symptoms present"
        ],
        contradictingFactors: [
          "Productive rather than dry cough",
          "No reported headache or myalgias"
        ],
        clinicalPearls: "Consider Mycoplasma or Chlamydia in younger patients with walking pneumonia",
        recommendedActions: ["Atypical pathogen panel", "Mycoplasma antibodies"]
      }
    ];
    
    setDiagnoses(generatedDiagnoses);
    updatePatientData('differentialDiagnoses', generatedDiagnoses);
    setIsAnalyzing(false);
  };
  
  const handleDiagnosisFeedback = (diagnosisId, isAgreed) => {
    // Update the diagnosis probability based on feedback
    const action = {
      type: isAgreed ? 'CONFIDENCE_BOOST' : 'DOUBT_DIAGNOSIS',
      diagnosis: diagnosisId
    };
    
    const updatedDiagnoses = updateDiagnosesFromChat(diagnoses, action);
    setDiagnoses(updatedDiagnoses);
    updatePatientData('differentialDiagnoses', updatedDiagnoses);
    
    // Add feedback to chat
    const diagnosis = diagnoses.find(d => d.id === diagnosisId);
    const feedbackMessage = {
      id: Date.now(),
      sender: 'user',
      message: `I ${isAgreed ? 'agree' : 'disagree'} with ${diagnosis.name} as a potential diagnosis.`,
      timestamp: new Date().toISOString(),
      isSystemGenerated: true
    };
    
    setChatMessages(prev => [...prev, feedbackMessage]);
    
    // Generate AI response
    setTimeout(() => {
      const { response, actions } = generateEnhancedAIResponse(
        feedbackMessage.message,
        updatedDiagnoses,
        patientData,
        chatMessages
      );
      
      const aiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        message: response,
        timestamp: new Date().toISOString()
      };
      
      setChatMessages(prev => [...prev, aiMessage]);
      
      // Process any actions from the AI response
      actions.forEach(action => {
        if (action.type === 'UPDATE_CLINICAL_DATA') {
          // Handle clinical data updates
        }
      });
    }, 500);
  };
  
  const handleContinue = () => {
    setCurrentStep('recommended-tests');
  };
  
  const handleBack = () => {
    setCurrentStep('physical-exam');
  };
  
  const handleSendMessage = (message) => {
    setChatMessages(prev => [...prev, message]);
    
    // Generate enhanced AI response
    setTimeout(() => {
      const { response, actions } = generateEnhancedAIResponse(
        message.message,
        diagnoses,
        patientData,
        chatMessages
      );
      
      const aiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        message: response,
        timestamp: new Date().toISOString()
      };
      
      setChatMessages(prev => [...prev, aiMessage]);
    }, 800);
  };
  
  const refreshAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Add a message to chat about refreshing
    const refreshMessage = {
      id: Date.now(),
      sender: 'ai',
      message: "I'm re-analyzing the clinical data with your feedback incorporated. This will help refine the diagnostic probabilities...",
      timestamp: new Date().toISOString()
    };
    setChatMessages(prev => [...prev, refreshMessage]);
    
    // Simulate enhanced analysis
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Update diagnoses based on feedback
    const updatedDiagnoses = diagnoses.map(d => {
      if (d.userFeedback === 'agreed') {
        return { ...d, probability: Math.min(d.probability + 0.05, 0.95) };
      } else if (d.userFeedback === 'disagreed') {
        return { ...d, probability: Math.max(d.probability - 0.05, 0.10) };
      }
      return d;
    }).sort((a, b) => b.probability - a.probability);
    
    setDiagnoses(updatedDiagnoses);
    updatePatientData('differentialDiagnoses', updatedDiagnoses);
    setIsAnalyzing(false);
    
    // Add completion message
    const completeMessage = {
      id: Date.now() + 1,
      sender: 'ai',
      message: "Analysis updated! I've adjusted the probabilities based on your clinical insights. The differential now better reflects your expertise combined with AI analysis.",
      timestamp: new Date().toISOString()
    };
    setChatMessages(prev => [...prev, completeMessage]);
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold text-gray-900">AI Diagnostic Analysis</h2>
          <div className="flex items-center space-x-2">
            <Brain className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-gray-600">Powered by AI</span>
          </div>
        </div>
        <p className="text-gray-600">
          Review AI-generated diagnoses and collaborate with the AI assistant to refine the differential
        </p>
      </div>
      
      {/* AI Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-amber-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-900 mb-1">Important Notice</p>
            <p className="text-sm text-amber-800">
              AI-generated diagnoses are meant to assist clinical decision-making but may contain errors. 
              Always verify findings with your clinical judgment and appropriate diagnostic tests.
            </p>
          </div>
        </div>
      </div>
      
      {/* Analysis Status */}
      {isAnalyzing ? (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <Brain className="absolute inset-0 m-auto w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-blue-900 font-medium">Analyzing clinical data...</p>
              <p className="text-blue-700 text-sm mt-1">
                Processing symptoms, vital signs, and clinical findings to generate evidence-based differentials
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
              <div>
                <p className="text-sm font-medium text-green-900">Analysis Complete</p>
                <p className="text-green-800 text-sm">
                  {diagnoses.length} conditions identified • {diagnoses.filter(d => d.probability > 0.50).length} high probability
                </p>
              </div>
            </div>
            <button
              onClick={refreshAnalysis}
              className="flex items-center space-x-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm font-medium">Refresh Analysis</span>
            </button>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedView('diagnoses')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'diagnoses'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          Differential Diagnoses
          <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full">
            {diagnoses.length}
          </span>
        </button>
        <button
          onClick={() => setSelectedView('chat')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'chat'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          AI Consultation
          {chatMessages.length > 1 && (
            <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full">
              {chatMessages.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setSelectedView('insights')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'insights'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Clinical Insights
        </button>
      </div>
      
      {/* Main Content Area */}
      <div className="mb-6">
        {selectedView === 'diagnoses' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Diagnoses List */}
            <div className="lg:col-span-2 space-y-4">
              {diagnoses.map((diagnosis, index) => (
                <DifferentialDiagnosisCard
                  key={diagnosis.id}
                  diagnosis={diagnosis}
                  index={index}
                  onFeedback={handleDiagnosisFeedback}
                />
              ))}
            </div>
            
            {/* Side Panel - Quick Insights and Advanced Tools */}
            <div className="lg:col-span-1 space-y-4">
              <div className="bg-gray-50 rounded-xl p-4 sticky top-4">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <Sparkles className="w-5 h-5 text-yellow-500 mr-2" />
                  Quick Insights
                </h4>
                
                {/* Top Diagnosis Summary */}
                <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Most Likely</p>
                  <p className="font-semibold text-gray-900">{diagnoses[0]?.name}</p>
                  <div className="flex items-center mt-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                        style={{ width: `${(diagnoses[0]?.probability * 100) || 0}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-700">{Math.round((diagnoses[0]?.probability || 0) * 100)}%</span>
                  </div>
                </div>
                
                {/* Key Actions */}
                <div className="space-y-2">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Recommended Actions</p>
                  {diagnoses[0]?.recommendedActions?.slice(0, 3).map((action, idx) => (
                    <div key={idx} className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      {action}
                    </div>
                  ))}
                </div>
                
                {/* Clinical Pearls */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs font-medium text-blue-900 mb-1">💡 Clinical Pearl</p>
                  <p className="text-xs text-blue-800">{diagnoses[0]?.clinicalPearls}</p>
                </div>
              </div>
              
              {/* Advanced Tools Panel */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
                <div className="flex items-start mb-3">
                  <Activity className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
                  <h4 className="font-semibold text-gray-900">Advanced Tools</h4>
                </div>
                <div className="space-y-3">
                  <button className="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-300 transition-colors">
                    <h5 className="font-medium text-purple-900 mb-1 text-sm">Bayesian Analysis</h5>
                    <p className="text-xs text-gray-600">Calculate posterior probabilities</p>
                  </button>
                  <button className="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-300 transition-colors">
                    <h5 className="font-medium text-purple-900 mb-1 text-sm">Decision Tree</h5>
                    <p className="text-xs text-gray-600">Visualize diagnostic pathways</p>
                  </button>
                  <button className="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-300 transition-colors">
                    <h5 className="font-medium text-purple-900 mb-1 text-sm">Similar Cases</h5>
                    <p className="text-xs text-gray-600">Review case database</p>
                  </button>
                  <button className="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-300 transition-colors">
                    <h5 className="font-medium text-purple-900 mb-1 text-sm">Literature Search</h5>
                    <p className="text-xs text-gray-600">Find recent guidelines</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : selectedView === 'chat' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AIChat 
                messages={chatMessages}
                onSendMessage={handleSendMessage}
                diagnoses={diagnoses}
              />
            </div>
            <div className="lg:col-span-1">
              <DiagnosisInsightsPanel 
                patientData={patientData}
                diagnoses={diagnoses}
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DiagnosisInsightsPanel 
              patientData={patientData}
              diagnoses={diagnoses}
            />
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Diagnostic Confidence Matrix</h3>
              <div className="space-y-3">
                {diagnoses.map((diagnosis) => (
                  <div key={diagnosis.id} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 font-medium">{diagnosis.name}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            diagnosis.confidence === 'high' ? 'bg-green-500' :
                            diagnosis.confidence === 'moderate' ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ 
                            width: `${
                              diagnosis.confidence === 'high' ? 90 :
                              diagnosis.confidence === 'moderate' ? 60 : 30
                            }%` 
                          }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-16 text-right">{diagnosis.confidence}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Navigation Buttons */}
      <div className="flex justify-between pt-6 border-t">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back to Physical Exam
        </button>
        
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center group"
        >
          Continue to Recommended Tests
          <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};

export default DiagnosticAnalysis;