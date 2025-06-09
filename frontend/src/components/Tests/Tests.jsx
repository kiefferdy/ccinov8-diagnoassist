import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  TestTube, 
  ChevronRight, 
  ChevronLeft,
  Plus,
  Check,
  X,
  FileText,
  Upload,
  Calendar,
  AlertCircle
} from 'lucide-react';

const Tests = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [recommendedTests, setRecommendedTests] = useState([]);
  const [orderedTests, setOrderedTests] = useState([]);
  const [testResults, setTestResults] = useState({});
  const [customTest, setCustomTest] = useState('');
  const [showResultInput, setShowResultInput] = useState({});
  
  useEffect(() => {
    // Extract unique tests from all diagnoses
    const allTests = new Set();
    patientData.differentialDiagnoses.forEach(diagnosis => {
      diagnosis.recommendedTests?.forEach(test => allTests.add(test));
    });
    
    const testsArray = Array.from(allTests).map((test, index) => ({
      id: index + 1,
      name: test,
      category: categorizeTest(test),
      priority: getPriority(test),
      status: 'pending'
    }));
    
    setRecommendedTests(testsArray);
    updatePatientData('recommendedTests', testsArray);
  }, []);
  
  const categorizeTest = (testName) => {
    const categories = {
      'Blood': ['CBC', 'Blood Culture', 'Complete Blood Count', 'Blood Gas', 'Electrolytes'],
      'Imaging': ['X-ray', 'CT', 'MRI', 'Ultrasound', 'Chest X-ray'],
      'Microbiology': ['Culture', 'Sputum', 'Urine Culture'],
      'Chemistry': ['Glucose', 'Creatinine', 'Liver Function'],
      'Other': []
    };
    
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => testName.toLowerCase().includes(keyword.toLowerCase()))) {
        return category;
      }
    }
    return 'Other';
  };
  
  const getPriority = (testName) => {
    // Simple priority assignment based on test type
    if (testName.toLowerCase().includes('x-ray') || testName.toLowerCase().includes('blood count')) {
      return 'high';
    }
    return 'medium';
  };
  
  const handleOrderTest = (test) => {
    if (!orderedTests.find(t => t.id === test.id)) {
      const updatedTest = { ...test, status: 'ordered', orderedAt: new Date().toISOString() };
      setOrderedTests([...orderedTests, updatedTest]);
      updatePatientData('orderedTests', [...orderedTests, updatedTest]);
    }
  };
  
  const handleRemoveOrder = (testId) => {
    const filtered = orderedTests.filter(t => t.id !== testId);
    setOrderedTests(filtered);
    updatePatientData('orderedTests', filtered);
  };
  
  const handleAddCustomTest = () => {
    if (customTest.trim()) {
      const newTest = {
        id: recommendedTests.length + 1,
        name: customTest,
        category: 'Other',
        priority: 'medium',
        status: 'pending',
        isCustom: true
      };
      setRecommendedTests([...recommendedTests, newTest]);
      setCustomTest('');
    }
  };
  
  const handleResultSubmit = (test, resultData) => {
    const result = {
      testId: test.id,
      testName: test.name,
      ...resultData,
      completedAt: new Date().toISOString()
    };
    
    const updatedResults = [...(patientData.testResults || []), result];
    updatePatientData('testResults', updatedResults);
    
    // Update test status
    const updatedOrdered = orderedTests.map(t => 
      t.id === test.id ? { ...t, status: 'completed' } : t
    );
    setOrderedTests(updatedOrdered);
    updatePatientData('orderedTests', updatedOrdered);
    
    // Hide result input
    setShowResultInput({ ...showResultInput, [test.id]: false });
  };
  
  const handleContinue = () => {
    setCurrentStep('final-diagnosis');
  };
  
  const handleBack = () => {
    setCurrentStep('diagnostic-analysis');
  };
  
  const isTestCompleted = (testId) => {
    return patientData.testResults?.some(r => r.testId === testId);
  };
  
  const getTestResult = (testId) => {
    return patientData.testResults?.find(r => r.testId === testId);
  };
  
  const canProceed = patientData.testResults && patientData.testResults.length > 0;
  
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Laboratory Tests & Results</h2>
        <p className="text-gray-600">Order recommended tests and input results to refine the diagnosis</p>
      </div>
      
      {/* Recommended Tests */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <TestTube className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Recommended Tests</h3>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={customTest}
              onChange={(e) => setCustomTest(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTest())}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Add custom test..."
            />
            <button
              onClick={handleAddCustomTest}
              className="p-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendedTests.map(test => (
            <div
              key={test.id}
              className={`p-4 border rounded-lg ${
                orderedTests.find(t => t.id === test.id)
                  ? 'border-blue-300 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-1">
                    <span className="font-medium text-gray-900">{test.name}</span>
                    {test.isCustom && (
                      <span className="ml-2 text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">Custom</span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      test.category === 'Blood' ? 'bg-red-100 text-red-700' :
                      test.category === 'Imaging' ? 'bg-blue-100 text-blue-700' :
                      test.category === 'Microbiology' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {test.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      test.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {test.priority} priority
                    </span>
                  </div>
                </div>
                
                {!orderedTests.find(t => t.id === test.id) ? (
                  <button
                    onClick={() => handleOrderTest(test)}
                    className="ml-2 px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Order
                  </button>
                ) : (
                  <button
                    onClick={() => handleRemoveOrder(test.id)}
                    className="ml-2 p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Ordered Tests & Results */}
      {orderedTests.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center mb-6">
            <FileText className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Ordered Tests & Results</h3>
          </div>
          
          <div className="space-y-4">
            {orderedTests.map(test => {
              const isCompleted = isTestCompleted(test.id);
              const result = getTestResult(test.id);
              
              return (
                <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <span className="font-medium text-gray-900">{test.name}</span>
                      {isCompleted && (
                        <span className="ml-2 flex items-center text-green-600">
                          <Check className="w-4 h-4 mr-1" />
                          Completed
                        </span>
                      )}
                    </div>
                    {!isCompleted && (
                      <button
                        onClick={() => setShowResultInput({ ...showResultInput, [test.id]: !showResultInput[test.id] })}
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        {showResultInput[test.id] ? 'Cancel' : 'Enter Results'}
                      </button>
                    )}
                  </div>
                  
                  {/* Result Display */}
                  {isCompleted && result && (
                    <div className="mt-2 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Result:</span> {result.value} {result.unit}
                      </p>
                      {result.interpretation && (
                        <p className="text-sm text-gray-700 mt-1">
                          <span className="font-medium">Interpretation:</span> {result.interpretation}
                        </p>
                      )}
                      {result.notes && (
                        <p className="text-sm text-gray-700 mt-1">
                          <span className="font-medium">Notes:</span> {result.notes}
                        </p>
                      )}
                    </div>
                  )}
                  
                  {/* Result Input Form */}
                  {showResultInput[test.id] && !isCompleted && (
                    <div className="mt-4 space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Result Value *
                          </label>
                          <input
                            type="text"
                            id={`result-value-${test.id}`}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="e.g., 120"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Unit
                          </label>
                          <input
                            type="text"
                            id={`result-unit-${test.id}`}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="e.g., mg/dL"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Interpretation
                        </label>
                        <select
                          id={`result-interpretation-${test.id}`}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Select interpretation</option>
                          <option value="normal">Normal</option>
                          <option value="abnormal-high">Abnormal - High</option>
                          <option value="abnormal-low">Abnormal - Low</option>
                          <option value="critical">Critical</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Additional Notes
                        </label>
                        <textarea
                          id={`result-notes-${test.id}`}
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Any additional findings or notes..."
                        />
                      </div>
                      
                      <div className="flex justify-end">
                        <button
                          onClick={() => {
                            const value = document.getElementById(`result-value-${test.id}`).value;
                            const unit = document.getElementById(`result-unit-${test.id}`).value;
                            const interpretation = document.getElementById(`result-interpretation-${test.id}`).value;
                            const notes = document.getElementById(`result-notes-${test.id}`).value;
                            
                            if (value) {
                              handleResultSubmit(test, { value, unit, interpretation, notes });
                            }
                          }}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Save Result
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Info Message */}
      {orderedTests.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-yellow-800">
              Please order at least one test to proceed. Test results will help refine the diagnostic analysis.
            </p>
          </div>
        </div>
      )}
      
      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          disabled={!canProceed}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center disabled:bg-gray-300"
        >
          Continue to Final Diagnosis
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default Tests;
