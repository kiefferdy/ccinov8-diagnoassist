import React from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  FileText, 
  User, 
  Calendar, 
  Heart, 
  Stethoscope, 
  Activity, 
  TestTube,
  Download,
  Printer,
  CheckCircle
} from 'lucide-react';

const SOAPSummary = () => {
  const { patientData } = usePatient();
  
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleDownload = () => {
    // In a real app, this would generate a PDF
    const soapText = generateSOAPText();
    const blob = new Blob([soapText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SOAP_${patientData.name}_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
  };
  
  const generateSOAPText = () => {
    return `SOAP NOTE
==================
Date: ${formatDate(new Date())}
Patient: ${patientData.name}, ${patientData.age} years old, ${patientData.gender}
Chief Complaint: ${patientData.chiefComplaint}

SUBJECTIVE (S)
--------------
History of Present Illness:
${patientData.historyOfPresentIllness || 'Not documented'}

Review of Systems:
${patientData.reviewOfSystems || 'Not documented'}

Past Medical History:
${patientData.pastMedicalHistory || patientData.medicalHistory?.join(', ') || 'None'}

Medications:
${patientData.medications?.join(', ') || 'None'}

Allergies:
${patientData.allergies?.join(', ') || 'NKDA'}

Social History:
${patientData.socialHistory || 'Not documented'}

Family History:
${patientData.familyHistory || 'Not documented'}

OBJECTIVE (O)
-------------
Vital Signs:
- Blood Pressure: ${patientData.physicalExam?.bloodPressure || 'Not recorded'}
- Heart Rate: ${patientData.physicalExam?.heartRate || 'Not recorded'} bpm
- Temperature: ${patientData.physicalExam?.temperature || 'Not recorded'}°C
- Respiratory Rate: ${patientData.physicalExam?.respiratoryRate || 'Not recorded'}/min
- O2 Saturation: ${patientData.physicalExam?.oxygenSaturation || 'Not recorded'}%
- Height: ${patientData.physicalExam?.height || 'Not recorded'} cm
- Weight: ${patientData.physicalExam?.weight || 'Not recorded'} kg
- BMI: ${patientData.physicalExam?.bmi || 'Not calculated'}

Physical Examination:
${patientData.physicalExam?.additionalFindings || 'No additional findings documented'}

ASSESSMENT (A)
--------------
${patientData.doctorDiagnosis || 'Not documented'}

Clinical Reasoning:
${patientData.diagnosticNotes || 'Not documented'}

PLAN (P)
--------
Diagnostic Tests:
${patientData.selectedTests?.map(test => `- ${test.name}`).join('\n') || 'None ordered'}

Medications:
${patientData.therapeuticPlan?.medications?.map(med => 
  `- ${med.name} ${med.dosage} ${med.frequency} for ${med.duration}`
).join('\n') || 'None prescribed'}

Follow-up:
${patientData.therapeuticPlan?.followUp || 'Not specified'}

Patient Education:
${patientData.therapeuticPlan?.patientEducation || 'Not documented'}

Provider: [Provider Name]
Date: ${formatDate(new Date())}
`;
  };
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">SOAP Note Summary</h2>
          <p className="text-gray-600">Complete clinical documentation for this visit</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center"
          >
            <Printer className="w-4 h-4 mr-2" />
            Print
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </button>
        </div>
      </div>
      
      {/* Patient Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{patientData.name}</h3>
            <div className="flex items-center space-x-4 mt-2 text-gray-600">
              <span className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                {patientData.age} years, {patientData.gender}
              </span>
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {formatDate(new Date())}
              </span>
              <span className="flex items-center">
                <Heart className="w-4 h-4 mr-1" />
                {patientData.chiefComplaint}
              </span>
            </div>
          </div>
          <CheckCircle className="w-12 h-12 text-green-500" />
        </div>
      </div>
      
      {/* SOAP Sections */}
      <div className="space-y-6 print:space-y-4">
        {/* Subjective */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 print:shadow-none">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 text-blue-600 mr-2" />
            Subjective (S)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">History of Present Illness</h4>
              <p className="text-gray-600 whitespace-pre-wrap">
                {patientData.historyOfPresentIllness || 'Not documented'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Review of Systems</h4>
              <p className="text-gray-600 whitespace-pre-wrap">
                {patientData.reviewOfSystems || 'Not documented'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Past Medical History</h4>
              <p className="text-gray-600">
                {patientData.medicalHistory?.join(', ') || 'None reported'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Current Medications</h4>
              <p className="text-gray-600">
                {patientData.medications?.join(', ') || 'None'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Allergies</h4>
              <p className="text-gray-600">
                {patientData.allergies?.length > 0 ? (
                  <span className="text-red-600 font-medium">
                    {patientData.allergies.join(', ')}
                  </span>
                ) : 'NKDA'}
              </p>
            </div>
          </div>
        </div>
        
        {/* Objective */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 print:shadow-none">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Stethoscope className="w-5 h-5 text-green-600 mr-2" />
            Objective (O)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {patientData.physicalExam?.bloodPressure && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Blood Pressure</p>
                <p className="text-lg font-semibold">{patientData.physicalExam.bloodPressure}</p>
              </div>
            )}
            {patientData.physicalExam?.heartRate && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Heart Rate</p>
                <p className="text-lg font-semibold">{patientData.physicalExam.heartRate} bpm</p>
              </div>
            )}
            {patientData.physicalExam?.temperature && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">Temperature</p>
                <p className="text-lg font-semibold">{patientData.physicalExam.temperature}°C</p>
              </div>
            )}
            {patientData.physicalExam?.oxygenSaturation && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">O2 Saturation</p>
                <p className="text-lg font-semibold">{patientData.physicalExam.oxygenSaturation}%</p>
              </div>
            )}
          </div>
          {patientData.physicalExam?.additionalFindings && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Physical Examination Findings</h4>
              <p className="text-gray-600 whitespace-pre-wrap">
                {patientData.physicalExam.additionalFindings}
              </p>
            </div>
          )}
        </div>
        
        {/* Assessment */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 print:shadow-none">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 text-purple-600 mr-2" />
            Assessment (A)
          </h3>
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">Primary Diagnosis</h4>
            <p className="text-lg text-gray-900 font-medium">
              {patientData.doctorDiagnosis || 'Not documented'}
            </p>
          </div>
          {patientData.diagnosticNotes && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Clinical Reasoning</h4>
              <p className="text-gray-600 whitespace-pre-wrap">
                {patientData.diagnosticNotes}
              </p>
            </div>
          )}
        </div>
        
        {/* Plan */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 print:shadow-none">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <TestTube className="w-5 h-5 text-orange-600 mr-2" />
            Plan (P)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Diagnostic Tests</h4>
              {patientData.selectedTests?.length > 0 ? (
                <ul className="space-y-1">
                  {patientData.selectedTests.map((test, idx) => (
                    <li key={idx} className="text-gray-600">• {test.name}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">None ordered</p>
              )}
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Medications</h4>
              {patientData.therapeuticPlan?.medications?.length > 0 ? (
                <ul className="space-y-1">
                  {patientData.therapeuticPlan.medications.map((med, idx) => (
                    <li key={idx} className="text-gray-600">
                      • {med.name} {med.dosage} {med.frequency} for {med.duration}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">None prescribed</p>
              )}
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Follow-up</h4>
              <p className="text-gray-600">
                {patientData.therapeuticPlan?.followUp || 'Not specified'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Patient Education</h4>
              <p className="text-gray-600">
                {patientData.therapeuticPlan?.patientEducation || 'Not documented'}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Print Styles */}
      <style jsx>{`
        @media print {
          .print\\:shadow-none {
            box-shadow: none !important;
          }
          .print\\:space-y-4 > * + * {
            margin-top: 1rem !important;
          }
        }
      `}</style>
    </div>
  );
};

export default SOAPSummary;