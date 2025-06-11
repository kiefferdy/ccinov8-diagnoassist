import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  FileText, 
  ChevronLeft,
  Check,
  AlertCircle,
  Download,
  Save,
  Printer,
  RefreshCw,
  Pill,
  Plus,
  X,
  Calendar,
  User
} from 'lucide-react';

const FinalDiagnosis = () => {
  const { patientData, updatePatientData, setCurrentStep, sessionId, resetPatient } = usePatient();
  const { addRecord, deleteSession } = useAppData();
  const [refinedDiagnoses, setRefinedDiagnoses] = useState([]);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState(null);
  const [customDiagnosis, setCustomDiagnosis] = useState('');
  const [treatmentPlan, setTreatmentPlan] = useState('');
  const [prescriptions, setPrescriptions] = useState([]);
  const [newPrescription, setNewPrescription] = useState({
    medication: '',
    dosage: '',
    frequency: '',
    duration: ''
  });
  const [showPrescriptionForm, setShowPrescriptionForm] = useState(false);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [assessmentNote, setAssessmentNote] = useState('');
  
  useEffect(() => {
    // Refine diagnoses based on test results
    refineAnalysis();
  }, []);
  
  const refineAnalysis = () => {
    // In a real app, this would call an API with test results
    // For now, we'll adjust probabilities based on mock logic
    const testResults = patientData.testResults || {};
    let refined = [...patientData.differentialDiagnoses];
    
    // Mock refinement logic
    const testResultsArray = Object.values(testResults);
    if (testResultsArray.some(r => r.testName && r.testName.includes('Chest X-ray'))) {
      refined = refined.map(d => {
        if (d.name.includes('Pneumonia')) {
          return { ...d, probability: 0.85, confidence: 'High' };
        } else if (d.name.includes('Bronchitis')) {
          return { ...d, probability: 0.10, confidence: 'Low' };
        }
        return d;
      });
    }
    
    // Sort by probability
    refined.sort((a, b) => b.probability - a.probability);
    setRefinedDiagnoses(refined);
    
    // Generate assessment note
    generateAssessmentNote(refined[0]);
  };
  
  const generateAssessmentNote = (topDiagnosis) => {
    const testResultsArray = Object.values(patientData.testResults || {});
    
    const note = `ASSESSMENT:
${patientData.age}-year-old ${patientData.gender} presenting with ${patientData.chiefComplaint}.

Physical examination revealed:
- BP: ${patientData.physicalExam.bloodPressure}
- HR: ${patientData.physicalExam.heartRate} bpm
- Temp: ${patientData.physicalExam.temperature}°C
- RR: ${patientData.physicalExam.respiratoryRate}/min
- O2 Sat: ${patientData.physicalExam.oxygenSaturation}%

${patientData.physicalExam.additionalFindings ? `Additional findings: ${patientData.physicalExam.additionalFindings}` : ''}

Laboratory/Imaging Results:
${testResultsArray.map(r => `- ${r.testName}: ${r.value} ${r.unit || ''} (${r.interpretation || 'pending'})`).join('\n')}

Based on clinical presentation and diagnostic results, the most likely diagnosis is ${topDiagnosis.name} (ICD-10: ${topDiagnosis.icd10}).

PLAN:
See treatment recommendations below.`;
    
    setAssessmentNote(note);
  };
  
  const handleDiagnosisSelect = async (diagnosis) => {
    setSelectedDiagnosis(diagnosis);
    updatePatientData('selectedDiagnosis', diagnosis);
    
    // Generate treatment plan
    await generateTreatmentPlan(diagnosis);
  };
  
  const handleCustomDiagnosis = () => {
    if (customDiagnosis.trim()) {
      const custom = {
        id: 'custom',
        name: customDiagnosis,
        isCustom: true,
        probability: 1.0,
        confidence: 'Doctor Override'
      };
      setSelectedDiagnosis(custom);
      updatePatientData('selectedDiagnosis', custom);
      generateTreatmentPlan(custom);
    }
  };
  
  const generateTreatmentPlan = async (diagnosis) => {
    setIsGeneratingPlan(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock treatment plan based on diagnosis
    let plan = '';
    let mockPrescriptions = [];
    
    if (diagnosis.name.includes('Pneumonia')) {
      plan = `1. Antibiotic therapy:
   - Start empirical treatment with amoxicillin-clavulanate
   - Consider macrolide addition if atypical pneumonia suspected

2. Supportive care:
   - Rest and adequate hydration
   - Antipyretics for fever (acetaminophen or ibuprofen)
   - Supplemental oxygen if O2 saturation < 92%

3. Follow-up:
   - Re-evaluate in 48-72 hours
   - Repeat chest X-ray in 4-6 weeks to ensure resolution
   - Consider admission if severe symptoms or comorbidities

4. Patient education:
   - Complete full course of antibiotics
   - Return if symptoms worsen or no improvement in 2-3 days
   - Smoking cessation counseling if applicable`;
   
      mockPrescriptions = [
        {
          id: 1,
          medication: 'Amoxicillin-Clavulanate',
          dosage: '875mg',
          frequency: 'Twice daily',
          duration: '7 days'
        },
        {
          id: 2,
          medication: 'Acetaminophen',
          dosage: '500mg',
          frequency: 'Every 6 hours as needed',
          duration: 'PRN for fever'
        }
      ];
    } else if (diagnosis.name.includes('Hypertension')) {
      plan = `1. Lifestyle modifications:
   - DASH diet implementation
   - Regular exercise (30 min/day, 5 days/week)
   - Weight reduction if BMI > 25
   - Limit sodium intake to < 2300mg/day
   - Limit alcohol consumption

2. Pharmacotherapy:
   - Start ACE inhibitor or ARB as first-line
   - Monitor blood pressure at home

3. Follow-up:
   - Recheck BP in 2-4 weeks
   - Annual labs: BMP, lipid panel, urinalysis
   - Assess for target organ damage

4. Risk factor modification:
   - Smoking cessation if applicable
   - Stress management techniques`;
   
      mockPrescriptions = [
        {
          id: 1,
          medication: 'Lisinopril',
          dosage: '10mg',
          frequency: 'Once daily',
          duration: 'Ongoing'
        }
      ];
    } else {
      plan = `1. Symptomatic treatment as indicated

2. Follow-up as needed based on symptom progression

3. Return precautions provided

4. Additional testing if symptoms persist or worsen`;
    }
    
    setTreatmentPlan(plan);
    setPrescriptions(mockPrescriptions);
    updatePatientData('treatmentPlan', plan);
    updatePatientData('prescriptions', mockPrescriptions);
    
    setIsGeneratingPlan(false);
  };
  
  const handleAddPrescription = () => {
    if (newPrescription.medication && newPrescription.dosage) {
      const prescription = {
        id: prescriptions.length + 1,
        ...newPrescription
      };
      setPrescriptions([...prescriptions, prescription]);
      updatePatientData('prescriptions', [...prescriptions, prescription]);
      setNewPrescription({
        medication: '',
        dosage: '',
        frequency: '',
        duration: ''
      });
      setShowPrescriptionForm(false);
    }
  };
  
  const handleRemovePrescription = (id) => {
    const filtered = prescriptions.filter(p => p.id !== id);
    setPrescriptions(filtered);
    updatePatientData('prescriptions', filtered);
  };
  
  const handleFinalize = () => {
    // Save final diagnosis
    updatePatientData('finalDiagnosis', selectedDiagnosis?.name || customDiagnosis);
    updatePatientData('assessmentNote', assessmentNote);
    
    // Create patient record
    const record = {
      patientId: patientData.id,
      sessionId: sessionId,
      chiefComplaint: patientData.chiefComplaint,
      finalDiagnosis: selectedDiagnosis?.name || customDiagnosis,
      icd10: selectedDiagnosis?.icd10 || 'Custom',
      physicalExam: patientData.physicalExam,
      prescriptions: prescriptions,
      treatmentPlan: treatmentPlan,
      testsPerformed: patientData.selectedTests || [],
      testResults: patientData.testResults || {},
      medicalHistory: patientData.medicalHistory,
      medications: patientData.medications,
      allergies: patientData.allergies,
      assessmentNote: assessmentNote,
      diagnosticNotes: patientData.diagnosticNotes || ''
    };
    
    // Save the record
    addRecord(record);
    
    // Delete the session if it exists (it's complete now)
    if (sessionId) {
      deleteSession(sessionId);
    }
    
    alert('Patient record has been finalized and saved successfully!');
    
    // Reset and go back to home
    resetPatient();
    setCurrentStep('home');
  };
  
  const handleBack = () => {
    setCurrentStep('test-results');
  };
  
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Final Diagnosis & Treatment Plan</h2>
        <p className="text-gray-600">Review refined analysis, confirm diagnosis, and create treatment plan</p>
      </div>
      
      {/* Patient Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-1">
              <User className="w-4 h-4 text-blue-600 mr-2" />
              <span className="font-medium text-blue-900">{patientData.name}</span>
              <span className="text-blue-700 ml-2">{patientData.age} years • {patientData.gender}</span>
            </div>
            <p className="text-blue-800">Chief Complaint: {patientData.chiefComplaint}</p>
          </div>
          <div className="text-right text-sm text-blue-700">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Refined Diagnoses */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center mb-6">
          <RefreshCw className="w-5 h-5 text-blue-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Refined Diagnostic Analysis</h3>
          <span className="ml-2 text-sm text-gray-500">(Based on test results)</span>
        </div>
        
        <div className="space-y-3">
          {refinedDiagnoses.map((diagnosis, index) => (
            <div
              key={diagnosis.id}
              onClick={() => handleDiagnosisSelect(diagnosis)}
              className={`p-4 border rounded-lg cursor-pointer transition-all ${
                selectedDiagnosis?.id === diagnosis.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {selectedDiagnosis?.id === diagnosis.id && (
                    <Check className="w-5 h-5 text-blue-600 mr-2" />
                  )}
                  <span className="font-medium text-gray-900">
                    {index + 1}. {diagnosis.name}
                  </span>
                  <span className="ml-2 text-sm text-gray-500">ICD-10: {diagnosis.icd10}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-700">
                    {(diagnosis.probability * 100).toFixed(0)}%
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    diagnosis.confidence === 'High' ? 'bg-green-100 text-green-700' :
                    diagnosis.confidence === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {diagnosis.confidence}
                  </span>
                </div>
              </div>
            </div>
          ))}
          
          {/* Custom Diagnosis Option */}
          <div className="mt-4 p-4 border border-dashed border-gray-300 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Or enter a custom diagnosis:</p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customDiagnosis}
                onChange={(e) => setCustomDiagnosis(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter diagnosis..."
              />
              <button
                onClick={handleCustomDiagnosis}
                disabled={!customDiagnosis.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300"
              >
                Select
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Treatment Plan */}
      {selectedDiagnosis && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Treatment Plan</h3>
            </div>
            {isGeneratingPlan && (
              <div className="flex items-center text-blue-600">
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                <span className="text-sm">Generating plan...</span>
              </div>
            )}
          </div>
          
          {treatmentPlan && (
            <div className="space-y-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Recommended Treatment:</h4>
                <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                  {treatmentPlan}
                </pre>
              </div>
              
              {/* Prescriptions */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900 flex items-center">
                    <Pill className="w-4 h-4 mr-2 text-blue-600" />
                    Prescriptions
                  </h4>
                  <button
                    onClick={() => setShowPrescriptionForm(!showPrescriptionForm)}
                    className="flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Prescription
                  </button>
                </div>
                
                {prescriptions.length > 0 && (
                  <div className="space-y-2 mb-3">
                    {prescriptions.map(rx => (
                      <div key={rx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{rx.medication}</p>
                          <p className="text-sm text-gray-600">
                            {rx.dosage} • {rx.frequency} • {rx.duration}
                          </p>
                        </div>
                        <button
                          onClick={() => handleRemovePrescription(rx.id)}
                          className="text-red-600 hover:bg-red-50 p-1 rounded transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                
                {showPrescriptionForm && (
                  <div className="p-4 bg-blue-50 rounded-lg space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Medication *
                        </label>
                        <input
                          type="text"
                          value={newPrescription.medication}
                          onChange={(e) => setNewPrescription({ ...newPrescription, medication: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., Amoxicillin"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Dosage *
                        </label>
                        <input
                          type="text"
                          value={newPrescription.dosage}
                          onChange={(e) => setNewPrescription({ ...newPrescription, dosage: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., 500mg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Frequency
                        </label>
                        <input
                          type="text"
                          value={newPrescription.frequency}
                          onChange={(e) => setNewPrescription({ ...newPrescription, frequency: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., Three times daily"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Duration
                        </label>
                        <input
                          type="text"
                          value={newPrescription.duration}
                          onChange={(e) => setNewPrescription({ ...newPrescription, duration: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., 7 days"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => setShowPrescriptionForm(false)}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleAddPrescription}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Assessment Note */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Medical Assessment Note:</h4>
                <textarea
                  value={assessmentNote}
                  onChange={(e) => setAssessmentNote(e.target.value)}
                  rows={10}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex space-x-3">
            <button className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </button>
            <button className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              <Printer className="w-4 h-4 mr-2" />
              Print
            </button>
          </div>
          <button
            onClick={handleFinalize}
            disabled={!selectedDiagnosis && !customDiagnosis}
            className="flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300"
          >
            <Save className="w-5 h-5 mr-2" />
            Finalize & Save Record
          </button>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
      </div>
    </div>
  );
};

export default FinalDiagnosis;
