import { useState, useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { ClipboardList, Upload, AlertTriangle, CheckCircle, Clock, FileText, TrendingUp, TrendingDown } from 'lucide-react'
import clsx from 'clsx'

export default function TestResults() {
  const { 
    recommendedTests, 
    selectedTests, 
    testResults, 
    updateTestResult 
  } = usePatientData()
  
  const [currentTestIndex, setCurrentTestIndex] = useState(0)
  const [resultNotes, setResultNotes] = useState({})

  const selectedTestsData = recommendedTests.filter(test => selectedTests.includes(test.id))
  const currentTest = selectedTestsData[currentTestIndex]

  useEffect(() => {
    if (selectedTestsData.length === 0) {
      // No tests selected, show message
    }
  }, [selectedTestsData])

  const handleResultChange = (testId, field, value) => {
    const currentResult = testResults[testId] || {}
    const updatedResult = { ...currentResult, [field]: value }
    updateTestResult(testId, updatedResult)
  }

  const handleFileUpload = (testId, files) => {
    // In a real app, this would upload files to a server
    const fileList = Array.from(files).map(file => ({
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString()
    }))
    
    handleResultChange(testId, 'attachments', fileList)
  }

  const getCompletionStatus = () => {
    const completed = selectedTestsData.filter(test => 
      testResults[test.id]?.status === 'completed'
    ).length
    return { completed, total: selectedTestsData.length }
  }

  const getTestResultStatus = (testId) => {
    const result = testResults[testId]
    if (!result) return 'pending'
    return result.status || 'pending'
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-100'
      case 'in-progress':
        return 'text-yellow-700 bg-yellow-100'
      case 'abnormal':
        return 'text-red-700 bg-red-100'
      default:
        return 'text-gray-700 bg-gray-100'
    }
  }

  const renderTestResultForm = (test) => {
    const result = testResults[test.id] || {}
    
    if (test.category === 'Laboratory') {
      return (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Test Status
              </label>
              <select
                value={result.status || 'pending'}
                onChange={(e) => handleResultChange(test.id, 'status', e.target.value)}
                className="input-field"
              >
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Result Date & Time
              </label>
              <input
                type="datetime-local"
                value={result.resultDateTime || ''}
                onChange={(e) => handleResultChange(test.id, 'resultDateTime', e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          
          {test.id === 'cbc-diff' && (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">CBC Results</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    WBC Count (K/μL)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={result.wbc || ''}
                    onChange={(e) => handleResultChange(test.id, 'wbc', e.target.value)}
                    className="input-field"
                    placeholder="4.5-11.0"
                  />
                  <span className="text-xs text-gray-500">Normal: 4.5-11.0</span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hemoglobin (g/dL)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={result.hemoglobin || ''}
                    onChange={(e) => handleResultChange(test.id, 'hemoglobin', e.target.value)}
                    className="input-field"
                    placeholder="12-16"
                  />
                  <span className="text-xs text-gray-500">Normal: 12-16 (F), 14-18 (M)</span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Platelets (K/μL)
                  </label>
                  <input
                    type="number"
                    value={result.platelets || ''}
                    onChange={(e) => handleResultChange(test.id, 'platelets', e.target.value)}
                    className="input-field"
                    placeholder="150-450"
                  />
                  <span className="text-xs text-gray-500">Normal: 150-450</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Neutrophil %
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={result.neutrophils || ''}
                  onChange={(e) => handleResultChange(test.id, 'neutrophils', e.target.value)}
                  className="input-field"
                  placeholder="50-70"
                />
                <span className="text-xs text-gray-500">Normal: 50-70%</span>
              </div>
            </div>
          )}
          
          {test.id === 'basic-metabolic' && (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Basic Metabolic Panel</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sodium (mEq/L)
                  </label>
                  <input
                    type="number"
                    value={result.sodium || ''}
                    onChange={(e) => handleResultChange(test.id, 'sodium', e.target.value)}
                    className="input-field"
                    placeholder="136-145"
                  />
                  <span className="text-xs text-gray-500">Normal: 136-145</span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Potassium (mEq/L)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={result.potassium || ''}
                    onChange={(e) => handleResultChange(test.id, 'potassium', e.target.value)}
                    className="input-field"
                    placeholder="3.5-5.0"
                  />
                  <span className="text-xs text-gray-500">Normal: 3.5-5.0</span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    BUN (mg/dL)
                  </label>
                  <input
                    type="number"
                    value={result.bun || ''}
                    onChange={(e) => handleResultChange(test.id, 'bun', e.target.value)}
                    className="input-field"
                    placeholder="7-20"
                  />
                  <span className="text-xs text-gray-500">Normal: 7-20</span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Creatinine (mg/dL)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={result.creatinine || ''}
                    onChange={(e) => handleResultChange(test.id, 'creatinine', e.target.value)}
                    className="input-field"
                    placeholder="0.6-1.2"
                  />
                  <span className="text-xs text-gray-500">Normal: 0.6-1.2</span>
                </div>
              </div>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overall Interpretation
            </label>
            <select
              value={result.interpretation || ''}
              onChange={(e) => handleResultChange(test.id, 'interpretation', e.target.value)}
              className="input-field"
            >
              <option value="">Select interpretation</option>
              <option value="normal">Normal</option>
              <option value="abnormal">Abnormal</option>
              <option value="critical">Critical</option>
              <option value="inconclusive">Inconclusive</option>
            </select>
          </div>
        </div>
      )
    }
    
    if (test.category === 'Imaging') {
      return (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Study Status
              </label>
              <select
                value={result.status || 'pending'}
                onChange={(e) => handleResultChange(test.id, 'status', e.target.value)}
                className="input-field"
              >
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Study Date & Time
              </label>
              <input
                type="datetime-local"
                value={result.studyDateTime || ''}
                onChange={(e) => handleResultChange(test.id, 'studyDateTime', e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Radiologist Report
            </label>
            <textarea
              value={result.radiologistReport || ''}
              onChange={(e) => handleResultChange(test.id, 'radiologistReport', e.target.value)}
              className="input-field"
              rows={6}
              placeholder="Enter the radiologist's interpretation and findings..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Key Findings
            </label>
            <textarea
              value={result.keyFindings || ''}
              onChange={(e) => handleResultChange(test.id, 'keyFindings', e.target.value)}
              className="input-field"
              rows={3}
              placeholder="Summarize the most important findings..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overall Impression
            </label>
            <select
              value={result.impression || ''}
              onChange={(e) => handleResultChange(test.id, 'impression', e.target.value)}
              className="input-field"
            >
              <option value="">Select impression</option>
              <option value="normal">Normal</option>
              <option value="abnormal">Abnormal</option>
              <option value="requires-follow-up">Requires Follow-up</option>
              <option value="inconclusive">Inconclusive</option>
            </select>
          </div>
        </div>
      )
    }
    
    // Generic form for other test types
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Status
            </label>
            <select
              value={result.status || 'pending'}
              onChange={(e) => handleResultChange(test.id, 'status', e.target.value)}
              className="input-field"
            >
              <option value="pending">Pending</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Result Date & Time
            </label>
            <input
              type="datetime-local"
              value={result.resultDateTime || ''}
              onChange={(e) => handleResultChange(test.id, 'resultDateTime', e.target.value)}
              className="input-field"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Test Results
          </label>
          <textarea
            value={result.results || ''}
            onChange={(e) => handleResultChange(test.id, 'results', e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Enter test results and values..."
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Interpretation
          </label>
          <select
            value={result.interpretation || ''}
            onChange={(e) => handleResultChange(test.id, 'interpretation', e.target.value)}
            className="input-field"
          >
            <option value="">Select interpretation</option>
            <option value="normal">Normal</option>
            <option value="abnormal">Abnormal</option>
            <option value="critical">Critical</option>
            <option value="inconclusive">Inconclusive</option>
          </select>
        </div>
      </div>
    )
  }

  if (selectedTestsData.length === 0) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Test Results</h2>
          <p className="mt-2 text-gray-600">
            Input results from diagnostic tests
          </p>
        </div>

        <div className="card text-center">
          <ClipboardList className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Tests Selected</h3>
          <p className="text-gray-600 mb-4">
            You need to select tests from the previous step before entering results.
          </p>
          <button className="btn-primary">
            Go Back to Test Selection
          </button>
        </div>
      </div>
    )
  }

  const completionStatus = getCompletionStatus()

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Test Results</h2>
        <p className="mt-2 text-gray-600">
          Input results from the {selectedTestsData.length} selected diagnostic tests
        </p>
      </div>

      {/* Progress Overview */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Results Entry Progress</h3>
            <p className="text-gray-600">
              {completionStatus.completed} of {completionStatus.total} tests completed
            </p>
          </div>
          <div className="text-right">
            <div className="w-32 bg-gray-200 rounded-full h-2 mb-1">
              <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(completionStatus.completed / completionStatus.total) * 100}%` }}
              ></div>
            </div>
            <span className="text-sm text-gray-600">
              {Math.round((completionStatus.completed / completionStatus.total) * 100)}% complete
            </span>
          </div>
        </div>
        
        {/* Test Navigation */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {selectedTestsData.map((test, index) => {
            const status = getTestResultStatus(test.id)
            return (
              <button
                key={test.id}
                onClick={() => setCurrentTestIndex(index)}
                className={clsx(
                  'p-3 rounded-lg text-left transition-colors duration-200',
                  currentTestIndex === index 
                    ? 'bg-primary-100 border-2 border-primary-500' 
                    : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">{test.name}</h4>
                    <p className="text-xs text-gray-600">{test.category}</p>
                  </div>
                  <span className={clsx(
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getStatusColor(status)
                  )}>
                    {status === 'completed' ? <CheckCircle className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Current Test Form */}
      {currentTest && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{currentTest.name}</h3>
              <p className="text-gray-600">{currentTest.category} • {currentTest.estimatedTime}</p>
            </div>
            <span className={clsx(
              'px-3 py-1 rounded-full text-sm font-medium',
              getStatusColor(getTestResultStatus(currentTest.id))
            )}>
              {getTestResultStatus(currentTest.id)}
            </span>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-2">
              <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Test Information</h4>
                <p className="text-blue-800 text-sm mt-1">{currentTest.reasoning}</p>
                <p className="text-blue-700 text-sm mt-2"><strong>Expected findings:</strong> {currentTest.expectedFindings}</p>
              </div>
            </div>
          </div>
          
          {renderTestResultForm(currentTest)}
          
          {/* File Upload Section */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attach Files (Reports, Images, etc.)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600 mb-2">Drop files here or click to upload</p>
              <input
                type="file"
                multiple
                onChange={(e) => handleFileUpload(currentTest.id, e.target.files)}
                className="hidden"
                id={`file-upload-${currentTest.id}`}
              />
              <label
                htmlFor={`file-upload-${currentTest.id}`}
                className="btn-secondary cursor-pointer"
              >
                Choose Files
              </label>
            </div>
            
            {testResults[currentTest.id]?.attachments && (
              <div className="mt-4">
                <h5 className="font-medium text-gray-900 mb-2">Attached Files</h5>
                <div className="space-y-2">
                  {testResults[currentTest.id].attachments.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">{file.name}</span>
                      <span className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Clinical Notes */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clinical Notes & Interpretation
            </label>
            <textarea
              value={resultNotes[currentTest.id] || ''}
              onChange={(e) => setResultNotes(prev => ({ ...prev, [currentTest.id]: e.target.value }))}
              className="input-field"
              rows={3}
              placeholder="Add your clinical interpretation, significance of findings, or additional notes..."
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      {selectedTestsData.length > 1 && (
        <div className="flex justify-between">
          <button
            onClick={() => setCurrentTestIndex(Math.max(0, currentTestIndex - 1))}
            disabled={currentTestIndex === 0}
            className={clsx(
              'btn-secondary',
              currentTestIndex === 0 && 'opacity-50 cursor-not-allowed'
            )}
          >
            Previous Test
          </button>
          <button
            onClick={() => setCurrentTestIndex(Math.min(selectedTestsData.length - 1, currentTestIndex + 1))}
            disabled={currentTestIndex === selectedTestsData.length - 1}
            className={clsx(
              'btn-secondary',
              currentTestIndex === selectedTestsData.length - 1 && 'opacity-50 cursor-not-allowed'
            )}
          >
            Next Test
          </button>
        </div>
      )}
    </div>
  )
}