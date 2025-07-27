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
      const subjectiveHasData = soap?.subjective?.hpi || soap?.subjective?.ros || 
        (soap?.subjective?.chiefComplaint && soap.subjective.chiefComplaint.trim());
      updateSectionProgress('subjective', subjectiveHasData ? 'partial' : 'empty');
      
      // Check Objective
      const objectiveHasData = 
        Object.values(soap?.objective?.vitals || {}).some(v => v) ||
        soap?.objective?.physicalExam?.general ||
        (soap?.objective?.diagnosticTests?.ordered || []).length > 0;
      updateSectionProgress('objective', objectiveHasData ? 'partial' : 'empty');
      
      // Check Assessment
      const assessmentHasData = 
        soap?.assessment?.clinicalImpression ||
        (soap?.assessment?.differentialDiagnosis || []).length > 0 ||
        soap?.assessment?.workingDiagnosis?.diagnosis;
      updateSectionProgress('assessment', assessmentHasData ? 'partial' : 'empty');
      
      // Check Plan
      const planHasData = 
        (soap?.plan?.medications || []).length > 0 ||
        (soap?.plan?.procedures || []).length > 0 ||
        soap?.plan?.followUp?.timeframe ||
        (soap?.plan?.patientEducation || []).length > 0;
      updateSectionProgress('plan', planHasData ? 'partial' : 'empty');
    };
    
    if (encounter?.soap) {
      checkSectionProgress();
    }
  }, [encounter, updateSectionProgress]);
  
  const handleSave = async () => {
    setSaving(true);
    try {
      await saveCurrentEncounter();
      if (window.showNotification) {
        window.showNotification('Encounter saved successfully', 'success');
      }
    } catch (error) {
      console.error('Failed to save encounter:', error);
      if (window.showNotification) {
        window.showNotification('Failed to save encounter', 'error');
      }
    }
    setSaving(false);
  };
  
  const handleSign = () => {
    // Check if all required sections have data
    const { soap } = encounter;
    
    const missingData = [];
    if (!soap.subjective?.hpi) missingData.push('History of Present Illness');
    if (!Object.values(soap.objective?.vitals || {}).some(v => v)) missingData.push('Vital Signs');
    if (!soap.assessment?.clinicalImpression) missingData.push('Clinical Assessment');
    if (!soap.plan?.followUp?.timeframe) missingData.push('Follow-up Plan');
    
    if (missingData.length > 0) {
      alert(`Please complete the following sections before signing:\n\n${missingData.join('\n')}`);
      return;
    }
    
    setShowSignDialog(true);
  };
  
  const confirmSign = async () => {
    try {
      setSaving(true);
      const providerName = encounter.provider?.name || patient.demographics?.name || 'Unknown Provider';
      const success = await signEncounter(encounter.id, providerName);
      
      if (success) {
        setShowSignDialog(false);
        if (window.showNotification) {
          window.showNotification('Encounter signed successfully', 'success');
        }
      } else {
        if (window.showNotification) {
          window.showNotification('Failed to sign encounter', 'error');
        }
      }
    } catch (error) {
      console.error('Error signing encounter:', error);
      if (window.showNotification) {
        window.showNotification('Failed to sign encounter', 'error');
      }
    } finally {
      setSaving(false);
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* SOAP Documentation */}
      <div className="flex-1 overflow-hidden">
        <SOAPContainer 
          encounter={encounter}
          episode={episode}
          patient={patient}
          onUpdate={updateCurrentEncounter}
          onSave={handleSave}
          onSign={handleSign}
          saving={saving}
          hasUnsavedChanges={hasUnsavedChanges}
          lastSaved={lastSaved}
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
            
            {/* Show encounter details */}
            <div className="bg-gray-50 rounded-lg p-3 mb-4 text-sm">
              <div className="flex justify-between items-center mb-1">
                <span className="text-gray-600">Provider:</span>
                <span className="font-medium">{encounter.provider?.name || 'Unknown Provider'}</span>
              </div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-gray-600">Date:</span>
                <span className="font-medium">{new Date(encounter.date).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Type:</span>
                <span className="font-medium capitalize">{encounter.type}</span>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowSignDialog(false)}
                disabled={saving}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmSign}
                disabled={saving}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
              >
                {saving && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                <span>{saving ? 'Signing...' : 'Sign Encounter'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncounterWorkspace;