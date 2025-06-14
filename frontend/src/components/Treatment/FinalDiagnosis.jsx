import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  FileText, 
  ChevronLeft,
  ChevronRight,
  Check,
  AlertCircle,
  Download,
  Save,
  Printer,
  RefreshCw,
  Calendar,
  User,
  Brain,
  Sparkles,
  MessageSquare,
  BarChart3,
  Activity,
  PlusCircle
} from 'lucide-react';
import RefinedDiagnosisCard from './components/RefinedDiagnosisCard';
import TreatmentPlanEditor from './components/TreatmentPlanEditor';
import DiagnosticSummaryPanel from './components/DiagnosticSummaryPanel';

const FinalDiagnosis = () => {
  const { patientData, updatePatientData, setCurrentStep, sessionId, resetPatient } = usePatient();
  const { addRecord, deleteSession } = useAppData();
  const [refinedDiagnoses, setRefinedDiagnoses] = useState([]);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState(null);
  const [customDiagnosis, setCustomDiagnosis] = useState('');
  const [treatmentPlan, setTreatmentPlan] = useState('');
  const [prescriptions, setPrescriptions] = useState([]);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [assessmentNote, setAssessmentNote] = useState('');
  const [selectedView, setSelectedView] = useState('overview'); // 'overview', 'detailed', 'summary'
  const [isRefining, setIsRefining] = useState(false);
  const [showCustomDiagnosisForm, setShowCustomDiagnosisForm] = useState(false);
  
  useEffect(() => {
    // Refine diagnoses based on test results
    refineAnalysis();
    
    // Load existing data if available
    if (patientData.treatmentPlan) {
      setTreatmentPlan(patientData.treatmentPlan);
    }
    if (patientData.prescriptions && patientData.prescriptions.length > 0) {
      setPrescriptions(patientData.prescriptions);
    }
    if (patientData.selectedDiagnosis) {
      setSelectedDiagnosis(patientData.selectedDiagnosis);
    }
  }, []);
  
  const refineAnalysis = async () => {
    setIsRefining(true);
    
    // In a real app, this would call an API with test results
    const testResults = patientData.testResults || {};
    let refined = [...patientData.differentialDiagnoses];
    
    // Enhanced refinement logic
    const testResultsArray = Object.values(testResults);
    if (testResultsArray.some(r => r.testName && r.testName.includes('Chest X-ray'))) {
      refined = refined.map(d => {
        if (d.name.includes('Pneumonia')) {
          return { 
            ...d, 
            probability: 0.85, 
            confidence: 'High',
            supportingFactors: [
              ...d.supportingFactors,
              'Chest X-ray shows consolidation'
            ]
          };
        } else if (d.name.includes('Bronchitis')) {
          return { 
            ...d, 
            probability: 0.10, 
            confidence: 'Low',
            contradictingFactors: [
              ...d.contradictingFactors,
              'Chest X-ray findings suggest pneumonia'
            ]
          };
        }
        return d;
      });
    }
    
    // Sort by probability
    refined.sort((a, b) => b.probability - a.probability);
    setRefinedDiagnoses(refined);
    
    // Generate assessment note
    generateAssessmentNote(refined[0]);
    
    setTimeout(() => setIsRefining(false), 1500);
  };
  
  const generateAssessmentNote = (topDiagnosis) => {
    const testResultsArray = Object.values(patientData.testResults || {});
    
    const note = `ASSESSMENT AND PLAN

PATIENT: ${patientData.name}, ${patientData.age}-year-old ${patientData.gender}
DATE: ${new Date().toLocaleDateString()}
CHIEF COMPLAINT: ${patientData.chiefComplaint}

HISTORY OF PRESENT ILLNESS:
${patientData.chiefComplaintDetails && patientData.chiefComplaintDetails.length > 0 
  ? patientData.chiefComplaintDetails
      .filter(q => q.answer && !q.skipped)
      .map(q => `${q.text}: ${q.answer}`)
      .join('\n') 
  : 'See clinical notes'}

PHYSICAL EXAMINATION:
Vital Signs:
- Blood Pressure: ${patientData.physicalExam.bloodPressure}
- Heart Rate: ${patientData.physicalExam.heartRate} bpm
- Temperature: ${patientData.physicalExam.temperature}°C
- Respiratory Rate: ${patientData.physicalExam.respiratoryRate}/min
- O2 Saturation: ${patientData.physicalExam.oxygenSaturation}%

${patientData.physicalExam.additionalFindings ? `Additional Findings:\n${patientData.physicalExam.additionalFindings}` : ''}

DIAGNOSTIC RESULTS:
${testResultsArray.length > 0 ? 
  testResultsArray.map(r => `- ${r.testName}: ${r.value || 'Completed'} ${r.unit || ''} ${r.interpretation ? `(${r.interpretation})` : ''}`).join('\n') :
  'No diagnostic tests performed'
}

ASSESSMENT:
Based on the clinical presentation, physical examination, and diagnostic results, the most likely diagnosis is ${topDiagnosis?.name || 'pending further evaluation'} (ICD-10: ${topDiagnosis?.icd10 || 'TBD'}).

Differential diagnoses considered included:
${refinedDiagnoses.slice(0, 3).map((d, i) => `${i + 1}. ${d.name} (${(d.probability * 100).toFixed(0)}% probability)`).join('\n')}

PLAN:
See treatment recommendations below.

${patientData.diagnosticNotes ? `\nCLINICAL NOTES:\n${patientData.diagnosticNotes}` : ''}`;
    
    setAssessmentNote(note);
    updatePatientData('assessmentNote', note);
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
        confidence: 'Doctor Override',
        icd10: 'Custom'
      };
      setSelectedDiagnosis(custom);
      updatePatientData('selectedDiagnosis', custom);
      generateTreatmentPlan(custom);
      setShowCustomDiagnosisForm(false);
      setCustomDiagnosis('');
    }
  };
  
  const generateTreatmentPlan = async (diagnosis) => {
    setIsGeneratingPlan(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Enhanced treatment plan generation
    let plan = '';
    let mockPrescriptions = [];
    
    if (diagnosis.name.includes('Pneumonia')) {
      plan = `1. Antibiotic Therapy:
   - Start empirical treatment with amoxicillin-clavulanate 875mg PO BID
   - Consider macrolide addition if atypical pneumonia suspected
   - Duration: 7-10 days based on clinical response

2. Supportive Care:
   - Rest and adequate hydration (2-3L daily unless contraindicated)
   - Antipyretics for fever (acetaminophen 500-1000mg q6h PRN)
   - Supplemental oxygen if O2 saturation < 92%
   - Chest physiotherapy if productive cough

3. Monitoring:
   - Daily temperature monitoring
   - Watch for signs of clinical deterioration
   - Monitor for medication side effects

4. Follow-up:
   - Re-evaluate in 48-72 hours (sooner if worsening)
   - Repeat chest X-ray in 4-6 weeks to ensure resolution
   - Consider admission if severe symptoms or comorbidities

5. Patient Education:
   - Complete full course of antibiotics
   - Return if symptoms worsen or no improvement in 2-3 days
   - Smoking cessation counseling if applicable
   - Pneumococcal and influenza vaccination when recovered`;
   
      mockPrescriptions = [
        {
          id: 1,
          medication: 'Amoxicillin-Clavulanate',
          dosage: '875mg',
          frequency: 'Twice daily',
          duration: '7 days',
          instructions: 'Take with food to minimize GI upset'
        },
        {
          id: 2,
          medication: 'Acetaminophen',
          dosage: '500mg',
          frequency: 'Every 6 hours as needed',
          duration: 'PRN for fever',
          instructions: 'Maximum 4g daily'
        },
        {
          id: 3,
          medication: 'Guaifenesin',
          dosage: '400mg',
          frequency: 'Every 4 hours as needed',
          duration: 'PRN for cough',
          instructions: 'Take with full glass of water'
        }
      ];
    } else {
      // Generic treatment plan
      plan = `1. Symptomatic Treatment:
   - Address specific symptoms as indicated
   - Pain management if needed
   - Rest and hydration

2. Monitoring:
   - Monitor symptom progression
   - Track vital signs if applicable

3. Follow-up:
   - As needed based on symptom progression
   - Sooner if symptoms worsen

4. Patient Education:
   - Return precautions provided
   - Lifestyle modifications as appropriate`;
    }
    
    setTreatmentPlan(plan);
    setPrescriptions(mockPrescriptions);
    updatePatientData('treatmentPlan', plan);
    updatePatientData('prescriptions', mockPrescriptions);
    
    setIsGeneratingPlan(false);
  };
  
  const handleFinalize = () => {
    // Validate required fields
    if (!selectedDiagnosis && !customDiagnosis) {
      alert('Please select or enter a diagnosis before finalizing.');
      return;
    }
    
    // Save final diagnosis
    updatePatientData('finalDiagnosis', selectedDiagnosis?.name || customDiagnosis);
    updatePatientData('assessmentNote', assessmentNote);
    
    // Create comprehensive patient record
    const record = {
      patientId: patientData.id,
      sessionId: sessionId,
      chiefComplaint: patientData.chiefComplaint,
      chiefComplaintDetails: patientData.chiefComplaintDetails,
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
      diagnosticNotes: patientData.diagnosticNotes || '',
      differentialDiagnoses: refinedDiagnoses,
      clinicalNotes: patientData.clinicalNotes || '',
      standardizedAssessments: patientData.standardizedAssessments || {}
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
  
  const exportPDF = () => {
    // In a real app, this would generate a proper PDF
    alert('PDF export functionality would be implemented here');
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold text-gray-900">Final Diagnosis & Treatment Plan</h2>
          <div className="flex items-center space-x-2">
            <Brain className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-gray-600">AI-Enhanced Decision Support</span>
          </div>
        </div>
        <p className="text-gray-600">
          Review AI-refined analysis based on test results and finalize the diagnosis with treatment plan
        </p>
      </div>
      
      {/* Patient Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-1">
              <User className="w-4 h-4 text-blue-600 mr-2" />
              <span className="font-medium text-blue-900">{patientData.name}</span>
              <span className="text-blue-700 ml-2">{patientData.age} years • {patientData.gender}</span>
            </div>
            <p className="text-blue-800">Chief Complaint: {patientData.chiefComplaint}</p>
          </div>
          <div className="text-right">
            <div className="flex items-center text-sm text-blue-700">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Refinement Status */}
      {isRefining && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-4 mb-6">
          <div className="flex items-center">
            <div className="relative mr-4">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600"></div>
              <Sparkles className="absolute inset-0 m-auto w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-purple-900 font-medium">Refining diagnoses with test results...</p>
              <p className="text-purple-700 text-sm">Using AI to correlate clinical findings and laboratory data</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedView('overview')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'overview'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Diagnostic Overview
        </button>
        <button
          onClick={() => setSelectedView('detailed')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'detailed'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          Treatment Details
        </button>
        <button
          onClick={() => setSelectedView('summary')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'summary'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Clinical Summary
        </button>
      </div>
      
      {/* Main Content */}
      {selectedView === 'overview' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Diagnoses List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900">Select Final Diagnosis</h3>
                <button
                  onClick={refineAnalysis}
                  className="flex items-center space-x-1 px-2.5 py-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors text-sm"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Re-analyze</span>
                </button>
              </div>
              <p className="text-sm text-gray-600">
                The diagnoses below are refined based on all clinical information gathered during the assessment, 
                including patient history, physical examination, and test results.
              </p>
            </div>
            
            {refinedDiagnoses.map((diagnosis, index) => (
              <RefinedDiagnosisCard
                key={diagnosis.id}
                diagnosis={diagnosis}
                index={index}
                isSelected={selectedDiagnosis?.id === diagnosis.id}
                onSelect={() => {
                  handleDiagnosisSelect(diagnosis);
                  // Automatically switch to treatment tab when diagnosis is selected
                  setSelectedView('detailed');
                }}
                testResults={patientData.testResults}
              />
            ))}
            
            {/* Custom Diagnosis Option */}
            {!showCustomDiagnosisForm ? (
              <button
                onClick={() => setShowCustomDiagnosisForm(true)}
                className="w-full p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-gray-400 transition-colors flex items-center justify-center text-gray-600 hover:text-gray-800"
              >
                <PlusCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Add Custom Diagnosis</span>
              </button>
            ) : (
              <div className="p-4 border-2 border-blue-300 rounded-xl bg-blue-50">
                <h4 className="font-medium text-gray-900 mb-3">Custom Diagnosis</h4>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={customDiagnosis}
                    onChange={(e) => setCustomDiagnosis(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter diagnosis..."
                    autoFocus
                  />
                  <button
                    onClick={handleCustomDiagnosis}
                    disabled={!customDiagnosis.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300"
                  >
                    Select
                  </button>
                  <button
                    onClick={() => {
                      setShowCustomDiagnosisForm(false);
                      setCustomDiagnosis('');
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Side Panel */}
          <div className="lg:col-span-1">
            <DiagnosticSummaryPanel 
              patientData={patientData}
              refinedDiagnoses={refinedDiagnoses}
              testResults={patientData.testResults}
            />
          </div>
        </div>
      ) : selectedView === 'detailed' ? (
        <div className="mb-6">
          {selectedDiagnosis ? (
            <TreatmentPlanEditor
              treatmentPlan={treatmentPlan}
              prescriptions={prescriptions}
              onTreatmentPlanChange={(plan) => {
                setTreatmentPlan(plan);
                updatePatientData('treatmentPlan', plan);
              }}
              onPrescriptionsChange={(rx) => {
                setPrescriptions(rx);
                updatePatientData('prescriptions', rx);
              }}
              isGenerating={isGeneratingPlan}
              selectedDiagnosis={selectedDiagnosis}
            />
          ) : (
            <div className="bg-gray-50 rounded-xl p-12 text-center">
              <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Diagnosis Selected</h3>
              <p className="text-gray-600">
                Please select a diagnosis from the overview tab to generate a treatment plan
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical Assessment Summary</h3>
            <textarea
              value={assessmentNote}
              onChange={(e) => {
                setAssessmentNote(e.target.value);
                updatePatientData('assessmentNote', e.target.value);
              }}
              rows={20}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Assessment notes will be generated automatically..."
            />
          </div>
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex space-x-3">
            <button 
              onClick={exportPDF}
              className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </button>
            <button className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              <Printer className="w-4 h-4 mr-2" />
              Print
            </button>
          </div>
          
          {selectedView === 'summary' ? (
            <button
              onClick={handleFinalize}
              disabled={!selectedDiagnosis && !customDiagnosis}
              className="flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300"
            >
              <Save className="w-5 h-5 mr-2" />
              Finalize & Save Record
            </button>
          ) : selectedView === 'detailed' ? (
            <button
              onClick={() => setSelectedView('summary')}
              disabled={!treatmentPlan}
              className="flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 group"
            >
              Continue to Clinical Summary
              <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          ) : (
            <button
              onClick={() => setSelectedView('detailed')}
              disabled={!selectedDiagnosis && !customDiagnosis}
              className="flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 group"
            >
              Continue to Treatment Plan
              <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          )}
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back to Test Results
        </button>
      </div>
    </div>
  );
};

export default FinalDiagnosis;