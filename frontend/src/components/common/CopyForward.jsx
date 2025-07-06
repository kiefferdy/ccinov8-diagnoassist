import React, { useState } from 'react';
import { Copy, Check, X } from 'lucide-react';

const CopyForward = ({ previousEncounters, onCopyForward }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedEncounter, setSelectedEncounter] = useState('');
  const [selectedSections, setSelectedSections] = useState({
    vitals: false,
    medications: false,
    allergies: false,
    physicalExam: false,
    assessment: false
  });
  
  const handleToggleSection = (section) => {
    setSelectedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const handleCopy = () => {
    if (!selectedEncounter) return;
    
    const sections = Object.keys(selectedSections).filter(key => selectedSections[key]);
    if (sections.length === 0) return;
    
    onCopyForward(selectedEncounter, sections);
    setShowModal(false);
    setSelectedEncounter('');
    setSelectedSections({
      vitals: false,
      medications: false,
      allergies: false,
      physicalExam: false,
      assessment: false
    });
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };
  
  if (previousEncounters.length === 0) return null;
  
  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="inline-flex items-center px-3 py-1.5 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
      >
        <Copy className="w-4 h-4 mr-1.5" />
        Copy Forward
      </button>
      
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Copy Forward from Previous Encounter</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Select Encounter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Previous Encounter
                </label>
                <select
                  value={selectedEncounter}
                  onChange={(e) => setSelectedEncounter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Choose an encounter...</option>
                  {previousEncounters.map((encounter, index) => (
                    <option key={encounter.id} value={encounter.id}>
                      Encounter #{previousEncounters.length - index} - {formatDate(encounter.date)} ({encounter.type})
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Select Sections */}
              {selectedEncounter && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Data to Copy
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedSections.vitals}
                        onChange={() => handleToggleSection('vitals')}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Vital Signs</span>
                    </label>
                    <label className="flex items-center p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedSections.medications}
                        onChange={() => handleToggleSection('medications')}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Current Medications</span>
                    </label>
                    <label className="flex items-center p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedSections.allergies}
                        onChange={() => handleToggleSection('allergies')}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Allergies</span>
                    </label>
                    <label className="flex items-center p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedSections.physicalExam}
                        onChange={() => handleToggleSection('physicalExam')}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Physical Exam Findings</span>
                    </label>
                    <label className="flex items-center p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedSections.assessment}
                        onChange={() => handleToggleSection('assessment')}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Previous Assessment</span>
                    </label>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCopy}
                disabled={!selectedEncounter || Object.values(selectedSections).every(v => !v)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <Check className="w-4 h-4 mr-1.5" />
                Copy Selected
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CopyForward;