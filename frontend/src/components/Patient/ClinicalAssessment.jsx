import React, { useState, useEffect, useRef } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  MessageSquare, 
  ChevronRight, 
  ChevronLeft, 
  Plus, 
  Loader, 
  X, 
  Edit3,
  FileText,
  Brain,
  AlertCircle,
  Activity,
  ClipboardList,
  PenTool,
  CheckCircle,
  Zap,
  SkipForward,
  History,
  Navigation,
  StickyNote,
  ArrowRight,
  HelpCircle,
  Stethoscope,
  User,
  BookOpen,
  Target,
  Route,
  Maximize2,
  Minimize2,
  ChevronUp,
  ChevronDown,
  Lightbulb,
  FileQuestion,
  Clock,
  ThermometerSun,
  ClipboardCheck
} from 'lucide-react';
import FileUpload from '../common/FileUpload';
import { generateNextQuestion, analyzeSymptoms, getStandardizedTools, getSuggestedDirections, generateAssessmentSummary } from './utils/clinicalAssessmentAI.jsx';
import StandardizedToolModal from './components/StandardizedToolModal.jsx';

const ClinicalAssessment = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false);
  const [showStandardizedTool, setShowStandardizedTool] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [completedTools, setCompletedTools] = useState([]);
  const [assessmentDocuments, setAssessmentDocuments] = useState(patientData.assessmentDocuments || []);
  const [assessmentSummary, setAssessmentSummary] = useState({ summary: '', insights: [] });
  const [redFlags, setRedFlags] = useState([]);
  const [showCustomQuestion, setShowCustomQuestion] = useState(false);
  const [customQuestionText, setCustomQuestionText] = useState('');
  const [suggestedDirections, setSuggestedDirections] = useState([]);
  const [showNotes, setShowNotes] = useState(true);
  const [notesExpanded, setNotesExpanded] = useState(false);
  const [clinicalNotes, setClinicalNotes] = useState(patientData.clinicalNotes || '');
  const [skipContext, setSkipContext] = useState('');
  const [showSkipDialog, setShowSkipDialog] = useState(false);
  const [showCustomPathway, setShowCustomPathway] = useState(false);
  const [customPathwayText, setCustomPathwayText] = useState('');
  const notesRef = useRef(null);
  
  // Initialize with first question
  useEffect(() => {
    if (patientData.chiefComplaint && !currentQuestion && questionHistory.length === 0) {
      generateInitialQuestion();
    }
  }, []);

  // Update assessment overview whenever questions are answered
  useEffect(() => {
    const allAnswers = {};
    questionHistory.forEach(q => {
      if (q.answer && !q.skipped) {
        allAnswers[q.id] = { question: q.text, answer: q.answer, category: q.category };
      }
    });
    
    if (Object.keys(allAnswers).length > 0) {
      const insights = analyzeSymptoms(patientData.chiefComplaint, allAnswers, patientData);
      setRedFlags(insights.redFlags || []);
      
      // Generate assessment summary
      const summary = generateAssessmentSummary(patientData.chiefComplaint, allAnswers, patientData);
      setAssessmentSummary(summary);
    }
  }, [questionHistory, patientData.chiefComplaint, patientData]);

  const generateInitialQuestion = async () => {
    setIsGeneratingQuestion(true);
    const firstQuestion = await generateNextQuestion(
      patientData.chiefComplaint, 
      [], 
      patientData
    );
    setCurrentQuestion(firstQuestion.question);
    setSuggestedDirections(firstQuestion.suggestedDirections || []);
    setIsGeneratingQuestion(false);
  };

  const handleAnswerSubmit = async () => {
    if (!currentAnswer.trim() && currentQuestion.type === 'text') return;

    // Save current Q&A to history
    const completedQuestion = {
      ...currentQuestion,
      answer: currentAnswer,
      timestamp: new Date().toISOString()
    };
    
    const newHistory = [...questionHistory, completedQuestion];
    setQuestionHistory(newHistory);
    
    // Update patient data
    updatePatientData('chiefComplaintDetails', newHistory);

    // Clear current answer
    setCurrentAnswer('');
    
    // Generate next question
    setIsGeneratingQuestion(true);
    const nextData = await generateNextQuestion(
      patientData.chiefComplaint,
      newHistory,
      patientData
    );
    
    if (nextData.question) {
      setCurrentQuestion(nextData.question);
      setSuggestedDirections(nextData.suggestedDirections || []);
    } else {
      setCurrentQuestion(null);
    }
    setIsGeneratingQuestion(false);
  };

  const handleSkipQuestion = () => {
    setShowSkipDialog(true);
  };

  const confirmSkip = async () => {
    const skippedQuestion = {
      ...currentQuestion,
      answer: '[Skipped]',
      skipContext: skipContext || '',
      skipped: true,
      timestamp: new Date().toISOString()
    };
    
    const newHistory = [...questionHistory, skippedQuestion];
    setQuestionHistory(newHistory);
    updatePatientData('chiefComplaintDetails', newHistory);
    
    // Generate next question with skip context
    setIsGeneratingQuestion(true);
    const nextData = await generateNextQuestion(
      patientData.chiefComplaint,
      newHistory,
      patientData,
      skipContext ? `skip_context: ${skipContext}` : null
    );
    
    if (nextData.question) {
      setCurrentQuestion(nextData.question);
      setSuggestedDirections(nextData.suggestedDirections || []);
    } else {
      setCurrentQuestion(null);
    }
    
    setShowSkipDialog(false);
    setSkipContext('');
    setIsGeneratingQuestion(false);
  };

  const handleCustomQuestion = async () => {
    if (!customQuestionText.trim()) return;
    
    const customQuestion = {
      id: `custom_${Date.now()}`,
      text: customQuestionText,
      type: 'text',
      category: 'Custom',
      isCustom: true,
      placeholder: 'Document the patient\'s response in detail...'
    };
    
    setCurrentQuestion(customQuestion);
    setCustomQuestionText('');
    setShowCustomQuestion(false);
    setSuggestedDirections([]);
  };

  const handleDirectionChoice = async (direction) => {
    setIsGeneratingQuestion(true);
    const nextData = await generateNextQuestion(
      patientData.chiefComplaint,
      questionHistory,
      patientData,
      direction.focus
    );
    
    if (nextData.question) {
      setCurrentQuestion(nextData.question);
      setSuggestedDirections(nextData.suggestedDirections || []);
    }
    setIsGeneratingQuestion(false);
  };

  const handleCustomPathway = async () => {
    if (!customPathwayText.trim()) return;
    
    const customDirection = {
      label: 'Custom pathway',
      description: customPathwayText,
      focus: `custom: ${customPathwayText}`
    };
    
    setShowCustomPathway(false);
    setCustomPathwayText('');
    handleDirectionChoice(customDirection);
  };

  const navigateToQuestion = (index) => {
    // Allow navigation back to previous questions
    if (index < questionHistory.length) {
      const targetQuestion = questionHistory[index];
      setCurrentQuestion(targetQuestion);
      setCurrentAnswer(targetQuestion.answer || '');
      // Remove questions after this point
      setQuestionHistory(questionHistory.slice(0, index));
    }
  };

  const handleNotesChange = (value) => {
    setClinicalNotes(value);
    updatePatientData('clinicalNotes', value);
  };

  const toggleNotesExpanded = () => {
    setNotesExpanded(!notesExpanded);
  };

  const renderQuestionInput = () => {
    if (!currentQuestion) return null;

    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        handleAnswerSubmit();
      }
    };

    switch (currentQuestion.type) {
      case 'boolean':
        return (
          <div className="space-y-4">
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setCurrentAnswer('Yes');
                  handleAnswerSubmit();
                }}
                className="flex-1 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
              >
                Yes
              </button>
              <button
                onClick={() => {
                  setCurrentAnswer('No');
                  handleAnswerSubmit();
                }}
                className="flex-1 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
              >
                No
              </button>
              <button
                onClick={() => {
                  setCurrentAnswer('Unknown/Not assessed');
                  handleAnswerSubmit();
                }}
                className="flex-1 px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
              >
                Unknown
              </button>
            </div>
            <div className="text-center">
              <button
                onClick={() => setCurrentAnswer('')}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Or provide detailed response below
              </button>
            </div>
          </div>
        );

      case 'severity':
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>No pain</span>
                <span>Moderate</span>
                <span>Severe pain</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                value={currentAnswer.split(' ')[0] || 0}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="text-center mt-3">
                <span className="text-3xl font-bold text-blue-600">{currentAnswer || 0}</span>
                <span className="text-gray-600 text-lg">/10</span>
              </div>
            </div>
            <textarea
              value={currentAnswer.includes('Additional') ? currentAnswer.split('Additional details: ')[1] : ''}
              onChange={(e) => setCurrentAnswer(`${currentAnswer.split(' ')[0] || 0}. Additional details: ${e.target.value}`)}
              onKeyDown={handleKeyPress}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              placeholder="Add qualitative description (optional)..."
            />
            <button
              onClick={handleAnswerSubmit}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Continue
            </button>
          </div>
        );

      default:
        return (
          <div className="space-y-4">
            <textarea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
              rows={4}
              placeholder={currentQuestion.placeholder || "Document the patient's response in detail..."}
              autoFocus
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Press Ctrl+Enter to submit</span>
              <button
                onClick={handleAnswerSubmit}
                disabled={!currentAnswer.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-300"
              >
                Continue
              </button>
            </div>
            
            {/* Quick response templates */}
            {currentQuestion.templates && (
              <div className="border-t pt-3">
                <p className="text-xs text-gray-500 mb-2">Quick templates:</p>
                <div className="flex flex-wrap gap-2">
                  {currentQuestion.templates.map((template, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentAnswer(template)}
                      className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
                    >
                      {template}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
    }
  };

  const renderMainContent = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Question Area */}
      <div className="lg:col-span-2 space-y-4">
        {/* Question History */}
        {questionHistory.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <History className="w-4 h-4 mr-2" />
                Assessment Progress
              </h3>
              <span className="text-sm text-gray-500">{questionHistory.length} questions documented</span>
            </div>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {questionHistory.map((q, index) => (
                <button
                  key={index}
                  onClick={() => navigateToQuestion(index)}
                  className="w-full text-left p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <span className="text-xs font-medium text-gray-500 uppercase">{q.category}</span>
                        {q.isCustom && (
                          <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Custom</span>
                        )}
                      </div>
                      <p className="text-sm font-medium text-gray-700">{q.text}</p>
                      <p className={`text-sm mt-1 ${q.skipped ? 'text-gray-400 italic' : 'text-gray-600'} line-clamp-2`}>
                        {q.skipped ? `Skipped${q.skipContext ? ` - Next focus: ${q.skipContext}` : ''}` : q.answer}
                      </p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-gray-600 ml-2 flex-shrink-0" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Current Question */}
        {currentQuestion ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="mb-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <Stethoscope className="w-5 h-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-blue-600">
                      {currentQuestion.category || 'Clinical Question'} • Question {questionHistory.length + 1}
                    </span>
                  </div>
                  <h3 className="text-xl font-medium text-gray-900">
                    {currentQuestion.text}
                  </h3>
                  {currentQuestion.helpText && (
                    <div className="mt-2 text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
                      <HelpCircle className="w-4 h-4 inline mr-1 text-blue-600" />
                      <span>{currentQuestion.helpText}</span>
                    </div>
                  )}
                </div>
              </div>

              {renderQuestionInput()}
            </div>

            {/* Question Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <button
                  onClick={handleSkipQuestion}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium flex items-center"
                >
                  <SkipForward className="w-4 h-4 mr-1" />
                  Skip
                </button>
                <button
                  onClick={() => setShowCustomQuestion(true)}
                  className="px-4 py-2 text-purple-600 hover:text-purple-700 font-medium flex items-center"
                >
                  <Edit3 className="w-4 h-4 mr-1" />
                  Custom Question
                </button>
              </div>
            </div>
            
            {/* Custom Question Input */}
            {showCustomQuestion && (
              <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <h4 className="font-medium text-purple-900 mb-3">Create Custom Question</h4>
                <div className="space-y-3">
                  <input
                    type="text"
                    value={customQuestionText}
                    onChange={(e) => setCustomQuestionText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleCustomQuestion()}
                    className="w-full px-4 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="What specific aspect would you like to explore with the patient?"
                    autoFocus
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => setShowCustomQuestion(false)}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCustomQuestion}
                      disabled={!customQuestionText.trim()}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300"
                    >
                      Use Question
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : isGeneratingQuestion ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div className="flex flex-col items-center">
              <Loader className="w-8 h-8 text-blue-600 animate-spin mb-4" />
              <p className="text-gray-600">Analyzing clinical context...</p>
              <p className="text-sm text-gray-500 mt-1">Generating relevant follow-up question</p>
            </div>
          </div>
        ) : (
          <div className="bg-green-50 rounded-xl border border-green-200 p-6">
            <div className="flex items-center mb-3">
              <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
              <h3 className="text-lg font-semibold text-green-900">Initial Assessment Complete</h3>
            </div>
            <p className="text-green-800 mb-4">
              You've documented {questionHistory.filter(q => !q.skipped).length} clinical findings. 
              The initial assessment appears comprehensive.
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setShowCustomQuestion(true)}
                className="px-4 py-2 bg-white border border-green-300 text-green-700 rounded-lg hover:bg-green-50 flex items-center"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add More Questions
              </button>
              <button
                className="px-4 py-2 bg-white border border-green-300 text-green-700 rounded-lg hover:bg-green-50 flex items-center"
              >
                <FileText className="w-4 h-4 mr-1" />
                Generate Summary
              </button>
            </div>
          </div>
        )}

        {/* Suggested Clinical Pathways */}
        {suggestedDirections.length > 0 && currentQuestion && (
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
            <h4 className="font-medium text-indigo-900 mb-3 flex items-center">
              <Route className="w-4 h-4 mr-2" />
              Suggested Clinical Pathways
            </h4>
            <p className="text-sm text-indigo-700 mb-3">
              Based on the clinical presentation, consider exploring:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {suggestedDirections.map((direction, index) => (
                <button
                  key={index}
                  onClick={() => handleDirectionChoice(direction)}
                  className="p-3 bg-white rounded-lg border border-indigo-200 hover:border-indigo-300 text-left transition-colors group"
                >
                  <div className="flex items-center">
                    <Target className="w-4 h-4 text-indigo-600 mr-2 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{direction.label}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{direction.description}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 ml-auto" />
                  </div>
                </button>
              ))}
              <button
                onClick={() => setShowCustomPathway(!showCustomPathway)}
                className="p-3 bg-white rounded-lg border border-indigo-200 hover:border-indigo-300 text-left transition-colors group"
              >
                <div className="flex items-center">
                  <Plus className="w-4 h-4 text-indigo-600 mr-2 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Custom pathway</p>
                    <p className="text-xs text-gray-600 mt-0.5">Define your own focus area</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 ml-auto" />
                </div>
              </button>
            </div>
            
            {/* Custom Pathway Input */}
            {showCustomPathway && (
              <div className="mt-3 p-3 bg-white rounded-lg border border-indigo-200">
                <input
                  type="text"
                  value={customPathwayText}
                  onChange={(e) => setCustomPathwayText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleCustomPathway()}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 text-sm"
                  placeholder="Describe the clinical area you want to explore..."
                  autoFocus
                />
                <div className="flex justify-end mt-2 space-x-2">
                  <button
                    onClick={() => setShowCustomPathway(false)}
                    className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCustomPathway}
                    disabled={!customPathwayText.trim()}
                    className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-300"
                  >
                    Use Pathway
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Standardized Tools */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
            <ClipboardList className="w-5 h-5 mr-2" />
            Standardized Assessment Tools
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {getStandardizedTools(patientData.chiefComplaint).map((tool) => (
              <button
                key={tool.id}
                onClick={() => {
                  setSelectedTool(tool);
                  setShowStandardizedTool(true);
                }}
                className="p-3 rounded-lg border border-gray-200 hover:border-blue-300 text-left transition-colors group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">{tool.name}</h4>
                    <p className="text-xs text-gray-600 mt-0.5">{tool.description}</p>
                  </div>
                  {completedTools.includes(tool.id) ? (
                    <CheckCircle className="w-4 h-4 text-green-500 ml-2" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 ml-2" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Smart Summary Sidebar */}
      <div className="lg:col-span-1 space-y-4">
        {/* Red Flags */}
        {redFlags.length > 0 && (
          <div className="bg-red-50 rounded-xl p-4 border border-red-200">
            <h4 className="font-semibold text-red-900 flex items-center mb-3">
              <AlertCircle className="w-5 h-5 mr-2" />
              Clinical Red Flags
            </h4>
            <ul className="space-y-2">
              {redFlags.map((flag, index) => (
                <li key={index} className="text-sm text-red-800 flex items-start">
                  <span className="text-red-500 mr-2">•</span>
                  {flag}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Assessment Overview */}
        <div className="bg-gray-50 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 flex items-center mb-3">
            <ClipboardCheck className="w-5 h-5 text-blue-600 mr-2" />
            Assessment Overview
          </h4>
          <div className="space-y-3">
            {assessmentSummary.summary ? (
              <>
                <div className="text-sm text-gray-700 p-3 bg-white rounded-lg">
                  <p className="font-medium mb-2">Clinical Summary:</p>
                  <p className="text-gray-600">{assessmentSummary.summary}</p>
                </div>
                {assessmentSummary.insights.map((insight, index) => (
                  <div key={index} className="text-sm text-gray-700 p-2 bg-white rounded-lg flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    {insight}
                  </div>
                ))}
              </>
            ) : (
              <p className="text-sm text-gray-500">Clinical findings will be summarized as you document the assessment</p>
            )}
          </div>
        </div>

        {/* Clinical Notes Panel */}
        <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all ${
          notesExpanded ? 'lg:row-span-2' : ''
        }`}>
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h4 className="font-semibold text-gray-900 flex items-center">
              <StickyNote className="w-4 h-4 mr-2" />
              Clinical Notes
            </h4>
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleNotesExpanded}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title={notesExpanded ? "Minimize" : "Expand"}
              >
                {notesExpanded ? (
                  <Minimize2 className="w-4 h-4 text-gray-500" />
                ) : (
                  <Maximize2 className="w-4 h-4 text-gray-500" />
                )}
              </button>
              <button
                onClick={() => setShowNotes(!showNotes)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                {showNotes ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                )}
              </button>
            </div>
          </div>
          {showNotes && (
            <div className="p-4">
              <textarea
                ref={notesRef}
                value={clinicalNotes}
                onChange={(e) => handleNotesChange(e.target.value)}
                className={`w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none transition-all ${
                  notesExpanded ? 'h-96' : 'h-48'
                }`}
                placeholder="Document clinical observations, patient demeanor, environmental factors, or any additional context that may be relevant to the assessment..."
              />
              <div className="mt-2 flex items-center justify-between">
                <p className="text-xs text-gray-500">
                  {clinicalNotes.length} characters
                </p>
                <p className="text-xs text-gray-500">
                  Auto-saved
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Quick Reference */}
        <div className="bg-blue-50 rounded-xl p-4">
          <h4 className="font-semibold text-blue-900 flex items-center mb-3">
            <BookOpen className="w-4 h-4 mr-2" />
            Quick Reference
          </h4>
          <div className="space-y-2 text-sm">
            <button className="w-full text-left p-2 hover:bg-blue-100 rounded transition-colors text-blue-800">
              → Clinical guidelines for {patientData.chiefComplaint}
            </button>
            <button className="w-full text-left p-2 hover:bg-blue-100 rounded transition-colors text-blue-800">
              → Differential diagnosis checklist
            </button>
            <button className="w-full text-left p-2 hover:bg-blue-100 rounded transition-colors text-blue-800">
              → Red flag symptoms reference
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const handleContinue = () => {
    updatePatientData('assessmentDocuments', assessmentDocuments);
    setCurrentStep('physical-exam');
  };

  const handleBack = () => {
    setCurrentStep('chief-complaint');
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Subjective (S)</h2>
        <p className="text-gray-600">Document the patient's story, symptoms, and history related to their chief complaint</p>
      </div>

      {/* Chief Complaint Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
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

      {/* Main Content */}
      {renderMainContent()}

      {/* File Upload Section */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <FileUpload
          label="Attach Supporting Documents"
          description="Upload test results, imaging, referral letters, or other relevant clinical documents"
          acceptedFormats="image/*,.pdf,.doc,.docx,.txt"
          maxFiles={10}
          maxSizeMB={20}
          onFilesChange={setAssessmentDocuments}
          existingFiles={assessmentDocuments}
        />
      </div>

      {/* Navigation Buttons */}
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
          Continue to Physical Exam
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>

      {/* Skip Question Dialog */}
      {showSkipDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-lg w-full mx-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Skip Current Question</h3>
            <p className="text-gray-600 mb-6">
              Optionally, guide the next question by specifying what you'd like to explore instead:
            </p>
            <input
              type="text"
              value={skipContext}
              onChange={(e) => setSkipContext(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-3 text-base"
              placeholder="e.g., 'Focus on sleep patterns' or 'Explore family history'"
              autoFocus
            />
            <p className="text-sm text-gray-500 mb-6">
              Leave blank to let the system choose the next question automatically
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowSkipDialog(false);
                  setSkipContext('');
                }}
                className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmSkip}
                className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Skip & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Standardized Tool Modal */}
      {showStandardizedTool && selectedTool && (
        <StandardizedToolModal
          tool={selectedTool}
          onClose={() => setShowStandardizedTool(false)}
          onComplete={(results) => {
            setCompletedTools([...completedTools, selectedTool.id]);
            updatePatientData('standardizedAssessments', {
              ...patientData.standardizedAssessments,
              [selectedTool.id]: results
            });
            setShowStandardizedTool(false);
          }}
        />
      )}
    </div>
  );
};

export default ClinicalAssessment;