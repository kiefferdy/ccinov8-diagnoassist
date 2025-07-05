import React, { useState, useEffect, useCallback } from 'react';
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
  EyeOff,
  MessageSquare,
  Sparkles,
  Mic,
  PenTool,
  Plus,
  X,
  Target,
  Loader,
  Search,
  AlertTriangle,
  HelpCircle,
  BookOpen,
  ChevronDown,
  Edit2
} from 'lucide-react';
import ClinicalInsightsPanel from './components/ClinicalInsightsPanel';
import SpeechToTextTranscriber from '../Patient/components/SpeechToTextTranscriber';
import { generatePostAssessmentQuestions } from '../Patient/utils/postAssessmentAI';

const DiagnosticAnalysis = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [activeTab, setActiveTab] = useState('diagnosis');
  const [doctorDiagnosis, setDoctorDiagnosis] = useState(patientData.doctorDiagnosis || '');
  const [diagnosticNotes, setDiagnosticNotes] = useState(patientData.diagnosticNotes || '');
  const [errors, setErrors] = useState({});
  const [assessmentMode, setAssessmentMode] = useState('manual'); // 'manual' or 'voice'
  const [isEditingTranscription, setIsEditingTranscription] = useState(false);
  const [transcribedData, setTranscribedData] = useState(null);
  
  // Clarifying Questions State
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [questionAnswers, setQuestionAnswers] = useState({});
  const [customQuestion, setCustomQuestion] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false);
  
  // Auto-save functionality
  useEffect(() => {
    const saveTimer = setTimeout(() => {
      updatePatientData('doctorDiagnosis', doctorDiagnosis);
      updatePatientData('diagnosticNotes', diagnosticNotes);
      updatePatientData('questionAnswers', questionAnswers);
    }, 1000);
    
    return () => clearTimeout(saveTimer);
  }, [doctorDiagnosis, diagnosticNotes, questionAnswers, updatePatientData]);
  
  const generateSmartQuestions = useCallback(() => {
    setIsGeneratingQuestions(true);
    
    setTimeout(() => {
      const questions = generatePostAssessmentQuestions(patientData);
      setSuggestedQuestions(questions);
      setIsGeneratingQuestions(false);
    }, 1500);
  }, [patientData]);
  
  // Auto-generate questions when tab is opened
  useEffect(() => {
    if (activeTab === 'questions' && suggestedQuestions.length === 0) {
      generateSmartQuestions();
    }
  }, [activeTab, suggestedQuestions.length, generateSmartQuestions]);
  
  const handleQuestionToggle = (questionId) => {
    if (selectedQuestions.includes(questionId)) {
      setSelectedQuestions(selectedQuestions.filter(id => id !== questionId));
      // Remove answer if question is deselected
      const newAnswers = { ...questionAnswers };
      delete newAnswers[questionId];
      setQuestionAnswers(newAnswers);
    } else {
      setSelectedQuestions([...selectedQuestions, questionId]);
    }
  };
  
  const handleAnswerChange = (questionId, answer) => {
    setQuestionAnswers({
      ...questionAnswers,
      [questionId]: answer
    });
  };
  
  const handleAddCustomQuestion = () => {
    if (customQuestion.trim()) {
      const newQuestion = {
        id: `custom-${Date.now()}`,
        category: 'Custom',
        question: customQuestion,
        rationale: 'Doctor-specified clarification',
        priority: 'high',
        isCustom: true
      };
      setSuggestedQuestions([...suggestedQuestions, newQuestion]);
      setSelectedQuestions([...selectedQuestions, newQuestion.id]);
      setCustomQuestion('');
      setShowCustomInput(false);
    }
  };
  
  const handleTranscriptionComplete = (parsedData) => {
    setTranscribedData(parsedData);
    setIsEditingTranscription(true);
    
    // For assessment, we might get diagnosis and notes
    if (parsedData.diagnosis) {
      setDoctorDiagnosis(parsedData.diagnosis);
    }
    if (parsedData.notes) {
      setDiagnosticNotes(parsedData.notes);
    }
  };
  
  const handleSaveTranscription = () => {
    setIsEditingTranscription(false);
    setAssessmentMode('manual');
    setTranscribedData(null);
  };
  
  const handleCancelTranscription = () => {
    setDoctorDiagnosis(patientData.doctorDiagnosis || '');
    setDiagnosticNotes(patientData.diagnosticNotes || '');
    
    setIsEditingTranscription(false);
    setAssessmentMode('manual');
    setTranscribedData(null);
  };
  
  const handleContinue = () => {
    if (!doctorDiagnosis.trim()) {
      setErrors({ doctorDiagnosis: 'Please enter your diagnosis before continuing' });
      return;
    }
    
    // Save all data including selected questions and answers
    const questionsToAsk = suggestedQuestions.filter(q => selectedQuestions.includes(q.id));
    updatePatientData('clarifyingQuestions', questionsToAsk);
    updatePatientData('questionAnswers', questionAnswers);
    updatePatientData('doctorDiagnosis', doctorDiagnosis);
    updatePatientData('diagnosticNotes', diagnosticNotes);
    
    setCurrentStep('recommended-tests');
  };
  
  const handleBack = () => {
    setCurrentStep('physical-exam');
  };
  
  const tabs = [
    { id: 'diagnosis', label: 'Clinical Diagnosis', icon: Brain },
    { id: 'questions', label: 'Clarifying Questions', icon: MessageSquare },
    { id: 'ask-ai', label: 'Ask AI', icon: Sparkles }
  ];
  
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
      
      {/* Tabs */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-xl">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                <span>{tab.label}</span>
                {tab.id === 'questions' && selectedQuestions.length > 0 && (
                  <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full">
                    {selectedQuestions.length}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
      
      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {/* Clinical Diagnosis Tab */}
          {activeTab === 'diagnosis' && (
            <div className="space-y-6">
              {/* Mode Toggle */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Clinical Assessment</h3>
                <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setAssessmentMode('manual')}
                    disabled={isEditingTranscription}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      assessmentMode === 'manual'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    } ${isEditingTranscription ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <PenTool className="w-4 h-4 inline mr-2" />
                    Manual Entry
                  </button>
                  <button
                    onClick={() => setAssessmentMode('voice')}
                    disabled={isEditingTranscription}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      assessmentMode === 'voice'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    } ${isEditingTranscription ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <Mic className="w-4 h-4 inline mr-2" />
                    Voice Transcription
                  </button>
                </div>
              </div>
              
              {/* Voice Transcription Mode */}
              {assessmentMode === 'voice' && !isEditingTranscription && (
                <SpeechToTextTranscriber 
                  onTranscriptionComplete={handleTranscriptionComplete}
                  patientData={patientData}
                  isAssessment={true}
                />
              )}
              
              {/* Editable Transcription Results */}
              {isEditingTranscription && transcribedData && (
                <div className="bg-purple-50 border border-purple-200 rounded-xl p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-purple-900 flex items-center">
                      <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
                      AI-Parsed Assessment (Editable)
                    </h4>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={handleSaveTranscription}
                        className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Save Changes
                      </button>
                      <button
                        onClick={handleCancelTranscription}
                        className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                  
                  <p className="text-sm text-purple-700 mb-4">
                    Review and edit the parsed assessment below. Click "Save Changes" when done.
                  </p>
                </div>
              )}
              
              {/* Manual Entry or Editing Mode */}
              {(assessmentMode === 'manual' || isEditingTranscription) && (
                <>
                  {/* Key Findings Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                        <FileText className="w-4 h-4 mr-2 text-blue-600" />
                        Subjective Findings
                      </h4>
                      <ul className="space-y-2 text-sm text-gray-700">
                        {patientData.chiefComplaint && (
                          <li className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span><strong>Chief Complaint:</strong> {patientData.chiefComplaint}</span>
                          </li>
                        )}
                        {patientData.chiefComplaintDuration && (
                          <li className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span><strong>Duration:</strong> {patientData.chiefComplaintDuration}</span>
                          </li>
                        )}
                        {patientData.historyOfPresentIllness && (
                          <li className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span><strong>HPI:</strong> {patientData.historyOfPresentIllness.substring(0, 100)}...</span>
                          </li>
                        )}
                        {patientData.medications && patientData.medications.length > 0 && (
                          <li className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span><strong>Medications:</strong> {patientData.medications.join(', ')}</span>
                          </li>
                        )}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                        <Activity className="w-4 h-4 mr-2 text-green-600" />
                        Objective Findings
                      </h4>
                      <ul className="space-y-2 text-sm text-gray-700">
                        {patientData.physicalExam.bloodPressure && (
                          <li className="flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            <span><strong>BP:</strong> {patientData.physicalExam.bloodPressure} mmHg</span>
                          </li>
                        )}
                        {patientData.physicalExam.heartRate && (
                          <li className="flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            <span><strong>HR:</strong> {patientData.physicalExam.heartRate} bpm</span>
                          </li>
                        )}
                        {patientData.physicalExam.temperature && (
                          <li className="flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            <span><strong>Temp:</strong> {patientData.physicalExam.temperature}°C</span>
                          </li>
                        )}
                        {patientData.physicalExam.respiratoryRate && (
                          <li className="flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            <span><strong>RR:</strong> {patientData.physicalExam.respiratoryRate} breaths/min</span>
                          </li>
                        )}
                        {patientData.physicalExam.additionalFindings && (
                          <li className="flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            <span><strong>Exam:</strong> {patientData.physicalExam.additionalFindings.substring(0, 80)}...</span>
                          </li>
                        )}
                      </ul>
                    </div>
                  </div>
                  
                  {/* Diagnosis Framework Helper */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                      <h5 className="font-medium text-purple-900 mb-2 flex items-center">
                        <Target className="w-4 h-4 mr-2" />
                        Primary Diagnosis
                      </h5>
                      <p className="text-sm text-purple-700">
                        What is the most likely diagnosis based on the clinical presentation?
                      </p>
                    </div>
                    
                    <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                      <h5 className="font-medium text-orange-900 mb-2 flex items-center">
                        <AlertTriangle className="w-4 h-4 mr-2" />
                        Differential Diagnoses
                      </h5>
                      <p className="text-sm text-orange-700">
                        What other conditions should be considered and ruled out?
                      </p>
                    </div>
                    
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h5 className="font-medium text-green-900 mb-2 flex items-center">
                        <Search className="w-4 h-4 mr-2" />
                        Clinical Reasoning
                      </h5>
                      <p className="text-sm text-green-700">
                        What findings support or refute each diagnosis?
                      </p>
                    </div>
                  </div>
                  
                  {/* Doctor's Diagnosis */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clinical Diagnosis *
                    </label>
                    <textarea
                      value={doctorDiagnosis}
                      onChange={(e) => {
                        setDoctorDiagnosis(e.target.value);
                        if (errors.doctorDiagnosis) {
                          setErrors({ ...errors, doctorDiagnosis: null });
                        }
                      }}
                      rows={4}
                      className={`w-full px-4 py-3 border ${
                        errors.doctorDiagnosis ? 'border-red-300' : 'border-gray-300'
                      } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none`}
                      placeholder="Enter your clinical diagnosis based on the subjective and objective findings..."
                    />
                    {errors.doctorDiagnosis && (
                      <p className="mt-1 text-sm text-red-600">{errors.doctorDiagnosis}</p>
                    )}
                  </div>
                  
                  {/* Diagnostic Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Assessment Notes
                    </label>
                    <textarea
                      value={diagnosticNotes}
                      onChange={(e) => setDiagnosticNotes(e.target.value)}
                      rows={6}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Include differential diagnoses, clinical reasoning, red flags, or any other relevant assessment notes..."
                    />
                    <div className="mt-2 flex items-center justify-between">
                      <p className="text-xs text-gray-500">{diagnosticNotes.length} characters</p>
                      <p className="text-xs text-gray-500">Auto-saving...</p>
                    </div>
                  </div>
                  
                  {/* Visual Diagnosis Helper */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-2 flex items-center">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      Diagnosis Documentation Tips
                    </h4>
                    <ul className="space-y-1 text-sm text-blue-800">
                      <li>• Include primary diagnosis and relevant differential diagnoses</li>
                      <li>• Document your clinical reasoning and key findings that support your diagnosis</li>
                      <li>• Note any uncertainties or areas requiring further investigation</li>
                      <li>• Consider severity, acuity, and potential complications</li>
                    </ul>
                  </div>
                </>
              )}
            </div>
          )}
          
          {/* Clarifying Questions Tab */}
          {activeTab === 'questions' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">AI-Suggested Clarifying Questions</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Based on the assessment, consider asking these targeted questions
                  </p>
                </div>
                <button
                  onClick={generateSmartQuestions}
                  disabled={isGeneratingQuestions}
                  className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors flex items-center disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isGeneratingQuestions ? 'animate-spin' : ''}`} />
                  Regenerate Questions
                </button>
              </div>
              
              {isGeneratingQuestions ? (
                <div className="flex flex-col items-center py-12">
                  <Loader className="w-8 h-8 text-purple-600 animate-spin mb-4" />
                  <p className="text-gray-600">Analyzing clinical data to generate relevant questions...</p>
                </div>
              ) : (
                <>
                  {/* Question List */}
                  <div className="space-y-3">
                    {suggestedQuestions.map((question) => (
                      <div
                        key={question.id}
                        className={`border rounded-lg p-4 transition-all ${
                          selectedQuestions.includes(question.id)
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200'
                        }`}
                      >
                        <div className="flex items-start">
                          <input
                            type="checkbox"
                            checked={selectedQuestions.includes(question.id)}
                            onChange={() => handleQuestionToggle(question.id)}
                            className="mt-1 mr-3"
                          />
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                                question.priority === 'high' 
                                  ? 'bg-red-100 text-red-700'
                                  : question.priority === 'medium'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {question.category}
                              </span>
                              {question.isCustom && (
                                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                  Custom
                                </span>
                              )}
                            </div>
                            <p className="font-medium text-gray-900 mb-1">{question.question}</p>
                            <p className="text-sm text-gray-600 mb-3">{question.rationale}</p>
                            
                            {/* Answer Input for Selected Questions */}
                            {selectedQuestions.includes(question.id) && (
                              <div className="mt-3 p-3 bg-white rounded-lg border border-purple-200">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  Patient's Response:
                                </label>
                                <textarea
                                  value={questionAnswers[question.id] || ''}
                                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                  rows={2}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none text-sm"
                                  placeholder="Enter patient's response..."
                                />
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Add Custom Question */}
                  {!showCustomInput ? (
                    <button
                      onClick={() => setShowCustomInput(true)}
                      className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-purple-300 hover:text-purple-600 transition-colors flex items-center justify-center"
                    >
                      <Plus className="w-5 h-5 mr-2" />
                      Add Custom Question
                    </button>
                  ) : (
                    <div className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                      <div className="flex items-start space-x-2">
                        <input
                          type="text"
                          value={customQuestion}
                          onChange={(e) => setCustomQuestion(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleAddCustomQuestion()}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Enter your custom question..."
                          autoFocus
                        />
                        <button
                          onClick={handleAddCustomQuestion}
                          className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                        >
                          Add
                        </button>
                        <button
                          onClick={() => {
                            setShowCustomInput(false);
                            setCustomQuestion('');
                          }}
                          className="px-3 py-2 text-gray-600 hover:text-gray-800"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Info Box */}
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-1 flex items-center">
                      <Target className="w-4 h-4 mr-2" />
                      Why these questions?
                    </h5>
                    <p className="text-sm text-blue-800">
                      These questions are generated based on gaps identified in the clinical data. 
                      They aim to rule out serious conditions, clarify ambiguous findings, and ensure comprehensive assessment.
                    </p>
                  </div>
                </>
              )}
            </div>
          )}
          
          {/* Ask AI Tab */}
          {activeTab === 'ask-ai' && (
            <div className="space-y-6">
              <ClinicalInsightsPanel 
                patientData={patientData}
                doctorDiagnosis={doctorDiagnosis}
              />
              
              {/* Clinical Chat Interface */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h4 className="font-medium text-gray-900 mb-4 flex items-center">
                  <MessageSquare className="w-5 h-5 text-purple-600 mr-2" />
                  Clinical Questions Assistant
                </h4>
                <div className="space-y-4">
                  {/* Sample Conversation */}
                  <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                    <div className="flex items-start space-x-2">
                      <Bot className="w-5 h-5 text-purple-600 mt-1" />
                      <div className="flex-1 bg-purple-50 rounded-lg p-3">
                        <p className="text-sm text-gray-800">
                          Based on the patient's presentation with {patientData.chiefComplaint}, I can help you explore differential diagnoses, treatment options, or clinical guidelines. What would you like to discuss?
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Quick Actions */}
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    <button className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-left">
                      <span className="font-medium">Differential Diagnosis</span>
                      <p className="text-xs text-gray-600">Explore possible diagnoses</p>
                    </button>
                    <button className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-left">
                      <span className="font-medium">Treatment Guidelines</span>
                      <p className="text-xs text-gray-600">Evidence-based approaches</p>
                    </button>
                    <button className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-left">
                      <span className="font-medium">Diagnostic Tests</span>
                      <p className="text-xs text-gray-600">Recommended investigations</p>
                    </button>
                    <button className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-left">
                      <span className="font-medium">Red Flags</span>
                      <p className="text-xs text-gray-600">Critical signs to watch for</p>
                    </button>
                  </div>
                  
                  {/* Input */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Ask about differential diagnoses, treatment options, or clinical guidelines..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    />
                    <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                      Ask AI
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
      </div>
      
      {/* Navigation Buttons */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          disabled={!doctorDiagnosis.trim()}
          className={`px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md ${
            !doctorDiagnosis.trim() ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          Continue to Plan
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default DiagnosticAnalysis;