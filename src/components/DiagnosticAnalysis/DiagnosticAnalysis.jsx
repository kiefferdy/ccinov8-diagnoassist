import { useState, useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { Brain, TrendingUp, TrendingDown, AlertCircle, CheckCircle, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react'
import clsx from 'clsx'

const mockDifferentialDiagnoses = [
  {
    id: '1',
    condition: 'Community-Acquired Pneumonia',
    probability: 75,
    reasoning: 'Patient presents with productive cough, fever, and elevated heart rate. Physical exam findings of decreased breath sounds and dullness to percussion are consistent with consolidation.',
    supportingFactors: [
      'Productive cough with fever',
      'Elevated heart rate (102 bpm)',
      'Decreased breath sounds in lower right lobe',
      'Patient appears acutely ill'
    ],
    contradictingFactors: [
      'No significant dyspnea reported',
      'Oxygen saturation normal (98%)'
    ],
    severity: 'moderate'
  },
  {
    id: '2',
    condition: 'Acute Bronchitis',
    probability: 65,
    reasoning: 'Viral or bacterial bronchitis could explain the cough and fever. However, the physical exam findings suggest more than just bronchial inflammation.',
    supportingFactors: [
      'Productive cough',
      'Fever present',
      'Recent URI symptoms'
    ],
    contradictingFactors: [
      'Physical exam suggests consolidation',
      'Patient appears more acutely ill than typical bronchitis'
    ],
    severity: 'mild'
  },
  {
    id: '3',
    condition: 'Pulmonary Embolism',
    probability: 25,
    reasoning: 'While less likely given the presentation, PE should be considered in any patient with acute respiratory symptoms, especially with elevated heart rate.',
    supportingFactors: [
      'Elevated heart rate',
      'Acute onset of symptoms'
    ],
    contradictingFactors: [
      'No chest pain or dyspnea',
      'No risk factors mentioned',
      'Productive cough more suggestive of infection'
    ],
    severity: 'high'
  },
  {
    id: '4',
    condition: 'Lung Cancer',
    probability: 10,
    reasoning: 'Chronic cough could suggest malignancy, but acute presentation with fever makes infection more likely.',
    supportingFactors: [
      'Chronic cough if present'
    ],
    contradictingFactors: [
      'Acute presentation with fever',
      'No weight loss mentioned',
      'No smoking history provided'
    ],
    severity: 'high'
  }
]

export default function DiagnosticAnalysis() {
  const { 
    patient, 
    chiefComplaint, 
    physicalExam, 
    initialDiagnosis, 
    setInitialDiagnosis 
  } = usePatientData()
  
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedDiagnosis, setSelectedDiagnosis] = useState(null)
  const [feedback, setFeedback] = useState({})
  const [doctorNotes, setDoctorNotes] = useState('')

  useEffect(() => {
    if (!initialDiagnosis.differentialDiagnoses.length) {
      generateDiagnosis()
    }
  }, [])

  const generateDiagnosis = async () => {
    setIsAnalyzing(true)
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // In a real app, this would call the AI backend
    const diagnosis = {
      differentialDiagnoses: mockDifferentialDiagnoses,
      reasoning: `Based on the patient's presentation of ${chiefComplaint} and physical examination findings, I've generated the following differential diagnoses ranked by probability. The analysis considers the patient's symptoms, vital signs, and physical exam findings.`,
      confidence: 78,
      generatedAt: new Date().toISOString()
    }
    
    setInitialDiagnosis(diagnosis)
    setIsAnalyzing(false)
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'mild':
        return 'text-green-600 bg-green-50 border-green-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getProbabilityColor = (probability) => {
    if (probability >= 70) return 'text-red-600 bg-red-100'
    if (probability >= 50) return 'text-yellow-600 bg-yellow-100'
    if (probability >= 30) return 'text-blue-600 bg-blue-100'
    return 'text-gray-600 bg-gray-100'
  }

  const handleFeedback = (diagnosisId, type) => {
    setFeedback(prev => ({
      ...prev,
      [diagnosisId]: type
    }))
  }

  const handleRegenerateDiagnosis = () => {
    setInitialDiagnosis({
      differentialDiagnoses: [],
      reasoning: '',
      confidence: null
    })
    generateDiagnosis()
  }

  if (isAnalyzing) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">AI Diagnostic Analysis</h2>
          <p className="mt-2 text-gray-600">
            AI is analyzing patient data to generate differential diagnoses
          </p>
        </div>

        <div className="card text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Analyzing Patient Data</h3>
              <p className="text-gray-600">Processing symptoms, history, and physical exam findings...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">AI Diagnostic Analysis</h2>
        <p className="mt-2 text-gray-600">
          AI-generated differential diagnoses based on patient presentation
        </p>
      </div>

      {/* Analysis Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Analysis Summary</h3>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-sm text-gray-600">Confidence Score</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div 
                    className={clsx(
                      'h-2 rounded-full',
                      initialDiagnosis.confidence >= 80 ? 'bg-green-500' :
                      initialDiagnosis.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    )}
                    style={{ width: `${initialDiagnosis.confidence}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium">{initialDiagnosis.confidence}%</span>
              </div>
            </div>
            <button
              onClick={handleRegenerateDiagnosis}
              className="btn-secondary text-sm"
            >
              Regenerate
            </button>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-gray-800">{initialDiagnosis.reasoning}</p>
        </div>
      </div>

      {/* Differential Diagnoses */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900">Differential Diagnoses</h3>
          <span className="text-sm text-gray-600">
            {initialDiagnosis.differentialDiagnoses?.length} conditions identified
          </span>
        </div>

        {initialDiagnosis.differentialDiagnoses?.map((diagnosis, index) => (
          <div key={diagnosis.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start space-x-4 flex-1">
                <div className="flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-600 rounded-full font-semibold text-sm">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-semibold text-gray-900">{diagnosis.condition}</h4>
                    <span className={clsx(
                      'px-2 py-1 rounded-full text-xs font-medium border',
                      getSeverityColor(diagnosis.severity)
                    )}>
                      {diagnosis.severity} severity
                    </span>
                  </div>
                  <p className="text-gray-700 mb-3">{diagnosis.reasoning}</p>
                </div>
              </div>
              
              <div className="text-right ml-4">
                <div className={clsx(
                  'px-3 py-1 rounded-lg font-bold text-lg',
                  getProbabilityColor(diagnosis.probability)
                )}>
                  {diagnosis.probability}%
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <h5 className="font-medium text-green-700 mb-2 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Supporting Factors
                </h5>
                <ul className="space-y-1">
                  {diagnosis.supportingFactors.map((factor, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h5 className="font-medium text-red-700 mb-2 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  Contradicting Factors
                </h5>
                <ul className="space-y-1">
                  {diagnosis.contradictingFactors.map((factor, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>Is this diagnosis helpful?</span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleFeedback(diagnosis.id, 'agree')}
                  className={clsx(
                    'flex items-center space-x-1 px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                    feedback[diagnosis.id] === 'agree' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-600'
                  )}
                >
                  <ThumbsUp className="w-4 h-4" />
                  <span>Agree</span>
                </button>
                <button
                  onClick={() => handleFeedback(diagnosis.id, 'disagree')}
                  className={clsx(
                    'flex items-center space-x-1 px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                    feedback[diagnosis.id] === 'disagree' 
                      ? 'bg-red-100 text-red-700' 
                      : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-600'
                  )}
                >
                  <ThumbsDown className="w-4 h-4" />
                  <span>Disagree</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Doctor's Notes */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <MessageSquare className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional clinical thoughts and differential considerations
          </label>
          <textarea
            value={doctorNotes}
            onChange={(e) => setDoctorNotes(e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Add your clinical reasoning, additional differentials to consider, or modifications to the AI analysis..."
          />
        </div>
      </div>

      {/* Action Items */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-center space-x-2 mb-4">
          <AlertCircle className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-blue-900">Next Steps</h3>
        </div>
        
        <div className="text-blue-800">
          <p className="mb-2">Based on the differential diagnoses, consider the following actions:</p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Order appropriate diagnostic tests to narrow down the differential</li>
            <li>Consider immediate interventions for high-severity conditions</li>
            <li>Review and validate AI recommendations with clinical judgment</li>
            <li>Document any additional findings or reasoning</li>
          </ul>
        </div>
      </div>
    </div>
  )
}