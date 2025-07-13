import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  MessageSquare, Send, X, Sparkles, ChevronDown, ChevronUp, 
  HelpCircle, Brain, FileText, AlertCircle,
  Maximize2, Minimize2, Mic, MicOff, Lightbulb,
  Paperclip, File, Image as ImageIcon, Copy, GripVertical
} from 'lucide-react';
import '../SOAP/animations.css';

// Global chat history stored in memory (not localStorage for prototype)
// Store history per encounter
let globalChatHistories = {};
let globalChatStates = {}; // Store open/closed state per encounter

const AIAssistant = ({ 
  episode, 
  currentSection,
  onInsightApply,
  className = "",
  encounterId // Add encounterId to track chat per encounter
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [recommendations, setRecommendations] = useState([]);
  const [clinicalInsights] = useState({ insights: [], redFlags: [] });
  
  // Resizing states
  const [customSize, setCustomSize] = useState({ width: 400, height: 600 }); 
  const [isResizing, setIsResizing] = useState(false);
  const [resizeDirection, setResizeDirection] = useState(null);
  
  // Voice input states
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  
  // File upload states
  const [attachedFiles, setAttachedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0); // Track drag enter/leave events
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const chatContainerRef = useRef(null);
  const previousEncounterIdRef = useRef(null);

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

  // Initialize/restore chat history for this encounter
  useEffect(() => {
    if (!encounterId) return;
    
    // Check if we switched to a different encounter
    if (previousEncounterIdRef.current && previousEncounterIdRef.current !== encounterId) {
      // Different encounter - close the chat
      setIsOpen(false);
      setIsMinimized(false);
      setIsExpanded(false);
    }
    
    previousEncounterIdRef.current = encounterId;
    
    // Initialize or restore chat history for this encounter
    if (!globalChatHistories[encounterId]) {
      globalChatHistories[encounterId] = [];
    }
    
    // Restore messages from this encounter's history
    setMessages(globalChatHistories[encounterId]);
    
    // Initialize with greeting if no history exists
    if (globalChatHistories[encounterId].length === 0 && episode) {
      const greeting = getContextualGreeting();
      const initialMessage = {
        id: Date.now(),
        type: 'ai',
        content: greeting,
        timestamp: new Date()
      };
      setMessages([initialMessage]);
      globalChatHistories[encounterId] = [initialMessage];
    }
  }, [encounterId, episode, getContextualGreeting]);

  // Update global chat history whenever messages change
  useEffect(() => {
    if (encounterId && messages.length > 0) {
      globalChatHistories[encounterId] = messages;
    }
  }, [messages, encounterId]);

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

  const generateRecommendations = useCallback(() => {
    if (!episode?.chiefComplaint) return [];
    
    const complaint = episode.chiefComplaint.toLowerCase();
    const recommendations = [];
    
    // Generate context-specific recommendations based on chief complaint
    if (currentSection === 'subjective') {
      recommendations.push({
        type: 'documentation',
        title: 'Complete OPQRST Assessment',
        description: 'Document Onset, Provocation/Palliation, Quality, Radiation, Severity (1-10), and Time course',
        priority: 'high'
      });
      
      if (complaint.includes('chest') || complaint.includes('pain')) {
        recommendations.push({
          type: 'assessment',
          title: 'Cardiac Risk Stratification',
          description: 'Calculate HEART score or TIMI risk score if chest pain. Document cardiac risk factors.',
          priority: 'high'
        });
      }
      
      recommendations.push({
        type: 'screening',
        title: 'Review Red Flag Symptoms',
        description: 'Screen for: sudden onset, neurological deficits, immunocompromised state, recent trauma',
        priority: 'high'
      });
    } else if (currentSection === 'objective') {
      recommendations.push({
        type: 'examination',
        title: 'Vital Signs Interpretation',
        description: `Check for SIRS criteria: Temp >38°C or <36°C, HR >90, RR >20, WBC >12k or <4k`,
        priority: 'high'
      });
      
      if (complaint.includes('abdom')) {
        recommendations.push({
          type: 'examination',
          title: 'Abdominal Exam Specifics',
          description: 'Document: Murphy\'s sign, McBurney\'s point, rebound/guarding, bowel sounds',
          priority: 'high'
        });
      }
      
      recommendations.push({
        type: 'diagnostic',
        title: 'Point-of-Care Testing',
        description: 'Consider: ECG (if chest pain), urine dipstick (if GU symptoms), glucose (if altered mental status)',
        priority: 'medium'
      });
    } else if (currentSection === 'assessment') {
      recommendations.push({
        type: 'diagnosis',
        title: 'Structured Differential',
        description: 'List 3-5 most likely diagnoses with supporting/refuting evidence for each',
        priority: 'high'
      });
      
      recommendations.push({
        type: 'risk',
        title: 'Risk Stratification',
        description: 'Use validated tools: Wells criteria (DVT/PE), CURB-65 (pneumonia), Alvarado (appendicitis)',
        priority: 'high'
      });
      
      recommendations.push({
        type: 'coding',
        title: 'Accurate ICD-10 Coding',
        description: 'Include laterality, acuity, and associated symptoms for specific coding',
        priority: 'medium'
      });
    } else if (currentSection === 'plan') {
      recommendations.push({
        type: 'treatment',
        title: 'Evidence-Based Treatment',
        description: 'Reference current guidelines: UpToDate, specialty society recommendations',
        priority: 'high'
      });
      
      recommendations.push({
        type: 'safety',
        title: 'Medication Reconciliation',
        description: 'Check for drug interactions, adjust for renal/hepatic function, verify allergies',
        priority: 'high'
      });
      
      recommendations.push({
        type: 'followup',
        title: 'Clear Return Precautions',
        description: 'Document specific symptoms requiring immediate return: fever >39°C, worsening pain, etc.',
        priority: 'high'
      });
      
      recommendations.push({
        type: 'education',
        title: 'Patient Education',
        description: 'Provide diagnosis explanation, expected course, self-care measures, medication instructions',
        priority: 'medium'
      });
    }
    
    return recommendations;
  }, [episode, currentSection]);
  // Generate recommendations when section changes
  useEffect(() => {
    const recs = generateRecommendations();
    setRecommendations(recs);
  }, [generateRecommendations]);

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
    
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = '40px';
    }
    
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
    const processedFiles = Array.from(newFiles).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      type: file.type,
      size: file.size,
      file: file
    }));
    setAttachedFiles(prev => [...prev, ...processedFiles]);
  };
  
  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesAdded(e.target.files);
    }
  };
  // Fixed drag and drop handlers to prevent getting stuck
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    dragCounter.current = 0;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesAdded(e.dataTransfer.files);
    }
  };

  // Reset drag counter when component unmounts or drag is cancelled
  useEffect(() => {
    const handleDragEnd = () => {
      dragCounter.current = 0;
      setIsDragging(false);
    };
    
    document.addEventListener('dragend', handleDragEnd);
    document.addEventListener('drop', handleDragEnd);
    document.addEventListener('mouseleave', handleDragEnd);
    
    return () => {
      document.removeEventListener('dragend', handleDragEnd);
      document.removeEventListener('drop', handleDragEnd);
      document.removeEventListener('mouseleave', handleDragEnd);
    };
  }, []);
  const handleFileRemove = (fileId) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const getAssistantStyles = () => {
    if (isExpanded) {
      return 'fixed bottom-0 right-0 w-1/2 h-1/2 bg-white rounded-tl-2xl shadow-2xl z-50';
    }
    return 'fixed bottom-0 right-0 bg-white rounded-tl-2xl shadow-2xl z-50';
  };
  
  const getContentHeight = () => {
    if (isExpanded) {
      return 'h-full';
    }
    return isMinimized ? 'h-14' : '';
  };
  
  // Enhanced resize mouse events with better edge detection
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing || !resizeDirection) return;
      
      const newSize = { ...customSize };
      
      if (resizeDirection.includes('left')) {
        newSize.width = Math.max(320, Math.min(800, window.innerWidth - e.clientX - 20));
      }
      if (resizeDirection.includes('top')) {
        newSize.height = Math.max(400, Math.min(window.innerHeight - 100, window.innerHeight - e.clientY - 20));
      }
      
      setCustomSize(newSize);
    };
    
    const handleMouseUp = () => {
      setIsResizing(false);
      setResizeDirection(null);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };
    
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = resizeDirection.includes('left') ? 'ew-resize' : 'ns-resize';
      document.body.style.userSelect = 'none';
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };
  }, [isResizing, resizeDirection, customSize]);
  return (
    <>
      {/* Floating AI Assistant Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={`fixed bottom-6 right-6 p-4 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white rounded-full shadow-lg hover:shadow-2xl transform hover:scale-110 transition-all duration-300 z-40 group ${className}`}
          title="AI Clinical Assistant"
        >
          <div className="relative">
            <Sparkles className="w-6 h-6 group-hover:animate-pulse" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </div>
        </button>
      )}

      {/* AI Assistant Panel */}
      {isOpen && (
        <div 
          className={`${getAssistantStyles()} ${getContentHeight()} transition-all duration-300 ${className} ${isResizing ? 'transition-none select-none' : ''} flex flex-col`}
          style={!isExpanded ? { width: `${customSize.width}px`, height: isMinimized ? '56px' : `${customSize.height}px` } : {}}
        >          {/* Enhanced Resize Handles with visual feedback */}
          {!isExpanded && !isMinimized && (
            <>
              {/* Left edge */}
              <div
                className="absolute left-0 top-16 bottom-0 w-2 cursor-ew-resize hover:bg-blue-400/20 transition-colors group"
                onMouseDown={() => {
                  setIsResizing(true);
                  setResizeDirection('left');
                }}
              >
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-16 bg-gray-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              {/* Top edge */}
              <div
                className="absolute top-0 left-16 right-0 h-2 cursor-ns-resize hover:bg-blue-400/20 transition-colors group"
                onMouseDown={() => {
                  setIsResizing(true);
                  setResizeDirection('top');
                }}
              >
                <div className="absolute top-0 left-1/2 -translate-x-1/2 h-1 w-16 bg-gray-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              {/* Top-left corner */}
              <div
                className="absolute top-0 left-0 w-16 h-16 cursor-nwse-resize z-10"
                onMouseDown={() => {
                  setIsResizing(true);
                  setResizeDirection('top-left');
                }}
              >
                <div className="absolute top-2 left-2 w-3 h-3 bg-gray-400 rounded-full opacity-0 hover:opacity-100 transition-opacity" />
              </div>
            </>
          )}          
          {/* Header */}
          <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 ${isExpanded ? 'rounded-t-2xl' : 'rounded-tl-2xl'} flex items-center justify-between shadow-lg flex-shrink-0`}>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span className="font-semibold">AI Clinical Assistant</span>
              {isResizing && (
                <span className="text-xs text-blue-100 ml-2">
                  {Math.round(customSize.width)} × {Math.round(customSize.height)}
                </span>
              )}
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
            <div className="flex flex-col flex-1 overflow-hidden">
              {/* Tabs */}
              <div className="border-b border-gray-200 px-2 bg-gray-50 flex-shrink-0">
                <div className="flex space-x-1">
                  {[
                    { id: 'chat', label: 'Chat', icon: MessageSquare },
                    { id: 'insights', label: 'Insights', icon: Brain },
                    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb }
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all duration-200 relative ${
                        activeTab === tab.id
                          ? 'bg-white text-blue-700 border-b-2 border-blue-600 shadow-sm'
                          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                      }`}
                    >
                      <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-blue-600' : ''}`} />
                      <span>{tab.label}</span>
                      {tab.id === 'insights' && episode?.chiefComplaint && (
                        <span className="ml-1 px-1.5 py-0.5 text-xs bg-red-100 text-red-600 rounded-full">3</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
              {/* Content Area with proper overflow handling */}
              <div className="flex-1 overflow-hidden flex flex-col">
                {activeTab === 'chat' && (
                  <div 
                    className="flex-1 flex flex-col overflow-hidden"
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                  >
                    {/* Drag overlay - Fixed to show properly */}
                    {isDragging && (
                      <div className="absolute inset-0 bg-blue-50/95 z-10 flex items-center justify-center pointer-events-none">
                        <div className="bg-white rounded-lg shadow-xl p-8 text-center pointer-events-none">
                          <Paperclip className="w-16 h-16 text-blue-600 mx-auto mb-3" />
                          <p className="text-xl font-medium text-blue-700">Drop files here to attach</p>
                          <p className="text-sm text-blue-600 mt-2">Images, PDFs, and documents supported</p>
                        </div>
                      </div>
                    )}
                    
                    {/* Messages Container with independent scrolling */}
                    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-gradient-to-b from-gray-50 to-white custom-scrollbar" ref={chatContainerRef}>
                      {messages.map(message => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                        >
                          <div className={`max-w-[80%] ${
                            message.type === 'user'
                              ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-2xl rounded-br-md shadow-lg'
                              : 'bg-white text-gray-800 rounded-2xl rounded-bl-md shadow-md border border-gray-100'
                          } px-4 py-3 transform transition-all hover:scale-[1.02] relative group`}>                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                            
                            {/* Timestamp and Copy button container */}
                            <div className={`flex items-center justify-between mt-2`}>
                              <div className={`text-xs ${message.type === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                                {new Date(message.timestamp).toLocaleTimeString('en-US', { 
                                  hour: '2-digit', 
                                  minute: '2-digit' 
                                })}
                              </div>
                              
                              {/* Copy button for AI messages */}
                              {message.type === 'ai' && (
                                <button
                                  onClick={() => {
                                    navigator.clipboard.writeText(message.content);
                                    if (window.showNotification) {
                                      window.showNotification('Message copied to clipboard', 'success');
                                    }
                                  }}
                                  className="p-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-600 opacity-0 group-hover:opacity-100 transition-all duration-200"
                                  title="Copy message"
                                >
                                  <Copy className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                            
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
                              <div className="mt-3 space-y-2">
                                {message.actions.map((action, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleQuickAction(action.value)}
                                    className="block w-full text-left text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg px-3 py-2 transition-all duration-200 hover:shadow-sm"
                                  >
                                    <span className="font-medium">{action.label}</span>
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {/* Typing indicator */}
                      {isTyping && (
                        <div className="flex justify-start animate-fadeIn">
                          <div className="bg-white rounded-2xl px-4 py-3 shadow-md border border-gray-100">
                            <div className="flex space-x-2">
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                    {/* Attached Files Preview */}
                    {attachedFiles.length > 0 && (
                      <div className="px-4 py-2 border-t border-gray-100 bg-gray-50 flex-shrink-0">
                        <div className="flex items-center flex-wrap gap-2">
                          {attachedFiles.map(file => (
                            <div key={file.id} className="flex items-center space-x-1 bg-white rounded-lg px-2 py-1 text-xs border border-gray-200">
                              {file.type.startsWith('image/') ? (
                                <ImageIcon className="w-3 h-3 text-gray-500" />
                              ) : (
                                <File className="w-3 h-3 text-gray-500" />
                              )}
                              <span className="max-w-[100px] truncate">{file.name}</span>
                              <button
                                onClick={() => handleFileRemove(file.id)}
                                className="ml-1 text-gray-400 hover:text-red-600"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Input Area - Fixed height */}
                    <div className="border-t border-gray-200 bg-gradient-to-b from-gray-50 to-white p-3 flex-shrink-0">
                      <div className="space-y-2">
                        {/* Textarea - Full width */}
                        <div className="relative">
                          <textarea
                            ref={inputRef}
                            value={inputMessage}
                            onChange={(e) => {
                              setInputMessage(e.target.value);
                              // Auto-resize textarea
                              const textarea = e.target;
                              textarea.style.height = 'auto';
                              const maxHeight = parseInt(window.getComputedStyle(textarea).maxHeight);
                              textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px';
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage();
                              }
                            }}
                            placeholder={isListening ? "Listening..." : "Ask me anything..."}
                            className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 hover:border-gray-400 overflow-y-auto"
                            style={{ 
                              minHeight: '40px',
                              maxHeight: `${Math.min(customSize.height * 0.5, 200)}px`,
                              height: '40px'
                            }}
                          />
                          {isListening && transcript && (
                            <div className="absolute bottom-full mb-2 left-0 right-0 bg-gray-900 text-white rounded-lg p-3 text-xs shadow-lg">
                              <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                                <span>{transcript}</span>
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {/* Buttons - Below textarea */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            {/* Hidden file input */}
                            <input
                              ref={fileInputRef}
                              type="file"
                              multiple
                              accept="image/*,.pdf,.doc,.docx,.txt"
                              onChange={handleFileInputChange}
                              className="hidden"
                            />
                            <button
                              onClick={() => fileInputRef.current?.click()}
                              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:scale-110"
                              title="Attach files"
                            >
                              <Paperclip className="w-5 h-5" />
                            </button>
                            <button
                              onClick={toggleVoiceInput}
                              className={`p-2 rounded-lg transition-all duration-200 hover:scale-110 ${
                                isListening 
                                  ? 'bg-red-100 text-red-600 hover:bg-red-200 animate-pulse' 
                                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                              }`}
                              title={isListening ? "Stop recording" : "Start voice input"}
                            >
                              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                            </button>
                          </div>
                          <button
                            onClick={handleSendMessage}
                            disabled={!inputMessage.trim() && attachedFiles.length === 0}
                            className="p-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-110 hover:shadow-lg"
                          >
                            <Send className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {activeTab === 'recommendations' && (
                  <div className="flex-1 overflow-y-auto p-4">
                    <div className="mb-3">
                      <h3 className="font-medium text-gray-900">AI Recommendations</h3>
                      <p className="text-xs text-gray-600 mt-1">
                        Recommendations update based on your current documentation section
                      </p>
                    </div>
                    <div className="space-y-3">
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
                              <div className="flex-1">
                                <p className="font-medium text-gray-900 text-sm">{rec.title}</p>
                                <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                              </div>
                              <span className={`text-xs px-2 py-1 rounded-full ml-2 flex-shrink-0 ${
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
                  </div>
                )}
                {activeTab === 'insights' && (
                  <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-white">
                    {/* Dynamic insights based on chief complaint */}
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Brain className="w-5 h-5 mr-2 text-purple-600" />
                        Clinical Decision Support
                      </h3>
                      
                      {/* Critical Values / Red Flags */}
                      <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
                        <h4 className="font-medium text-red-800 mb-2 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          Critical Considerations
                        </h4>
                        <ul className="text-sm text-red-700 space-y-1">
                          <li>• Monitor for signs of sepsis if fever &gt;38.5°C with tachycardia</li>
                          <li>• Consider PE if dyspnea with pleuritic chest pain and risk factors</li>
                          <li>• Rule out meningitis if headache with neck stiffness and photophobia</li>
                        </ul>
                      </div>
                      
                      {/* Differential Diagnosis Insights */}
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <h4 className="font-medium text-purple-800 mb-2">Differential Diagnosis Considerations</h4>
                        <div className="text-sm text-purple-700 space-y-2">
                          <p><strong>Most Likely:</strong> Based on presentation, consider viral URI, bacterial pharyngitis, or allergic rhinitis</p>
                          <p><strong>Can't Miss:</strong> Peritonsillar abscess, epiglottitis (if dysphagia), Ludwig's angina</p>
                          <p><strong>Likelihood Ratios:</strong> Centor criteria 3-4: LR+ 5.2 for GAS pharyngitis</p>
                        </div>
                      </div>                      
                      {/* Evidence-Based Testing */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h4 className="font-medium text-blue-800 mb-2">Diagnostic Recommendations</h4>
                        <div className="text-sm text-blue-700 space-y-2">
                          <p><strong>Indicated Tests:</strong></p>
                          <ul className="ml-4 space-y-1">
                            <li>• Rapid strep test (if Centor ≥3)</li>
                            <li>• CBC with diff if systemic symptoms</li>
                            <li>• Mono spot if lymphadenopathy + pharyngitis</li>
                          </ul>
                          <p className="mt-2"><strong>Avoid:</strong> Routine chest X-ray without respiratory symptoms (Choosing Wisely)</p>
                        </div>
                      </div>
                      
                      {/* Treatment Insights */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <h4 className="font-medium text-green-800 mb-2">Treatment Considerations</h4>
                        <div className="text-sm text-green-700 space-y-2">
                          <p><strong>First-line:</strong> Amoxicillin 500mg TID x 10 days (if GAS confirmed)</p>
                          <p><strong>Penicillin allergy:</strong> Azithromycin 500mg day 1, then 250mg daily x 4 days</p>
                          <p><strong>Symptomatic:</strong> Acetaminophen/NSAIDs, throat lozenges, salt water gargles</p>
                          <p className="text-xs mt-2 italic">NNT for antibiotics in pharyngitis: 14 to prevent 1 case of rheumatic fever</p>
                        </div>
                      </div>
                      
                      {/* Clinical Pearls */}
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                        <h4 className="font-medium text-amber-800 mb-2">Clinical Pearls</h4>
                        <ul className="text-sm text-amber-700 space-y-1">
                          <li>• Absence of cough increases likelihood of GAS pharyngitis (LR+ 1.5)</li>
                          <li>• Palatal petechiae highly specific for GAS (specificity 95%)</li>
                          <li>• Consider EBV in young adults with pharyngitis + posterior cervical LAD</li>
                          <li>• Corticosteroids may reduce pain duration by 4.8 hours (NNT=4)</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default AIAssistant;