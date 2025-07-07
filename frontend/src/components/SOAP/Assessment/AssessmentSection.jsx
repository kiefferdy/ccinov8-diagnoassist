import React, { useState } from 'react';
import { 
  Brain, Plus, X, AlertTriangle, CheckCircle, HelpCircle, 
  Sparkles, ChevronDown, ChevronUp, Target, Search, 
  FileSearch, Lightbulb, BookOpen, TrendingUp, Shield,
  AlertCircle, ChevronRight, Stethoscope, Activity,
  Microscope, FileText, Info, Zap
} from 'lucide-react';
import { generateId } from '../../../utils/storage';
import AIAssistant from '../../common/AIAssistant';

const AssessmentSection = ({ data, patient, episode, encounter, onUpdate }) => {
  const [showAddDiagnosis, setShowAddDiagnosis] = useState(false);
  const [newDiagnosis, setNewDiagnosis] = useState({
    diagnosis: '',
    icd10: '',
    probability: 'medium',
    supportingEvidence: '',
    contradictingEvidence: ''
  });
  const [expandedDiagnosis, setExpandedDiagnosis] = useState(null);
  const [showRiskAssessment, setShowRiskAssessment] = useState(false);
  
  // Common diagnoses based on chief complaint
  const getCommonDiagnoses = () => {
    const chiefComplaint = episode?.chiefComplaint?.toLowerCase() || '';
    
    const diagnosesByComplaint = {
      'chest pain': [
        { diagnosis: 'Acute Coronary Syndrome', icd10: 'I20.9' },
        { diagnosis: 'Gastroesophageal Reflux Disease', icd10: 'K21.9' },
        { diagnosis: 'Costochondritis', icd10: 'M94.0' },
        { diagnosis: 'Pulmonary Embolism', icd10: 'I26.9' },
        { diagnosis: 'Anxiety/Panic Disorder', icd10: 'F41.0' }
      ],
      'headache': [
        { diagnosis: 'Migraine', icd10: 'G43.9' },
        { diagnosis: 'Tension Headache', icd10: 'G44.2' },
        { diagnosis: 'Cluster Headache', icd10: 'G44.0' },
        { diagnosis: 'Sinusitis', icd10: 'J32.9' },
        { diagnosis: 'Temporal Arteritis', icd10: 'M31.6' }
      ],
      'abdominal pain': [
        { diagnosis: 'Appendicitis', icd10: 'K37' },
        { diagnosis: 'Cholecystitis', icd10: 'K81.9' },
        { diagnosis: 'Gastroenteritis', icd10: 'K52.9' },
        { diagnosis: 'Peptic Ulcer Disease', icd10: 'K27.9' },
        { diagnosis: 'Urinary Tract Infection', icd10: 'N39.0' }
      ],
      'cough': [
        { diagnosis: 'Upper Respiratory Infection', icd10: 'J06.9' },
        { diagnosis: 'Pneumonia', icd10: 'J18.9' },
        { diagnosis: 'Bronchitis', icd10: 'J20.9' },
        { diagnosis: 'Asthma Exacerbation', icd10: 'J45.901' },
        { diagnosis: 'COVID-19', icd10: 'U07.1' }
      ]
    };
    
    // Find matching diagnoses
    for (const [complaint, diagnoses] of Object.entries(diagnosesByComplaint)) {
      if (chiefComplaint.includes(complaint)) {
        return diagnoses;
      }
    }
    
    return [];
  };
  
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
  
  const handleRiskAssessmentUpdate = (value) => {
    onUpdate({ riskAssessment: value });
  };
  
  const handleAIInsight = (insight) => {
    if (insight.type === 'differential') {
      // Parse differential diagnosis from AI
      const lines = insight.content.split('\n').filter(line => line.includes('(') && line.includes(')'));
      const newDiagnoses = lines.map(line => {
        const match = line.match(/•?\s*(.+)\s*\(([A-Z]\d+\.?\d*)\)/);
        if (match) {
          return {
            id: generateId('D'),
            diagnosis: match[1].trim(),
            icd10: match[2],
            probability: 'medium',
            supportingEvidence: [],
            contradictingEvidence: []
          };
        }
        return null;
      }).filter(Boolean);
      
      if (newDiagnoses.length > 0) {
        onUpdate({
          differentialDiagnosis: [...(data.differentialDiagnosis || []), ...newDiagnoses]
        });
      }
    }
  };
  
  const getProbabilityConfig = (probability) => {
    const configs = {
      high: {
        color: 'text-red-700 bg-red-100 border-red-300',
        icon: AlertCircle,
        label: 'High Probability'
      },
      medium: {
        color: 'text-yellow-700 bg-yellow-100 border-yellow-300',
        icon: TrendingUp,
        label: 'Medium Probability'
      },
      low: {
        color: 'text-green-700 bg-green-100 border-green-300',
        icon: Shield,
        label: 'Low Probability'
      }
    };
    return configs[probability] || configs.medium;
  };
  
  const getConfidenceConfig = (confidence) => {
    const configs = {
      confirmed: {
        color: 'text-green-700 bg-green-100 border-green-300',
        icon: CheckCircle,
        label: 'Confirmed Diagnosis'
      },
      probable: {
        color: 'text-blue-700 bg-blue-100 border-blue-300',
        icon: Target,
        label: 'Probable Diagnosis'
      },
      possible: {
        color: 'text-gray-700 bg-gray-100 border-gray-300',
        icon: HelpCircle,
        label: 'Possible Diagnosis'
      }
    };
    return configs[confidence] || configs.possible;
  };
  
  // Sort differential diagnoses by probability
  const sortedDifferentialDiagnosis = [...(data.differentialDiagnosis || [])].sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a.probability] - order[b.probability];
  });
  
  return (
    <div className="space-y-6">
      {/* Assessment Overview */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2 flex items-center">
              <Brain className="w-6 h-6 mr-2" />
              Clinical Assessment
            </h3>
            <p className="text-purple-100">
              Synthesize findings into diagnoses and clinical reasoning
            </p>
          </div>
          <div className="bg-white/20 rounded-xl p-4 backdrop-blur-sm">
            <div className="text-center">
              <div className="text-3xl font-bold">
                {(data.differentialDiagnosis?.length || 0) + (data.workingDiagnosis?.diagnosis ? 1 : 0)}
              </div>
              <div className="text-sm text-purple-200">Total Diagnoses</div>
            </div>
          </div>
        </div>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Activity className="w-5 h-5 mb-1" />
            <div className="text-sm font-medium">Differential</div>
            <div className="text-lg font-bold">{data.differentialDiagnosis?.length || 0}</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Target className="w-5 h-5 mb-1" />
            <div className="text-sm font-medium">Working Dx</div>
            <div className="text-lg font-bold">{data.workingDiagnosis?.diagnosis ? 1 : 0}</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Shield className="w-5 h-5 mb-1" />
            <div className="text-sm font-medium">Risk Level</div>
            <div className="text-lg font-bold">{data.riskAssessment ? 'Done' : 'Pending'}</div>
          </div>
        </div>
      </div>
      
      {/* Clinical Impression */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
          Clinical Impression
        </h3>
        <textarea
          value={data.clinicalImpression || ''}
          onChange={(e) => handleClinicalImpressionUpdate(e.target.value)}
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          placeholder="Summarize your clinical impression based on the history and examination findings..."
        />
        <div className="mt-3 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            {data.clinicalImpression?.length || 0} characters
          </p>
          <button className="text-sm text-purple-600 hover:text-purple-700 flex items-center">
            <Sparkles className="w-4 h-4 mr-1" />
            AI Suggestions
          </button>
        </div>
      </div>
      
      {/* Differential Diagnosis */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Microscope className="w-5 h-5 mr-2 text-purple-600" />
              Differential Diagnosis
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              List possible diagnoses in order of probability
            </p>
          </div>
          <button
            onClick={() => setShowAddDiagnosis(true)}
            className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-md hover:shadow-lg"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Diagnosis
          </button>
        </div>
        
        {sortedDifferentialDiagnosis.length > 0 ? (
          <div className="space-y-3">
            {sortedDifferentialDiagnosis.map((diagnosis) => {
              const probabilityConfig = getProbabilityConfig(diagnosis.probability);
              const ProbabilityIcon = probabilityConfig.icon;
              
              return (
                <div 
                  key={diagnosis.id} 
                  className={`border-2 rounded-xl p-4 transition-all hover:shadow-md ${
                    expandedDiagnosis === diagnosis.id ? 'border-purple-300 bg-purple-50' : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 flex-wrap">
                        <h4 className="font-semibold text-gray-900 text-lg">{diagnosis.diagnosis}</h4>
                        {diagnosis.icd10 && (
                          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                            ICD-10: {diagnosis.icd10}
                          </span>
                        )}
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${probabilityConfig.color}`}>
                          <ProbabilityIcon className="w-3 h-3 mr-1" />
                          {probabilityConfig.label}
                        </div>
                      </div>
                      
                      <button
                        onClick={() => setExpandedDiagnosis(expandedDiagnosis === diagnosis.id ? null : diagnosis.id)}
                        className="text-sm text-purple-600 hover:text-purple-700 mt-3 flex items-center font-medium"
                      >
                        {expandedDiagnosis === diagnosis.id ? (
                          <>
                            <ChevronUp className="w-4 h-4 mr-1" />
                            Hide Clinical Evidence
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4 mr-1" />
                            Show Clinical Evidence
                          </>
                        )}
                      </button>
                      
                      {expandedDiagnosis === diagnosis.id && (
                        <div className="mt-4 grid md:grid-cols-2 gap-4">
                          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                            <p className="font-medium text-green-800 mb-2 flex items-center">
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Supporting Evidence
                            </p>
                            {diagnosis.supportingEvidence.length > 0 ? (
                              <ul className="space-y-1">
                                {diagnosis.supportingEvidence.map((evidence, idx) => (
                                  <li key={idx} className="text-sm text-green-700 flex items-start">
                                    <span className="text-green-500 mr-2">•</span>
                                    {evidence}
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-sm text-gray-500 italic">No evidence added</p>
                            )}
                          </div>
                          
                          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                            <p className="font-medium text-red-800 mb-2 flex items-center">
                              <X className="w-4 h-4 mr-1" />
                              Contradicting Evidence
                            </p>
                            {diagnosis.contradictingEvidence.length > 0 ? (
                              <ul className="space-y-1">
                                {diagnosis.contradictingEvidence.map((evidence, idx) => (
                                  <li key={idx} className="text-sm text-red-700 flex items-start">
                                    <span className="text-red-500 mr-2">•</span>
                                    {evidence}
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-sm text-gray-500 italic">No contradictions noted</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-start gap-2 ml-4">
                      <select
                        value={diagnosis.probability}
                        onChange={(e) => handleUpdateProbability(diagnosis.id, e.target.value)}
                        className="text-sm border border-gray-300 rounded-lg px-2 py-1 bg-white"
                      >
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                      <button
                        onClick={() => handleSetWorkingDiagnosis(diagnosis)}
                        className="p-1.5 text-purple-600 hover:text-purple-700 hover:bg-purple-100 rounded-lg transition-colors"
                        title="Set as working diagnosis"
                      >
                        <Target className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleRemoveDiagnosis(diagnosis.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border-2 border-dashed border-purple-300">
            <Microscope className="w-16 h-16 mx-auto mb-4 text-purple-400" />
            <p className="text-gray-600 font-medium mb-4">No differential diagnoses added yet</p>
            <button
              onClick={() => setShowAddDiagnosis(true)}
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add First Diagnosis
            </button>
          </div>
        )}
      </div>
      
      {/* Working Diagnosis */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-blue-600" />
          Working Diagnosis
        </h3>
        
        {data.workingDiagnosis?.diagnosis ? (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-blue-900 text-xl">{data.workingDiagnosis.diagnosis}</h4>
                  {data.workingDiagnosis.icd10 && (
                    <p className="text-blue-700 mt-1 font-medium">ICD-10: {data.workingDiagnosis.icd10}</p>
                  )}
                </div>
                <div className="ml-4">
                  {(() => {
                    const confidenceConfig = getConfidenceConfig(data.workingDiagnosis.confidence);
                    const ConfidenceIcon = confidenceConfig.icon;
                    return (
                      <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${confidenceConfig.color}`}>
                        <ConfidenceIcon className="w-4 h-4 mr-2" />
                        {confidenceConfig.label}
                      </div>
                    );
                  })()}
                </div>
              </div>
              
              <div className="mt-4 flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Confidence Level:</label>
                <div className="flex gap-2">
                  {['confirmed', 'probable', 'possible'].map(level => (
                    <button
                      key={level}
                      onClick={() => handleWorkingDiagnosisUpdate('confidence', level)}
                      className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                        data.workingDiagnosis.confidence === level
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 items-center">
                <BookOpen className="w-4 h-4 mr-1" />
                Clinical Reasoning
              </label>
              <textarea
                value={data.workingDiagnosis.clinicalReasoning || ''}
                onChange={(e) => handleWorkingDiagnosisUpdate('clinicalReasoning', e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Explain your reasoning for this diagnosis based on clinical findings..."
              />
            </div>
          </div>
        ) : (
          <div className="text-center py-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-dashed border-blue-300">
            <Target className="w-12 h-12 mx-auto mb-3 text-blue-400" />
            <p className="text-gray-600 mb-2">No working diagnosis selected</p>
            <p className="text-sm text-gray-500">Select a diagnosis from the differential list or add a new one</p>
          </div>
        )}
      </div>
      
      {/* Risk Assessment */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-red-600" />
            Risk Assessment & Safety Considerations
          </h3>
          <button
            onClick={() => setShowRiskAssessment(!showRiskAssessment)}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            {showRiskAssessment ? 'Hide' : 'Show'} Assessment
          </button>
        </div>
        
        {showRiskAssessment && (
          <div className="space-y-4">
            <div className="bg-red-50 rounded-xl p-4 border border-red-200">
              <p className="text-sm font-medium text-red-800 mb-2">Consider and document:</p>
              <ul className="space-y-1 text-sm text-red-700">
                <li className="flex items-start">
                  <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                  Red flag symptoms requiring immediate action
                </li>
                <li className="flex items-start">
                  <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                  Risk factors for serious conditions
                </li>
                <li className="flex items-start">
                  <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                  Safety-netting advice for the patient
                </li>
              </ul>
            </div>
            
            <textarea
              value={data.riskAssessment || ''}
              onChange={(e) => handleRiskAssessmentUpdate(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              placeholder="Document risk assessment, red flags identified, and safety considerations..."
            />
          </div>
        )}
      </div>
      
      {/* Add Diagnosis Modal */}
      {showAddDiagnosis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold flex items-center">
                  <Microscope className="w-6 h-6 mr-2" />
                  Add Differential Diagnosis
                </h3>
                <button
                  onClick={() => setShowAddDiagnosis(false)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
              <div className="space-y-6">
                {/* Common Diagnoses Suggestions */}
                {getCommonDiagnoses().length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Common diagnoses for "{episode?.chiefComplaint}"
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {getCommonDiagnoses().map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => setNewDiagnosis({
                            ...newDiagnosis,
                            diagnosis: suggestion.diagnosis,
                            icd10: suggestion.icd10
                          })}
                          className="text-left px-4 py-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-colors"
                        >
                          <p className="font-medium text-purple-900">{suggestion.diagnosis}</p>
                          <p className="text-sm text-purple-700">ICD-10: {suggestion.icd10}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Diagnosis Name <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={newDiagnosis.diagnosis}
                        onChange={(e) => setNewDiagnosis({ ...newDiagnosis, diagnosis: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="e.g., Acute Myocardial Infarction"
                      />
                      <Search className="absolute right-3 top-3.5 w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      ICD-10 Code
                    </label>
                    <input
                      type="text"
                      value={newDiagnosis.icd10}
                      onChange={(e) => setNewDiagnosis({ ...newDiagnosis, icd10: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="e.g., I21.9"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Initial Probability Assessment
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'high', label: 'High', color: 'red', description: 'Strong clinical suspicion' },
                      { value: 'medium', label: 'Medium', color: 'yellow', description: 'Moderate likelihood' },
                      { value: 'low', label: 'Low', color: 'green', description: 'Less likely but possible' }
                    ].map(({ value, label, color, description }) => (
                      <button
                        key={value}
                        onClick={() => setNewDiagnosis({ ...newDiagnosis, probability: value })}
                        className={`p-4 rounded-xl border-2 transition-all ${
                          newDiagnosis.probability === value
                            ? `bg-${color}-100 border-${color}-500`
                            : 'bg-white border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <p className={`font-medium ${
                          newDiagnosis.probability === value ? `text-${color}-700` : 'text-gray-700'
                        }`}>{label}</p>
                        <p className="text-xs text-gray-500 mt-1">{description}</p>
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Supporting Evidence
                  </label>
                  <textarea
                    value={newDiagnosis.supportingEvidence}
                    onChange={(e) => setNewDiagnosis({ ...newDiagnosis, supportingEvidence: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    placeholder="List clinical findings that support this diagnosis (comma-separated)..."
                  />
                  <p className="text-xs text-gray-500 mt-1">Separate multiple items with commas</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contradicting Evidence
                  </label>
                  <textarea
                    value={newDiagnosis.contradictingEvidence}
                    onChange={(e) => setNewDiagnosis({ ...newDiagnosis, contradictingEvidence: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    placeholder="List findings that make this diagnosis less likely (comma-separated)..."
                  />
                  <p className="text-xs text-gray-500 mt-1">Separate multiple items with commas</p>
                </div>
              </div>
            </div>
            
            <div className="border-t border-gray-200 p-6 bg-gray-50">
              <div className="flex justify-between items-center">
                <button className="text-purple-600 hover:text-purple-700 flex items-center">
                  <Sparkles className="w-4 h-4 mr-1" />
                  AI Assist
                </button>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowAddDiagnosis(false)}
                    className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddDifferentialDiagnosis}
                    disabled={!newDiagnosis.diagnosis.trim()}
                    className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                  >
                    Add Diagnosis
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* AI Assistant */}
      <AIAssistant
        patient={patient}
        episode={episode}
        encounter={encounter}
        currentSection="assessment"
        onInsightApply={handleAIInsight}
      />
    </div>
  );
};

export default AssessmentSection;