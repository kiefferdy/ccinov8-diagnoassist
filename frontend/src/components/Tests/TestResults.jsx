import React, { useState, useEffect, useMemo } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  FileText, 
  ChevronRight, 
  ChevronLeft,
  Check,
  Upload,
  Calendar,
  AlertCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Edit3
} from 'lucide-react';
import FileUpload from '../common/FileUpload';

const TestResults = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [testResults, setTestResults] = useState(patientData.testResults || {});
  const [showResultInput, setShowResultInput] = useState({});
  const [resultDocuments, setResultDocuments] = useState({});
  const [editingResult, setEditingResult] = useState(null);
  
  // Get selected tests from previous step
  const selectedTests = useMemo(() => patientData.selectedTests || [], [patientData.selectedTests]);
  
  useEffect(() => {
    // Initialize test results for selected tests
    setTestResults(prev => {
      const initialResults = {};
      selectedTests.forEach(test => {
        if (!prev[test.id]) {
          initialResults[test.id] = {
            testId: test.id,
            testName: test.name,
            status: 'pending',
            value: '',
            unit: '',
            referenceRange: '',
            interpretation: '',
            notes: '',
            documents: [],
            completedAt: null
          };
        }
      });
      
      if (Object.keys(initialResults).length > 0) {
        return { ...prev, ...initialResults };
      }
      return prev;
    });
  }, [selectedTests]);
  
  const handleResultSubmit = (testId) => {
    const result = testResults[testId];
    if (!result.value && (!result.documents || result.documents.length === 0)) {
      alert('Please enter a result value or upload result documents');
      return;
    }
    
    const updatedResult = {
      ...result,
      status: 'completed',
      completedAt: new Date().toISOString(),
      documents: resultDocuments[testId] || []
    };
    
    const updatedResults = {
      ...testResults,
      [testId]: updatedResult
    };
    
    setTestResults(updatedResults);
    updatePatientData('testResults', updatedResults);
    setShowResultInput({ ...showResultInput, [testId]: false });
    setEditingResult(null);
  };
  
  const handleResultChange = (testId, field, value) => {
    setTestResults(prev => ({
      ...prev,
      [testId]: {
        ...prev[testId],
        [field]: value
      }
    }));
  };
  
  const handleDocumentsChange = (testId, files) => {
    setResultDocuments(prev => ({
      ...prev,
      [testId]: files
    }));
  };
  
  const getInterpretationIcon = (interpretation) => {
    switch (interpretation) {
      case 'normal':
        return <Check className="w-5 h-5 text-green-600" />;
      case 'abnormal-high':
        return <TrendingUp className="w-5 h-5 text-red-600" />;
      case 'abnormal-low':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };
  
  const getInterpretationText = (interpretation) => {
    switch (interpretation) {
      case 'normal':
        return 'Normal';
      case 'abnormal-high':
        return 'Abnormal - High';
      case 'abnormal-low':
        return 'Abnormal - Low';
      case 'critical':
        return 'Critical';
      default:
        return 'Pending';
    }
  };
  
  const getInterpretationColor = (interpretation) => {
    switch (interpretation) {
      case 'normal':
        return 'text-green-600 bg-green-50';
      case 'abnormal-high':
      case 'abnormal-low':
        return 'text-orange-600 bg-orange-50';
      case 'critical':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };
  
  const suggestReferenceRange = (testName) => {
    const references = {
      'CBC': {
        'WBC': '4.5-11.0 x10³/µL',
        'RBC': 'M: 4.5-5.9, F: 4.1-5.1 x10⁶/µL',
        'Hemoglobin': 'M: 13.5-17.5, F: 12.0-15.5 g/dL',
        'Hematocrit': 'M: 41-53%, F: 36-46%',
        'Platelets': '150-400 x10³/µL'
      },
      'Basic Metabolic Panel': {
        'Glucose': '70-110 mg/dL (fasting)',
        'BUN': '7-20 mg/dL',
        'Creatinine': '0.6-1.2 mg/dL',
        'Sodium': '136-145 mEq/L',
        'Potassium': '3.5-5.0 mEq/L',
        'Chloride': '98-107 mEq/L',
        'CO2': '22-29 mEq/L'
      },
      'Liver Function': {
        'ALT': '7-56 U/L',
        'AST': '10-40 U/L',
        'Alkaline Phosphatase': '44-147 U/L',
        'Total Bilirubin': '0.1-1.2 mg/dL',
        'Albumin': '3.5-5.0 g/dL'
      }
    };
    
    // Check if test name contains any of the reference test names
    for (const [category, tests] of Object.entries(references)) {
      if (testName.includes(category)) {
        return Object.entries(tests).map(([test, range]) => `${test}: ${range}`).join('\n');
      }
    }
    
    return '';
  };
  
  const handleContinue = () => {
    const completedTests = Object.values(testResults).filter(r => r.status === 'completed').length;
    if (completedTests === 0) {
      alert('Please enter results for at least one test before continuing');
      return;
    }
    setCurrentStep('final-diagnosis');
  };
  
  const handleBack = () => {
    setCurrentStep('recommended-tests');
  };
  
  const completedCount = Object.values(testResults).filter(r => r.status === 'completed').length;
  const totalCount = selectedTests.length;
  const completionPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
  
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Results Review</h2>
        <p className="text-gray-600">Review and document the test results as they become available</p>
      </div>
      
      {/* Progress Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">Test Completion Progress</h3>
          <span className="text-sm text-gray-600">
            {completedCount} of {totalCount} completed
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>
      
      {/* Test Results Cards */}
      <div className="space-y-4 mb-6">
        {selectedTests.map(test => {
          const result = testResults[test.id] || {};
          const isCompleted = result.status === 'completed';
          const isEditing = editingResult === test.id || showResultInput[test.id];
          
          return (
            <div 
              key={test.id} 
              className={`bg-white rounded-xl shadow-sm border-2 p-6 transition-all ${
                isCompleted ? 'border-green-200' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-blue-600 mr-2" />
                    <h4 className="text-lg font-semibold text-gray-900">{test.name}</h4>
                    {isCompleted && (
                      <span className="ml-3 flex items-center text-green-600 text-sm">
                        <Check className="w-4 h-4 mr-1" />
                        Completed
                      </span>
                    )}
                  </div>
                  <div className="mt-1 flex items-center space-x-3 text-sm text-gray-600">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      test.category === 'Blood' ? 'bg-red-100 text-red-700' :
                      test.category === 'Imaging' ? 'bg-blue-100 text-blue-700' :
                      test.category === 'Microbiology' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {test.category}
                    </span>
                    {isCompleted && result.completedAt && (
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {new Date(result.completedAt).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                
                {!isEditing && (
                  <button
                    onClick={() => {
                      setShowResultInput({ ...showResultInput, [test.id]: true });
                      if (isCompleted) setEditingResult(test.id);
                    }}
                    className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    {isCompleted ? 'Edit Result' : 'Enter Result'}
                  </button>
                )}
              </div>
              
              {/* Result Display */}
              {isCompleted && !isEditing && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.value && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Result Value</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {result.value} {result.unit}
                        </p>
                      </div>
                    )}
                    
                    {result.referenceRange && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Reference Range</p>
                        <p className="text-gray-900">{result.referenceRange}</p>
                      </div>
                    )}
                    
                    {result.interpretation && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Interpretation</p>
                        <div className={`inline-flex items-center px-3 py-1 rounded-full ${getInterpretationColor(result.interpretation)}`}>
                          {getInterpretationIcon(result.interpretation)}
                          <span className="ml-1 font-medium">
                            {getInterpretationText(result.interpretation)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {result.notes && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700">Clinical Notes</p>
                      <p className="text-gray-900 mt-1">{result.notes}</p>
                    </div>
                  )}
                  
                  {result.documents && result.documents.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Attached Documents</p>
                      <div className="flex flex-wrap gap-2">
                        {result.documents.map((doc, idx) => (
                          <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            {doc.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Result Input Form */}
              {isEditing && (
                <div className="mt-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Result Value
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={result.value || ''}
                          onChange={(e) => handleResultChange(test.id, 'value', e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., 120"
                        />
                        <input
                          type="text"
                          value={result.unit || ''}
                          onChange={(e) => handleResultChange(test.id, 'unit', e.target.value)}
                          className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Unit"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Reference Range
                      </label>
                      <input
                        type="text"
                        value={result.referenceRange || ''}
                        onChange={(e) => handleResultChange(test.id, 'referenceRange', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., 80-120 mg/dL"
                      />
                      {suggestReferenceRange(test.name) && (
                        <button
                          type="button"
                          onClick={() => handleResultChange(test.id, 'referenceRange', suggestReferenceRange(test.name))}
                          className="mt-1 text-xs text-blue-600 hover:text-blue-700"
                        >
                          Use suggested reference ranges
                        </button>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Interpretation
                    </label>
                    <select
                      value={result.interpretation || ''}
                      onChange={(e) => handleResultChange(test.id, 'interpretation', e.target.value)}
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
                      Clinical Notes
                    </label>
                    <textarea
                      value={result.notes || ''}
                      onChange={(e) => handleResultChange(test.id, 'notes', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Any additional findings, observations, or clinical significance..."
                    />
                  </div>
                  
                  <div>
                    <FileUpload
                      label="Attach Result Reports"
                      description="Upload lab reports, images, or scanned documents"
                      acceptedFormats="image/*,.pdf,.doc,.docx"
                      maxFiles={5}
                      maxSizeMB={10}
                      onFilesChange={(files) => handleDocumentsChange(test.id, files)}
                      existingFiles={resultDocuments[test.id] || result.documents || []}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => {
                        setShowResultInput({ ...showResultInput, [test.id]: false });
                        setEditingResult(null);
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleResultSubmit(test.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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
      
      {/* Info Message */}
      {completedCount === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-yellow-800 font-medium">Enter test results to refine the diagnosis</p>
              <p className="text-yellow-700 text-sm mt-1">
                Test results will help confirm or rule out potential diagnoses. You can upload lab reports or enter values manually.
              </p>
            </div>
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
          Back to Test Selection
        </button>
        
        <button
          onClick={handleContinue}
          disabled={completedCount === 0}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center disabled:bg-gray-300 shadow-sm hover:shadow-md"
        >
          Continue to Final Diagnosis
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default TestResults;