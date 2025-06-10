import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  MessageSquare, 
  ChevronRight, 
  ChevronLeft, 
  Plus, 
  Loader, 
  X, 
  SkipForward,
  Edit3,
  FileText,
  ChevronDown
} from 'lucide-react';
import FileUpload from '../common/FileUpload';

// Mock API function - replace with actual API call
const generateFollowUpQuestion = async (chiefComplaint, answers) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock questions based on chief complaint
  const questionBank = {
    chest: [
      "How long have you been experiencing this chest pain?",
      "On a scale of 1-10, how would you rate the pain?",
      "Does the pain radiate to other parts of your body?",
      "Is the pain worse with physical activity?",
      "Do you experience shortness of breath with the pain?",
      "Have you had any previous heart conditions?"
    ],
    head: [
      "How long have you been experiencing headaches?",
      "Where exactly is the pain located?",
      "Is the headache constant or does it come and go?",
      "Do you experience any visual disturbances?",
      "Have you noticed any triggers for your headaches?",
      "Do you have any nausea or vomiting with the headaches?"
    ],
    stomach: [
      "How long have you been experiencing stomach pain?",
      "Where exactly is the pain located in your abdomen?",
      "Is the pain constant or intermittent?",
      "Does eating make the pain better or worse?",
      "Have you experienced any changes in bowel movements?",
      "Do you have any nausea or vomiting?"
    ],
    cough: [
      "How long have you had this cough?",
      "Is the cough dry or productive?",
      "If productive, what color is the sputum?",
      "Do you have any fever or chills?",
      "Have you experienced any shortness of breath?",
      "Have you been exposed to anyone who is sick?"
    ]
  };
  
  // Determine which question bank to use
  let questions = [];
  const complaintLower = chiefComplaint.toLowerCase();
  
  if (complaintLower.includes('chest')) questions = questionBank.chest;
  else if (complaintLower.includes('head')) questions = questionBank.head;
  else if (complaintLower.includes('stomach') || complaintLower.includes('abdom')) questions = questionBank.stomach;
  else if (complaintLower.includes('cough')) questions = questionBank.cough;
  else {
    // Generic questions
    questions = [
      "How long have you been experiencing these symptoms?",
      "On a scale of 1-10, how severe are your symptoms?",
      "Have the symptoms been getting better, worse, or staying the same?",
      "Have you tried any treatments or medications?",
      "Do you have any other symptoms?",
      "Is there anything that makes your symptoms better or worse?"
    ];
  }
  
  // Return a question that hasn't been asked yet
  const askedQuestions = answers.map(a => a.question);
  const availableQuestions = questions.filter(q => !askedQuestions.includes(q));
  
  if (availableQuestions.length === 0) {
    return null; // No more questions
  }
  
  return availableQuestions[0];
};

