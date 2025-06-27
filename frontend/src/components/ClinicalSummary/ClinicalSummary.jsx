import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  ChevronLeft,
  FileText,
  Download,
  Printer,
  Save,
  Calendar,
  User,
  Clock,
  AlertCircle,
  CheckCircle,
  Activity,
  Stethoscope,
  Pill,
  Brain,
  Heart,
  ClipboardList,
  Share2,
  Mail,
  Copy,
  Check,
  FileCheck,
  Clipboard,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const ClinicalSummary = () => {
  const { patientData, updatePatientData, setCurrentStep, sessionId, resetPatient } = usePatient();
  const { addRecord, deleteSession } = useAppData();
  const [clinicalSummary, setClinicalSummary] = useState('');
  const [selectedView, setSelectedView] = useState('summary'); // 'summary' or 'timeline'
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    patientInfo: true,
    chiefComplaint: true,
    physicalExam: true,
    diagnosticTests: true,
    diagnosis: true,
    treatment: true,
    followUp: true
  });
  
  useEffect(() => {
    // Generate comprehensive clinical summary
    if (!clinicalSummary) {
      generateClinicalSummary();
    }
  }, []);
  
  const generateClinicalSummary = () => {
    setIsGeneratingSummary(true);
    
    const diagnosis = patientData.selectedDiagnosis || { name: patientData.finalDiagnosis };
    const testResultsArray = Object.values(patientData.testResults || {});
    
    const summary = `CLINICAL SUMMARY REPORT
═══════════════════════════════════════════════════════════════════

PATIENT INFORMATION
─────────────────────────────────────────────────────────────────
Name: ${patientData.name}
Age: ${patientData.age} years
Gender: ${patientData.gender}
Date of Birth: ${patientData.dateOfBirth || 'Not specified'}
Visit Date: ${new Date().toLocaleDateString()}
Report Generated: ${new Date().toLocaleString()}

CHIEF COMPLAINT
─────────────────────────────────────────────────────────────────
${patientData.chiefComplaint}

HISTORY OF PRESENT ILLNESS
─────────────────────────────────────────────────────────────────
${patientData.chiefComplaintDetails && patientData.chiefComplaintDetails.length > 0 
  ? patientData.chiefComplaintDetails
      .filter(q => q.answer && !q.skipped)
      .map(q => `• ${q.text}: ${q.answer}`)
      .join('\n') 
  : 'See clinical notes'}

${patientData.clinicalNotes ? `\nAdditional Clinical Notes:\n${patientData.clinicalNotes}` : ''}

PAST MEDICAL HISTORY
─────────────────────────────────────────────────────────────────
${patientData.medicalHistory && patientData.medicalHistory.length > 0
  ? patientData.medicalHistory.map(h => `• ${h}`).join('\n')
  : 'No significant past medical history reported'}

CURRENT MEDICATIONS
─────────────────────────────────────────────────────────────────
${patientData.medications && patientData.medications.length > 0
  ? patientData.medications.map(m => `• ${m}`).join('\n')
  : 'No current medications'}

ALLERGIES
─────────────────────────────────────────────────────────────────
${patientData.allergies && patientData.allergies.length > 0
  ? patientData.allergies.map(a => `• ${a}`).join('\n')
  : 'No known allergies'}

PHYSICAL EXAMINATION
─────────────────────────────────────────────────────────────────
Vital Signs:
• Blood Pressure: ${patientData.physicalExam.bloodPressure}
• Heart Rate: ${patientData.physicalExam.heartRate} bpm
• Temperature: ${patientData.physicalExam.temperature}°C
• Respiratory Rate: ${patientData.physicalExam.respiratoryRate}/min
• Oxygen Saturation: ${patientData.physicalExam.oxygenSaturation}%
${patientData.physicalExam.height ? `• Height: ${patientData.physicalExam.height} cm` : ''}
${patientData.physicalExam.weight ? `• Weight: ${patientData.physicalExam.weight} kg` : ''}
${patientData.physicalExam.bmi ? `• BMI: ${patientData.physicalExam.bmi}` : ''}

${patientData.physicalExam.additionalFindings ? `Additional Findings:\n${patientData.physicalExam.additionalFindings}` : ''}

DIAGNOSTIC TESTS PERFORMED
─────────────────────────────────────────────────────────────────
${testResultsArray.length > 0 ? 
  testResultsArray.map(r => {
    let result = `• ${r.testName}: `;
    if (r.value) {
      result += `${r.value} ${r.unit || ''}`;
      if (r.referenceRange) result += ` (Ref: ${r.referenceRange})`;
      if (r.interpretation) result += ` - ${r.interpretation}`;
    } else {
      result += 'Completed';
    }
    return result;
  }).join('\n') :
  'No diagnostic tests performed'}

FINAL DIAGNOSIS
─────────────────────────────────────────────────────────────────
Primary Diagnosis: ${diagnosis.name}
ICD-10 Code: ${diagnosis.icd10 || 'Not specified'}
${diagnosis.confidence ? `Diagnostic Confidence: ${diagnosis.confidence}` : ''}

TREATMENT PLAN
─────────────────────────────────────────────────────────────────
${patientData.treatmentPlan || 'Treatment plan pending'}

PRESCRIPTIONS
─────────────────────────────────────────────────────────────────
${patientData.prescriptions && patientData.prescriptions.length > 0
  ? patientData.prescriptions.map((p, i) => 
      `${i + 1}. ${p.medication} ${p.dosage}
   Route: ${p.route}
   Frequency: ${p.frequency}
   Duration: ${p.duration}
   Instructions: ${p.instructions}`
    ).join('\n\n')
  : 'No prescriptions ordered'}

FOLLOW-UP RECOMMENDATIONS
─────────────────────────────────────────────────────────────────
${patientData.followUpRecommendations || 'Standard follow-up as indicated'}

PATIENT EDUCATION
─────────────────────────────────────────────────────────────────
${patientData.patientEducation || 'Patient education materials provided'}

CLINICAL DECISION SUPPORT
─────────────────────────────────────────────────────────────────
This assessment was supported by AI-enhanced clinical decision tools.
All diagnoses and treatment recommendations have been reviewed and 
approved by the attending physician.

─────────────────────────────────────────────────────────────────
Generated by DiagnoAssist AI Clinical Decision Support System
${new Date().toLocaleString()}`;
    
    setClinicalSummary(summary);
    updatePatientData('clinicalSummary', summary);
    
    setTimeout(() => setIsGeneratingSummary(false), 1000);
  };
  
  const handleFinalize = async () => {
    setIsSaving(true);
    
    // Create comprehensive patient record
    const record = {
      patientId: patientData.id,
      sessionId: sessionId,
      timestamp: new Date().toISOString(),
      chiefComplaint: patientData.chiefComplaint,
      chiefComplaintDetails: patientData.chiefComplaintDetails,
      clinicalNotes: patientData.clinicalNotes,
      standardizedAssessments: patientData.standardizedAssessments,
      medicalHistory: patientData.medicalHistory,
      medications: patientData.medications,
      allergies: patientData.allergies,
      physicalExam: patientData.physicalExam,
      differentialDiagnoses: patientData.differentialDiagnoses,
      selectedDiagnosis: patientData.selectedDiagnosis,
      finalDiagnosis: patientData.finalDiagnosis,
      diagnosticNotes: patientData.diagnosticNotes,
      selectedTests: patientData.selectedTests || [],
      testResults: patientData.testResults || {},
      treatmentPlan: patientData.treatmentPlan,
      prescriptions: patientData.prescriptions,
      followUpRecommendations: patientData.followUpRecommendations,
      patientEducation: patientData.patientEducation,
      clinicalSummary: clinicalSummary,
      assessmentNote: patientData.assessmentNote
    };
    
    // Save the record
    addRecord(record);
    
    // Delete the session if it exists (it's complete now)
    if (sessionId) {
      deleteSession(sessionId);
    }
    
    setTimeout(() => {
      setIsSaving(false);
      alert('Patient record has been finalized and saved successfully!');
      
      // Reset and go back to home
      resetPatient();
      setCurrentStep('home');
    }, 1500);
  };
  
  const handleBack = () => {
    setCurrentStep('treatment-plan');
  };
  
  const exportPDF = () => {
    // In a real app, this would generate a proper PDF
    alert('PDF export functionality would be implemented here');
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(clinicalSummary).then(() => {
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    });
  };
  
  const handleEmailReport = () => {
    // In a real app, this would open an email client or send via API
    alert('Email functionality would be implemented here');
  };
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const renderTimeline = () => {
    const events = [
      { time: 'Initial Assessment', icon: User, color: 'blue', description: `Chief complaint: ${patientData.chiefComplaint}` },
      { time: 'Physical Examination', icon: Stethoscope, color: 'green', description: 'Vital signs recorded' },
      { time: 'Diagnostic Analysis', icon: Brain, color: 'purple', description: `${patientData.differentialDiagnoses.length} differential diagnoses generated` },
      { time: 'Laboratory Tests', icon: Activity, color: 'yellow', description: `${Object.keys(patientData.testResults || {}).length} tests performed` },
      { time: 'Final Diagnosis', icon: CheckCircle, color: 'green', description: patientData.finalDiagnosis },
      { time: 'Treatment Plan', icon: Pill, color: 'red', description: `${patientData.prescriptions?.length || 0} medications prescribed` }
    ];
    
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Clinical Timeline</h3>
        <div className="relative">
          {events.map((event, index) => (
            <div key={index} className="flex items-start mb-8 last:mb-0">
              <div className="relative">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full bg-${event.color}-100 flex items-center justify-center z-10`}>
                  <event.icon className={`w-5 h-5 text-${event.color}-600`} />
                </div>
                {index < events.length - 1 && (
                  <div className="absolute left-5 top-10 w-0.5 h-20 bg-gray-200"></div>
                )}
              </div>
              <div className="ml-4 flex-1">
                <p className="font-medium text-gray-900">{event.time}</p>
                <p className="text-sm text-gray-600 mt-1">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  const renderSummarySection = (title, icon, content, sectionKey) => {
    const isExpanded = expandedSections[sectionKey];
    const Icon = icon;
    
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <Icon className="w-5 h-5 text-gray-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>
        {isExpanded && (
          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
            <div className="prose prose-sm max-w-none text-gray-700">
              {content}
            </div>
          </div>
        )}
      </div>
    );
  };
  
  const renderFormattedSummary = () => {
    const diagnosis = patientData.selectedDiagnosis || { name: patientData.finalDiagnosis };
    const testResultsArray = Object.values(patientData.testResults || {});
    
    return (
      <div>
        {/* Patient Information */}
        {renderSummarySection(
          'Patient Information',
          User,
          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Name:</span> {patientData.name}
              </div>
              <div>
                <span className="font-medium">Age:</span> {patientData.age} years
              </div>
              <div>
                <span className="font-medium">Gender:</span> {patientData.gender}
              </div>
              <div>
                <span className="font-medium">Date of Birth:</span> {patientData.dateOfBirth || 'Not specified'}
              </div>
            </div>
            <div className="pt-2 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">Visit Date:</span> {new Date().toLocaleDateString()}
                </div>
                <div>
                  <span className="font-medium">Report Generated:</span> {new Date().toLocaleString()}
                </div>
              </div>
            </div>
          </div>,
          'patientInfo'
        )}
        
        {/* Chief Complaint & History */}
        {renderSummarySection(
          'Chief Complaint & History',
          ClipboardList,
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Chief Complaint</h4>
              <p className="text-gray-700 bg-white p-3 rounded border border-gray-200">
                {patientData.chiefComplaint}
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">History of Present Illness</h4>
              <div className="space-y-1">
                {patientData.chiefComplaintDetails && patientData.chiefComplaintDetails.length > 0 ? (
                  patientData.chiefComplaintDetails
                    .filter(q => q.answer && !q.skipped)
                    .map((q, idx) => (
                      <div key={idx} className="flex items-start">
                        <span className="text-gray-500 mr-2">•</span>
                        <span><strong>{q.text}:</strong> {q.answer}</span>
                      </div>
                    ))
                ) : (
                  <p className="text-gray-600 italic">No detailed history recorded</p>
                )}
              </div>
            </div>
            
            {patientData.clinicalNotes && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Additional Clinical Notes</h4>
                <p className="text-gray-700 bg-white p-3 rounded border border-gray-200">
                  {patientData.clinicalNotes}
                </p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Medical History</h4>
                <div className="bg-white p-3 rounded border border-gray-200">
                  {patientData.medicalHistory && patientData.medicalHistory.length > 0 ? (
                    patientData.medicalHistory.map((h, idx) => (
                      <div key={idx} className="flex items-start">
                        <span className="text-gray-500 mr-2">•</span>
                        <span>{h}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 italic">None reported</p>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Current Medications</h4>
                <div className="bg-white p-3 rounded border border-gray-200">
                  {patientData.medications && patientData.medications.length > 0 ? (
                    patientData.medications.map((m, idx) => (
                      <div key={idx} className="flex items-start">
                        <span className="text-gray-500 mr-2">•</span>
                        <span>{m}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 italic">None</p>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Allergies</h4>
                <div className="bg-white p-3 rounded border border-gray-200">
                  {patientData.allergies && patientData.allergies.length > 0 ? (
                    patientData.allergies.map((a, idx) => (
                      <div key={idx} className="flex items-start text-red-600">
                        <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{a}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 italic">No known allergies</p>
                  )}
                </div>
              </div>
            </div>
          </div>,
          'chiefComplaint'
        )}
        
        {/* Physical Examination */}
        {renderSummarySection(
          'Physical Examination',
          Stethoscope,
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Vital Signs</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Blood Pressure</p>
                  <p className="font-semibold text-lg">{patientData.physicalExam.bloodPressure}</p>
                </div>
                <div className="bg-white p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Heart Rate</p>
                  <p className="font-semibold text-lg">{patientData.physicalExam.heartRate} bpm</p>
                </div>
                <div className="bg-white p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Temperature</p>
                  <p className="font-semibold text-lg">{patientData.physicalExam.temperature}°C</p>
                </div>
                <div className="bg-white p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Respiratory Rate</p>
                  <p className="font-semibold text-lg">{patientData.physicalExam.respiratoryRate}/min</p>
                </div>
                <div className="bg-white p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">O2 Saturation</p>
                  <p className="font-semibold text-lg">{patientData.physicalExam.oxygenSaturation}%</p>
                </div>
                {patientData.physicalExam.bmi && (
                  <div className="bg-white p-3 rounded border border-gray-200">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">BMI</p>
                    <p className="font-semibold text-lg">{patientData.physicalExam.bmi}</p>
                  </div>
                )}
              </div>
            </div>
            
            {patientData.physicalExam.additionalFindings && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Additional Findings</h4>
                <p className="text-gray-700 bg-white p-3 rounded border border-gray-200">
                  {patientData.physicalExam.additionalFindings}
                </p>
              </div>
            )}
          </div>,
          'physicalExam'
        )}
        
        {/* Diagnostic Tests */}
        {renderSummarySection(
          'Diagnostic Tests Performed',
          Activity,
          <div>
            {testResultsArray.length > 0 ? (
              <div className="space-y-2">
                {testResultsArray.map((r, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border border-gray-200">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-800">{r.testName}</p>
                        {r.value && (
                          <p className="text-gray-700">
                            Result: <span className="font-semibold">{r.value} {r.unit || ''}</span>
                            {r.referenceRange && <span className="text-gray-500 ml-2">(Ref: {r.referenceRange})</span>}
                          </p>
                        )}
                        {r.interpretation && (
                          <p className="text-sm text-gray-600 mt-1">
                            <span className="font-medium">Interpretation:</span> {r.interpretation}
                          </p>
                        )}
                      </div>
                      {r.status === 'completed' && (
                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No diagnostic tests performed</p>
            )}
          </div>,
          'diagnosticTests'
        )}
        
        {/* Final Diagnosis */}
        {renderSummarySection(
          'Final Diagnosis',
          FileCheck,
          <div className="bg-white p-4 rounded border-2 border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-lg font-semibold text-gray-800">{diagnosis.name}</h4>
              {diagnosis.confidence && (
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  diagnosis.confidence === 'High' ? 'bg-green-100 text-green-800' :
                  diagnosis.confidence === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {diagnosis.confidence} Confidence
                </span>
              )}
            </div>
            {diagnosis.icd10 && (
              <p className="text-gray-600">
                <span className="font-medium">ICD-10 Code:</span> {diagnosis.icd10}
              </p>
            )}
          </div>,
          'diagnosis'
        )}
        
        {/* Treatment Plan */}
        {renderSummarySection(
          'Treatment Plan & Prescriptions',
          Heart,
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Treatment Plan</h4>
              <div className="bg-white p-4 rounded border border-gray-200">
                <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700">
                  {patientData.treatmentPlan || 'Treatment plan pending'}
                </pre>
              </div>
            </div>
            
            {patientData.prescriptions && patientData.prescriptions.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Prescriptions</h4>
                <div className="space-y-3">
                  {patientData.prescriptions.map((p, idx) => (
                    <div key={idx} className="bg-white p-4 rounded border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">
                            {idx + 1}. {p.medication} {p.dosage}
                          </p>
                          <div className="mt-1 space-y-1 text-sm text-gray-600">
                            <p><span className="font-medium">Route:</span> {p.route}</p>
                            <p><span className="font-medium">Frequency:</span> {p.frequency}</p>
                            <p><span className="font-medium">Duration:</span> {p.duration}</p>
                            {p.instructions && (
                              <p className="text-amber-700 bg-amber-50 px-2 py-1 rounded mt-2">
                                <AlertCircle className="inline w-3 h-3 mr-1" />
                                {p.instructions}
                              </p>
                            )}
                          </div>
                        </div>
                        <Pill className="w-5 h-5 text-blue-500 flex-shrink-0" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>,
          'treatment'
        )}
        
        {/* Follow-up & Education */}
        {renderSummarySection(
          'Follow-up & Patient Education',
          Calendar,
          <div className="space-y-4">
            {patientData.followUpRecommendations && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Follow-up Recommendations</h4>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700">
                    {patientData.followUpRecommendations}
                  </pre>
                </div>
              </div>
            )}
            
            {patientData.patientEducation && (
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Patient Education</h4>
                <div className="bg-blue-50 p-4 rounded border border-blue-200">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700">
                    {patientData.patientEducation}
                  </pre>
                </div>
              </div>
            )}
          </div>,
          'followUp'
        )}
      </div>
    );
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold text-gray-900">Clinical Summary</h2>
          <div className="flex items-center space-x-2">
            <ClipboardList className="w-6 h-6 text-indigo-600" />
            <span className="text-sm text-gray-600">Comprehensive Patient Report</span>
          </div>
        </div>
        <p className="text-gray-600">
          Review the complete clinical summary and finalize the patient record
        </p>
      </div>
      
      {/* Patient Summary Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-1">
              <User className="w-4 h-4 text-indigo-600 mr-2" />
              <span className="font-medium text-indigo-900">{patientData.name}</span>
              <span className="text-indigo-700 ml-2">{patientData.age} years • {patientData.gender}</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <Stethoscope className="w-4 h-4 text-indigo-600 mr-1" />
                <p className="text-indigo-800 text-sm">
                  Diagnosis: <span className="font-medium">{patientData.selectedDiagnosis?.name || patientData.finalDiagnosis}</span>
                </p>
              </div>
              <div className="flex items-center">
                <Pill className="w-4 h-4 text-indigo-600 mr-1" />
                <p className="text-indigo-800 text-sm">
                  {patientData.prescriptions?.length || 0} medications
                </p>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center text-sm text-indigo-700">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date().toLocaleDateString()}
            </div>
            <div className="flex items-center text-sm text-indigo-700 mt-1">
              <Clock className="w-4 h-4 mr-1" />
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Generation Status */}
      {isGeneratingSummary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
          <div className="flex items-center">
            <div className="animate-pulse flex space-x-2">
              <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
              <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
              <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
            </div>
            <p className="text-blue-900 font-medium ml-4">Generating comprehensive clinical summary...</p>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedView('summary')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'summary'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          Full Summary
        </button>
        <button
          onClick={() => setSelectedView('timeline')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedView === 'timeline'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Clock className="w-4 h-4 mr-2" />
          Clinical Timeline
        </button>
      </div>
      
      {/* Main Content */}
      <div className="mb-6">
        {selectedView === 'summary' ? (
          <>
            {renderFormattedSummary()}
            
            {/* Export Options */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Export & Share Options</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                  onClick={exportPDF}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-300 rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all group"
                >
                  <Download className="w-8 h-8 text-gray-600 group-hover:text-gray-800 mb-2" />
                  <span className="font-medium text-gray-900">Export PDF</span>
                </button>
                
                <button
                  onClick={handlePrint}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-300 rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all group"
                >
                  <Printer className="w-8 h-8 text-gray-600 group-hover:text-gray-800 mb-2" />
                  <span className="font-medium text-gray-900">Print</span>
                </button>
                
                <button
                  onClick={handleEmailReport}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-300 rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all group"
                >
                  <Mail className="w-8 h-8 text-gray-600 group-hover:text-gray-800 mb-2" />
                  <span className="font-medium text-gray-900">Email</span>
                </button>
                
                <button
                  onClick={handleCopyToClipboard}
                  className={`flex flex-col items-center justify-center p-4 border-2 rounded-xl transition-all group ${
                    copySuccess 
                      ? 'border-green-300 bg-green-50' 
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                >
                  {copySuccess ? (
                    <>
                      <Check className="w-8 h-8 text-green-600 mb-2" />
                      <span className="font-medium text-green-600">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-8 h-8 text-gray-600 group-hover:text-gray-800 mb-2" />
                      <span className="font-medium text-gray-900">Copy Text</span>
                    </>
                  )}
                </button>
              </div>
              
              {/* Privacy Notice */}
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-1">Privacy & Security</p>
                    <p className="text-sm text-blue-800">
                      All patient data is encrypted and transmitted securely. Ensure you have proper 
                      authorization before sharing patient information. Always follow HIPAA guidelines 
                      and institutional policies for patient data handling.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          renderTimeline()
        )}
      </div>
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          {isSaving ? (
            <div className="flex items-center space-x-2 text-blue-600">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <span className="font-medium">Saving patient record...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-gray-500">
              <Heart className="w-5 h-5" />
              <span>Ready to finalize patient record</span>
            </div>
          )}
          
          <button
            onClick={handleFinalize}
            disabled={isSaving}
            className="flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 group"
          >
            <Save className="w-5 h-5 mr-2" />
            Finalize & Save Record
          </button>
        </div>
      </div>
      
      {/* Warning */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-amber-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-900 mb-1">Final Review Required</p>
            <p className="text-sm text-amber-800">
              Please review all information carefully before finalizing. Once saved, the patient 
              record will be permanently stored and the current session will be closed. Ensure all 
              diagnoses, treatments, and recommendations are accurate and complete.
            </p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back to Treatment Plan
        </button>
      </div>
    </div>
  );
};

export default ClinicalSummary;