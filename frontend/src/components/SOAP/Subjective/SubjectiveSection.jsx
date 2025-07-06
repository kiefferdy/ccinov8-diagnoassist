import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, Mic, History, Clock, AlertCircle, 
  Sparkles, ChevronRight, FileText, User, Calendar,
  Stethoscope, Pill, Heart, Brain, Shield, Info,
  Activity, X, Wind
} from 'lucide-react';
import VoiceTranscription from '../../common/VoiceTranscription';
import AIAssistant from '../../common/AIAssistant';

const SubjectiveSection = ({ data, patient, episode, encounter, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('hpi');
  const [showVoiceTranscription, setShowVoiceTranscription] = useState(false);
  const [transcribingField, setTranscribingField] = useState('');
  const [rosExpanded, setRosExpanded] = useState(false);
  
  const handleFieldUpdate = (field, value) => {
    onUpdate({ [field]: value });
  };
  
  const handleVoiceTranscription = (field) => {
    setTranscribingField(field);
    setShowVoiceTranscription(true);
  };
  
  const handleTranscriptionSave = (text) => {
    if (transcribingField && text) {
      const currentValue = data[transcribingField] || '';
      handleFieldUpdate(transcribingField, currentValue + (currentValue ? '\n' : '') + text);
    }
    setShowVoiceTranscription(false);
    setTranscribingField('');
  };
  
  const handleAIInsight = (insight) => {
    if (insight.type === 'template' && insight.section === 'subjective') {
      // Apply template content to appropriate field
      if (insight.content.includes('Review of Systems:')) {
        // Parse ROS template
        const rosData = {};
        const lines = insight.content.split('\n');
        lines.forEach(line => {
          const match = line.match(/^(\w+):\s*(.+)$/);
          if (match) {
            const system = match[1].toLowerCase();
            rosData[system] = match[2];
          }
        });
        handleFieldUpdate('ros', { ...data.ros, ...rosData });
        setActiveTab('ros');
      } else {
        // Apply to HPI
        handleFieldUpdate('hpi', data.hpi ? `${data.hpi}\n\n${insight.content}` : insight.content);
      }
    } else if (insight.type === 'question') {
      // Add question to HPI
      handleFieldUpdate('hpi', data.hpi ? `${data.hpi}\n\n${insight.content}` : insight.content);
    }
  };
  
  const tabs = [
    { id: 'hpi', label: 'HPI', icon: MessageSquare, color: 'blue' },
    { id: 'ros', label: 'Review of Systems', icon: Clock, color: 'purple' },
    { id: 'history', label: 'History', icon: History, color: 'green' }
  ];
  
  // Calculate completion status
  const calculateTabCompletion = (tabId) => {
    switch (tabId) {
      case 'hpi':
        return data.hpi && data.hpi.length > 50 ? 'complete' : data.hpi ? 'partial' : 'empty';
      case 'ros':
        const rosSystems = Object.values(data.ros || {}).filter(v => v);
        return rosSystems.length > 10 ? 'complete' : rosSystems.length > 0 ? 'partial' : 'empty';
      case 'history':
        const historyFields = [data.pmh, data.medications, data.allergies, data.socialHistory, data.familyHistory];
        const filledFields = historyFields.filter(f => f);
        return filledFields.length >= 4 ? 'complete' : filledFields.length > 0 ? 'partial' : 'empty';
      default:
        return 'empty';
    }
  };
  
  const getCompletionIcon = (status) => {
    switch (status) {
      case 'complete':
        return <div className="w-2 h-2 bg-green-500 rounded-full" />;
      case 'partial':
        return <div className="w-2 h-2 bg-yellow-500 rounded-full" />;
      default:
        return <div className="w-2 h-2 bg-gray-300 rounded-full" />;
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Chief Complaint Card */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-2 flex items-center">
              <Stethoscope className="w-6 h-6 mr-2" />
              Chief Complaint
            </h3>
            <p className="text-2xl font-semibold mb-3">{episode.chiefComplaint}</p>
            <div className="flex items-center space-x-4 text-blue-100">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                <span className="text-sm">Started: {new Date(episode.createdAt).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                <span className="text-sm">{patient.name}, {patient.age} yo {patient.gender}</span>
              </div>
            </div>
          </div>
          <div className="ml-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Activity className="w-8 h-8" />
            </div>
          </div>
        </div>
      </div>
      
      {/* Tab Navigation with Enhanced Design */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="border-b border-gray-200 bg-gray-50">
          <nav className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const completion = calculateTabCompletion(tab.id);
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex-1 flex items-center justify-center px-6 py-4 text-sm font-medium 
                    border-b-3 transition-all duration-200 relative group
                    ${activeTab === tab.id
                      ? `text-${tab.color}-600 border-${tab.color}-600 bg-white`
                      : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  <span>{tab.label}</span>
                  <div className="ml-2">
                    {getCompletionIcon(completion)}
                  </div>
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-indigo-500" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* HPI Tab */}
          {activeTab === 'hpi' && (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <label className="text-lg font-semibold text-gray-900 flex items-center">
                      History of Present Illness
                      <Info className="w-4 h-4 ml-2 text-gray-400" title="Document the chronological story of the patient's illness" />
                    </label>
                    <p className="text-sm text-gray-600 mt-1">
                      Describe onset, location, duration, characteristics, aggravating/alleviating factors, radiation, and timing
                    </p>
                  </div>
                  <button
                    onClick={() => handleVoiceTranscription('hpi')}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
                  >
                    <Mic className="w-4 h-4 mr-2" />
                    Voice Input
                  </button>
                </div>
                <div className="relative">
                  <textarea
                    value={data.hpi || ''}
                    onChange={(e) => handleFieldUpdate('hpi', e.target.value)}
                    rows={8}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-800"
                    placeholder="Begin documenting the history of present illness..."
                  />
                  <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                    {(data.hpi || '').length} characters
                  </div>
                </div>
                
                {/* Quick Templates */}
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Quick Templates:</p>
                  <div className="flex flex-wrap gap-2">
                    {['OLDCARTS', 'OPQRST', 'SOCRATES'].map(template => (
                      <button
                        key={template}
                        onClick={() => {
                          const templates = {
                            'OLDCARTS': 'Onset:\nLocation:\nDuration:\nCharacteristics:\nAggravating factors:\nRelieving factors:\nTiming:\nSeverity:',
                            'OPQRST': 'Onset:\nProvocation/Palliation:\nQuality:\nRegion/Radiation:\nSeverity:\nTiming:',
                            'SOCRATES': 'Site:\nOnset:\nCharacter:\nRadiation:\nAssociations:\nTime course:\nExacerbating/Relieving factors:\nSeverity:'
                          };
                          handleFieldUpdate('hpi', templates[template]);
                        }}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Review of Systems Tab */}
          {activeTab === 'ros' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Review of Systems</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Document pertinent positives and negatives for each system
                  </p>
                </div>
                <button
                  onClick={() => setRosExpanded(!rosExpanded)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {rosExpanded ? 'Collapse All' : 'Expand All'}
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { id: 'constitutional', label: 'Constitutional', icon: Heart, placeholder: 'Fever, chills, weight loss, fatigue...' },
                  { id: 'eyes', label: 'Eyes', icon: Brain, placeholder: 'Vision changes, pain, discharge...' },
                  { id: 'ent', label: 'Ears, Nose, Throat', icon: MessageSquare, placeholder: 'Hearing loss, tinnitus, congestion...' },
                  { id: 'cardiovascular', label: 'Cardiovascular', icon: Heart, placeholder: 'Chest pain, palpitations, edema...' },
                  { id: 'respiratory', label: 'Respiratory', icon: Wind, placeholder: 'Cough, dyspnea, wheezing...' },
                  { id: 'gastrointestinal', label: 'Gastrointestinal', icon: Pill, placeholder: 'Nausea, vomiting, diarrhea...' },
                  { id: 'genitourinary', label: 'Genitourinary', icon: Shield, placeholder: 'Dysuria, frequency, discharge...' },
                  { id: 'musculoskeletal', label: 'Musculoskeletal', icon: Activity, placeholder: 'Joint pain, stiffness, swelling...' },
                  { id: 'integumentary', label: 'Integumentary', icon: Shield, placeholder: 'Rash, itching, lesions...' },
                  { id: 'neurological', label: 'Neurological', icon: Brain, placeholder: 'Headache, dizziness, weakness...' },
                  { id: 'psychiatric', label: 'Psychiatric', icon: Brain, placeholder: 'Depression, anxiety, sleep...' },
                  { id: 'endocrine', label: 'Endocrine', icon: Activity, placeholder: 'Polyuria, polydipsia, heat intolerance...' },
                  { id: 'hematologic', label: 'Hematologic', icon: Heart, placeholder: 'Bruising, bleeding, lymphadenopathy...' },
                  { id: 'allergic', label: 'Allergic/Immunologic', icon: Shield, placeholder: 'Allergies, reactions, immunodeficiency...' }
                ].map((system) => {
                  const SystemIcon = system.icon;
                  return (
                    <div key={system.id} className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:border-gray-300 transition-colors">
                      <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                        <SystemIcon className="w-4 h-4 mr-2 text-gray-500" />
                        {system.label}
                      </label>
                      {rosExpanded ? (
                        <textarea
                          value={data.ros?.[system.id] || ''}
                          onChange={(e) => handleFieldUpdate('ros', {
                            ...data.ros,
                            [system.id]: e.target.value
                          })}
                          rows={2}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                          placeholder={system.placeholder}
                        />
                      ) : (
                        <input
                          type="text"
                          value={data.ros?.[system.id] || ''}
                          onChange={(e) => handleFieldUpdate('ros', {
                            ...data.ros,
                            [system.id]: e.target.value
                          })}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder={system.placeholder}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Quick ROS Templates */}
              <div className="mt-6 p-4 bg-purple-50 rounded-xl border border-purple-200">
                <p className="text-sm font-medium text-purple-900 mb-2">Quick Actions:</p>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      const negativeROS = {
                        constitutional: 'Denies fever, chills, weight loss, fatigue',
                        eyes: 'Denies vision changes, pain, discharge',
                        ent: 'Denies hearing loss, tinnitus, sore throat',
                        cardiovascular: 'Denies chest pain, palpitations, edema',
                        respiratory: 'Denies cough, dyspnea, wheezing',
                        gastrointestinal: 'Denies nausea, vomiting, diarrhea, constipation',
                        genitourinary: 'Denies dysuria, frequency, discharge',
                        musculoskeletal: 'Denies joint pain, stiffness, swelling',
                        integumentary: 'Denies rash, itching, lesions',
                        neurological: 'Denies headache, dizziness, weakness',
                        psychiatric: 'Denies depression, anxiety, SI/HI',
                        endocrine: 'Denies polyuria, polydipsia, heat/cold intolerance',
                        hematologic: 'Denies bruising, bleeding, lymphadenopathy',
                        allergic: 'Denies allergies, reactions'
                      };
                      handleFieldUpdate('ros', negativeROS);
                    }}
                    className="px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                  >
                    All Systems Negative
                  </button>
                  <button
                    onClick={() => handleFieldUpdate('ros', {})}
                    className="px-3 py-1.5 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                  >
                    Clear All
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              {/* Past Medical History */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                  <Clock className="w-5 h-5 mr-2 text-green-600" />
                  Past Medical History
                </label>
                <textarea
                  value={data.pmh || ''}
                  onChange={(e) => handleFieldUpdate('pmh', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                  placeholder="Document significant past medical history, surgeries, hospitalizations..."
                />
                {patient.medicalBackground?.chronicConditions?.length > 0 && (
                  <div className="mt-3 p-4 bg-white rounded-lg border border-green-200">
                    <p className="text-sm font-medium text-green-800 mb-2 flex items-center">
                      <Info className="w-4 h-4 mr-1" />
                      Documented Chronic Conditions:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {patient.medicalBackground.chronicConditions.map((c, idx) => (
                        <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                          {c.condition} ({c.icd10})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Medications */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                  <Pill className="w-5 h-5 mr-2 text-blue-600" />
                  Current Medications
                </label>
                <textarea
                  value={data.medications || ''}
                  onChange={(e) => handleFieldUpdate('medications', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="List all current medications with dosages and frequencies..."
                />
                {patient.medicalBackground?.medications?.filter(m => m.ongoing).length > 0 && (
                  <div className="mt-3 p-4 bg-white rounded-lg border border-blue-200">
                    <p className="text-sm font-medium text-blue-800 mb-2 flex items-center">
                      <Info className="w-4 h-4 mr-1" />
                      Active Medications on File:
                    </p>
                    <div className="space-y-1">
                      {patient.medicalBackground.medications
                        .filter(m => m.ongoing)
                        .map((med, idx) => (
                          <div key={idx} className="flex items-center justify-between text-sm">
                            <span className="font-medium text-gray-800">{med.name}</span>
                            <span className="text-gray-600">{med.dosage} - {med.frequency}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Allergies */}
              <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
                <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                  <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
                  Allergies
                </label>
                <textarea
                  value={data.allergies || ''}
                  onChange={(e) => handleFieldUpdate('allergies', e.target.value)}
                  rows={2}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                  placeholder="Document all known allergies and reactions..."
                />
                {patient.medicalBackground?.allergies?.length > 0 && (
                  <div className="mt-3 p-4 bg-white rounded-lg border border-red-300">
                    <div className="flex items-start">
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-bold text-red-800 mb-2">⚠️ KNOWN ALLERGIES:</p>
                        <div className="space-y-2">
                          {patient.medicalBackground.allergies.map((allergy, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-red-50 rounded-lg p-2">
                              <span className="font-medium text-red-900">{allergy.allergen}</span>
                              <span className="text-sm text-red-700">
                                {allergy.reaction} - {allergy.severity}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Social History */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
                <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                  <User className="w-5 h-5 mr-2 text-purple-600" />
                  Social History
                </label>
                <textarea
                  value={data.socialHistory || ''}
                  onChange={(e) => handleFieldUpdate('socialHistory', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  placeholder="Document tobacco use, alcohol use, drug use, occupation, living situation..."
                />
                <div className="mt-3 flex flex-wrap gap-2">
                  {['Never smoker', 'Former smoker', 'Current smoker', 'Social drinker', 'No alcohol', 'No illicit drugs'].map(template => (
                    <button
                      key={template}
                      onClick={() => {
                        const current = data.socialHistory || '';
                        handleFieldUpdate('socialHistory', current ? `${current}, ${template}` : template);
                      }}
                      className="px-3 py-1 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm"
                    >
                      + {template}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Family History */}
              <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-200">
                <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                  <Heart className="w-5 h-5 mr-2 text-indigo-600" />
                  Family History
                </label>
                <textarea
                  value={data.familyHistory || ''}
                  onChange={(e) => handleFieldUpdate('familyHistory', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  placeholder="Document significant family medical history..."
                />
                <div className="mt-3 flex flex-wrap gap-2">
                  {['HTN', 'DM', 'CAD', 'Cancer', 'Stroke', 'Mental illness'].map(condition => (
                    <button
                      key={condition}
                      onClick={() => {
                        const current = data.familyHistory || '';
                        handleFieldUpdate('familyHistory', current ? `${current}, ${condition}` : condition);
                      }}
                      className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
                    >
                      + {condition}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Voice Transcription Modal */}
      {showVoiceTranscription && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">Voice Transcription</h3>
                <button
                  onClick={() => setShowVoiceTranscription(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <VoiceTranscription
                onSave={handleTranscriptionSave}
                sectionName={transcribingField.toUpperCase()}
                placeholder={`Start speaking to record ${transcribingField}...`}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* AI Assistant */}
      <AIAssistant
        patient={patient}
        episode={episode}
        encounter={encounter}
        currentSection="subjective"
        onInsightApply={handleAIInsight}
      />
    </div>
  );
};

export default SubjectiveSection;