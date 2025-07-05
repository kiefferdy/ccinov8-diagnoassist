import React from 'react';
import { Brain } from 'lucide-react';

const AssessmentSection = ({ data, patient, episode, encounter, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2" />
          Clinical Assessment
        </h3>
        <p className="text-gray-600">Assessment section - To be implemented</p>
      </div>
    </div>
  );
};

export default AssessmentSection;