import React, { useState, useEffect } from 'react';
import { usePatient } from '../../../contexts/PatientContext';
import { generatePostAssessmentQuestions } from '../utils/postAssessmentAI';
import { 
  MessageSquare, 
  ChevronRight, 
  Loader, 
  Brain,
  Target,
  Search,
  AlertTriangle,
  CheckCircle,
  Plus,
  X
} from 'lucide-react';

const PostAssessmentQuestions = ({ onComplete }) => {
  const { patientData, updatePatientData } = usePatient();
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [customQuestion, setCustomQuestion] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [isGenerating, setIsGenerating] = useState(true);
  
  useEffect(() => {
    const generateSmartQuestions = () => {
      // Analyze subjective and objective data to generate targeted questions
      setIsGenerating(true);
      
      setTimeout(() => {
        // Use enhanced AI to generate questions based on SOAP data
        const questions = generatePostAssessmentQuestions(patientData);
        
        setSuggestedQuestions(questions);
        setIsGenerating(false);
      }, 1500);
    };
    
    generateSmartQuestions();
  }, [patientData]);
  
  const handleQuestionToggle = (questionId) => {
    if (selectedQuestions.includes(questionId)) {
      setSelectedQuestions(selectedQuestions.filter(id => id !== questionId));
    } else {
      setSelectedQuestions([...selectedQuestions, questionId]);
    }
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
  
  const handleContinue = () => {
    // Save selected questions for the doctor to ask
    const questionsToAsk = suggestedQuestions.filter(q => selectedQuestions.includes(q.id));
    updatePatientData('clarifyingQuestions', questionsToAsk);
    onComplete();
  };  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Brain className="w-5 h-5 text-purple-600 mr-2" />
            AI-Suggested Clarifying Questions
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Based on the subjective and objective findings, consider asking these targeted questions
          </p>
        </div>
      </div>
      
      {isGenerating ? (
        <div className="flex flex-col items-center py-12">
          <Loader className="w-8 h-8 text-purple-600 animate-spin mb-4" />
          <p className="text-gray-600">Analyzing clinical data to generate relevant questions...</p>
        </div>
      ) : (
        <>
          {/* Question Categories */}
          <div className="space-y-3 mb-6">
            {suggestedQuestions.map((question) => (
              <div
                key={question.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedQuestions.includes(question.id)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleQuestionToggle(question.id)}
              >
                <div className="flex items-start">
                  <div className={`w-5 h-5 rounded border-2 mr-3 mt-0.5 flex items-center justify-center ${
                    selectedQuestions.includes(question.id)
                      ? 'border-purple-500 bg-purple-500'
                      : 'border-gray-300'
                  }`}>
                    {selectedQuestions.includes(question.id) && (
                      <CheckCircle className="w-3 h-3 text-white" />
                    )}
                  </div>
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
                    <p className="text-sm text-gray-600">{question.rationale}</p>
                    {question.soapRelevance && (
                      <div className="mt-1 flex items-center space-x-2">
                        {question.soapRelevance.map((section, idx) => (
                          <span key={idx} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                            {section.charAt(0).toUpperCase() + section.slice(1)}
                          </span>
                        ))}
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
          
          {/* Summary and Actions */}
          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {selectedQuestions.length} question{selectedQuestions.length !== 1 ? 's' : ''} selected
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => onComplete()}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Skip Questions
              </button>
              <button
                onClick={handleContinue}
                disabled={selectedQuestions.length === 0}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 flex items-center"
              >
                Use Selected Questions
                <ChevronRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
          
          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-1 flex items-center">
              <Target className="w-4 h-4 mr-2" />
              Why these questions?
            </h5>
            <p className="text-sm text-blue-800">
              These questions are generated based on gaps identified in the subjective and objective data collected. 
              They aim to rule out serious conditions, clarify ambiguous findings, and ensure comprehensive assessment.
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default PostAssessmentQuestions;