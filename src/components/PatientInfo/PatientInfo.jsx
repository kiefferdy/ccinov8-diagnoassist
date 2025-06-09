import { useState, useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { showSuccess, showInfo } from '../Layout/NotificationSystem'
import { debounce } from '../../utils/helpers'
import { Plus, Trash2, MessageSquare, Clock, User, Save } from 'lucide-react'
import { v4 as uuidv4 } from 'uuid'

export default function PatientInfo() {
  const {
    patient,
    chiefComplaint,
    presentIllness,
    medicalHistory,
    dynamicQuestions,
    dynamicAnswers,
    additionalObservations,
    updatePatient,
    setChiefComplaint,
    setPresentIllness,
    addMedicalHistory,
    addDynamicQuestion,
    updateDynamicAnswer,
    setAdditionalObservations
  } = usePatientData()

  const [newHistoryItem, setNewHistoryItem] = useState('')
  const [showAddQuestion, setShowAddQuestion] = useState(false)
  const [newQuestion, setNewQuestion] = useState('')
  const [lastSaved, setLastSaved] = useState(new Date())

  // Auto-save functionality
  const autoSave = debounce(() => {
    setLastSaved(new Date())
    showInfo('Patient information auto-saved')
  }, 2000)

  useEffect(() => {
    if (!patient.id) {
      updatePatient({ id: uuidv4() })
    }
  }, [])

  const handlePatientInfoChange = (field, value) => {
    updatePatient({ [field]: value })
    autoSave()
  }

  const calculateBMI = (height, weight) => {
    if (height && weight) {
      const heightInM = height / 100
      const bmi = weight / (heightInM * heightInM)
      return bmi.toFixed(1)
    }
    return ''
  }

  const addHistoryItem = () => {
    if (newHistoryItem.trim()) {
      addMedicalHistory({
        id: uuidv4(),
        condition: newHistoryItem.trim(),
        dateAdded: new Date().toISOString()
      })
      setNewHistoryItem('')
    }
  }

  const addDynamicQuestionHandler = () => {
    if (newQuestion.trim()) {
      addDynamicQuestion({
        id: uuidv4(),
        question: newQuestion.trim(),
        type: 'text',
        required: false
      })
      setNewQuestion('')
      setShowAddQuestion(false)
    }
  }

  const generateFollowUpQuestions = () => {
    const followUpQuestions = []
    
    if (chiefComplaint.toLowerCase().includes('pain')) {
      followUpQuestions.push({
        id: uuidv4(),
        question: 'On a scale of 1-10, how would you rate your pain?',
        type: 'number',
        required: true
      })
      followUpQuestions.push({
        id: uuidv4(),
        question: 'When did the pain start?',
        type: 'text',
        required: true
      })
      followUpQuestions.push({
        id: uuidv4(),
        question: 'What makes the pain better or worse?',
        type: 'text',
        required: false
      })
    }

    if (chiefComplaint.toLowerCase().includes('fever')) {
      followUpQuestions.push({
        id: uuidv4(),
        question: 'What is your highest recorded temperature?',
        type: 'text',
        required: true
      })
      followUpQuestions.push({
        id: uuidv4(),
        question: 'How long have you had the fever?',
        type: 'text',
        required: true
      })
    }

    if (chiefComplaint.toLowerCase().includes('cough')) {
      followUpQuestions.push({
        id: uuidv4(),
        question: 'Is your cough dry or productive?',
        type: 'select',
        options: ['Dry', 'Productive', 'Both'],
        required: true
      })
      followUpQuestions.push({
        id: uuidv4(),
        question: 'How long have you had the cough?',
        type: 'text',
        required: true
      })
    }

    followUpQuestions.forEach(question => {
      if (!dynamicQuestions.find(q => q.question === question.question)) {
        addDynamicQuestion(question)
      }
    })
  }

  useEffect(() => {
    if (chiefComplaint) {
      generateFollowUpQuestions()
    }
  }, [chiefComplaint])

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Patient Information & Clinical Assessment</h2>
        <p className="mt-2 text-gray-600">
          Gather comprehensive patient details and conduct dynamic clinical assessment
        </p>
        <div className="mt-4 flex items-center justify-center space-x-2 text-sm text-gray-500">
          <Save className="w-4 h-4" />
          <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Patient Demographics */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <User className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Patient Demographics</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              value={patient.name || ''}
              onChange={(e) => handlePatientInfoChange('name', e.target.value)}
              className="input-field"
              placeholder="Enter patient's full name"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Medical Record Number
            </label>
            <input
              type="text"
              value={patient.medicalRecordNumber || ''}
              onChange={(e) => handlePatientInfoChange('medicalRecordNumber', e.target.value)}
              className="input-field"
              placeholder="Enter MRN"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Age *
            </label>
            <input
              type="number"
              value={patient.age || ''}
              onChange={(e) => handlePatientInfoChange('age', e.target.value)}
              className="input-field"
              placeholder="Age"
              min="0"
              max="150"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gender *
            </label>
            <select
              value={patient.gender || ''}
              onChange={(e) => handlePatientInfoChange('gender', e.target.value)}
              className="input-field"
              required
            >
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
          </div>
        </div>
      </div>

      {/* Chief Complaint */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <MessageSquare className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Chief Complaint</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What is the main reason for today's visit? *
          </label>
          <textarea
            value={chiefComplaint}
            onChange={(e) => setChiefComplaint(e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Describe the main concern or symptom..."
            required
          />
        </div>
      </div>

      {/* Dynamic Follow-up Questions */}
      {dynamicQuestions.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold text-gray-900">Follow-up Questions</h3>
            </div>
            <span className="text-sm text-gray-500">{dynamicQuestions.length} questions</span>
          </div>
          
          <div className="space-y-4">
            {dynamicQuestions.map((question) => (
              <div key={question.id}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {question.question}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                
                {question.type === 'select' ? (
                  <select
                    value={dynamicAnswers[question.id] || ''}
                    onChange={(e) => updateDynamicAnswer(question.id, e.target.value)}
                    className="input-field"
                    required={question.required}
                  >
                    <option value="">Select an option</option>
                    {question.options?.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                ) : question.type === 'number' ? (
                  <input
                    type="number"
                    value={dynamicAnswers[question.id] || ''}
                    onChange={(e) => updateDynamicAnswer(question.id, e.target.value)}
                    className="input-field"
                    required={question.required}
                    min={question.question.includes('pain') ? '1' : '0'}
                    max={question.question.includes('pain') ? '10' : undefined}
                  />
                ) : (
                  <textarea
                    value={dynamicAnswers[question.id] || ''}
                    onChange={(e) => updateDynamicAnswer(question.id, e.target.value)}
                    className="input-field"
                    rows={2}
                    required={question.required}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Present Illness */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Clock className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">History of Present Illness</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Detailed description of the current illness
          </label>
          <textarea
            value={presentIllness}
            onChange={(e) => setPresentIllness(e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Provide a detailed timeline and description of the current illness..."
          />
        </div>
      </div>

      {/* Medical History */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Clock className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Past Medical History</h3>
        </div>
        
        <div className="space-y-4">
          {medicalHistory.length > 0 && (
            <div className="space-y-2">
              {medicalHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-900">{item.condition}</span>
                  <button
                    onClick={() => {
                      // Remove history item logic would go here
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={newHistoryItem}
              onChange={(e) => setNewHistoryItem(e.target.value)}
              className="flex-1 input-field"
              placeholder="Add past medical condition..."
              onKeyPress={(e) => e.key === 'Enter' && addHistoryItem()}
            />
            <button
              onClick={addHistoryItem}
              className="btn-primary flex items-center space-x-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>
        </div>
      </div>

      {/* Additional Clinical Observations */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <MessageSquare className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Additional Clinical Observations</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional notes and observations
          </label>
          <textarea
            value={additionalObservations}
            onChange={(e) => setAdditionalObservations(e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Any additional observations, social history, family history, etc..."
          />
        </div>
      </div>

      {/* Custom Question Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Custom Questions</h3>
          <button
            onClick={() => setShowAddQuestion(true)}
            className="btn-secondary flex items-center space-x-1"
          >
            <Plus className="w-4 h-4" />
            <span>Add Question</span>
          </button>
        </div>
        
        {showAddQuestion && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Question
              </label>
              <input
                type="text"
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                className="input-field"
                placeholder="Enter your custom question..."
                onKeyPress={(e) => e.key === 'Enter' && addDynamicQuestionHandler()}
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={addDynamicQuestionHandler}
                className="btn-primary"
              >
                Add Question
              </button>
              <button
                onClick={() => setShowAddQuestion(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}