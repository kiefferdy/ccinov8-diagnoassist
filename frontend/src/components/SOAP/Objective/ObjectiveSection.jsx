import React, { useState } from 'react';
import { Activity, Stethoscope, FlaskConical, FileText, Mic, Plus, X, Calendar, AlertCircle } from 'lucide-react';
import { generateId } from '../../../utils/storage';

const ObjectiveSection = ({ data, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('vitals');
  const [showAddTestModal, setShowAddTestModal] = useState(false);
  const [newTest, setNewTest] = useState({ test: '', urgency: 'routine', notes: '' });
  
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
  
  const tabs = [
    { id: 'vitals', label: 'Vitals & Exam', icon: Stethoscope },
    { id: 'tests', label: 'Diagnostic Tests', icon: FlaskConical },
    { id: 'results', label: 'Test Results', icon: FileText }
  ];
  
  return (
    <div className="space-y-6">
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
          {/* Vitals & Exam Tab */}
          {activeTab === 'vitals' && (
            <div className="space-y-6">
              {/* Vital Signs */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-4">Vital Signs</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Blood Pressure
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.bloodPressure || ''}
                      onChange={(e) => handleVitalsUpdate('bloodPressure', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="120/80"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Heart Rate
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.heartRate || ''}
                      onChange={(e) => handleVitalsUpdate('heartRate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="72 bpm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Temperature
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.temperature || ''}
                      onChange={(e) => handleVitalsUpdate('temperature', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="98.6°F"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Respiratory Rate
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.respiratoryRate || ''}
                      onChange={(e) => handleVitalsUpdate('respiratoryRate', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="16 breaths/min"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      O2 Saturation
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.oxygenSaturation || ''}
                      onChange={(e) => handleVitalsUpdate('oxygenSaturation', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="98%"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weight
                    </label>
                    <input
                      type="text"
                      value={data.vitals?.weight || ''}
                      onChange={(e) => handleVitalsUpdate('weight', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="150 lbs"
                    />
                  </div>
                </div>
              </div>
              
              {/* Physical Examination */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-4">Physical Examination</h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      General Appearance
                    </label>
                    <textarea
                      value={data.physicalExam?.general || ''}
                      onChange={(e) => handlePhysicalExamUpdate('general', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Alert and oriented, appears well..."
                    />
                  </div>
                  
                  {/* System-specific exams based on chief complaint */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      System-Specific Findings
                    </label>
                    <textarea
                      value={data.physicalExam?.additionalFindings || ''}
                      onChange={(e) => handlePhysicalExamUpdate('additionalFindings', e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Ordered Tests</h4>
                <button
                  onClick={() => setShowAddTestModal(true)}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Order Test
                </button>
              </div>
              
              {data.diagnosticTests?.ordered?.length > 0 ? (
                <div className="space-y-3">
                  {data.diagnosticTests.ordered.map((test) => (
                    <div key={test.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900">{test.test}</h5>
                          <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                            <span className={`
                              inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                              ${test.urgency === 'stat' ? 'bg-red-100 text-red-700' : 
                                test.urgency === 'urgent' ? 'bg-orange-100 text-orange-700' : 
                                'bg-gray-100 text-gray-700'}
                            `}>
                              {test.urgency.toUpperCase()}
                            </span>
                            <span className="flex items-center">
                              <Calendar className="w-3 h-3 mr-1" />
                              {new Date(test.orderedAt).toLocaleString()}
                            </span>
                          </div>
                          {test.notes && (
                            <p className="text-sm text-gray-600 mt-2">{test.notes}</p>
                          )}
                        </div>
                        <select
                          value={test.status}
                          onChange={(e) => handleTestStatusUpdate(test.id, e.target.value)}
                          className="ml-4 text-sm border border-gray-300 rounded px-2 py-1"
                        >
                          <option value="ordered">Ordered</option>
                          <option value="pending">Pending</option>
                          <option value="resulted">Resulted</option>
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FlaskConical className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No tests ordered yet</p>
                </div>
              )}
            </div>
          )}
          
          {/* Test Results Tab */}
          {activeTab === 'results' && (
            <div className="space-y-4">
              <h4 className="text-md font-medium text-gray-900 mb-4">Test Results</h4>
              
              {data.diagnosticTests?.results?.length > 0 ? (
                <div className="space-y-3">
                  {data.diagnosticTests.results.map((result) => (
                    <div key={result.id} className="bg-white rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900">{result.test}</h5>
                          <div className="mt-2">
                            <p className="text-sm text-gray-700">{result.result}</p>
                            {result.abnormal && (
                              <div className="flex items-center mt-2 text-amber-600">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                <span className="text-sm font-medium">Abnormal Result</span>
                              </div>
                            )}
                            {result.interpretation && (
                              <div className="mt-2 p-3 bg-gray-50 rounded">
                                <p className="text-sm text-gray-700">
                                  <span className="font-medium">Interpretation:</span> {result.interpretation}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(result.resultedAt).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No test results available</p>
                  {data.diagnosticTests?.ordered?.some(t => t.status !== 'resulted') && (
                    <p className="text-sm mt-2">Some tests are still pending results</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Add Test Modal */}
      {showAddTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Order Diagnostic Test</h3>
              <button
                onClick={() => setShowAddTestModal(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Test Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newTest.test}
                  onChange={(e) => setNewTest({ ...newTest, test: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., CBC, Chest X-ray, ECG..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Urgency
                </label>
                <select
                  value={newTest.urgency}
                  onChange={(e) => setNewTest({ ...newTest, urgency: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="routine">Routine</option>
                  <option value="urgent">Urgent</option>
                  <option value="stat">STAT</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes (Optional)
                </label>
                <textarea
                  value={newTest.notes}
                  onChange={(e) => setNewTest({ ...newTest, notes: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Any special instructions..."
                />
              </div>
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowAddTestModal(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddTest}
                disabled={!newTest.test.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Order Test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ObjectiveSection;