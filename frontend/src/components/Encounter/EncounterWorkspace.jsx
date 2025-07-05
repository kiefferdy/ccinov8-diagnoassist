import React, { useState, useEffect } from 'react';
import { useEncounter } from '../../contexts/EncounterContext';
import { useNavigation } from '../../contexts/NavigationContext';
import SOAPContainer from '../SOAP/SOAPContainer';
import AutoSaveIndicator from '../common/AutoSaveIndicator';
import { Save, CheckCircle, AlertCircle } from 'lucide-react';

const EncounterWorkspace = ({ encounter, episode, patient }) => {
  const { 
    updateCurrentEncounter, 
    saveCurrentEncounter, 
    signEncounter,
    hasUnsavedChanges,
    lastSaved 
  } = useEncounter();
  
  const { updateSectionProgress } = useNavigation();
  const [saving, setSaving] = useState(false);
  const [showSignDialog, setShowSignDialog] = useState(false);
  
  // Update section progress based on encounter data
  useEffect(() => {
    const checkSectionProgress = () => {
      const { soap } = encounter;
      
      // Check Subjective
      const subjectiveHasData = soap.subjective.hpi || soap.subjective.ros;
      updateSectionProgress('subjective', subjectiveHasData ? 'partial' : 'empty');
      
      // Check Objective
      const objectiveHasData = 
        Object.values(soap.objective.vitals).some(v => v) ||
        soap.objective.physicalExam.general ||
        soap.objective.diagnosticTests.ordered.length > 0;
      updateSectionProgress('objective', objectiveHasData ? 'partial' : 'empty');
      
      // Check Assessment
      const assessmentHasData = 
        soap.assessment.clinicalImpression ||
        soap.assessment.differentialDiagnosis.length > 0;
      updateSectionProgress('assessment', assessmentHasData ? 'partial' : 'empty');
      
      // Check Plan
      const planHasData = 
        soap.plan.medications.length > 0 ||
        soap.plan.procedures.length > 0 ||
        soap.plan.followUp.timeframe;
      updateSectionProgress('plan', planHasData ? 'partial' : 'empty');
    };
    
    checkSectionProgress();
  }, [encounter, updateSectionProgress]);
  
  const handleSave = async () => {
    setSaving(true);
    try {
      await saveCurrentEncounter();
    } catch (error) {
      console.error('Failed to save encounter:', error);
    }
    setSaving(false);
  };
  
  const handleSign = () => {
    // Check if all required sections have data
    const { soap } = encounter;
    
    const missingData = [];
    if (!soap.subjective.hpi) missingData.push('History of Present Illness');
    if (!Object.values(soap.objective.vitals).some(v => v)) missingData.push('Vital Signs');
    if (!soap.assessment.clinicalImpression) missingData.push('Clinical Assessment');
    if (!soap.plan.followUp.timeframe) missingData.push('Follow-up Plan');
    
    if (missingData.length > 0) {
      alert(`Please complete the following sections before signing:\n\n${missingData.join('\n')}`);
      return;
    }
    
    setShowSignDialog(true);
  };
  
  const confirmSign = () => {
    signEncounter(encounter.id, patient.demographics.name);
    setShowSignDialog(false);
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Encounter Documentation
            </h2>
            <AutoSaveIndicator 
              hasUnsavedChanges={hasUnsavedChanges}
              lastSaved={lastSaved}
            />
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleSave}
              disabled={!hasUnsavedChanges || saving}
              className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Save className="w-4 h-4 mr-1.5" />
              {saving ? 'Saving...' : 'Save'}
            </button>
            
            {encounter.status !== 'signed' && (
              <button
                onClick={handleSign}
                className="inline-flex items-center px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <CheckCircle className="w-4 h-4 mr-1.5" />
                Sign Encounter
              </button>
            )}
          </div>
        </div>
        
        {encounter.status === 'signed' && (
          <div className="mt-2 flex items-center text-sm text-green-700 bg-green-50 px-3 py-1 rounded-full w-fit">
            <CheckCircle className="w-4 h-4 mr-1.5" />
            Signed by {encounter.signedBy} on {new Date(encounter.signedAt).toLocaleString()}
          </div>
        )}
      </div>
      
      {/* SOAP Documentation */}
      <div className="flex-1 overflow-hidden">
        <SOAPContainer 
          encounter={encounter}
          episode={episode}
          patient={patient}
          onUpdate={updateCurrentEncounter}
        />
      </div>
      
      {/* Sign Confirmation Dialog */}
      {showSignDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Sign Encounter?</h3>
            <p className="text-gray-600 mb-4">
              Once signed, this encounter will be locked and cannot be edited. 
              Please ensure all information is accurate and complete.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowSignDialog(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmSign}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Sign Encounter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncounterWorkspace;