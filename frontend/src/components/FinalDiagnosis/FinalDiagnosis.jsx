import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  FileText, 
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  RefreshCw,
  Calendar,
  User,
  Brain,
  Sparkles,
  MessageSquare,
  BarChart3,
  PlusCircle,
  Activity,
  Info
} from 'lucide-react';
import RefinedDiagnosisCard from '../Treatment/components/RefinedDiagnosisCard';
import DiagnosticSummaryPanel from '../Treatment/components/DiagnosticSummaryPanel';
import FinalDiagnosisAIChat from './components/FinalDiagnosisAIChat';

const FinalDiagnosis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [refinedDiagnoses, setRefinedDiagnoses] = useState([]);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState(null);
  const [customDiagnosis, setCustomDiagnosis] = useState('');
  const [selectedView, setSelectedView] = useState('overview'); // 'overview' or 'ai-consultation'
  const [isRefining, setIsRefining] = useState(false);
  const [showCustomDiagnosisForm, setShowCustomDiagnosisForm] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  
  useEffect(() => {
    // Refine diagnoses based on test results
    refineAnalysis();
    
    // Load existing data if available
    if (patientData.selectedDiagnosis) {
      setSelectedDiagnosis(patientData.selectedDiagnosis);
    }
    
    // Initialize chat with welcome message
    if (chatMessages.length === 0) {
      setChatMessages([
        {
          id: 1,
          sender: 'ai',
          message: "I've reviewed all the clinical data including test results. Based on the comprehensive analysis, I can help you finalize the diagnosis. Would you like to discuss any specific findings or need clarification on the diagnostic conclusions?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, []);
  
  const refineAnalysis = async () => {
    setIsRefining(true);
    
    // In a real app, this would call an API with test results
    const testResults = patientData.testResults || {};
    let refined = [...patientData.differentialDiagnoses];
    
    // Enhanced refinement logic based on test results
    const testResultsArray = Object.values(testResults);
    if (testResultsArray.some(r => r.testName && r.testName.includes('Chest X-ray'))) {
      refined = refined.map(d => {
        if (d.name.includes('Pneumonia')) {
          return { 
            ...d, 
            probability: 0.85, 
            confidence: 'High',
            supportingFactors: [
              ...d.supportingFactors,
              'Chest X-ray shows consolidation'
            ]
          };
        } else if (d.name.includes('Bronchitis')) {
          return { 
            ...d, 
            probability: 0.10, 
            confidence: 'Low',
            contradictingFactors: [
              ...d.contradictingFactors,
              'Chest X-ray findings suggest pneumonia'
            ]
          };
        }
        return d;
      });
    }
    
    // Sort by probability
    refined.sort((a, b) => b.probability - a.probability);
    setRefinedDiagnoses(refined);
    
    setTimeout(() => setIsRefining(false), 1500);
  };
  
  const handleDiagnosisSelect = (diagnosis) => {
    setSelectedDiagnosis(diagnosis);
    updatePatientData('selectedDiagnosis', diagnosis);
  };
  
  const handleCustomDiagnosis = () => {
    if (customDiagnosis.trim()) {
      const custom = {
        id: 'custom',
        name: customDiagnosis,
        isCustom: true,
        probability: 1.0,
        confidence: 'Doctor Override',
        icd10: 'Custom'
      };
      setSelectedDiagnosis(custom);
      updatePatientData('selectedDiagnosis', custom);
      setShowCustomDiagnosisForm(false);
      setCustomDiagnosis('');
    }
  };
  
  const handleContinue = () => {
    if (!selectedDiagnosis && !customDiagnosis) {
      alert('Please select or enter a diagnosis before continuing.');
      return;
    }
    
    // Save final diagnosis
    updatePatientData('finalDiagnosis', selectedDiagnosis?.name || customDiagnosis);
    
    // Navigate to treatment plan
    setCurrentStep('treatment-plan');
  };
  
  const handleBack = () => {
    setCurrentStep('test-results');
  };
  
  const handleSendMessage = (message) => {
    setChatMessages(prev => [...prev, message]);
    
    // Generate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        sender: 'ai',
        message: generateAIResponse(message.message),
        timestamp: new Date().toISOString()
      };
      
      setChatMessages(prev => [...prev, aiResponse]);
    }, 800);
  };
  
  const generateAIResponse = (userMessage) => {
    // Simple AI response generation - in a real app, this would use an AI service
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('pneumonia')) {
      return "Based on the clinical presentation and test results, the diagnosis of pneumonia is strongly supported. The chest X-ray findings, elevated white blood cell count, and physical exam findings all correlate with this diagnosis. The patient's symptoms and vital signs are also consistent with bacterial pneumonia.";
    } else if (lowerMessage.includes('treatment')) {
      return "For the confirmed diagnosis, I recommend proceeding to the treatment plan phase where we can discuss appropriate antibiotic therapy, supportive care measures, and follow-up recommendations. The treatment plan will be tailored based on the severity and type of infection identified.";
    } else if (lowerMessage.includes('severity')) {
      return "Based on the clinical data, this appears to be a moderate severity case. The patient's vital signs show some elevation but remain stable, and there are no signs of respiratory failure or septic shock. This would typically be managed as an outpatient with close follow-up.";
    } else {
      return "I understand your inquiry. Based on all the available clinical data, test results, and the patient's presentation, the diagnostic confidence is high. Would you like me to elaborate on any specific aspect of the diagnosis or discuss alternative considerations?";
    }
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold text-gray-900">Final Diagnosis</h2>
          <div className="flex items-center space-x-2">
            <Brain className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-gray-600">AI-Enhanced Decision Support</span>
          </div>
        </div>
        <p className="text-gray-600">
          Review refined analysis based on all clinical findings and finalize the diagnosis
        </p>
      </div>
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-1">
              <User className="w-4 h-4 text-blue-600 mr-2" />
              <span className="font-medium text-blue-900">{patientData.name}</span>
              <span className="text-blue-700 ml-2">{patientData.age} years • {patientData.gender}</span>
            </div>
            <p className="text-blue-800">Chief Complaint: {patientData.chiefComplaint}</p>
          </div>
          <div className="text-right">
            <div className="flex items-center text-sm text-blue-700">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Refinement Status */}
      {isRefining && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-4 mb-6">
          <div className="flex items-center">
            <div className="relative mr-4">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600"></div>
              <Sparkles className="absolute inset-0 m-auto w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-purple-900 font-medium">Refining diagnoses with test results...</p>
              <p className="text-purple-700 text-sm">Correlating all clinical findings and laboratory data</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedView('overview')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'overview'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Diagnostic Overview
        </button>
        <button
          onClick={() => setSelectedView('ai-consultation')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'ai-consultation'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Ask AI
          {chatMessages.length > 1 && (
            <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full">
              {chatMessages.length}
            </span>
          )}
        </button>
      </div>
      
      {/* Main Content */}
      {selectedView === 'overview' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Diagnoses List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900">Select Final Diagnosis</h3>
                <button
                  onClick={refineAnalysis}
                  className="flex items-center space-x-1 px-2.5 py-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors text-sm"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Re-analyze</span>
                </button>
              </div>
              <p className="text-sm text-gray-600">
                The diagnoses below are refined based on all clinical information including test results. 
                Select the most appropriate diagnosis to proceed with treatment planning.
              </p>
            </div>
            
            {refinedDiagnoses.map((diagnosis, index) => (
              <RefinedDiagnosisCard
                key={diagnosis.id}
                diagnosis={diagnosis}
                index={index}
                isSelected={selectedDiagnosis?.id === diagnosis.id}
                onSelect={() => handleDiagnosisSelect(diagnosis)}
                testResults={patientData.testResults}
              />
            ))}
            
            {/* Custom Diagnosis Option */}
            {!showCustomDiagnosisForm ? (
              <button
                onClick={() => setShowCustomDiagnosisForm(true)}
                className="w-full p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-gray-400 transition-colors flex items-center justify-center text-gray-600 hover:text-gray-800"
              >
                <PlusCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Add Custom Diagnosis</span>
              </button>
            ) : (
              <div className="p-4 border-2 border-blue-300 rounded-xl bg-blue-50">
                <h4 className="font-medium text-gray-900 mb-3">Custom Diagnosis</h4>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={customDiagnosis}
                    onChange={(e) => setCustomDiagnosis(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter diagnosis..."
                    autoFocus
                  />
                  <button
                    onClick={handleCustomDiagnosis}
                    disabled={!customDiagnosis.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300"
                  >
                    Select
                  </button>
                  <button
                    onClick={() => {
                      setShowCustomDiagnosisForm(false);
                      setCustomDiagnosis('');
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
            
            {/* Information Note */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">Next Steps</p>
                  <p className="text-sm text-blue-800">
                    After selecting the final diagnosis, you'll proceed to create a comprehensive treatment plan 
                    tailored to the patient's specific condition and needs.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Side Panel */}
          <div className="lg:col-span-1">
            <DiagnosticSummaryPanel 
              patientData={patientData}
              refinedDiagnoses={refinedDiagnoses}
              testResults={patientData.testResults}
            />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <FinalDiagnosisAIChat 
              messages={chatMessages}
              onSendMessage={handleSendMessage}
              diagnoses={refinedDiagnoses}
              selectedDiagnosis={selectedDiagnosis}
              patientData={patientData}
            />
          </div>
          <div className="lg:col-span-1">
            <DiagnosticSummaryPanel 
              patientData={patientData}
              refinedDiagnoses={refinedDiagnoses}
              testResults={patientData.testResults}
            />
          </div>
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          {selectedDiagnosis ? (
            <div className="flex items-center space-x-2 text-green-600">
              <Activity className="w-5 h-5" />
              <span className="font-medium">Diagnosis Selected: {selectedDiagnosis.name}</span>
            </div>
          ) : (
            <div className="text-gray-500">
              No diagnosis selected yet
            </div>
          )}
          
          <button
            onClick={handleContinue}
            disabled={!selectedDiagnosis && !customDiagnosis}
            className="flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 group"
          >
            Continue to Treatment Plan
            <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back to Test Results
        </button>
      </div>
    </div>
  );
};

export default FinalDiagnosis;