import React from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { Save, Check } from 'lucide-react';

const AutoSaveIndicator = () => {
  const { lastSaved } = usePatient();
  
  if (!lastSaved) return null;
  
  const timeSinceLastSave = Date.now() - new Date(lastSaved).getTime();
  const isRecent = timeSinceLastSave < 5000; // Show for 5 seconds after save
  
  if (!isRecent) return null;
  
  return (
    <div className="fixed bottom-4 right-4 flex items-center bg-green-50 border border-green-200 rounded-lg px-4 py-2 shadow-lg animate-fade-in">
      <Check className="w-4 h-4 text-green-600 mr-2" />
      <span className="text-sm text-green-700">Session auto-saved</span>
    </div>
  );
};

export default AutoSaveIndicator;
