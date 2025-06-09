import { useState, useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { 
  FileText, 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  CheckCircle, 
  AlertCircle, 
  Pill,
  Calendar,
  Save,
  Download,
  Printer
} from 'lucide-react'
import clsx from 'clsx'

const mockRefinedDiagnoses = [
  {
    id: '1',
    condition: 'Community-Acquired Pneumonia',
    probability: 90,
    reasoning: 'Elevated WBC count (14.2 K/μL) with left shift (82% neutrophils) and chest X-ray showing right lower lobe consolidation strongly support bacterial pneumonia diagnosis.',
    supportingFactors: [
      'Chest X-ray: Right lower lobe consolidation',
      'Elevated WBC count (14.2 K/μL)',
      'Left shift (82% neutrophils)',
      'Productive cough with fever',
      'Physical exam consistent with consolidation'
    ],
    contradictingFactors: [],
    severity: 'moderate',
    changes: 'Probability increased from 75% due to supportive lab and imaging findings'
  },
  {
    id: '2',
    condition: 'Acute Bronchitis',
    probability: 15,
    reasoning: 'While chest X-ray shows consolidation rather than just bronchial inflammation, viral bronchitis could still be considered as a secondary diagnosis.',
    supportingFactors: [
      'Productive cough',
      'Fever present'
    ],
    contradictingFactors: [
      'Chest X-ray shows consolidation',
      'Elevated WBC suggests bacterial infection'
    ],
    severity: 'mild',
    changes: 'Probability decreased from 65% due to imaging and lab findings'
  }
]

const mockTreatmentOptions = [
  {
    medication: 'Amoxicillin-Clavulanate',
    dosage: '875mg/125mg PO BID',
    duration: '7-10 days',
    indication: 'First-line treatment for community-acquired pneumonia',
    contraindications: ['Penicillin allergy'],
    sideEffects: ['GI upset', 'Diarrhea']
  },
  {
    medication: 'Azithromycin',
    dosage: '500mg PO daily',
    duration: '5 days',
    indication: 'Alternative for penicillin-allergic patients',
    contraindications: ['QT prolongation', 'Liver disease'],
    sideEffects: ['GI upset', 'QT prolongation']
  },
  {
    medication: 'Dextromethorphan',
    dosage: '15mg PO q4h PRN',
    duration: 'As needed',
    indication: 'Cough suppressant',
    contraindications: ['MAOI use'],
    sideEffects: ['Drowsiness', 'Dizziness']
  }
]

export default function FinalDiagnosis() {
  const {
    patient,
    testResults,
    selectedTests,
    refinedDiagnosis,
    finalDiagnosis,
    setRefinedDiagnosis,
    updateFinalDiagnosis
  } = usePatientData()

  const [isRefining, setIsRefining] = useState(false)
  const [selectedTreatments, setSelectedTreatments] = useState([])
  const [customTreatment, setCustomTreatment] = useState('')
  const [followUpInstructions, setFollowUpInstructions] = useState('')
  const [additionalNotes, setAdditionalNotes] = useState('')

  useEffect(() => {
    if (!refinedDiagnosis.differentialDiagnoses.length && selectedTests.length > 0) {
      refineAnalysis()
    }
  }, [])

  const refineAnalysis = async () => {
    setIsRefining(true)
    
    // Simulate API call to refine diagnosis based on test results
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const refined = {
      differentialDiagnoses: mockRefinedDiagnoses,
      reasoning: 'Based on the test results, the differential diagnosis has been refined. Laboratory findings show elevated WBC count with left shift, and chest X-ray confirms consolidation, significantly supporting the diagnosis of community-acquired pneumonia.',
      confidence: 90,
      changes: [
        'Community-Acquired Pneumonia probability increased from 75% to 90%',
        'Acute Bronchitis probability decreased from 65% to 15%',
        'Pulmonary Embolism ruled out based on normal chest X-ray and clinical presentation',
        'Lung Cancer ruled out based on acute presentation and imaging findings'
      ],
      refinedAt: new Date().toISOString()
    }
    
    setRefinedDiagnosis(refined)
    setIsRefining(false)
  }

  const handlePrimaryDiagnosisChange = (condition) => {
    updateFinalDiagnosis({ primaryDiagnosis: condition })
  }

  const toggleSecondaryDiagnosis = (condition) => {
    const current = finalDiagnosis.secondaryDiagnoses || []
    const updated = current.includes(condition)
      ? current.filter(d => d !== condition)
      : [...current, condition]
    updateFinalDiagnosis({ secondaryDiagnoses: updated })
  }

  const toggleTreatment = (treatment) => {
    const isSelected = selectedTreatments.find(t => t.medication === treatment.medication)
    if (isSelected) {
      setSelectedTreatments(selectedTreatments.filter(t => t.medication !== treatment.medication))
    } else {
      setSelectedTreatments([...selectedTreatments, treatment])
    }
  }

  const generateMedicalNote = () => {
    const primaryDx = finalDiagnosis.primaryDiagnosis || refinedDiagnosis.differentialDiagnoses[0]?.condition
    const completedTests = selectedTests.filter(testId => testResults[testId]?.status === 'completed')
    
    return `
PATIENT: ${patient.name}
AGE: ${patient.age} years
GENDER: ${patient.gender}
DATE: ${new Date().toLocaleDateString()}

ASSESSMENT AND PLAN:

PRIMARY DIAGNOSIS: ${primaryDx}

DIFFERENTIAL DIAGNOSES CONSIDERED:
${refinedDiagnosis.differentialDiagnoses.map(dx => 
  `- ${dx.condition} (${dx.probability}%): ${dx.reasoning}`
).join('\n')}

DIAGNOSTIC TESTS COMPLETED:
${completedTests.map(testId => {
  const result = testResults[testId]
  return `- ${testId.replace('-', ' ').toUpperCase()}: ${result.interpretation || 'Pending interpretation'}`
}).join('\n')}

TREATMENT PLAN:
${selectedTreatments.map(treatment => 
  `- ${treatment.medication} ${treatment.dosage} for ${treatment.duration}`
).join('\n')}
${customTreatment ? `- ${customTreatment}` : ''}

FOLLOW-UP:
${followUpInstructions || 'Follow up as needed'}

ADDITIONAL NOTES:
${additionalNotes || 'None'}

Confidence Level: ${refinedDiagnosis.confidence}%
Generated by DiagnoAssist AI on ${new Date().toLocaleString()}
`.trim()
  }

  const handleSaveDiagnosis = () => {
    updateFinalDiagnosis({
      treatmentPlan: selectedTreatments.map(t => 
        `${t.medication} ${t.dosage} for ${t.duration}`
      ).join(', ') + (customTreatment ? `, ${customTreatment}` : ''),
      followUpInstructions: followUpInstructions,
      notes: additionalNotes,
      finalizedAt: new Date().toISOString()
    })
    
    // In a real app, this would save to the backend and update the patient's medical record
    alert('Diagnosis and treatment plan saved successfully!')
  }

  const handlePrintReport = () => {
    const medicalNote = generateMedicalNote()
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>Medical Report - ${patient.name}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            pre { white-space: pre-wrap; font-family: Arial, sans-serif; }
          </style>
        </head>
        <body>
          <pre>${medicalNote}</pre>
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }

  if (isRefining) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Final Diagnosis & Treatment Plan</h2>
          <p className="mt-2 text-gray-600">
            AI is refining the diagnosis based on test results
          </p>
        </div>

        <div className="card text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Refining Analysis</h3>
              <p className="text-gray-600">Incorporating test results to update differential diagnosis...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Final Diagnosis & Treatment Plan</h2>
        <p className="mt-2 text-gray-600">
          Refined AI analysis and treatment recommendations
        </p>
      </div>

      {/* Refined Analysis Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Refined Analysis</h3>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-sm text-gray-600">Updated Confidence</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${refinedDiagnosis.confidence}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-green-600">{refinedDiagnosis.confidence}%</span>
              </div>
            </div>
            <button
              onClick={refineAnalysis}
              className="btn-secondary text-sm"
            >
              Re-analyze
            </button>
          </div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <p className="text-gray-800">{refinedDiagnosis.reasoning}</p>
        </div>

        {refinedDiagnosis.changes && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Key Changes from Initial Analysis:</h4>
            <ul className="space-y-1">
              {refinedDiagnosis.changes.map((change, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{change}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Updated Differential Diagnoses */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-900">Updated Differential Diagnoses</h3>
        
        {refinedDiagnosis.differentialDiagnoses?.map((diagnosis, index) => (
          <div key={diagnosis.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start space-x-4 flex-1">
                <div className="flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-600 rounded-full font-semibold text-sm">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-semibold text-gray-900">{diagnosis.condition}</h4>
                    <span className="text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      {diagnosis.changes}
                    </span>
                  </div>
                  <p className="text-gray-700 mb-3">{diagnosis.reasoning}</p>
                </div>
              </div>
              
              <div className="text-right ml-4">
                <div className={clsx(
                  'px-3 py-1 rounded-lg font-bold text-lg',
                  diagnosis.probability >= 70 ? 'text-green-700 bg-green-100' :
                  diagnosis.probability >= 50 ? 'text-yellow-700 bg-yellow-100' :
                  'text-gray-700 bg-gray-100'
                )}>
                  {diagnosis.probability}%
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-green-700 mb-2 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Supporting Evidence
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
              
              {diagnosis.contradictingFactors.length > 0 && (
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
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Final Diagnosis Selection */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <FileText className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Final Diagnosis Selection</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Diagnosis
            </label>
            <select
              value={finalDiagnosis.primaryDiagnosis || ''}
              onChange={(e) => handlePrimaryDiagnosisChange(e.target.value)}
              className="input-field"
            >
              <option value="">Select primary diagnosis</option>
              {refinedDiagnosis.differentialDiagnoses?.map(diagnosis => (
                <option key={diagnosis.id} value={diagnosis.condition}>
                  {diagnosis.condition} ({diagnosis.probability}%)
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Secondary Diagnoses (Optional)
            </label>
            <div className="space-y-2">
              {refinedDiagnosis.differentialDiagnoses?.filter(d => 
                d.condition !== finalDiagnosis.primaryDiagnosis
              ).map(diagnosis => (
                <label key={diagnosis.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={finalDiagnosis.secondaryDiagnoses?.includes(diagnosis.condition) || false}
                    onChange={() => toggleSecondaryDiagnosis(diagnosis.condition)}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="text-gray-700">{diagnosis.condition}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Treatment Plan */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Pill className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Treatment Plan</h3>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Recommended Medications</h4>
          <div className="space-y-3">
            {mockTreatmentOptions.map((treatment, index) => (
              <div key={index} className={clsx(
                'p-4 border rounded-lg cursor-pointer transition-colors',
                selectedTreatments.find(t => t.medication === treatment.medication)
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:bg-gray-50'
              )}
              onClick={() => toggleTreatment(treatment)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={selectedTreatments.find(t => t.medication === treatment.medication) !== undefined}
                      onChange={() => toggleTreatment(treatment)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500 mt-1"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div>
                      <h5 className="font-medium text-gray-900">{treatment.medication}</h5>
                      <p className="text-sm text-gray-600">{treatment.dosage} for {treatment.duration}</p>
                      <p className="text-xs text-gray-500 mt-1">{treatment.indication}</p>
                      {treatment.contraindications.length > 0 && (
                        <p className="text-xs text-red-600 mt-1">
                          Contraindications: {treatment.contraindications.join(', ')}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Treatment Instructions
            </label>
            <textarea
              value={customTreatment}
              onChange={(e) => setCustomTreatment(e.target.value)}
              className="input-field"
              rows={3}
              placeholder="Add any additional medications, non-pharmacological treatments, or special instructions..."
            />
          </div>
        </div>
      </div>

      {/* Follow-up Instructions */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Calendar className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Follow-up Instructions</h3>
        </div>
        
        <div>
          <textarea
            value={followUpInstructions}
            onChange={(e) => setFollowUpInstructions(e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Specify follow-up appointments, monitoring requirements, warning signs to watch for, when to return..."
          />
        </div>
      </div>

      {/* Additional Notes */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <FileText className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Additional Clinical Notes</h3>
        </div>
        
        <div>
          <textarea
            value={additionalNotes}
            onChange={(e) => setAdditionalNotes(e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Add any additional clinical notes, patient education provided, special considerations..."
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <div className="space-x-3">
          <button
            onClick={handlePrintReport}
            className="btn-secondary flex items-center space-x-2"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report</span>
          </button>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
        
        <div className="space-x-3">
          <button className="btn-secondary">
            Save as Draft
          </button>
          <button
            onClick={handleSaveDiagnosis}
            className="btn-primary flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Finalize Diagnosis</span>
          </button>
        </div>
      </div>
    </div>
  )
}