import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Square, Loader2, Volume2, X, Check } from 'lucide-react';

const VoiceTranscription = ({ 
  onTranscript, 
  onSave,
  placeholder = "Click the microphone to start recording...",
  className = "",
  autoSummarize = true,
  sectionName = ""
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [showSummary, setShowSummary] = useState(false);
  const [error, setError] = useState('');
  
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    // Check for browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition is not supported in your browser.');
      return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript + ' ';
        } else {
          interim += result[0].transcript;
        }
      }
      
      if (final) {
        setTranscript(prev => prev + final);
        if (onTranscript) {
          onTranscript(final);
        }
      }
      setInterimTranscript(interim);
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setError(`Recognition error: ${event.error}`);
      stopRecording();
    };
    
    recognition.onend = () => {
      if (isRecording) {
        // Restart if still recording
        recognition.start();
      }
    };
    
    recognitionRef.current = recognition;
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isRecording, onTranscript]);

  const startRecording = async () => {
    try {
      setError('');
      setTranscript('');
      setInterimTranscript('');
      setSummary('');
      setShowSummary(false);
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
      
      // Start audio recording for better quality (optional)
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
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

  const stopRecording = () => {
    // Stop speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    // Stop media recording
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    
    setIsRecording(false);
    
    // Process the transcript if we have one
    if ((transcript + interimTranscript).trim() && autoSummarize) {
      generateSummary(transcript + interimTranscript);
    }
  };

  const generateSummary = async (text) => {
    setIsProcessing(true);
    
    try {
      // Simulate AI processing - in real app, this would call an AI API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Generate a medical-style summary
      const sentences = text.split(/[.!?]+/).filter(s => s.trim());
      const keyPoints = sentences.slice(0, 3).join('. ');
      
      const summaryText = `${sectionName ? sectionName + ': ' : ''}${keyPoints}${keyPoints ? '.' : ''}`;
      setSummary(summaryText);
      setShowSummary(true);
    } catch (err) {
      console.error('Error generating summary:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSave = () => {
    const finalText = showSummary ? summary : (transcript + interimTranscript);
    if (onSave && finalText.trim()) {
      onSave(finalText.trim());
      // Clear after saving
      setTranscript('');
      setInterimTranscript('');
      setSummary('');
      setShowSummary(false);
    }
  };

  const handleClear = () => {
    setTranscript('');
    setInterimTranscript('');
    setSummary('');
    setShowSummary(false);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className={`voice-transcription ${className}`}>
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        {/* Header */}
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">
                Voice Transcription {sectionName && `- ${sectionName}`}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {isProcessing && (
                <div className="flex items-center text-sm text-blue-600">
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  Processing...
                </div>
              )}
              {error && (
                <span className="text-sm text-red-600">{error}</span>
              )}
            </div>
          </div>
        </div>

        {/* Transcription Area */}
        <div className="p-4">
          <div className="min-h-[120px] max-h-[300px] overflow-y-auto mb-4">
            {showSummary ? (
              <div className="space-y-3">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-900 mb-1">AI Summary</p>
                      <p className="text-sm text-blue-800">{summary}</p>
                    </div>
                    <button
                      onClick={() => setShowSummary(false)}
                      className="ml-2 text-blue-600 hover:text-blue-700"
                      title="Show original transcript"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => setShowSummary(false)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  View original transcript
                </button>
              </div>
            ) : (
              <div>
                <p className="text-gray-800 whitespace-pre-wrap">
                  {transcript}
                  {interimTranscript && (
                    <span className="text-gray-400 italic">{interimTranscript}</span>
                  )}
                </p>
                {!transcript && !interimTranscript && !isRecording && (
                  <p className="text-gray-400 italic">{placeholder}</p>
                )}
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleRecording}
                className={`p-3 rounded-full transition-all ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
                title={isRecording ? 'Stop recording' : 'Start recording'}
              >
                {isRecording ? (
                  <Square className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
              
              {transcript && !showSummary && autoSummarize && (
                <button
                  onClick={() => generateSummary(transcript + interimTranscript)}
                  disabled={isProcessing}
                  className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Generate Summary
                </button>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {(transcript || summary) && (
                <>
                  <button
                    onClick={handleClear}
                    className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Clear
                  </button>
                  <button
                    onClick={handleSave}
                    className="inline-flex items-center px-4 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Check className="w-4 h-4 mr-1" />
                    Save to {sectionName || 'Section'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Recording Indicator */}
        {isRecording && (
          <div className="px-4 py-2 bg-red-50 border-t border-red-200">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm text-red-700 font-medium">Recording in progress...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceTranscription;