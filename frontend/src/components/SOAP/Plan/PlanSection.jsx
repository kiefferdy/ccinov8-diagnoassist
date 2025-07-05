import React from 'react';
import { ClipboardList } from 'lucide-react';

const PlanSection = ({ data, patient, episode, encounter, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ClipboardList className="w-5 h-5 mr-2" />
          Treatment Plan
        </h3>
        <p className="text-gray-600">Plan section - To be implemented</p>
      </div>
    </div>
  );
};

export default PlanSection;