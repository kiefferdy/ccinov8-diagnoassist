import React, { useState } from 'react';
import { Brain, Plus, X, AlertTriangle, CheckCircle, HelpCircle, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { generateId } from '../../../utils/storage';

const AssessmentSection = ({ data, onUpdate }) => {
  const [showAddDiagnosis, setShowAddDiagnosis] = useState(false);
  const [newDiagnosis, setNewDiagnosis] = useState({
    diagnosis: '',
    icd10: '',
    probability: 'medium',
    supportingEvidence: '',
    contradictingEvidence: ''
  });
  const [expandedDiagnosis, setExpandedDiagnosis] = useState(null);
  const [showAIConsult, setShowAIConsult] = useState(false);
  
  const handleClinicalImpressionUpdate = (value) => {
    onUpdate({ clinicalImpression: value });
  };
  
  const handleAddDifferentialDiagnosis = () => {
    if (!newDiagnosis.diagnosis.trim()) return;
    
    const diagnosis = {
      id: generateId('D'),
      diagnosis: newDiagnosis.diagnosis,
      icd10: newDiagnosis.icd10,
      probability: newDiagnosis.probability,
      supportingEvidence: newDiagnosis.supportingEvidence.split(',').map(s => s.trim()).filter(Boolean),
      contradictingEvidence: newDiagnosis.contradictingEvidence.split(',').map(s => s.trim()).filter(Boolean)
    };
    
    onUpdate({
      differentialDiagnosis: [...(data.differentialDiagnosis || []), diagnosis]
    });
    
    setNewDiagnosis({
      diagnosis: '',
      icd10: '',
      probability: 'medium',
      supportingEvidence: '',
      contradictingEvidence: ''
    });
    setShowAddDiagnosis(false);
  };
  
  const handleRemoveDiagnosis = (diagnosisId) => {
    onUpdate({
      differentialDiagnosis: data.differentialDiagnosis.filter(d => d.id !== diagnosisId)
    });
  };
  
  const handleUpdateProbability = (diagnosisId, probability) => {
    onUpdate({
      differentialDiagnosis: data.differentialDiagnosis.map(d =>
        d.id === diagnosisId ? { ...d, probability } : d
      )
    });
  };
  
  const handleSetWorkingDiagnosis = (diagnosis) => {
    onUpdate({
      workingDiagnosis: {
        diagnosis: diagnosis.diagnosis,
        icd10: diagnosis.icd10,
        confidence: 'probable',
        clinicalReasoning: data.clinicalImpression || ''
      }
    });
  };
  
  const handleWorkingDiagnosisUpdate = (field, value) => {
    onUpdate({
      workingDiagnosis: {
        ...data.workingDiagnosis,
        [field]: value
      }
    });
  };
  
  const getProbabilityColor = (probability) => {
    switch (probability) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };
  
  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'confirmed': return 'text-green-600 bg-green-50';
      case 'probable': return 'text-blue-600 bg-blue-50';
      case 'possible': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Clinical Impression */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2" />
          Clinical Impression
        </h3>
        <textarea
          value={data.clinicalImpression || ''}
          onChange={(e) => handleClinicalImpressionUpdate(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Summarize your clinical impression based on the history and examination findings..."
        />
      </div>
      {/* Differential Diagnosis */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Differential Diagnosis</h3>
          <button
            onClick={() => setShowAddDiagnosis(true)}
            className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Diagnosis
          </button>
        </div>
        
        {data.differentialDiagnosis?.length > 0 ? (
          <div className="space-y-3">
            {data.differentialDiagnosis.map((diagnosis) => (
              <div key={diagnosis.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium text-gray-900">{diagnosis.diagnosis}</h4>
                      {diagnosis.icd10 && (
                        <span className="text-sm text-gray-500">ICD-10: {diagnosis.icd10}</span>
                      )}
                      <select
                        value={diagnosis.probability}
                        onChange={(e) => handleUpdateProbability(diagnosis.id, e.target.value)}
                        className={`text-xs px-2 py-1 rounded-full font-medium ${getProbabilityColor(diagnosis.probability)}`}
                      >
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                    </div>
                    
                    <button
                      onClick={() => setExpandedDiagnosis(expandedDiagnosis === diagnosis.id ? null : diagnosis.id)}
                      className="text-sm text-blue-600 hover:text-blue-700 mt-2 flex items-center"
                    >
                      {expandedDiagnosis === diagnosis.id ? (
                        <>Hide Evidence <ChevronUp className="w-3 h-3 ml-1" /></>
                      ) : (
                        <>Show Evidence <ChevronDown className="w-3 h-3 ml-1" /></>
                      )}
                    </button>
                    
                    {expandedDiagnosis === diagnosis.id && (
                      <div className="mt-3 space-y-2 text-sm">
                        {diagnosis.supportingEvidence.length > 0 && (
                          <div>
                            <p className="font-medium text-green-700">Supporting Evidence:</p>
                            <ul className="list-disc list-inside text-gray-600 ml-2">
                              {diagnosis.supportingEvidence.map((evidence, idx) => (
                                <li key={idx}>{evidence}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {diagnosis.contradictingEvidence.length > 0 && (
                          <div>
                            <p className="font-medium text-red-700">Contradicting Evidence:</p>
                            <ul className="list-disc list-inside text-gray-600 ml-2">
                              {diagnosis.contradictingEvidence.map((evidence, idx) => (
                                <li key={idx}>{evidence}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleSetWorkingDiagnosis(diagnosis)}
                      className="text-sm text-blue-600 hover:text-blue-700"
                      title="Set as working diagnosis"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleRemoveDiagnosis(diagnosis.id)}
                      className="text-sm text-gray-400 hover:text-red-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>No differential diagnoses added yet</p>
          </div>
        )}
      </div>
      
      {/* Working Diagnosis */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Working Diagnosis</h3>
        
        {data.workingDiagnosis?.diagnosis ? (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-medium text-blue-900">{data.workingDiagnosis.diagnosis}</h4>
                  {data.workingDiagnosis.icd10 && (
                    <p className="text-sm text-blue-700 mt-1">ICD-10: {data.workingDiagnosis.icd10}</p>
                  )}
                </div>
                <select
                  value={data.workingDiagnosis.confidence || 'possible'}
                  onChange={(e) => handleWorkingDiagnosisUpdate('confidence', e.target.value)}
                  className={`text-xs px-3 py-1 rounded-full font-medium ${getConfidenceColor(data.workingDiagnosis.confidence)}`}
                >
                  <option value="confirmed">Confirmed</option>
                  <option value="probable">Probable</option>
                  <option value="possible">Possible</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Clinical Reasoning
              </label>
              <textarea
                value={data.workingDiagnosis.clinicalReasoning || ''}
                onChange={(e) => handleWorkingDiagnosisUpdate('clinicalReasoning', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Explain your reasoning for this diagnosis..."
              />
            </div>
          </div>
        ) : (
          <div className="text-center py-6 text-gray-500">
            <HelpCircle className="w-10 h-10 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">Select a diagnosis from the differential list to set as working diagnosis</p>
          </div>
        )}
      </div>
      
      {/* AI Consultation (Optional) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Sparkles className="w-5 h-5 mr-2" />
            AI Clinical Assistant
          </h3>
          <button
            onClick={() => setShowAIConsult(!showAIConsult)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            {showAIConsult ? 'Hide' : 'Show'} Assistant
          </button>
        </div>
        
        {showAIConsult && (
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-3">
              Get AI-powered insights based on your clinical findings
            </p>
            <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
              <Sparkles className="w-4 h-4 mr-2" />
              Generate Clinical Insights
            </button>
          </div>
        )}
      </div>
      {/* Add Diagnosis Modal */}
      {showAddDiagnosis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Add Differential Diagnosis</h3>
              <button
                onClick={() => setShowAddDiagnosis(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diagnosis <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newDiagnosis.diagnosis}
                  onChange={(e) => setNewDiagnosis({ ...newDiagnosis, diagnosis: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Community-acquired pneumonia"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ICD-10 Code
                </label>
                <input
                  type="text"
                  value={newDiagnosis.icd10}
                  onChange={(e) => setNewDiagnosis({ ...newDiagnosis, icd10: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., J18.9"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Probability
                </label>
                <select
                  value={newDiagnosis.probability}
                  onChange={(e) => setNewDiagnosis({ ...newDiagnosis, probability: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Supporting Evidence
                </label>
                <textarea
                  value={newDiagnosis.supportingEvidence}
                  onChange={(e) => setNewDiagnosis({ ...newDiagnosis, supportingEvidence: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="List supporting findings separated by commas (e.g., fever, productive cough, rhonchi on exam)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contradicting Evidence
                </label>
                <textarea
                  value={newDiagnosis.contradictingEvidence}
                  onChange={(e) => setNewDiagnosis({ ...newDiagnosis, contradictingEvidence: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="List contradicting findings separated by commas (e.g., normal chest X-ray)"
                />
              </div>
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowAddDiagnosis(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddDifferentialDiagnosis}
                disabled={!newDiagnosis.diagnosis.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Diagnosis
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssessmentSection;