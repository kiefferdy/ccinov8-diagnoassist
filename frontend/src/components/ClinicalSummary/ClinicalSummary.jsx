import React, { useState } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { useAppData } from '../../contexts/AppDataContext';
import { 
  ChevronLeft,
  Save,
  CheckCircle,
  Home
} from 'lucide-react';
import SOAPSummary from './SOAPSummary';

const ClinicalSummary = () => {
  const { patientData, setCurrentStep, sessionId, resetPatient } = usePatient();
  const { addRecord, deleteSession } = useAppData();
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  
  const handleSaveAndComplete = async () => {
    setIsSaving(true);
    
    try {
      // Create a complete patient record
      const record = {
        id: Date.now().toString(),
        patientId: patientData.id,
        date: new Date().toISOString(),
        chiefComplaint: patientData.chiefComplaint,
        historyOfPresentIllness: patientData.historyOfPresentIllness,
        reviewOfSystems: patientData.reviewOfSystems,
        pastMedicalHistory: patientData.pastMedicalHistory,
        socialHistory: patientData.socialHistory,
        familyHistory: patientData.familyHistory,
        medicalHistory: patientData.medicalHistory,
        medications: patientData.medications,
        allergies: patientData.allergies,
        physicalExam: patientData.physicalExam,
        doctorDiagnosis: patientData.doctorDiagnosis,
        diagnosticNotes: patientData.diagnosticNotes,
        finalDiagnosis: patientData.doctorDiagnosis || patientData.finalDiagnosis,
        icd10: patientData.icd10 || 'Z00.00',
        selectedTests: patientData.selectedTests,
        testsPerformed: patientData.selectedTests || [], // Add this for compatibility
        testResults: patientData.testResults,
        therapeuticPlan: patientData.therapeuticPlan,
        treatmentPlan: patientData.treatmentPlan || patientData.therapeuticPlan?.patientEducation,
        prescriptions: patientData.therapeuticPlan?.medications || [],
        followUp: patientData.therapeuticPlan?.followUp,
        clinicalSummary: generateSOAPSummaryText()
      };
      
      // Save the record
      addRecord(record);
      
      // Delete the session
      if (sessionId) {
        deleteSession(sessionId);
      }
      
      setSaved(true);
      setTimeout(() => {
        // Reset and go home
        resetPatient();
        setCurrentStep('home');
      }, 2000);
      
    } catch (error) {
      console.error('Error saving record:', error);
      alert('Error saving record. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };
  
  const generateSOAPSummaryText = () => {
    return `SOAP Note - ${new Date().toLocaleDateString()}
Patient: ${patientData.name}, ${patientData.age}y ${patientData.gender}
Chief Complaint: ${patientData.chiefComplaint}

S: ${patientData.historyOfPresentIllness || 'See detailed note'}
O: Vitals recorded. ${patientData.physicalExam?.additionalFindings || 'See exam details'}
A: ${patientData.doctorDiagnosis}
P: ${patientData.selectedTests?.length || 0} tests ordered, ${patientData.therapeuticPlan?.medications?.length || 0} medications prescribed`;
  };
  
  const handleBack = () => {
    setCurrentStep('treatment-plan');
  };
  
  const handleHome = () => {
    if (window.confirm('Are you sure? Any unsaved changes will be lost.')) {
      resetPatient();
      setCurrentStep('home');
    }
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Clinical Summary</h2>
          <p className="text-gray-600">Review the complete SOAP documentation before finalizing</p>
        </div>
        {saved && (
          <div className="flex items-center text-green-600">
            <CheckCircle className="w-6 h-6 mr-2" />
            <span className="font-medium">Visit saved successfully!</span>
          </div>
        )}
      </div>
      
      {/* SOAP Summary Component */}
      <SOAPSummary />
      
      {/* Action Buttons */}
      <div className="mt-8 flex justify-between items-center bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex space-x-3">
          <button
            onClick={handleBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
          >
            <ChevronLeft className="mr-2 w-5 h-5" />
            Back
          </button>
          <button
            onClick={handleHome}
            className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
          >
            <Home className="mr-2 w-5 h-5" />
            Exit Without Saving
          </button>
        </div>
        
        <button
          onClick={handleSaveAndComplete}
          disabled={isSaving || saved}
          className="px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-all flex items-center shadow-sm hover:shadow-md disabled:bg-gray-400"
        >
          {isSaving ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Saving...
            </>
          ) : saved ? (
            <>
              <CheckCircle className="mr-2 w-5 h-5" />
              Saved
            </>
          ) : (
            <>
              <Save className="mr-2 w-5 h-5" />
              Save & Complete Visit
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default ClinicalSummary;