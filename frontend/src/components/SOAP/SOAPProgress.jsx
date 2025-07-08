import React from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { CheckCircle, Circle, Loader } from 'lucide-react';

const SOAPProgress = () => {
  const { getOverallProgress, sectionProgress } = useNavigation();
  const progress = getOverallProgress();
  
  const sections = [
    { id: 'subjective', label: 'S', name: 'Subjective' },
    { id: 'objective', label: 'O', name: 'Objective' },
    { id: 'assessment', label: 'A', name: 'Assessment' },
    { id: 'plan', label: 'P', name: 'Plan' }
  ];
  
  const getProgressColor = (percentage) => {
    if (percentage === 100) return 'from-green-500 to-green-600';
    if (percentage >= 75) return 'from-blue-500 to-blue-600';
    if (percentage >= 50) return 'from-yellow-500 to-yellow-600';
    if (percentage >= 25) return 'from-orange-500 to-orange-600';
    return 'from-red-500 to-red-600';
  };
  
  const getSectionIcon = (status) => {
    if (status === 'complete') {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (status === 'partial') {
      return <Loader className="w-4 h-4 text-yellow-500 animate-spin" />;
    }
    return <Circle className="w-4 h-4 text-gray-300" />;
  };
  
  return (
    <div className="bg-gradient-to-r from-gray-50 to-blue-50 p-4">
      {/* Progress Stats */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-4">
          <div className="text-sm">
            <span className="text-gray-600">Documentation Progress</span>
            <div className="flex items-baseline space-x-1 mt-1">
              <span className="text-2xl font-bold text-gray-900">{progress.percentage}%</span>
              <span className="text-xs text-gray-500">Complete</span>
            </div>
          </div>
          
          {/* Section Icons */}
          <div className="flex items-center space-x-3 ml-6">
            {sections.map((section) => (
              <div 
                key={section.id}
                className="relative group"
              >
                <div className="flex items-center justify-center w-10 h-10 bg-white rounded-full shadow-sm border border-gray-200 transition-all duration-300 group-hover:shadow-md">
                  <span className="text-xs font-bold text-gray-700">{section.label}</span>
                </div>
                <div className="absolute -top-1 -right-1">
                  {getSectionIcon(sectionProgress[section.id])}
                </div>
                
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                  <div className="bg-gray-900 text-white text-xs rounded-lg px-2 py-1 whitespace-nowrap">
                    {section.name}: {sectionProgress[section.id] || 'Not started'}
                  </div>
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 -translate-y-1 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Completion Badge */}
        {progress.percentage === 100 && (
          <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-1.5 rounded-full animate-pulse">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Ready to Sign</span>
          </div>
        )}
      </div>
      
      {/* Modern Progress Bar */}
      <div className="relative">
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${getProgressColor(progress.percentage)} transition-all duration-500 ease-out relative overflow-hidden`}
            style={{ width: `${progress.percentage}%` }}
          >
            {/* Animated Shine Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
          </div>
        </div>
        
        {/* Progress Markers */}
        <div className="absolute inset-0 flex justify-between px-1">
          {[25, 50, 75].map((marker) => (
            <div 
              key={marker}
              className="w-0.5 h-3 bg-white/50"
              style={{ marginLeft: `${marker}%` }}
            />
          ))}
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="flex items-center justify-between mt-3 text-xs text-gray-600">
        <span>{progress.completed} of {progress.total} sections completed</span>
        <span>Last updated: {new Date().toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

export default SOAPProgress;