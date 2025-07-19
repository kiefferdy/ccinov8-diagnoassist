import React, { useState, useRef, useEffect } from 'react';
import {
  Mic, MicOff, Square, Loader2, Volume2, X, Check,
  Sparkles, MessageSquare, Stethoscope, Brain, FileText,
  ChevronRight, AlertCircle, Clock, ChevronDown, ChevronUp,
  Activity, CheckCircle
} from 'lucide-react';

const UnifiedVoiceInput = ({ 
  // encounter,  // Not used currently
  onUpdateSections,
  className = "" 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [processedData, setProcessedData] = useState(null);
  const [error, setError] = useState('');
  const [showTranscript, setShowTranscript] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);

  // Timer for recording duration
  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } else {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      setRecordingDuration(0);
    }
    
    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    };
  }, [isRecording]);
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      setError('');
      setTranscript('');
      setInterimTranscript('');
      setProcessedData(null);
      setIsExpanded(true); 
      
      audioChunksRef.current = [];

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { 
            type: 'audio/wav'
          });
          
          const base64Audio = await blobToBase64(audioBlob);
          //console.log('Base64 audio data:', base64Audio);

          setIsProcessing(true)

          try {
            const response = await fetch('http://localhost:8000/transcribe', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                audio_data: base64Audio
              })
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const res = await response.json();
            //console.log('API response:', result);

            if (res.success) {
              console.log(res)
              const result = res.result
              console.log(result)
              setProcessedData(result)
            }
            
          } catch (apiError) {
            console.error('Error sending audio to API:', apiError);
            setError('Failed to process audio. Please try again.');
          }

          setIsProcessing(false)
          
          stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder;
      }
      
      setIsRecording(true);
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  };

  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processTranscript = async (text) => {
    setIsProcessing(true);
    console.log('Processing transcript:', text); // Debug log
    
    try {
      // Simulate AI processing - in a real app, this would call an AI API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Extract and organize information for different SOAP sections
      const processed = extractSOAPData(text);
      console.log('Processed data:', processed); // Debug log
      
      setProcessedData(processed);
    } catch (err) {
      console.error('Error processing transcript:', err);
      setError('Failed to process transcript. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };
  const extractSOAPData = (text) => {
    // This is a simplified extraction logic - in a real app, this would use NLP/AI
    const sections = {
      subjective: {
        hpi: '',
        ros: {},
        chiefComplaint: ''
      },
      objective: {
        vitals: {},
        physicalExam: {},
        labResults: []
      },
      assessment: {
        clinicalImpression: '',
        differentialDiagnosis: []
      },
      plan: {
        diagnostics: [],
        treatments: [],
        followUp: ''
      }
    };

    // Simple keyword-based extraction for demo
    const lowerText = text.toLowerCase();
    
    // Extract chief complaint
    const ccPatterns = ['complaining of', 'presents with', 'here for', 'chief complaint'];
    for (const pattern of ccPatterns) {
      const index = lowerText.indexOf(pattern);
      if (index !== -1) {
        const startIndex = index + pattern.length;
        const endIndex = text.indexOf('.', startIndex);
        if (endIndex !== -1) {
          sections.subjective.chiefComplaint = text.substring(startIndex, endIndex).trim();
          break;
        }
      }
    }
    // Extract HPI - history of present illness
    const hpiKeywords = ['started', 'began', 'duration', 'severity', 'location', 'quality', 'timing'];
    let hpiSentences = [];
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    
    sentences.forEach(sentence => {
      const lower = sentence.toLowerCase();
      if (hpiKeywords.some(keyword => lower.includes(keyword))) {
        hpiSentences.push(sentence.trim());
      }
    });
    
    sections.subjective.hpi = hpiSentences.join('. ') || text.substring(0, 200) + '...';

    // Extract vital signs
    const vitalPatterns = {
      bloodPressure: /blood pressure\s*[:=]?\s*(\d+\/\d+)/i,
      temperature: /temp(?:erature)?\s*[:=]?\s*(\d+\.?\d*)/i,
      pulse: /pulse\s*[:=]?\s*(\d+)/i,
      respiratoryRate: /resp(?:iratory rate)?\s*[:=]?\s*(\d+)/i,
      oxygenSaturation: /o2\s*sat(?:uration)?\s*[:=]?\s*(\d+)/i
    };

    for (const [vital, pattern] of Object.entries(vitalPatterns)) {
      const match = text.match(pattern);
      if (match) {
        sections.objective.vitals[vital] = match[1];
      }
    }

    // Extract physical exam findings
    const examKeywords = ['exam', 'examination', 'appears', 'noted', 'observed', 'palpation', 'auscultation'];
    const examSentences = sentences.filter(s => 
      examKeywords.some(keyword => s.toLowerCase().includes(keyword))
    );
    
    if (examSentences.length > 0) {
      sections.objective.physicalExam.general = examSentences.join('. ');
    }
    // Extract assessment
    const assessmentKeywords = ['assessment', 'diagnosis', 'impression', 'likely', 'suspect', 'consistent with'];
    const assessmentSentences = sentences.filter(s => 
      assessmentKeywords.some(keyword => s.toLowerCase().includes(keyword))
    );
    
    if (assessmentSentences.length > 0) {
      sections.assessment.clinicalImpression = assessmentSentences.join('. ');
    }

    // Extract plan items
    const planKeywords = ['order', 'prescribe', 'recommend', 'follow-up', 'return', 'start', 'continue'];
    const planSentences = sentences.filter(s => 
      planKeywords.some(keyword => s.toLowerCase().includes(keyword))
    );
    
    planSentences.forEach(sentence => {
      const lower = sentence.toLowerCase();
      if (lower.includes('follow-up') || lower.includes('return')) {
        sections.plan.followUp = sentence;
      } else if (lower.includes('test') || lower.includes('lab') || lower.includes('imaging')) {
        sections.plan.diagnostics.push(sentence);
      } else {
        sections.plan.treatments.push(sentence);
      }
    });

    // For demo purposes, add some sample data if sections are empty
    if (!sections.subjective.chiefComplaint) {
      sections.subjective.chiefComplaint = "Patient presents with acute respiratory symptoms";
    }
    
    if (Object.keys(sections.objective.vitals).length === 0) {
      sections.objective.vitals = {
        bloodPressure: "120/80",
        temperature: "98.6",
        pulse: "72",
        respiratoryRate: "16"
      };
    }

    return sections;
  };
  const applyToSections = () => {
    if (processedData && onUpdateSections) {
      onUpdateSections(processedData);
      
      // Clear the processed data after applying
      setProcessedData(null);
      setTranscript('');
      setInterimTranscript('');
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setIsExpanded(false); // Collapse after showing success
      }, 2000);
      
      setError(''); // Clear any errors
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const clearAll = () => {
    setTranscript('');
    setInterimTranscript('');
    setProcessedData(null);
    setError('');
  };

  return (
    <div className={`unified-voice-input ${className}`}>
      {/* Success Notification */}
      {showSuccess && (
        <div className="bg-green-500 rounded-xl shadow-lg p-4 mb-2 animate-pulse">
          <div className="flex items-center space-x-3 text-white">
            <CheckCircle className="w-5 h-5" />
            <div>
              <h4 className="font-semibold">Successfully Applied!</h4>
              <p className="text-sm text-white/80">The voice data has been organized into SOAP sections</p>
            </div>
          </div>
        </div>
      )}

      {/* Collapsed View */}
      {!isExpanded && !isRecording && !isProcessing && !processedData && !showSuccess && (
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl shadow-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="text-white">
                <h4 className="font-semibold">AI Voice Documentation</h4>
                <p className="text-sm text-white/80">Click to start recording patient encounter</p>
              </div>
            </div>
            <button
              onClick={() => setIsExpanded(true)}
              className="p-3 bg-white/20 rounded-lg hover:bg-white/30 transition-all backdrop-blur-sm"
            >
              <Mic className="w-6 h-6 text-white" />
            </button>
          </div>
        </div>
      )}

      {/* Expanded View */}
      {(isExpanded || isRecording || isProcessing || processedData || showSuccess) && (
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">AI-Powered Voice Documentation</h3>
                  <p className="text-sm text-white/80">
                    Record your patient interaction and let AI organize it into SOAP format
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {/* Recording Button */}
                <button
                  onClick={toggleRecording}
                  disabled={isProcessing}
                  className={`
                    p-4 rounded-full transition-all transform hover:scale-105
                    ${isRecording
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg'
                      : 'bg-white/20 hover:bg-white/30 backdrop-blur-sm'
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                  title={isRecording ? 'Stop recording' : 'Start recording'}
                >
                  {isRecording ? (
                    <Square className="w-8 h-8" />
                  ) : (
                    <Mic className="w-8 h-8" />
                  )}
                </button>
                
                {/* Test Button for Demo */}
                {!isRecording && !isProcessing && !processedData && (
                  <button
                    onClick={() => {
                      const sampleTranscript = "Patient complains of persistent cough and fever for the past 3 days. Temperature is 101.5 degrees. Blood pressure is 130 over 85. On examination, throat appears red and inflamed. Lungs are clear to auscultation. Assessment is likely viral upper respiratory infection. Plan to prescribe acetaminophen for fever and recommend rest and fluids. Follow up in one week if symptoms persist.";
                      processTranscript(sampleTranscript);
                    }}
                    className="px-3 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg transition-all text-sm font-medium"
                    title="Use sample data"
                  >
                    Demo
                  </button>
                )}
                
                {/* Collapse Button */}
                {!isRecording && !isProcessing && !processedData && (
                  <button
                    onClick={() => setIsExpanded(false)}
                    className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-all backdrop-blur-sm"
                    title="Collapse"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          </div>

        {/* Recording Status */}
        {isRecording && (
          <div className="px-6 py-3 bg-red-500/20 border-t border-white/10">
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse" />
                  <span className="font-medium">Recording in progress</span>
                </div>
                <span className="text-white/70">|</span>
                <span className="font-mono text-white/90">{formatDuration(recordingDuration)}</span>
              </div>
            </div>
          </div>
        )}
        {/* Live Transcript */}
        {showTranscript && (transcript || interimTranscript) && (
          <div className="px-6 py-4 bg-blue-900/20 border-t border-white/10">
            <div className="max-h-32 overflow-y-auto">
              <p className="text-white/90 text-sm">
                {transcript}
                {interimTranscript && (
                  <span className="text-white/60 italic">{interimTranscript}</span>
                )}
              </p>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="bg-white">
          {/* Processing Status */}
          {isProcessing && (
            <div className="px-6 py-8">
              <div className="text-center">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">Processing your recording...</p>
                <p className="text-sm text-gray-600">
                  AI is analyzing the conversation and organizing it into SOAP sections
                </p>
              </div>
            </div>
          )}

          {/* Processed Data Preview */}
          {processedData && !isProcessing && (
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-blue-600" />
                  AI-Extracted Information
                </h4>
                <button
                  onClick={clearAll}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear
                </button>
              </div>
              {/* Section Previews */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Subjective Preview */}
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="flex items-center mb-2">
                    <MessageSquare className="w-5 h-5 text-blue-600 mr-2" />
                    <h5 className="font-medium text-blue-900">Subjective</h5>
                  </div>
                  <div className="space-y-2 text-sm">
                    {processedData.subjective.chiefComplaint && (
                      <p className="text-gray-700">
                        <span className="font-medium">Chief Complaint:</span> {processedData.subjective.chiefComplaint}
                      </p>
                    )}
                    {processedData.subjective.hpi && (
                      <p className="text-gray-700 line-clamp-2">
                        <span className="font-medium">HPI:</span> {processedData.subjective.hpi}
                      </p>
                    )}
                  </div>
                </div>

                {/* Objective Preview */}
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <div className="flex items-center mb-2">
                    <Stethoscope className="w-5 h-5 text-green-600 mr-2" />
                    <h5 className="font-medium text-green-900">Objective</h5>
                  </div>
                  <div className="space-y-2 text-sm">
                    {Object.keys(processedData.objective.vitals).length > 0 && (
                      <div>
                        <span className="font-medium text-gray-700">Vitals:</span>
                        <div className="ml-2 text-gray-600">
                          {Object.entries(processedData.objective.vitals).map(([key, value]) => (
                            <div key={key}>{key}: {value}</div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                {/* Assessment Preview */}
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <div className="flex items-center mb-2">
                    <Brain className="w-5 h-5 text-purple-600 mr-2" />
                    <h5 className="font-medium text-purple-900">Assessment</h5>
                  </div>
                  <div className="space-y-2 text-sm">
                    {processedData.assessment.clinicalImpression && (
                      <p className="text-gray-700 line-clamp-2">
                        <span className="font-medium">Clinical Impression:</span> {processedData.assessment.clinicalImpression}
                      </p>
                    )}
                  </div>
                </div>

                {/* Plan Preview */}
                <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                  <div className="flex items-center mb-2">
                    <FileText className="w-5 h-5 text-orange-600 mr-2" />
                    <h5 className="font-medium text-orange-900">Plan</h5>
                  </div>
                  <div className="space-y-2 text-sm text-gray-700">
                    {processedData.plan.treatments.length > 0 && (
                      <div>
                        <span className="font-medium">Treatments:</span>
                        <ul className="ml-2 list-disc list-inside">
                          {processedData.plan.treatments.slice(0, 2).map((treatment, idx) => (
                            <li key={idx} className="line-clamp-1">{treatment}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {processedData.plan.followUp && (
                      <p className="line-clamp-1">
                        <span className="font-medium">Follow-up:</span> {processedData.plan.followUp}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              {/* Apply Button */}
              <div className="flex justify-center mt-6">
                <button
                  onClick={applyToSections}
                  className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  <Check className="w-5 h-5 mr-2" />
                  Apply to SOAP Sections
                </button>
              </div>

              <div className="mt-4 p-4 bg-blue-100 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Review and edit the extracted information in each section as needed. 
                  The AI provides a starting point based on your recording.
                </p>
              </div>
            </div>
          )}

          {/* Empty State / Instructions */}
          {!isRecording && !isProcessing && !processedData && !transcript && (
            <div className="p-8 text-center">
              <div className="max-w-2xl mx-auto">
                <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  Start Recording Your Patient Encounter
                </h4>
                <p className="text-gray-600 mb-6">
                  Click the microphone button above to begin recording. Speak naturally about the patient's 
                  condition, examination findings, and treatment plan. The AI will automatically organize 
                  your notes into the appropriate SOAP sections.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2 flex items-center">
                      <MessageSquare className="w-4 h-4 mr-2 text-blue-600" />
                      Example Phrases
                    </h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• "Patient complains of..."</li>
                      <li>• "Blood pressure is 120 over 80"</li>
                      <li>• "On examination, lungs are clear"</li>
                      <li>• "Assessment is acute bronchitis"</li>
                      <li>• "Plan to start antibiotics"</li>
                    </ul>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Clock className="w-4 h-4 mr-2 text-green-600" />
                      Tips for Best Results
                    </h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Speak clearly and naturally</li>
                      <li>• Include relevant details</li>
                      <li>• Mention vital signs explicitly</li>
                      <li>• State your assessment clearly</li>
                      <li>• Describe the treatment plan</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="px-6 py-4 bg-red-50 border-t border-red-200">
              <div className="flex items-center text-red-800">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      )}
    </div>
  );
};

export default UnifiedVoiceInput;
