import React, { useState, useEffect } from 'react';
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
  ClipboardCheck,
  Mic,
  Sparkles,
  Heart,
  Calendar,
  Save,
  Edit2
} from 'lucide-react';
import FileUpload from '../common/FileUpload';
import SpeechToTextTranscriber from './components/SpeechToTextTranscriber.jsx';

const ClinicalAssessment = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [assessmentMode, setAssessmentMode] = useState('manual'); // 'manual' or 'voice'
  const [chiefComplaint, setChiefComplaint] = useState(patientData.chiefComplaint || '');
  const [duration, setDuration] = useState(patientData.chiefComplaintDuration || '');
  const [onset, setOnset] = useState(patientData.chiefComplaintOnset || '');
  const [historyOfPresentIllness, setHistoryOfPresentIllness] = useState(patientData.historyOfPresentIllness || '');
  const [assessmentDocuments, setAssessmentDocuments] = useState(patientData.assessmentDocuments || []);
  const [errors, setErrors] = useState({});
  const [showDocumentationTips, setShowDocumentationTips] = useState(false);
  const [isEditingTranscription, setIsEditingTranscription] = useState(false);
  const [transcribedData, setTranscribedData] = useState(null);
  
  // Auto-save functionality
  useEffect(() => {
    const saveTimer = setTimeout(() => {
      updatePatientData('chiefComplaint', chiefComplaint);
      updatePatientData('chiefComplaintDuration', duration);
      updatePatientData('chiefComplaintOnset', onset);
      updatePatientData('historyOfPresentIllness', historyOfPresentIllness);
    }, 1000);
    
    return () => clearTimeout(saveTimer);
  }, [chiefComplaint, duration, onset, historyOfPresentIllness]);
  
  const handleTranscriptionComplete = (parsedData) => {
    setTranscribedData(parsedData);
    setIsEditingTranscription(true);
    
    // Pre-fill the fields with parsed data
    if (parsedData.chiefComplaint) {
      setChiefComplaint(parsedData.chiefComplaint);
    }
    
    if (parsedData.history?.presentIllness?.length > 0) {
      setHistoryOfPresentIllness(parsedData.history.presentIllness.join('\n'));
    }
    
    // Extract duration and onset if available
    if (parsedData.duration) {
      setDuration(parsedData.duration);
    }
    if (parsedData.onset) {
      setOnset(parsedData.onset);
    }
    
    // Update medications and allergies if found
    if (parsedData.history?.medications?.length > 0) {
      updatePatientData('medications', [...(patientData.medications || []), ...parsedData.history.medications]);
    }
    if (parsedData.history?.allergies?.length > 0) {
      updatePatientData('allergies', [...(patientData.allergies || []), ...parsedData.history.allergies]);
    }
    
    // Automatically switch to manual mode for editing
    setAssessmentMode('manual');
  };
  
  const handleSaveTranscription = () => {
    setIsEditingTranscription(false);
    setAssessmentMode('manual');
    setTranscribedData(null);
  };
  
  const handleCancelTranscription = () => {
    // Reset to previous values
    setChiefComplaint(patientData.chiefComplaint || '');
    setDuration(patientData.chiefComplaintDuration || '');
    setOnset(patientData.chiefComplaintOnset || '');
    setHistoryOfPresentIllness(patientData.historyOfPresentIllness || '');
    
    setIsEditingTranscription(false);
    setAssessmentMode('manual');
    setTranscribedData(null);
  };
  
  const handleContinue = () => {
    // Validate chief complaint
    const newErrors = {};
    if (!chiefComplaint.trim()) {
      newErrors.chiefComplaint = 'Chief complaint is required';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    updatePatientData('assessmentDocuments', assessmentDocuments);
    setCurrentStep('physical-exam');
  };
  
  const handleBack = () => {
    setCurrentStep('patient-info');
  };
  
  const handleDocumentsChange = (files) => {
    setAssessmentDocuments(files);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Subjective (S)</h2>
        <p className="text-gray-600">Document the patient's chief complaint and history of present illness</p>
      </div>
      
      {/* Patient Context */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <User className="w-5 h-5 text-blue-600 mr-2" />
          <span className="font-medium text-blue-900">
            {patientData.name}, {patientData.age} years old, {patientData.gender}
          </span>
        </div>
        {patientData.allergies && patientData.allergies.length > 0 && (
          <div className="mt-2 flex items-start">
            <AlertCircle className="w-4 h-4 text-red-600 mr-2 mt-0.5" />
            <span className="text-sm text-red-800">
              Allergies: {patientData.allergies.join(', ')}
            </span>
          </div>
        )}
      </div>
      
      {/* Assessment Mode Toggle */}
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Clinical Information</h3>
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
        />
      )}
      
      {/* Editable Transcription Results */}
      {isEditingTranscription && transcribedData && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-purple-900 flex items-center">
              <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
              AI-Parsed Information
            </h4>
          </div>
          
          <p className="text-sm text-purple-700 mb-4">
            The information below has been automatically extracted from the voice recording. 
            Please review and make any necessary edits before proceeding to the next step.
          </p>
        </div>
      )}
      
      {/* Manual Entry Mode or Editing Transcription */}
      {(assessmentMode === 'manual' || isEditingTranscription) && (
        <div className="space-y-6">
          {/* Documentation Tips - Collapsible */}
          <div className="bg-blue-50 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowDocumentationTips(!showDocumentationTips)}
              className="w-full p-4 flex items-center justify-between hover:bg-blue-100 transition-colors"
            >
              <h4 className="font-semibold text-blue-900 flex items-center">
                <Lightbulb className="w-4 h-4 mr-2" />
                Documentation Tips
              </h4>
              <ChevronDown className={`w-5 h-5 text-blue-700 transform transition-transform ${
                showDocumentationTips ? 'rotate-180' : ''
              }`} />
            </button>
            
            {showDocumentationTips && (
              <div className="px-4 pb-4 border-t border-blue-200">
                <ul className="space-y-2 text-sm text-blue-800 mt-3">
                  <li>• Be thorough but concise in documenting the patient's narrative</li>
                  <li>• Use the patient's own words when relevant (in quotes)</li>
                  <li>• Include timeline and progression of symptoms</li>
                  <li>• Document what makes symptoms better or worse</li>
                  <li>• Note any treatments already tried and their effectiveness</li>
                  <li>• Document pertinent negatives (what the patient denies)</li>
                </ul>
              </div>
            )}
          </div>
          
          {/* Chief Complaint Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Heart className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Chief Complaint</h3>
              {isEditingTranscription && (
                <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                  AI Parsed
                </span>
              )}
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What brings the patient in today? *
                </label>
                <textarea
                  value={chiefComplaint}
                  onChange={(e) => {
                    setChiefComplaint(e.target.value);
                    if (errors.chiefComplaint) {
                      setErrors({ ...errors, chiefComplaint: null });
                    }
                  }}
                  rows={3}
                  className={`w-full px-4 py-2 border ${
                    errors.chiefComplaint ? 'border-red-300' : 'border-gray-300'
                  } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none`}
                  placeholder="Describe the patient's main concern or symptoms in their own words..."
                />
                {errors.chiefComplaint && (
                  <p className="mt-1 text-sm text-red-600">{errors.chiefComplaint}</p>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Duration
                  </label>
                  <input
                    type="text"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 3 days, 2 weeks"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-4 h-4 inline mr-1" />
                    Onset
                  </label>
                  <input
                    type="text"
                    value={onset}
                    onChange={(e) => setOnset(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Sudden, Gradual"
                  />
                </div>
              </div>
            </div>
          </div>
          
          {/* History of Present Illness */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Clock className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">History of Present Illness</h3>
              {isEditingTranscription && (
                <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                  AI Parsed
                </span>
              )}
            </div>
            
            <textarea
              value={historyOfPresentIllness}
              onChange={(e) => setHistoryOfPresentIllness(e.target.value)}
              rows={12}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Document the chronological story of the patient's current symptoms. Include onset, duration, severity, associated symptoms, aggravating/alleviating factors, and previous treatments tried..."
            />
            <div className="mt-2 flex items-center justify-between">
              <p className="text-xs text-gray-500">{historyOfPresentIllness.length} characters</p>
              <p className="text-xs text-gray-500">Auto-saving...</p>
            </div>
          </div>
          
          {/* Updated Medications/Allergies Alert */}
          {isEditingTranscription && transcribedData && (
            (transcribedData.history?.medications?.length > 0 || transcribedData.history?.allergies?.length > 0) && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-900">Additional Information Extracted</h4>
                    {transcribedData.history?.medications?.length > 0 && (
                      <p className="text-sm text-green-800 mt-1">
                        Medications: {transcribedData.history.medications.join(', ')}
                      </p>
                    )}
                    {transcribedData.history?.allergies?.length > 0 && (
                      <p className="text-sm text-green-800 mt-1">
                        Allergies: {transcribedData.history.allergies.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}
      
      {/* File Upload Section */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <FileUpload
          label="Attach Supporting Documents"
          description="Upload test results, imaging, referral letters, or other relevant clinical documents"
          acceptedFormats="image/*,.pdf,.doc,.docx,.txt"
          maxFiles={10}
          maxSizeMB={20}
          onFilesChange={handleDocumentsChange}
          existingFiles={assessmentDocuments}
        />
      </div>
      
      {/* Navigation */}
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
          disabled={isEditingTranscription}
          className={`px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md ${
            isEditingTranscription ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          Continue to Physical Exam
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ClinicalAssessment;