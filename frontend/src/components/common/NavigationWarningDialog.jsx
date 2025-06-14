import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

const NavigationWarningDialog = ({ isOpen, onClose, onConfirm, targetStep, currentStep }) => {
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex items-start mb-4">
            <div className="flex-shrink-0 mr-3">
              <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Unsaved Changes Detected
              </h3>
              <p className="text-sm text-gray-600">
                You have unsaved changes in <span className="font-medium">{getStepName(currentStep)}</span>.
              </p>
            </div>
            <button
              onClick={onClose}
              className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-amber-800">
              <strong>Warning:</strong> Going back to <span className="font-medium">{getStepName(targetStep)}</span> 
              and making changes will reset the progress for subsequent steps. Some data may be preserved:
            </p>
            <ul className="mt-2 text-sm text-amber-700 space-y-1">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Test results that have already been entered will be kept</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Previously selected tests will be retained if results exist</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Other step-specific data may need to be re-entered</span>
              </li>
            </ul>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Stay on Current Step
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 px-4 py-2.5 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 transition-colors"
            >
              Continue & Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavigationWarningDialog;