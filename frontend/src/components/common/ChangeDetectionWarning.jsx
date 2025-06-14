import React, { useEffect, useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

const ChangeDetectionWarning = ({ 
  isOpen, 
  onClose, 
  onContinue, 
  onSave,
  currentStep,
  affectsSteps 
}) => {
  if (!isOpen) return null;
  
  const getStepName = (step) => {
    const stepNames = {
      'patient-info': 'Patient Information',
      'clinical-assessment': 'Clinical Assessment',
      'physical-exam': 'Physical Exam',
      'diagnostic-analysis': 'Diagnostic Analysis',
      'recommended-tests': 'Recommended Tests',
      'test-results': 'Test Results',
      'final-diagnosis': 'Final Diagnosis'
    };
    return stepNames[step] || step;
  };
  
  return (
    <div className="fixed bottom-4 right-4 max-w-md w-full mx-4 z-50 animate-slide-up">
      <div className="bg-white rounded-xl shadow-2xl border-2 border-amber-400">
        <div className="p-5">
          <div className="flex items-start mb-3">
            <div className="flex-shrink-0 mr-3">
              <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-base font-semibold text-gray-900 mb-1">
                Changes Detected
              </h3>
              <p className="text-sm text-gray-600">
                You've made changes to <span className="font-medium">{getStepName(currentStep)}</span> 
                that will affect subsequent steps.
              </p>
            </div>
            <button
              onClick={onClose}
              className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
            <p className="text-xs text-amber-800 font-medium mb-1">
              Saving these changes will reset:
            </p>
            <ul className="text-xs text-amber-700 space-y-0.5">
              {affectsSteps.map(step => (
                <li key={step} className="flex items-center">
                  <span className="mr-2">•</span>
                  <span>{getStepName(step)}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={onContinue}
              className="flex-1 px-3 py-2 border border-gray-300 text-gray-700 font-medium text-sm rounded-lg hover:bg-gray-50 transition-colors"
            >
              Continue Without Saving
            </button>
            <button
              onClick={onSave}
              className="flex-1 px-3 py-2 bg-amber-600 text-white font-medium text-sm rounded-lg hover:bg-amber-700 transition-colors"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChangeDetectionWarning;