import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  MessageSquare, Send, X, Sparkles, ChevronDown, ChevronUp, 
  HelpCircle, Stethoscope, Brain, FileText, AlertCircle,
  Maximize2, Minimize2, Mic, MicOff, Upload, Lightbulb,
  Paperclip, File, Image as ImageIcon
} from 'lucide-react';
// import { generateNextQuestion, analyzeSymptoms, getStandardizedTools } from '../Patient/utils/clinicalAssessmentAI';
import FileUploadDropbox from './FileUploadDropbox';

const AIAssistant = ({ 
  // patient,  // Not used currently
  episode, 
  // encounter,  // Not used currently
  currentSection,
  onInsightApply,
  className = "" 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeTab, setActiveTab] = useState('chat'); // chat, recommendations, insights, tools
  const [recommendations, setRecommendations] = useState([]);
  const [clinicalInsights] = useState({ insights: [], redFlags: [] });  // setClinicalInsights not used currently
  const [assessmentTools] = useState([]);  // setAssessmentTools not used currently
  
  // Voice input states
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  
  // File upload states
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }
        
        if (finalTranscript) {
          setInputMessage(prev => prev + finalTranscript);
        }
        setTranscript(interimTranscript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const getContextualGreeting = useCallback(() => {
    const section = currentSection || 'general';
    const chiefComplaint = episode?.chiefComplaint || 'the patient\'s concern';
    
    const greetings = {
      subjective: `I'm here to help you document the subjective findings for ${chiefComplaint}. Would you like me to suggest relevant questions or help analyze the patient's history?`,
      objective: `Let's document the objective findings. I can help you with physical exam templates, vital sign interpretation, or suggest relevant diagnostic tests for ${chiefComplaint}.`,
      assessment: `I'll help you formulate the assessment. I can assist with differential diagnosis, clinical reasoning, or ICD-10 coding for ${chiefComplaint}.`,
      plan: `Let's create a comprehensive treatment plan. I can suggest evidence-based treatments, help with medication dosing, or provide patient education materials.`,
      general: `Hello! I'm your AI clinical assistant. I'm here to help with ${chiefComplaint}. How can I assist you?`
    };
    
    return greetings[section] || greetings.general;
  }, [currentSection, episode]);

  const generateRecommendations = useCallback(() => {
    if (!episode?.chiefComplaint) return [];
    
    // const complaint = episode.chiefComplaint.toLowerCase();  // Not used currently
    const recommendations = [];
    
    // Generate context-specific recommendations
    if (currentSection === 'subjective') {
      recommendations.push({
        type: 'documentation',
        title: 'Document OPQRST for pain',
        description: 'Onset, Provocation, Quality, Radiation, Severity, Time',
        priority: 'high'
      });
      recommendations.push({
        type: 'assessment',
        title: 'Screen for red flags',
        description: 'Check for warning signs that require immediate attention',
        priority: 'high'
      });
    } else if (currentSection === 'objective') {
      recommendations.push({
        type: 'examination',
        title: 'Perform focused physical exam',
        description: `Focus on systems relevant to ${episode.chiefComplaint}`,
        priority: 'high'
      });
      recommendations.push({
        type: 'diagnostic',
        title: 'Consider diagnostic tests',
        description: 'Order appropriate labs or imaging based on findings',
        priority: 'medium'
      });
    } else if (currentSection === 'assessment') {
      recommendations.push({
        type: 'diagnosis',
        title: 'Generate differential diagnosis',
        description: 'List possible conditions in order of likelihood',
        priority: 'high'
      });
      recommendations.push({
        type: 'coding',
        title: 'Assign ICD-10 codes',
        description: 'Select appropriate diagnosis codes for billing',
        priority: 'medium'
      });
    } else if (currentSection === 'plan') {
      recommendations.push({
        type: 'treatment',
        title: 'Create treatment plan',
        description: 'Evidence-based interventions for the diagnosis',
        priority: 'high'
      });
      recommendations.push({
        type: 'followup',
        title: 'Schedule follow-up',
        description: 'Determine appropriate timing for reassessment',
        priority: 'medium'
      });
    }
    
    return recommendations;
  }, [episode, currentSection]);

  // Initialize with context-aware greeting and recommendations
  useEffect(() => {
    if (messages.length === 0 && episode) {
      const greeting = getContextualGreeting();
      setMessages([{
        id: Date.now(),
        type: 'ai',
        content: greeting,
        timestamp: new Date()
      }]);
    }
    
    // Generate recommendations
    const recs = generateRecommendations();
    setRecommendations(recs);
  }, [episode, messages.length, getContextualGreeting, generateRecommendations]);
  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && attachedFiles.length === 0) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      files: attachedFiles,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setAttachedFiles([]);
    setIsTyping(true);
    
    // Process the message and generate response
    const response = await processUserMessage(inputMessage, attachedFiles);
    
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'ai',
        content: response.content,
        actions: response.actions,
        timestamp: new Date()
      }]);
      setIsTyping(false);
    }, 1000);
  };

  const processUserMessage = async (message, files) => {
    const lowerMessage = message.toLowerCase();
    
    // Check if files were uploaded
    if (files && files.length > 0) {
      const fileTypes = files.map(f => f.type);
      if (fileTypes.some(t => t.startsWith('image/'))) {
        return {
          content: "I've received the image(s). Based on what I can see, here are my observations:\n\n• Consider documenting visible findings in the objective section\n• Compare with previous images if available\n• Note any changes in appearance or measurements",
          actions: [
            { label: "Add to Objective Findings", value: "add_image_findings" },
            { label: "Request Specialist Opinion", value: "specialist_consult" }
          ]
        };
      } else if (fileTypes.some(t => t.includes('pdf'))) {
        return {
          content: "I've received the document(s). These appear to be medical records or test results. Key points to consider:\n\n• Review for relevant past medical history\n• Note any abnormal findings\n• Compare with current presentation",
          actions: [
            { label: "Summarize Key Findings", value: "summarize_docs" },
            { label: "Add to Medical History", value: "add_to_history" }
          ]
        };
      }
    }
    
    // Context-aware responses based on current section
    if (currentSection === 'subjective') {
      if (lowerMessage.includes('question') || lowerMessage.includes('ask')) {
        return {
          content: "Here are some relevant questions you might ask:",
          actions: [
            { label: "Review of Systems", value: "ros_template" },
            { label: "Pain Assessment", value: "pain_opqrst" },
            { label: "Social History", value: "social_history" }
          ]
        };
      }
    }
    
    // Default intelligent response
    return {
      content: generateIntelligentResponse(),
      actions: []
    };
  };

  const generateIntelligentResponse = () => {
    const responses = [
      "Based on the clinical presentation, I suggest considering additional history about onset, duration, and associated symptoms.",
      "The symptoms described align with several possible conditions. Would you like me to help generate a differential diagnosis?",
      "For this presentation, evidence-based guidelines recommend the following diagnostic approach...",
      "I can help you document this finding. Which section would you like to add it to?"
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'ros_template':
        if (onInsightApply) {
          onInsightApply({
            type: 'template',
            section: 'subjective',
            content: getROSTemplate()
          });
        }
        break;
      case 'add_image_findings':
        if (onInsightApply) {
          onInsightApply({
            type: 'image_findings',
            section: 'objective',
            content: 'Physical examination findings from uploaded images: [To be documented]'
          });
        }
        break;
      default:
        console.log('Action:', action);
    }
  };

  const getROSTemplate = () => {
    return `Review of Systems:
Constitutional: Denies fever, chills, weight loss, fatigue
HEENT: Denies headache, vision changes, hearing loss, sore throat
Cardiovascular: [To be completed based on chief complaint]
Respiratory: [To be completed based on chief complaint]
GI: Denies nausea, vomiting, diarrhea, constipation
GU: Denies dysuria, frequency, urgency
Musculoskeletal: Denies joint pain, swelling, stiffness
Skin: Denies rash, lesions, pruritus
Neurological: Denies numbness, tingling, weakness
Psychiatric: Denies depression, anxiety, SI/HI
Endocrine: Denies polyuria, polydipsia, heat/cold intolerance
Heme/Lymph: Denies easy bruising, bleeding, lymphadenopathy
Allergic/Immunologic: Denies seasonal allergies, frequent infections`;
  };

  const handleFilesAdded = (newFiles) => {
    setAttachedFiles(prev => [...prev, ...newFiles]);
    setShowFileUpload(false);
  };

  const handleFileRemove = (fileId) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const getAssistantStyles = () => {
    if (isExpanded) {
      return 'fixed inset-4 md:inset-8 bg-white rounded-2xl shadow-2xl z-50';
    }
    return 'fixed bottom-0 right-0 w-96 bg-white rounded-tl-2xl shadow-2xl z-50';
  };

  const getContentHeight = () => {
    if (isExpanded) {
      return 'h-full';
    }
    return isMinimized ? 'h-14' : 'h-[600px]';
  };

  return (
    <>
      {/* Floating AI Assistant Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={`fixed bottom-6 right-6 p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300 z-40 ${className}`}
          title="AI Clinical Assistant"
        >
          <div className="relative">
            <Sparkles className="w-6 h-6" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </div>
        </button>
      )}

      {/* AI Assistant Panel */}
      {isOpen && (
        <div className={`${getAssistantStyles()} ${getContentHeight()} transition-all duration-300 ${className}`}>
          {/* Header */}
          <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 ${isExpanded ? 'rounded-t-2xl' : 'rounded-tl-2xl'} flex items-center justify-between`}>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span className="font-semibold">AI Clinical Assistant</span>
            </div>
            <div className="flex items-center space-x-2">
              {!isMinimized && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-1 hover:bg-white/20 rounded transition-colors"
                  title={isExpanded ? "Minimize to corner" : "Expand fullscreen"}
                >
                  {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                </button>
              )}
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                {isMinimized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              <button
                onClick={() => {
                  setIsOpen(false);
                  setIsExpanded(false);
                }}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          {!isMinimized && (
            <>
              {/* Tabs */}
              <div className="border-b border-gray-200 px-2">
                <div className="flex space-x-1">
                  {[
                    { id: 'chat', label: 'Chat', icon: MessageSquare },
                    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
                    { id: 'insights', label: 'Insights', icon: Brain },
                    { id: 'tools', label: 'Tools', icon: Stethoscope }
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-1 px-3 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600'
                          : 'text-gray-600 hover:text-gray-800'
                      }`}
                    >
                      <tab.icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-hidden flex flex-col" style={{ height: 'calc(100% - 120px)' }}>
                {activeTab === 'chat' && (
                  <>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                      {messages.map(message => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-[80%] ${
                            message.type === 'user'
                              ? 'bg-blue-600 text-white rounded-bl-2xl rounded-tl-2xl rounded-tr-2xl'
                              : 'bg-gray-100 text-gray-800 rounded-br-2xl rounded-tr-2xl rounded-tl-2xl'
                          } px-4 py-2 shadow-sm`}>
                            <p className="text-sm">{message.content}</p>
                            
                            {/* Display attached files */}
                            {message.files && message.files.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {message.files.map(file => (
                                  <div key={file.id} className="flex items-center space-x-2 text-xs opacity-90">
                                    {file.type.startsWith('image/') ? (
                                      <ImageIcon className="w-3 h-3" />
                                    ) : (
                                      <File className="w-3 h-3" />
                                    )}
                                    <span className="truncate">{file.name}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                            
                            {message.actions && message.actions.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {message.actions.map((action, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleQuickAction(action.value)}
                                    className="block w-full text-left text-xs bg-white/20 hover:bg-white/30 rounded px-2 py-1 transition-colors"
                                  >
                                    {action.label}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      {isTyping && (
                        <div className="flex justify-start">
                          <div className="bg-gray-100 rounded-2xl px-4 py-2">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* File Upload Modal */}
                    {showFileUpload && (
                      <div className="absolute bottom-16 left-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-10">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-sm font-medium text-gray-900">Attach Files</h4>
                          <button
                            onClick={() => setShowFileUpload(false)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                        <FileUploadDropbox
                          onFilesAdded={handleFilesAdded}
                          existingFiles={[]}
                          acceptedTypes="image/*,.pdf,.doc,.docx,.txt"
                          maxFileSize={10 * 1024 * 1024}
                          maxFiles={5}
                        />
                      </div>
                    )}

                    {/* Attached Files Preview */}
                    {attachedFiles.length > 0 && (
                      <div className="px-4 py-2 border-t border-gray-100">
                        <div className="flex items-center space-x-2 text-xs text-gray-600">
                          <Paperclip className="w-3 h-3" />
                          <span>{attachedFiles.length} file(s) attached</span>
                          {attachedFiles.map(file => (
                            <button
                              key={file.id}
                              onClick={() => handleFileRemove(file.id)}
                              className="hover:text-red-600"
                              title={`Remove ${file.name}`}
                            >
                              <X className="w-3 h-3" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Input */}
                    <div className="border-t border-gray-200 p-3">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setShowFileUpload(!showFileUpload)}
                          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                          title="Attach files"
                        >
                          <Paperclip className="w-4 h-4" />
                        </button>
                        <button
                          onClick={toggleVoiceInput}
                          className={`p-2 rounded-lg transition-colors ${
                            isListening 
                              ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                              : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                          }`}
                          title={isListening ? "Stop recording" : "Start voice input"}
                        >
                          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                        </button>
                        <div className="relative flex-1">
                          <input
                            ref={inputRef}
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                            placeholder={isListening ? "Listening..." : "Ask me anything..."}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          {isListening && transcript && (
                            <div className="absolute bottom-full mb-2 left-0 right-0 bg-gray-100 rounded-lg p-2 text-xs text-gray-600">
                              {transcript}
                            </div>
                          )}
                        </div>
                        <button
                          onClick={handleSendMessage}
                          disabled={!inputMessage.trim() && attachedFiles.length === 0}
                          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </>
                )}
                {activeTab === 'recommendations' && (
                  <div className="p-4 space-y-3 overflow-y-auto">
                    <h3 className="font-medium text-gray-900 mb-3">
                      AI Recommendations for {currentSection || 'Current'} Section
                    </h3>
                    {recommendations.length > 0 ? (
                      recommendations.map((rec, idx) => (
                        <div 
                          key={idx} 
                          className={`border rounded-lg p-3 ${
                            rec.priority === 'high' 
                              ? 'border-red-200 bg-red-50' 
                              : rec.priority === 'medium'
                              ? 'border-yellow-200 bg-yellow-50'
                              : 'border-gray-200 bg-gray-50'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-medium text-gray-900 text-sm">{rec.title}</p>
                              <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              rec.priority === 'high'
                                ? 'bg-red-200 text-red-700'
                                : rec.priority === 'medium'
                                ? 'bg-yellow-200 text-yellow-700'
                                : 'bg-gray-200 text-gray-700'
                            }`}>
                              {rec.priority}
                            </span>
                          </div>
                          <button
                            onClick={() => {
                              if (onInsightApply) {
                                onInsightApply({
                                  type: 'recommendation',
                                  content: rec.title + ': ' + rec.description
                                });
                              }
                            }}
                            className="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                          >
                            Apply Recommendation
                          </button>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Lightbulb className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p className="text-sm">No specific recommendations at this time.</p>
                        <p className="text-xs mt-1">Continue documenting to receive AI suggestions.</p>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'insights' && (
                  <div className="p-4 space-y-4 overflow-y-auto">
                    {clinicalInsights.redFlags.length > 0 && (
                      <div>
                        <h3 className="font-medium text-red-700 mb-2 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          Red Flags
                        </h3>
                        <div className="space-y-2">
                          {clinicalInsights.redFlags.map((flag, idx) => (
                            <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                              <p className="text-sm text-red-800">{flag}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Clinical Insights</h3>
                      <div className="space-y-2">
                        {clinicalInsights.insights.length > 0 ? (
                          clinicalInsights.insights.map((insight, idx) => (
                            <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                              <p className="text-sm text-gray-700">{insight}</p>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-8 text-gray-500">
                            <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                            <p className="text-sm">Analyzing clinical data...</p>
                            <p className="text-xs mt-1">Insights will appear as you document.</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'tools' && (
                  <div className="p-4 space-y-3 overflow-y-auto">
                    <h3 className="font-medium text-gray-900 mb-3">Clinical Assessment Tools</h3>
                    {assessmentTools.length > 0 ? (
                      assessmentTools.map((tool, idx) => (
                        <div key={idx} className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="text-sm font-medium text-purple-900">{tool.name}</p>
                              <p className="text-xs text-purple-700 mt-1">{tool.description}</p>
                            </div>
                            <button
                              onClick={() => {
                                if (onInsightApply) {
                                  onInsightApply({
                                    type: 'tool',
                                    content: tool
                                  });
                                }
                              }}
                              className="ml-2 p-1.5 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
                            >
                              <FileText className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Stethoscope className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p className="text-sm">No specific tools recommended yet.</p>
                        <p className="text-xs mt-1">Tools will be suggested based on the chief complaint.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default AIAssistant;