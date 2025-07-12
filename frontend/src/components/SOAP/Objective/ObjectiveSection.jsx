import React, { useState } from 'react';
import { 
  Activity, Stethoscope, FlaskConical, FileText, Mic, Plus, X, 
  Calendar, AlertCircle, Heart, Thermometer, Wind, Droplets,
  TrendingUp, TrendingDown, CheckCircle, Clock, Upload,
  Sparkles, BarChart3, Brain, Zap, FileSearch, ChevronRight,
  Info, AlertTriangle, Paperclip
} from 'lucide-react';
import { generateId } from '../../../utils/storage';
import VoiceTranscription from '../../common/VoiceTranscription';
import AIAssistant from '../../common/AIAssistant';
import FileUploadDropbox from '../../common/FileUploadDropbox';

const ObjectiveSection = ({ data, patient, episode, encounter, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('vitals');
  const [showAddTestModal, setShowAddTestModal] = useState(false);
  const [showVoiceTranscription, setShowVoiceTranscription] = useState(false);
  const [transcribingField, setTranscribingField] = useState('');
  const [newTest, setNewTest] = useState({ test: '', urgency: 'routine', notes: '' });
  const [examTemplateOpen, setExamTemplateOpen] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState(data.attachedFiles || []);
  
  const handleVitalsUpdate = (field, value) => {
    onUpdate({
      vitals: {
        ...data.vitals,
        [field]: value
      }
    });
  };
  
  const handlePhysicalExamUpdate = (field, value) => {
    onUpdate({
      physicalExam: {
        ...data.physicalExam,
        [field]: value
      }
    });
  };
  
  const handleAddTest = () => {
    if (!newTest.test.trim()) return;
    
    const test = {
      id: generateId('T'),
      test: newTest.test,
      urgency: newTest.urgency,
      status: 'ordered',
      orderedAt: new Date().toISOString(),
      notes: newTest.notes
    };
    
    onUpdate({
      diagnosticTests: {
        ...data.diagnosticTests,
        ordered: [...(data.diagnosticTests?.ordered || []), test]
      }
    });
    
    setNewTest({ test: '', urgency: 'routine', notes: '' });
    setShowAddTestModal(false);
  };
  
  const handleTestStatusUpdate = (testId, status) => {
    const updatedTests = data.diagnosticTests.ordered.map(test =>
      test.id === testId ? { ...test, status } : test
    );
    
    onUpdate({
      diagnosticTests: {
        ...data.diagnosticTests,
        ordered: updatedTests
      }
    });
  };
  
  const handleVoiceTranscription = (field) => {
    setTranscribingField(field);
    setShowVoiceTranscription(true);
  };
  
  const handleTranscriptionSave = (text) => {
    if (transcribingField === 'general' || transcribingField === 'additionalFindings') {
      handlePhysicalExamUpdate(transcribingField, text);
    }
    setShowVoiceTranscription(false);
    setTranscribingField('');
  };
  
  const handleFilesAdded = (newFiles) => {
    const updatedFiles = [...attachedFiles, ...newFiles];
    setAttachedFiles(updatedFiles);
    onUpdate({ attachedFiles: updatedFiles });
  };
  
  const handleFileRemove = (fileId) => {
    const updatedFiles = attachedFiles.filter(f => f.id !== fileId);
    setAttachedFiles(updatedFiles);
    onUpdate({ attachedFiles: updatedFiles });
  };
  
  const handleAIInsight = (insight) => {
    if (insight.type === 'template' && insight.section === 'objective') {
      // Apply exam template
      const lines = insight.content.split('\n');
      let updates = {};
      lines.forEach(line => {
        if (line.includes('General:')) {
          updates.general = line.replace('General:', '').trim();
        } else if (line.length > 0) {
          updates.additionalFindings = (updates.additionalFindings || '') + line + '\n';
        }
      });
      
      onUpdate({
        physicalExam: {
          ...data.physicalExam,
          ...updates
        }
      });
    }
  };
  
  // Calculate BMI when height and weight are provided
  const calculateBMI = () => {
    if (data.vitals?.weight && data.vitals?.height) {
      const weight = parseFloat(data.vitals.weight);
      const height = parseFloat(data.vitals.height);
      if (!isNaN(weight) && !isNaN(height) && height > 0) {
        const bmi = (weight / (height * height)) * 703; // Imperial formula
        return bmi.toFixed(1);
      }
    }
    return '';
  };
  
  // Check for abnormal vitals
  const getVitalStatus = (vital, value) => {
    const normalRanges = {
      bloodPressure: { 
        check: (v) => {
          const [systolic, diastolic] = v.split('/').map(n => parseInt(n));
          return systolic >= 90 && systolic <= 120 && diastolic >= 60 && diastolic <= 80;
        }
      },
      heartRate: { min: 60, max: 100 },
      temperature: { min: 97, max: 99.5 },
      respiratoryRate: { min: 12, max: 20 },
      oxygenSaturation: { min: 95, max: 100 }
    };
    
    const range = normalRanges[vital];
    if (!range || !value) return 'normal';
    
    if (range.check) {
      return range.check(value) ? 'normal' : 'abnormal';
    }
    
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return 'normal';
    
    if (numValue < range.min || numValue > range.max) return 'abnormal';
    return 'normal';
  };
  
  const tabs = [
    { id: 'vitals', label: 'Vitals & Exam', icon: Stethoscope, color: 'blue' },
    { id: 'tests', label: 'Diagnostic Tests', icon: FlaskConical, color: 'purple' },
    { id: 'results', label: 'Test Results', icon: FileText, color: 'green' }
  ];
  
  // Calculate tab completion
  const calculateTabCompletion = (tabId) => {
    switch (tabId) {
      case 'vitals': {
        const vitalFields = Object.values(data.vitals || {}).filter(v => v);
        const examFields = [data.physicalExam?.general, data.physicalExam?.additionalFindings].filter(v => v);
        return vitalFields.length >= 5 && examFields.length >= 1 ? 'complete' : 
               vitalFields.length > 0 || examFields.length > 0 ? 'partial' : 'empty';
      }
      case 'tests':
        return (data.diagnosticTests?.ordered?.length || 0) > 0 ? 'partial' : 'empty';
      case 'results':
        return (data.diagnosticTests?.results?.length || 0) > 0 ? 'partial' : 'empty';
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
  
  const commonTests = {
    'Laboratory': [
      'Complete Blood Count (CBC)',
      'Basic Metabolic Panel (BMP)',
      'Comprehensive Metabolic Panel (CMP)',
      'Lipid Panel',
      'Thyroid Function Tests',
      'Urinalysis',
      'HbA1c',
      'Liver Function Tests',
      'Cardiac Enzymes',
      'D-dimer',
      'Blood Cultures'
    ],
    'Imaging': [
      'Chest X-ray',
      'CT Head',
      'CT Chest',
      'CT Abdomen/Pelvis',
      'MRI Brain',
      'Ultrasound Abdomen',
      'Echocardiogram',
      'X-ray (specify location)'
    ],
    'Cardiac': [
      'ECG/EKG',
      'Troponin',
      'BNP/NT-proBNP',
      'Stress Test',
      'Holter Monitor'
    ],
    'Other': [
      'Pulse Oximetry',
      'Peak Flow',
      'Rapid Strep Test',
      'Rapid Flu Test',
      'COVID-19 Test',
      'Pregnancy Test'
    ]
  };
  
  return (
    <div className="space-y-6">
      {/* Quick Stats Banner */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2 flex items-center">
              <Activity className="w-6 h-6 mr-2" />
              Objective Findings
            </h3>
            <p className="text-indigo-100">Document physical examination and diagnostic test results</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold">{Object.values(data.vitals || {}).filter(v => v).length}</div>
              <div className="text-sm text-indigo-200">Vitals Recorded</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{data.diagnosticTests?.ordered?.length || 0}</div>
              <div className="text-sm text-indigo-200">Tests Ordered</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{data.diagnosticTests?.results?.length || 0}</div>
              <div className="text-sm text-indigo-200">Results Available</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
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
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* Vitals & Exam Tab */}
          {activeTab === 'vitals' && (
            <div className="space-y-8">
              {/* Vital Signs */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Heart className="w-5 h-5 mr-2 text-red-500" />
                  Vital Signs
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { field: 'bloodPressure', label: 'Blood Pressure', icon: Heart, placeholder: '120/80 mmHg', color: 'red' },
                    { field: 'heartRate', label: 'Heart Rate', icon: Activity, placeholder: '72 bpm', color: 'pink' },
                    { field: 'temperature', label: 'Temperature', icon: Thermometer, placeholder: '98.6°F', color: 'orange' },
                    { field: 'respiratoryRate', label: 'Respiratory Rate', icon: Wind, placeholder: '16 breaths/min', color: 'blue' },
                    { field: 'oxygenSaturation', label: 'O2 Saturation', icon: Droplets, placeholder: '98%', color: 'cyan' },
                    { field: 'weight', label: 'Weight', icon: BarChart3, placeholder: '150 lbs', color: 'purple' },
                    { field: 'height', label: 'Height', icon: TrendingUp, placeholder: '68 inches', color: 'indigo' },
                    { field: 'bmi', label: 'BMI', icon: BarChart3, placeholder: 'Auto-calculated', color: 'green', readonly: true }
                  ].map((item) => {
                    const { field, label, placeholder, color, readonly } = item;
                    const status = getVitalStatus(field, data.vitals?.[field]);
                    const isAbnormal = status === 'abnormal';
                    
                    // Color mapping for icon colors
                    const colorClasses = {
                      orange: 'text-orange-600',
                      red: 'text-red-600',
                      green: 'text-green-600',
                      blue: 'text-blue-600',
                      cyan: 'text-cyan-600',
                      purple: 'text-purple-600',
                      indigo: 'text-indigo-600'
                    };
                    
                    return (
                      <div key={field} className={`bg-gradient-to-br from-${color}-50 to-${color}-100 rounded-xl p-4 border ${isAbnormal ? 'border-red-300' : 'border-gray-200'}`}>
                        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                          <item.icon className={`w-4 h-4 mr-2 ${colorClasses[color] || 'text-gray-600'}`} />
                          {label}
                          {isAbnormal && <AlertTriangle className="w-4 h-4 ml-auto text-red-600" />}
                        </label>
                        <input
                          type="text"
                          value={field === 'bmi' ? calculateBMI() : (data.vitals?.[field] || '')}
                          onChange={(e) => !readonly && handleVitalsUpdate(field, e.target.value)}
                          className={`w-full px-3 py-2 border ${isAbnormal ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'} rounded-lg focus:ring-2 focus:ring-${color}-500 focus:border-transparent`}
                          placeholder={placeholder}
                          readOnly={readonly}
                        />
                      </div>
                    );
                  })}
                </div>
                
                {/* Abnormal Vitals Alert */}
                {Object.entries(data.vitals || {}).some(([key, value]) => getVitalStatus(key, value) === 'abnormal') && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
                    <div className="flex items-start">
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-red-800">Abnormal Vital Signs Detected</p>
                        <p className="text-sm text-red-700 mt-1">Please review and consider appropriate interventions</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Physical Examination */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Stethoscope className="w-5 h-5 mr-2 text-blue-600" />
                  Physical Examination
                </h4>
                
                {/* Quick Exam Templates */}
                <div className="mb-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-blue-900">Quick Exam Templates</p>
                    <button
                      onClick={() => setExamTemplateOpen(!examTemplateOpen)}
                      className="text-sm text-blue-600 hover:text-blue-700"
                    >
                      {examTemplateOpen ? 'Hide' : 'Show'} Templates
                    </button>
                  </div>
                  {examTemplateOpen && (
                    <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2">
                      {['Normal Exam', 'Cardiac Focused', 'Respiratory Focused', 'Abdominal Focused', 'Neuro Focused', 'MSK Focused'].map(template => (
                        <button
                          key={template}
                          onClick={() => {
                            const templates = {
                              'Normal Exam': {
                                general: 'Alert and oriented x3, in no acute distress',
                                additionalFindings: 'HEENT: Normocephalic, atraumatic. Pupils equal, round, reactive to light.\nCardiac: Regular rate and rhythm, no murmurs.\nRespiratory: Clear to auscultation bilaterally.\nAbdomen: Soft, non-tender, non-distended.\nExtremities: No edema, normal pulses.'
                              },
                              'Cardiac Focused': {
                                general: 'Alert, appears comfortable at rest',
                                additionalFindings: 'Cardiac: Regular rate and rhythm. No murmurs, rubs, or gallops. No JVD. No peripheral edema.\nRespiratory: Clear to auscultation bilaterally, no crackles or wheezes.\nExtremities: Pulses 2+ and equal bilaterally. No cyanosis or clubbing.'
                              }
                              // Add more templates as needed
                            };
                            const examData = templates[template] || templates['Normal Exam'];
                            onUpdate({
                              physicalExam: {
                                ...data.physicalExam,
                                ...examData
                              }
                            });
                          }}
                          className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                        >
                          {template}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">
                        General Appearance
                      </label>
                      <button
                        onClick={() => handleVoiceTranscription('general')}
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                      >
                        <Mic className="w-4 h-4 mr-1" />
                        Voice Input
                      </button>
                    </div>
                    <textarea
                      value={data.physicalExam?.general || ''}
                      onChange={(e) => handlePhysicalExamUpdate('general', e.target.value)}
                      rows={2}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Alert and oriented, appears well..."
                    />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">
                        System-Specific Findings
                      </label>
                      <button
                        onClick={() => handleVoiceTranscription('additionalFindings')}
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                      >
                        <Mic className="w-4 h-4 mr-1" />
                        Voice Input
                      </button>
                    </div>
                    <textarea
                      value={data.physicalExam?.additionalFindings || ''}
                      onChange={(e) => handlePhysicalExamUpdate('additionalFindings', e.target.value)}
                      rows={6}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Document examination findings relevant to the chief complaint..."
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Diagnostic Tests Tab */}
          {activeTab === 'tests' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <FlaskConical className="w-5 h-5 mr-2 text-purple-600" />
                    Diagnostic Tests
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Order and track diagnostic tests</p>
                </div>
                <button
                  onClick={() => setShowAddTestModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Order Test
                </button>
              </div>
              
              {data.diagnosticTests?.ordered?.length > 0 ? (
                <div className="space-y-3">
                  {data.diagnosticTests.ordered.map((test) => (
                    <div key={test.id} className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-5 border border-purple-200 hover:border-purple-300 transition-all hover:shadow-md">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-900 text-lg">{test.test}</h5>
                          <div className="flex items-center gap-4 mt-2">
                            <span className={`
                              inline-flex items-center px-3 py-1 rounded-full text-xs font-medium
                              ${test.urgency === 'stat' ? 'bg-red-100 text-red-700 border border-red-200' : 
                                test.urgency === 'urgent' ? 'bg-orange-100 text-orange-700 border border-orange-200' : 
                                'bg-gray-100 text-gray-700 border border-gray-200'}
                            `}>
                              <Zap className="w-3 h-3 mr-1" />
                              {test.urgency.toUpperCase()}
                            </span>
                            <span className="flex items-center text-sm text-gray-600">
                              <Clock className="w-3 h-3 mr-1" />
                              {new Date(test.orderedAt).toLocaleString()}
                            </span>
                          </div>
                          {test.notes && (
                            <div className="mt-3 p-3 bg-white rounded-lg border border-purple-100">
                              <p className="text-sm text-gray-700">
                                <span className="font-medium">Notes:</span> {test.notes}
                              </p>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <select
                            value={test.status}
                            onChange={(e) => handleTestStatusUpdate(test.id, e.target.value)}
                            className={`text-sm border rounded-lg px-3 py-1.5 font-medium transition-colors ${
                              test.status === 'resulted' ? 'border-green-300 bg-green-50 text-green-700' :
                              test.status === 'pending' ? 'border-yellow-300 bg-yellow-50 text-yellow-700' :
                              'border-gray-300 bg-gray-50 text-gray-700'
                            }`}
                          >
                            <option value="ordered">Ordered</option>
                            <option value="pending">Pending</option>
                            <option value="resulted">Resulted</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl border-2 border-dashed border-purple-300">
                  <FlaskConical className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                  <p className="text-gray-600 font-medium mb-4">No tests ordered yet</p>
                  <button
                    onClick={() => setShowAddTestModal(true)}
                    className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Order First Test
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Test Results Tab */}
          {activeTab === 'results' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <FileSearch className="w-5 h-5 mr-2 text-green-600" />
                    Test Results
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Review and interpret diagnostic test results</p>
                </div>
                <button className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  <Upload className="w-4 h-4 mr-2" />
                  Import Results
                </button>
              </div>
              
              {data.diagnosticTests?.results?.length > 0 ? (
                <div className="space-y-4">
                  {data.diagnosticTests.results.map((result) => (
                    <div key={result.id} className={`bg-white rounded-xl border-2 ${result.abnormal ? 'border-red-300' : 'border-green-300'} shadow-md hover:shadow-lg transition-all`}>
                      <div className="p-5">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h5 className="font-semibold text-gray-900 text-lg flex items-center">
                              {result.test}
                              {result.abnormal && (
                                <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                  <AlertTriangle className="w-3 h-3 mr-1" />
                                  Abnormal
                                </span>
                              )}
                            </h5>
                            <span className="text-sm text-gray-500">
                              {new Date(result.resultedAt).toLocaleString()}
                            </span>
                          </div>
                          {!result.abnormal && (
                            <CheckCircle className="w-6 h-6 text-green-500" />
                          )}
                        </div>
                        
                        <div className="bg-gray-50 rounded-lg p-4 mb-3">
                          <p className="text-sm font-medium text-gray-700 mb-1">Result:</p>
                          <p className="text-gray-800 whitespace-pre-wrap">{result.result}</p>
                        </div>
                        
                        {result.interpretation && (
                          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                            <p className="text-sm font-medium text-blue-900 mb-1 flex items-center">
                              <Brain className="w-4 h-4 mr-1" />
                              Clinical Interpretation:
                            </p>
                            <p className="text-sm text-blue-800">{result.interpretation}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border-2 border-dashed border-green-300">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-green-400" />
                  <p className="text-gray-600 font-medium mb-2">No test results available yet</p>
                  {data.diagnosticTests?.ordered?.some(t => t.status !== 'resulted') && (
                    <p className="text-sm text-gray-500">
                      {data.diagnosticTests.ordered.filter(t => t.status !== 'resulted').length} test(s) pending results
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Add Test Modal */}
      {showAddTestModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold flex items-center">
                  <FlaskConical className="w-6 h-6 mr-2" />
                  Order Diagnostic Test
                </h3>
                <button
                  onClick={() => setShowAddTestModal(false)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
              <div className="space-y-6">
                {/* Quick Select Common Tests */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Quick Select Common Tests
                  </label>
                  <div className="space-y-3">
                    {Object.entries(commonTests).map(([category, tests]) => (
                      <div key={category} className="bg-gray-50 rounded-xl p-4">
                        <p className="text-sm font-medium text-gray-900 mb-2">{category}</p>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                          {tests.map(test => (
                            <button
                              key={test}
                              onClick={() => setNewTest({ ...newTest, test })}
                              className="text-left px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-purple-50 hover:border-purple-300 transition-colors text-sm"
                            >
                              {test}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Custom Test Entry */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Test Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={newTest.test}
                    onChange={(e) => setNewTest({ ...newTest, test: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Enter test name or select from above..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Urgency Level
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'routine', label: 'Routine', color: 'gray' },
                      { value: 'urgent', label: 'Urgent', color: 'orange' },
                      { value: 'stat', label: 'STAT', color: 'red' }
                    ].map(({ value, label, color }) => (
                      <button
                        key={value}
                        onClick={() => setNewTest({ ...newTest, urgency: value })}
                        className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                          newTest.urgency === value
                            ? `bg-${color}-100 border-${color}-500 text-${color}-700`
                            : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Clinical Notes
                  </label>
                  <textarea
                    value={newTest.notes}
                    onChange={(e) => setNewTest({ ...newTest, notes: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    placeholder="Any special instructions or clinical context..."
                  />
                </div>
              </div>
            </div>
            
            <div className="border-t border-gray-200 p-6 bg-gray-50">
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowAddTestModal(false)}
                  className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddTest}
                  disabled={!newTest.test.trim()}
                  className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  Order Test
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Voice Transcription Modal */}
      {showVoiceTranscription && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">Voice Input - Physical Exam</h3>
                <button
                  onClick={() => setShowVoiceTranscription(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <VoiceTranscription
                onSave={handleTranscriptionSave}
                sectionName={transcribingField === 'general' ? 'General Appearance' : 'Physical Exam Findings'}
                placeholder="Start speaking to record examination findings..."
              />
            </div>
          </div>
        </div>
      )}
      
      {/* File Upload Section */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Paperclip className="w-5 h-5 mr-2 text-gray-600" />
          Test Results & Images
          {attachedFiles.length > 0 && (
            <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
              {attachedFiles.length} file{attachedFiles.length !== 1 ? 's' : ''}
            </span>
          )}
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Upload lab results, imaging studies, ECGs, or other diagnostic test results.
        </p>
        <FileUploadDropbox
          onFilesAdded={handleFilesAdded}
          existingFiles={attachedFiles}
          onFileRemove={handleFileRemove}
          acceptedTypes="image/*,.pdf,.doc,.docx,.txt,.dicom"
          maxFileSize={50 * 1024 * 1024} // 50MB for medical images
          maxFiles={20}
        />
      </div>
      
      {/* AI Assistant */}
      <AIAssistant
        patient={patient}
        episode={episode}
        encounter={encounter}
        currentSection="objective"
        onInsightApply={handleAIInsight}
      />
    </div>
  );
};

export default ObjectiveSection;