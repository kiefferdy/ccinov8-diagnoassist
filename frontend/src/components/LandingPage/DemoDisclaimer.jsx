import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, ArrowRight, X } from 'lucide-react';

const DemoDisclaimer = ({ onClose }) => {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(5);
  const [canProceed, setCanProceed] = useState(false);
  
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanProceed(true);
    }
  }, [countdown]);
  
  const handleProceed = () => {
    navigate('/');
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
        
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-yellow-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Demo Environment Notice
          </h2>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            You are about to enter the DiagnoAssist demo environment. Please note:
          </p>
          <ul className="text-left space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-yellow-500 mr-2 mt-1">•</span>
              <span>All patient data and diagnoses shown are <strong>hard-coded examples</strong> for demonstration purposes only</span>
            </li>
            <li className="flex items-start">
              <span className="text-yellow-500 mr-2 mt-1">•</span>
              <span>The AI diagnostic features are <strong>not yet functional</strong> - this is a preview of the interface and workflow</span>
            </li>
            <li className="flex items-start">
              <span className="text-yellow-500 mr-2 mt-1">•</span>
              <span>You can navigate through the interface to explore the planned features and user experience</span>
            </li>
            <li className="flex items-start">
              <span className="text-yellow-500 mr-2 mt-1">•</span>
              <span>The actual product will launch in <strong>Q3 2025</strong> with full AI capabilities</span>
            </li>
          </ul>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <strong>Why show a demo?</strong> We want to give healthcare professionals a preview of 
            how DiagnoAssist will streamline their workflow, even though the AI engine is still in development.
          </p>
        </div>
        
        <div className="flex justify-center space-x-4">
          <button
            onClick={onClose}
            className="px-6 py-3 text-gray-600 hover:text-gray-900 transition-colors"
          >
            Go Back
          </button>
          <button
            onClick={handleProceed}
            disabled={!canProceed}
            className={`px-8 py-3 rounded-lg font-semibold transition-all flex items-center ${
              canProceed
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {canProceed ? (
              <>
                Proceed to Demo
                <ArrowRight className="ml-2 w-5 h-5" />
              </>
            ) : (
              `Please wait ${countdown}s...`
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DemoDisclaimer;