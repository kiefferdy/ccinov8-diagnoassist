import React, { useState } from 'react';
import { MessageSquare, Mic, History, Clock, AlertCircle } from 'lucide-react';
import SpeechToTextTranscriber from '../../Patient/components/SpeechToTextTranscriber';

const SubjectiveSection = ({ data, patient, episode, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('hpi');
  const [showTranscriber, setShowTranscriber] = useState(false);
  const [transcribingField, setTranscribingField] = useState('');
  
  const handleFieldUpdate = (field, value) => {
    onUpdate({ [field]: value });
  };
  
  const handleTranscription = (field) => {
    setTranscribingField(field);
    setShowTranscriber(true);
  };
  
  const handleTranscriptionComplete = (text) => {
    if (transcribingField && text) {
      const currentValue = data[transcribingField] || '';
      handleFieldUpdate(transcribingField, currentValue + (currentValue ? '\n' : '') + text);
    }
    setShowTranscriber(false);
    setTranscribingField('');
  };
  
  const tabs = [
    { id: 'hpi', label: 'HPI', icon: MessageSquare },
    { id: 'ros', label: 'Review of Systems', icon: Clock },
    { id: 'history', label: 'History', icon: History }
  ];
  
  return (
    <div className="space-y-6">
      {/* Chief Complaint */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Chief Complaint</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-900 font-medium">{episode.chiefComplaint}</p>
          <p className="text-sm text-blue-700 mt-1">
            Episode started: {new Date(episode.createdAt).toLocaleDateString()}
          </p>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors
                    ${activeTab === tab.id
                      ? 'text-blue-600 border-blue-600'
                      : 'text-gray-500 border-transparent hover:text-gray-700'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* HPI Tab */}
          {activeTab === 'hpi' && (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    History of Present Illness
                  </label>
                  <button
                    onClick={() => handleTranscription('hpi')}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    <Mic className="w-4 h-4 mr-1" />
                    Transcribe
                  </button>
                </div>
                <textarea
                  value={data.hpi || ''}
                  onChange={(e) => handleFieldUpdate('hpi', e.target.value)}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the history of the present illness..."
                />
              </div>
            </div>
          )}
          {/* Review of Systems Tab */}
          {activeTab === 'ros' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600 mb-4">
                Document pertinent positives and negatives for each system
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { id: 'constitutional', label: 'Constitutional' },
                  { id: 'eyes', label: 'Eyes' },
                  { id: 'ent', label: 'Ears, Nose, Throat' },
                  { id: 'cardiovascular', label: 'Cardiovascular' },
                  { id: 'respiratory', label: 'Respiratory' },
                  { id: 'gastrointestinal', label: 'Gastrointestinal' },
                  { id: 'genitourinary', label: 'Genitourinary' },
                  { id: 'musculoskeletal', label: 'Musculoskeletal' },
                  { id: 'integumentary', label: 'Integumentary' },
                  { id: 'neurological', label: 'Neurological' },
                  { id: 'psychiatric', label: 'Psychiatric' },
                  { id: 'endocrine', label: 'Endocrine' },
                  { id: 'hematologic', label: 'Hematologic' },
                  { id: 'allergic', label: 'Allergic/Immunologic' }
                ].map((system) => (
                  <div key={system.id}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {system.label}
                    </label>
                    <input
                      type="text"
                      value={data.ros?.[system.id] || ''}
                      onChange={(e) => handleFieldUpdate('ros', {
                        ...data.ros,
                        [system.id]: e.target.value
                      })}
                      className="w-full px-3 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter findings..."
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              {/* Past Medical History */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Past Medical History
                </label>
                <textarea
                  value={data.pmh || ''}
                  onChange={(e) => handleFieldUpdate('pmh', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Document past medical history..."
                />
                {patient.medicalBackground?.chronicConditions?.length > 0 && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-600 mb-1">Chronic Conditions:</p>
                    <p className="text-sm text-gray-700">
                      {patient.medicalBackground.chronicConditions.map(c => c.condition).join(', ')}
                    </p>
                  </div>
                )}
              </div>
              
              {/* Medications */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Medications
                </label>
                <textarea
                  value={data.medications || ''}
                  onChange={(e) => handleFieldUpdate('medications', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="List current medications..."
                />
                {patient.medicalBackground?.medications?.filter(m => m.ongoing).length > 0 && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-600 mb-1">From Patient Record:</p>
                    <p className="text-sm text-gray-700">
                      {patient.medicalBackground.medications
                        .filter(m => m.ongoing)
                        .map(m => `${m.name} ${m.dosage} ${m.frequency}`)
                        .join(', ')}
                    </p>
                  </div>
                )}
              </div>
              
              {/* Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Allergies
                </label>
                <div className="relative">
                  <textarea
                    value={data.allergies || ''}
                    onChange={(e) => handleFieldUpdate('allergies', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Document allergies..."
                  />
                  {patient.medicalBackground?.allergies?.length > 0 && (
                    <div className="mt-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                      <div className="flex items-start">
                        <AlertCircle className="w-4 h-4 text-orange-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-orange-800 mb-1">Known Allergies:</p>
                          <p className="text-sm text-orange-700">
                            {patient.medicalBackground.allergies
                              .map(a => `${a.allergen} (${a.reaction})`)
                              .join(', ')}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Social History */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Social History
                </label>
                <textarea
                  value={data.socialHistory || ''}
                  onChange={(e) => handleFieldUpdate('socialHistory', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Document social history..."
                />
              </div>
              
              {/* Family History */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Family History
                </label>
                <textarea
                  value={data.familyHistory || ''}
                  onChange={(e) => handleFieldUpdate('familyHistory', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Document family history..."
                />
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Speech to Text Transcriber Modal */}
      {showTranscriber && (
        <SpeechToTextTranscriber
          onClose={() => setShowTranscriber(false)}
          onTranscriptionComplete={handleTranscriptionComplete}
          fieldName={transcribingField}
        />
      )}
    </div>
  );
};

export default SubjectiveSection;