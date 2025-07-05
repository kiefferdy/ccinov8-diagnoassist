import React from 'react';
import { useNavigation } from '../../contexts/NavigationContext';

const SOAPProgress = () => {
  const { getOverallProgress } = useNavigation();
  const progress = getOverallProgress();
  
  return (
    <div className="px-6 pb-2">
      <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
        <span>Documentation Progress</span>
        <span>{progress.percentage}% Complete</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress.percentage}%` }}
        />
      </div>
    </div>
  );
};

export default SOAPProgress;