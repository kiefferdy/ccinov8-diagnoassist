import React, { useState, useRef, useEffect } from 'react';
import { 
  Mic, 
  MicOff, 
  Loader, 
  AlertCircle, 
  CheckCircle,
  FileText,
  Sparkles,
  Volume2,
  Pause,
  Play,
  RotateCcw,
  Save,
  Edit2,
  X
} from 'lucide-react';

const SpeechToTextTranscriber = ({ onTranscriptionComplete, patientData, isObjective = false, isAssessment = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [parsedSections, setParsedSections] = useState(null);
  const [showParsedPreview, setShowParsedPreview] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState(null);
  
  const timerRef = useRef(null);
  const transcriptIntervalRef = useRef(null);
  
  // Sample conversation data
  const sampleSubjectiveConversation = `Doctor: So what brings you in today?
Patient: I've been having this persistent cough for about two weeks now. It started off as just a dry cough, but now I'm coughing up some phlegm.
Doctor: I see. Can you describe the phlegm?
Patient: It's yellowish-green, and there's quite a bit of it, especially in the morning.
Doctor: Any fever or chills?
Patient: Yes, I've had a low-grade fever, around 100 to 101 degrees, on and off for the past week. And I do get chills at night sometimes.
Doctor: How about any chest pain or shortness of breath?
Patient: I do feel a bit short of breath when I climb stairs, which isn't normal for me. And there's some chest tightness when I cough really hard.
Doctor: Have you been around anyone who's been sick recently?
Patient: Actually, yes. My coworker had a bad cold a few weeks ago, and we share an office.
Doctor: Are you taking any medications currently?
Patient: Just my regular blood pressure medication - lisinopril, 10mg daily. Oh, and I've been taking over-the-counter cough syrup, but it hasn't helped much.
Doctor: Any known allergies?
Patient: I'm allergic to penicillin - I get a rash. No other allergies that I know of.`;

  const sampleObjectiveConversation = `Doctor: Let me check your vital signs first. Blood pressure is 138 over 82, slightly elevated. Heart rate is 98 beats per minute, also a bit high. Temperature is 100.8 degrees Fahrenheit, so you do have a low-grade fever. Respiratory rate is 22 breaths per minute, which is slightly elevated. Oxygen saturation is 96% on room air, which is acceptable but on the lower side of normal.

Now let me listen to your lungs. Take a deep breath in... and out. I can hear some crackles in your lower right lung field. Again... yes, definitely some crackling sounds, particularly at the base of your right lung. 

Let me check your throat. Say "ah" please. Your throat looks a bit red, but no obvious exudate or swelling of the tonsils. 

I'm going to feel your lymph nodes now. I can feel some slight swelling in the anterior cervical nodes on both sides, but they're not particularly tender.

Your heart sounds are regular, no murmurs appreciated. Abdomen is soft, non-tender, no organomegaly noted.`;
  
  const sampleAssessmentConversation = `Doctor: Based on the history and physical examination, my assessment is that you have community-acquired pneumonia. The productive cough with greenish sputum, fever, shortness of breath, and most importantly, the crackles I heard in your right lung base all point to this diagnosis.

This is likely a bacterial pneumonia given the color of the sputum and your symptoms. The fact that you were exposed to someone who was sick recently also supports an infectious cause.

I'm concerned about the pneumonia progressing, especially given your shortness of breath with exertion. We need to start treatment promptly. I'm also considering the possibility of bronchitis as a differential diagnosis, but the lung findings make pneumonia more likely.

Given that you're allergic to penicillin, we'll need to use an alternative antibiotic. I'm going to prescribe azithromycin, which is effective against the common bacteria that cause community-acquired pneumonia.

We should also get a chest X-ray to confirm the diagnosis and see the extent of the infection. A complete blood count would help us assess the severity of the infection as well.`;
  
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (transcriptIntervalRef.current) {
        clearInterval(transcriptIntervalRef.current);
      }
    };
  }, []);
  
  const startRecording = async () => {
    try {
      setError(null);
      setTranscript('');
      setParsedSections(null);
      setIsRecording(true);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // Simulate live transcription
      const fullTranscript = isAssessment ? sampleAssessmentConversation : 
                            isObjective ? sampleObjectiveConversation : 
                            sampleSubjectiveConversation;
      const words = fullTranscript.split(' ');
      let currentIndex = 0;
      
      transcriptIntervalRef.current = setInterval(() => {
        if (currentIndex < words.length) {
          setTranscript(prev => {
            const newWord = words[currentIndex];
            currentIndex++;
            return prev ? `${prev} ${newWord}` : newWord;
          });
        } else {
          stopRecording();
        }
      }, 200); // Add one word every 200ms
      
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Unable to start recording simulation.');
    }
  };
  
  const stopRecording = () => {
    // Stop timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (transcriptIntervalRef.current) {
      clearInterval(transcriptIntervalRef.current);
      transcriptIntervalRef.current = null;
    }
    
    setIsRecording(false);
    setRecordingTime(0);
    
    // Process the transcript if we have one
    if (transcript) {
      processTranscript();
    }
  };
  
  const processTranscript = async () => {
    setIsProcessing(true);
    
    // Simulate AI processing
    setTimeout(() => {
      const parsed = isAssessment ? parseAssessmentTranscript(transcript) :
                    isObjective ? parseObjectiveTranscript(transcript) : 
                    parseSubjectiveTranscript(transcript);
      setParsedSections(parsed);
      setShowParsedPreview(true);
      setIsProcessing(false);
    }, 2000);
  };
  
  const parseSubjectiveTranscript = (text) => {
    // Parse the sample subjective conversation
    return {
      chiefComplaint: 'Persistent cough for two weeks with phlegm production',
      duration: '2 weeks',
      onset: 'Gradual',
      history: {
        presentIllness: [
          'Started as dry cough 2 weeks ago',
          'Now productive with yellowish-green phlegm',
          'Worse in the morning',
          'Associated with low-grade fever (100-101°F) for past week',
          'Intermittent chills at night',
          'Shortness of breath with exertion',
          'Chest tightness with severe coughing'
        ],
        exposures: ['Coworker with recent cold - shared office space'],
        medications: ['Lisinopril 10mg daily for blood pressure', 'Over-the-counter cough syrup (ineffective)'],
        allergies: ['Penicillin - causes rash']
      },
      clinicalNotes: [`Patient appears mildly ill but in no acute distress. Alert and oriented, able to speak in full sentences.`]
    };
  };
  
  const parseObjectiveTranscript = (text) => {
    // Parse the sample objective examination
    return {
      vitalSigns: {
        bloodPressure: '138/82',
        heartRate: '98',
        temperature: '38.2', // Changed from 100.8°F to 38.2°C
        respiratoryRate: '22',
        oxygenSaturation: '96%'
      },
      physicalExam: {
        general: 'Patient appears mildly ill',
        respiratory: 'Crackles noted in lower right lung field, particularly at the base',
        cardiovascular: 'Regular heart sounds, no murmurs',
        throat: 'Mild erythema, no exudate or tonsillar swelling',
        lymphNodes: 'Slight bilateral anterior cervical lymphadenopathy, non-tender',
        abdomen: 'Soft, non-tender, no organomegaly'
      }
    };
  };
  
  const parseAssessmentTranscript = (text) => {
    // Parse the sample assessment conversation
    return {
      diagnosis: 'Community-acquired pneumonia',
      notes: `Based on history and physical examination findings:
- Productive cough with greenish sputum
- Fever and shortness of breath
- Crackles in right lung base on auscultation
- Likely bacterial etiology given sputum characteristics
- Recent exposure to sick contact supports infectious cause

Differential diagnosis includes:
1. Community-acquired pneumonia (most likely)
2. Acute bronchitis (less likely given lung findings)

Treatment plan considerations:
- Azithromycin (patient allergic to penicillin)
- Chest X-ray for confirmation
- CBC to assess infection severity`,
      differentialDiagnoses: [
        'Community-acquired pneumonia',
        'Acute bronchitis'
      ],
      recommendedTests: [
        'Chest X-ray',
        'Complete blood count'
      ]
    };
  };  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const handleSaveParsedData = () => {
    if (parsedSections && onTranscriptionComplete) {
      onTranscriptionComplete(parsedSections);
      setShowParsedPreview(false);
      setTranscript('');
      setParsedSections(null);
    }
  };
  
  const handleReset = () => {
    setTranscript('');
    setParsedSections(null);
    setShowParsedPreview(false);
    setError(null);
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
            AI-Powered Voice Transcription {isAssessment ? '(Clinical Assessment)' : isObjective ? '(Physical Exam)' : '(Patient History)'}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Demo: Simulated conversation transcription and parsing
          </p>
        </div>
        {isRecording && (
          <div className="flex items-center text-red-600">
            <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse mr-2"></div>
            <span className="text-sm font-medium">{formatTime(recordingTime)}</span>
          </div>
        )}
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      
      {/* Recording Controls */}
      <div className="flex items-center justify-center mb-6">
        {!isRecording ? (
          <button
            type="button"
            onClick={startRecording}
            disabled={isProcessing}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center disabled:bg-gray-400"
          >
            <Mic className="w-5 h-5 mr-2" />
            Start Recording (Demo)
          </button>
        ) : (
          <button
            type="button"
            onClick={stopRecording}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center animate-pulse"
          >
            <MicOff className="w-5 h-5 mr-2" />
            Stop Recording
          </button>
        )}
      </div>
      
      {/* Live Transcript */}
      {(transcript || isRecording) && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Live Transcript</h4>
          <div className="p-4 bg-gray-50 rounded-lg max-h-48 overflow-y-auto">
            <p className="text-sm text-gray-800 whitespace-pre-wrap">
              {transcript || (isRecording ? 'Listening...' : 'No transcript yet')}
            </p>
          </div>
        </div>
      )}
      
      {/* Processing Indicator */}
      {isProcessing && (
        <div className="flex flex-col items-center py-8">
          <Loader className="w-8 h-8 text-purple-600 animate-spin mb-4" />
          <p className="text-gray-600">AI is organizing the conversation into clinical sections...</p>
        </div>
      )}
      
      {/* Parsed Preview */}
      {showParsedPreview && parsedSections && (
        <div className="mt-6 border-t pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">AI-Parsed Clinical Information</h4>
          
          <div className="space-y-4 mb-6">
            {isAssessment ? (
              <>
                {/* Assessment Data Display */}
                {parsedSections.diagnosis && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Clinical Diagnosis</h5>
                    <p className="p-3 bg-purple-50 rounded-lg font-medium text-purple-900">
                      {parsedSections.diagnosis}
                    </p>
                  </div>
                )}
                
                {parsedSections.notes && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Assessment Notes</h5>
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-900 whitespace-pre-line">{parsedSections.notes}</p>
                    </div>
                  </div>
                )}
                
                {parsedSections.differentialDiagnoses && parsedSections.differentialDiagnoses.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Differential Diagnoses</h5>
                    <ul className="text-sm text-gray-700 p-3 bg-yellow-50 rounded-lg space-y-1">
                      {parsedSections.differentialDiagnoses.map((dx, idx) => (
                        <li key={idx}>• {dx}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {parsedSections.recommendedTests && parsedSections.recommendedTests.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Recommended Tests</h5>
                    <ul className="text-sm text-gray-700 p-3 bg-green-50 rounded-lg space-y-1">
                      {parsedSections.recommendedTests.map((test, idx) => (
                        <li key={idx}>• {test}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : isObjective ? (
              <>
                {/* Objective Data Display */}
                {parsedSections.vitalSigns && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Vital Signs</h5>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-600">Blood Pressure</p>
                        <p className="font-semibold">{parsedSections.vitalSigns.bloodPressure}</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-600">Heart Rate</p>
                        <p className="font-semibold">{parsedSections.vitalSigns.heartRate} bpm</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-600">Temperature</p>
                        <p className="font-semibold">{parsedSections.vitalSigns.temperature}°F</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-600">Respiratory Rate</p>
                        <p className="font-semibold">{parsedSections.vitalSigns.respiratoryRate}/min</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-600">O2 Saturation</p>
                        <p className="font-semibold">{parsedSections.vitalSigns.oxygenSaturation}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {parsedSections.physicalExam && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Physical Examination Findings</h5>
                    <div className="space-y-2">
                      {Object.entries(parsedSections.physicalExam).map(([system, finding]) => (
                        <div key={system} className="p-3 bg-green-50 rounded-lg">
                          <p className="text-sm font-medium text-gray-700 capitalize">{system}:</p>
                          <p className="text-sm text-gray-600">{finding}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <>
                {/* Subjective Data Display */}
                {parsedSections.chiefComplaint && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-1">Chief Complaint</h5>
                    <p className="text-sm text-gray-600 p-3 bg-blue-50 rounded-lg">
                      {parsedSections.chiefComplaint}
                    </p>
                  </div>
                )}
                
                {parsedSections.history.presentIllness.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-1">History of Present Illness</h5>
                    <ul className="text-sm text-gray-600 p-3 bg-green-50 rounded-lg space-y-1">
                      {parsedSections.history.presentIllness.map((item, idx) => (
                        <li key={idx}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {parsedSections.history.medications.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-1">Current Medications</h5>
                    <ul className="text-sm text-gray-600 p-3 bg-purple-50 rounded-lg space-y-1">
                      {parsedSections.history.medications.map((item, idx) => (
                        <li key={idx}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {parsedSections.history.allergies.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-1">Allergies</h5>
                    <ul className="text-sm text-gray-600 p-3 bg-red-50 rounded-lg space-y-1">
                      {parsedSections.history.allergies.map((item, idx) => (
                        <li key={idx}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {parsedSections.history.exposures && parsedSections.history.exposures.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-1">Relevant Exposures</h5>
                    <ul className="text-sm text-gray-600 p-3 bg-yellow-50 rounded-lg space-y-1">
                      {parsedSections.history.exposures.map((item, idx) => (
                        <li key={idx}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              Review the parsed information carefully and make edits if necessary
            </p>
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <RotateCcw className="w-4 h-4 inline mr-1" />
                Reset
              </button>
              <button
                type="button"
                onClick={handleSaveParsedData}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
              >
                <Edit2 className="w-4 h-4 mr-2" />
                Edit
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Instructions */}
      {!isRecording && !transcript && !isProcessing && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h5 className="font-medium text-blue-900 mb-2">Demo Mode:</h5>
          <p className="text-sm text-blue-800 mb-2">
            This is a simulated demonstration showing how the AI voice transcription would work.
          </p>
          <ol className="text-sm text-blue-800 space-y-1">
            <li>1. Click "Start Recording" to see a sample doctor-patient conversation</li>
            <li>2. Watch as the AI transcribes the conversation in real-time</li>
            <li>3. The AI will automatically parse and organize the information</li>
            <li>4. Review and save the structured data to your assessment</li>
          </ol>
        </div>
      )}
    </div>
  );
};

export default SpeechToTextTranscriber;