const ClinicalAssessment = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [additionalNotes, setAdditionalNotes] = useState(patientData.additionalClinicalNotes || '');
  const [showAdditionalNotes, setShowAdditionalNotes] = useState(false);
  const [showCustomQuestion, setShowCustomQuestion] = useState(false);
  const [customQuestion, setCustomQuestion] = useState('');
  const [assessmentDocuments, setAssessmentDocuments] = useState(patientData.assessmentDocuments || []);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedAnswer, setEditedAnswer] = useState('');
  const [skipReason, setSkipReason] = useState('');
  const [showSkipDialog, setShowSkipDialog] = useState(false);
  
  useEffect(() => {
    // Generate first question when component mounts
    if (patientData.chiefComplaintDetails.length === 0 && patientData.chiefComplaint) {
      generateInitialQuestion();
    }
  }, []);
  
  const generateInitialQuestion = async () => {
    setIsLoading(true);
    const question = await generateFollowUpQuestion(patientData.chiefComplaint, []);
    setCurrentQuestion(question || '');
    setIsLoading(false);
  };
  
  const handleAnswerSubmit = async () => {
    if (!currentAnswer.trim()) return;
    
    // Save the current Q&A
    const newDetail = {
      question: currentQuestion,
      answer: currentAnswer,
      timestamp: new Date().toISOString(),
      isCustom: false
    };
    
    const updatedDetails = [...patientData.chiefComplaintDetails, newDetail];
    updatePatientData('chiefComplaintDetails', updatedDetails);
    
    // Clear current answer
    setCurrentAnswer('');
    
    // Generate next question
    setIsLoading(true);
    const nextQuestion = await generateFollowUpQuestion(patientData.chiefComplaint, updatedDetails);
    
    if (nextQuestion) {
      setCurrentQuestion(nextQuestion);
    } else {
      setCurrentQuestion('');
    }
    setIsLoading(false);
  };
  
  const handleSkipQuestion = () => {
    setShowSkipDialog(true);
  };
  
  const confirmSkip = () => {
    // Save skipped question
    const skippedDetail = {
      question: currentQuestion,
      answer: `[Skipped: ${skipReason || 'No reason provided'}]`,
      timestamp: new Date().toISOString(),
      isSkipped: true
    };
    
    const updatedDetails = [...patientData.chiefComplaintDetails, skippedDetail];
    updatePatientData('chiefComplaintDetails', updatedDetails);
    
    // Generate next question
    setIsLoading(true);
    generateFollowUpQuestion(patientData.chiefComplaint, updatedDetails).then(nextQuestion => {
      if (nextQuestion) {
        setCurrentQuestion(nextQuestion);
      } else {
        setCurrentQuestion('');
      }
      setIsLoading(false);
    });
    
    setShowSkipDialog(false);
    setSkipReason('');
  };
  
  const handleCustomQuestionSubmit = () => {
    if (!customQuestion.trim()) return;
    
    setCurrentQuestion(customQuestion);
    setCustomQuestion('');
    setShowCustomQuestion(false);
  };
  
  const handleRemoveQuestion = (index) => {
    const updatedDetails = patientData.chiefComplaintDetails.filter((_, i) => i !== index);
    updatePatientData('chiefComplaintDetails', updatedDetails);
  };
  
  const handleEditAnswer = (index) => {
    setEditingIndex(index);
    setEditedAnswer(patientData.chiefComplaintDetails[index].answer);
  };
  
  const handleSaveEdit = () => {
    const updatedDetails = [...patientData.chiefComplaintDetails];
    updatedDetails[editingIndex] = {
      ...updatedDetails[editingIndex],
      answer: editedAnswer,
      edited: true,
      editedAt: new Date().toISOString()
    };
    updatePatientData('chiefComplaintDetails', updatedDetails);
    setEditingIndex(null);
    setEditedAnswer('');
  };
  
  const handleDocumentsChange = (files) => {
    setAssessmentDocuments(files);
  };
  
  const handleContinue = () => {
    if (additionalNotes.trim()) {
      updatePatientData('additionalClinicalNotes', additionalNotes);
    }
    updatePatientData('assessmentDocuments', assessmentDocuments);
    setCurrentStep('physical-exam');
  };
  
  const handleBack = () => {
    setCurrentStep('patient-info');
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Clinical Assessment</h2>
        <p className="text-gray-600">Gather detailed information about the patient's chief complaint</p>
      </div>
      
      {/* Chief Complaint Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
        <p className="text-sm font-medium text-blue-900 mb-1">Chief Complaint:</p>
        <p className="text-lg text-blue-800">{patientData.chiefComplaint}</p>
      </div>
      
      {/* Q&A History */}
      {patientData.chiefComplaintDetails.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment History</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {patientData.chiefComplaintDetails.map((detail, index) => (
              <div 
                key={index} 
                className={`border-l-4 pl-4 pr-2 ${
                  detail.isSkipped ? 'border-gray-400' : 
                  detail.isCustom ? 'border-purple-500' : 
                  'border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 mb-1 flex items-center">
                      {detail.question}
                      {detail.isCustom && (
                        <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Custom</span>
                      )}
                    </p>
                    {editingIndex === index ? (
                      <div className="flex items-center space-x-2 mt-2">
                        <input
                          type="text"
                          value={editedAnswer}
                          onChange={(e) => setEditedAnswer(e.target.value)}
                          className="flex-1 px-3 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <button
                          onClick={handleSaveEdit}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingIndex(null)}
                          className="px-3 py-1 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <p className={`text-gray-700 ${detail.isSkipped ? 'italic' : ''}`}>
                        {detail.answer}
                        {detail.edited && (
                          <span className="ml-2 text-xs text-gray-500">(edited)</span>
                        )}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 ml-2">
                    {!detail.isSkipped && editingIndex !== index && (
                      <button
                        onClick={() => handleEditAnswer(index)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleRemoveQuestion(index)}
                      className="p-1 text-red-400 hover:text-red-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Current Question */}
      {currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <MessageSquare className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Follow-up Question</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowCustomQuestion(!showCustomQuestion)}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                Custom Question
              </button>
              <button
                onClick={handleSkipQuestion}
                className="text-sm text-gray-600 hover:text-gray-700 font-medium flex items-center"
              >
                <SkipForward className="w-4 h-4 mr-1" />
                Skip
              </button>
            </div>
          </div>
          
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="w-6 h-6 text-blue-600 animate-spin" />
              <span className="ml-2 text-gray-600">Generating question...</span>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-lg text-gray-800">{currentQuestion}</p>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnswerSubmit()}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Type patient's response..."
                />
                <button
                  onClick={handleAnswerSubmit}
                  disabled={!currentAnswer.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300"
                >
                  Submit
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Custom Question Input */}
      {showCustomQuestion && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
          <div className="flex items-center mb-3">
            <Edit3 className="w-5 h-5 text-purple-600 mr-2" />
            <h4 className="font-medium text-purple-900">Create Custom Question</h4>
          </div>
          <div className="flex space-x-2">
            <input
              type="text"
              value={customQuestion}
              onChange={(e) => setCustomQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCustomQuestionSubmit()}
              className="flex-1 px-4 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Type your custom question..."
            />
            <button
              onClick={handleCustomQuestionSubmit}
              disabled={!customQuestion.trim()}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-300"
            >
              Use Question
            </button>
          </div>
        </div>
      )}
      
      {/* Skip Question Dialog */}
      {showSkipDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Skip Question</h3>
            <p className="text-gray-600 mb-4">Please provide a reason for skipping this question (optional):</p>
            <input
              type="text"
              value={skipReason}
              onChange={(e) => setSkipReason(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
              placeholder="e.g., Not applicable, Patient unable to answer..."
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowSkipDialog(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmSkip}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Skip Question
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* No More Questions */}
      {!currentQuestion && !isLoading && patientData.chiefComplaintDetails.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-6">
          <p className="text-green-800 font-medium">
            ✓ Initial assessment complete. You've gathered {patientData.chiefComplaintDetails.filter(d => !d.isSkipped).length} responses.
          </p>
          <button
            onClick={() => setShowCustomQuestion(true)}
            className="mt-3 text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            Add another custom question
          </button>
        </div>
      )}
      
      {/* Additional Notes */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <button
          type="button"
          onClick={() => setShowAdditionalNotes(!showAdditionalNotes)}
          className="w-full flex items-center justify-between mb-4"
        >
          <div className="flex items-center">
            <Plus className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Additional Clinical Notes</h3>
            <span className="ml-2 text-sm text-gray-500">(Optional)</span>
          </div>
          <ChevronDown className={`w-5 h-5 text-gray-400 transform transition-transform ${showAdditionalNotes ? 'rotate-180' : ''}`} />
        </button>
        
        {showAdditionalNotes && (
          <div className="space-y-4">
            <div>
              <textarea
                value={additionalNotes}
                onChange={(e) => setAdditionalNotes(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Add any additional observations or clinical notes..."
              />
            </div>
            
            <div>
              <FileUpload
                label="Attach Supporting Documents"
                description="Upload clinical notes, referral letters, or other relevant documents"
                acceptedFormats="image/*,.pdf,.doc,.docx,.txt"
                maxFiles={5}
                maxSizeMB={10}
                onFilesChange={handleDocumentsChange}
                existingFiles={assessmentDocuments}
              />
            </div>
          </div>
        )}
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
          disabled={patientData.chiefComplaintDetails.length === 0}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center disabled:bg-gray-300 shadow-sm hover:shadow-md"
        >
          Continue to Physical Exam
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ClinicalAssessment;