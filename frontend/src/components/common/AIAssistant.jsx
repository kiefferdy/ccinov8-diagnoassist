import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Sparkles, ChevronDown, ChevronUp, HelpCircle, Stethoscope, Brain, FileText, AlertCircle } from 'lucide-react';
import { generateNextQuestion, analyzeSymptoms, getStandardizedTools, generateAssessmentSummary } from '../Patient/utils/clinicalAssessmentAI';

const AIAssistant = ({ 
  patient, 
  episode, 
  encounter, 
  currentSection,
  onInsightApply,
  className = "" 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeTab, setActiveTab] = useState('chat'); // chat, questions, insights, tools
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [clinicalInsights, setClinicalInsights] = useState({ insights: [], redFlags: [] });
  const [assessmentTools, setAssessmentTools] = useState([]);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize with context-aware greeting
  useEffect(() => {
    if (messages.length === 0 && episode) {
      const greeting = getContextualGreeting();
      setMessages([{
        id: Date.now(),
        type: 'ai',
        content: greeting,
        timestamp: new Date()
      }]);
      
      // Generate initial suggestions based on chief complaint
      generateInitialSuggestions();
    }
  }, [episode, messages.length]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getContextualGreeting = () => {
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
  };

  const generateInitialSuggestions = async () => {
    if (!episode?.chiefComplaint) return;
    
    // Generate suggested questions
    const { question, suggestedDirections } = await generateNextQuestion(
      episode.chiefComplaint,
      [],
      patient
    );
    
    if (question) {
      setSuggestedQuestions([question]);
    }
    
    // Get assessment tools
    const tools = getStandardizedTools(episode.chiefComplaint);
    setAssessmentTools(tools);
    
    // Initial analysis
    const analysis = analyzeSymptoms(episode.chiefComplaint, {}, patient);
    setClinicalInsights(analysis);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);
    
    // Process the message and generate response
    const response = await processUserMessage(inputMessage);
    
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

  const processUserMessage = async (message) => {
    const lowerMessage = message.toLowerCase();
    
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
    } else if (currentSection === 'objective') {
      if (lowerMessage.includes('exam') || lowerMessage.includes('physical')) {
        return {
          content: "I can provide physical exam templates relevant to the chief complaint:",
          actions: [
            { label: "Focused Exam", value: "focused_exam" },
            { label: "Complete Exam", value: "complete_exam" },
            { label: "System-Specific", value: "system_exam" }
          ]
        };
      }
    } else if (currentSection === 'assessment') {
      if (lowerMessage.includes('differential') || lowerMessage.includes('diagnosis')) {
        const ddx = generateDifferentialDiagnosis(episode.chiefComplaint);
        return {
          content: `Based on "${episode.chiefComplaint}", here are potential differential diagnoses:\n\n${ddx}`,
          actions: [
            { label: "Add to Assessment", value: "add_ddx" },
            { label: "ICD-10 Lookup", value: "icd10_search" }
          ]
        };
      }
    } else if (currentSection === 'plan') {
      if (lowerMessage.includes('treatment') || lowerMessage.includes('medication')) {
        return {
          content: "I can help with evidence-based treatment recommendations:",
          actions: [
            { label: "Medication Guide", value: "med_guide" },
            { label: "Follow-up Planning", value: "followup" },
            { label: "Patient Education", value: "education" }
          ]
        };
      }
    }
    
    // Default intelligent response
    return {
      content: generateIntelligentResponse(message, episode, encounter),
      actions: []
    };
  };

  const generateDifferentialDiagnosis = (chiefComplaint) => {
    // Simplified differential diagnosis generator
    const ddxMap = {
      'chest pain': [
        '• Acute Coronary Syndrome (I20.9)',
        '• Pulmonary Embolism (I26.9)', 
        '• Gastroesophageal Reflux (K21.9)',
        '• Costochondritis (M94.0)',
        '• Anxiety/Panic Disorder (F41.0)'
      ],
      'headache': [
        '• Migraine (G43.9)',
        '• Tension Headache (G44.2)',
        '• Cluster Headache (G44.0)',
        '• Secondary Headache (G44.8)',
        '• Sinusitis (J32.9)'
      ],
      'abdominal pain': [
        '• Appendicitis (K37)',
        '• Cholecystitis (K81.9)',
        '• Gastroenteritis (K52.9)',
        '• Peptic Ulcer (K27.9)',
        '• Urinary Tract Infection (N39.0)'
      ]
    };
    
    const complaint = chiefComplaint.toLowerCase();
    for (const [key, values] of Object.entries(ddxMap)) {
      if (complaint.includes(key)) {
        return values.join('\n');
      }
    }
    
    return '• Please provide more specific symptoms for targeted differential diagnosis\n• Consider broad categories: Infectious, Inflammatory, Neoplastic, Vascular, Traumatic';
  };

  const generateIntelligentResponse = (message, episode, encounter) => {
    // Analyze message intent and provide contextual response
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
      case 'focused_exam':
        if (onInsightApply) {
          onInsightApply({
            type: 'template', 
            section: 'objective',
            content: getFocusedExamTemplate(episode.chiefComplaint)
          });
        }
        break;
      case 'add_ddx':
        if (onInsightApply) {
          onInsightApply({
            type: 'differential',
            section: 'assessment',
            content: generateDifferentialDiagnosis(episode.chiefComplaint)
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

  const getFocusedExamTemplate = (chiefComplaint) => {
    // Return focused exam based on chief complaint
    const complaint = chiefComplaint.toLowerCase();
    
    if (complaint.includes('chest')) {
      return `Cardiovascular: Regular rate and rhythm, no murmurs/rubs/gallops. No JVD. No peripheral edema.
Respiratory: Clear to auscultation bilaterally, no wheezes/rales/rhonchi. No respiratory distress.
Chest Wall: No tenderness to palpation, no reproducible pain.`;
    } else if (complaint.includes('abdom')) {
      return `Abdomen: Soft, non-distended. Tenderness to palpation in [specify quadrant]. No rebound/guarding. 
Bowel sounds present in all quadrants. No masses palpated. Murphy's sign negative.`;
    }
    
    return `General: Alert and oriented x3, in no acute distress
Vital Signs: [Document from objective section]
Focused Exam: [Customize based on chief complaint]`;
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
        <div className={`fixed bottom-0 right-0 w-96 bg-white rounded-tl-2xl shadow-2xl z-50 transition-all duration-300 ${
          isMinimized ? 'h-14' : 'h-[600px]'
        } ${className}`}>
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-tl-2xl flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span className="font-semibold">AI Clinical Assistant</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                {isMinimized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
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
                    { id: 'questions', label: 'Questions', icon: HelpCircle },
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

                    {/* Input */}
                    <div className="border-t border-gray-200 p-3">
                      <div className="flex space-x-2">
                        <input
                          ref={inputRef}
                          type="text"
                          value={inputMessage}
                          onChange={(e) => setInputMessage(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                          placeholder="Ask me anything..."
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <button
                          onClick={handleSendMessage}
                          disabled={!inputMessage.trim()}
                          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'questions' && (
                  <div className="p-4 space-y-3">
                    <h3 className="font-medium text-gray-900 mb-3">Suggested Clinical Questions</h3>
                    {suggestedQuestions.map((question, idx) => (
                      <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <p className="text-sm text-blue-900 font-medium mb-1">{question.text}</p>
                        <p className="text-xs text-blue-700">{question.helpText}</p>
                        <button
                          onClick={() => {
                            if (onInsightApply) {
                              onInsightApply({
                                type: 'question',
                                content: question.text
                              });
                            }
                          }}
                          className="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                        >
                          Add to Documentation
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'insights' && (
                  <div className="p-4 space-y-4">
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
                        {clinicalInsights.insights.map((insight, idx) => (
                          <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                            <p className="text-sm text-gray-700">{insight}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'tools' && (
                  <div className="p-4 space-y-3">
                    <h3 className="font-medium text-gray-900 mb-3">Assessment Tools</h3>
                    {assessmentTools.map((tool, idx) => (
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
                    ))}
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