import React from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { CheckCircle, Circle } from 'lucide-react';

const SOAPProgress = () => {
  const { getOverallProgress, sectionProgress, currentSection } = useNavigation();
  const { currentEncounter } = useEncounter();
  const progress = getOverallProgress();
  
  const getSectionDetails = (sectionId) => {
    const encounter = currentEncounter?.soap || {};
    
    switch (sectionId) {
      case 'subjective': {
        const data = encounter.subjective || {};
        const filled = [
          data.hpi ? 1 : 0,
          data.ros && Object.values(data.ros).some(v => v) ? 1 : 0,
          (data.pmh || data.medications || data.allergies || data.socialHistory || data.familyHistory) ? 1 : 0
        ].reduce((a, b) => a + b, 0);
        return { filled, total: 3, subsections: ['HPI', 'Review of Systems', 'History'] };
      }
      case 'objective': {
        const data = encounter.objective || {};
        const filled = [
          data.vitals && Object.values(data.vitals).some(v => v) ? 1 : 0,
          (data.physicalExam?.general || data.physicalExam?.additionalFindings) ? 1 : 0,
          data.diagnosticTests?.ordered?.length > 0 ? 1 : 0
        ].reduce((a, b) => a + b, 0);
        return { filled, total: 3, subsections: ['Vitals', 'Physical Exam', 'Diagnostic Tests'] };
      }
      case 'assessment': {
        const data = encounter.assessment || {};
        const filled = [
          data.clinicalImpression ? 1 : 0,
          data.differentialDiagnosis?.length > 0 ? 1 : 0
        ].reduce((a, b) => a + b, 0);
        return { filled, total: 2, subsections: ['Clinical Impression', 'Differential Diagnosis'] };
      }
      case 'plan': {
        const data = encounter.plan || {};
        const filled = [
          data.medications?.length > 0 ? 1 : 0,
          data.procedures?.length > 0 ? 1 : 0,
          data.referrals?.length > 0 ? 1 : 0,
          data.followUp?.timeframe ? 1 : 0,
          data.patientEducation ? 1 : 0,
          data.activityDiet ? 1 : 0
        ].reduce((a, b) => a + b, 0);
        return { filled, total: 6, subsections: ['Medications', 'Procedures', 'Referrals', 'Follow-up', 'Education', 'Activity & Diet'] };
      }
      default:
        return { filled: 0, total: 0, subsections: [] };
    }
  };
  
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
  
  const getSectionStatus = (sectionId) => {
    const details = getSectionDetails(sectionId);
    if (details.filled === 0) return 'empty';
    if (details.filled === details.total) return 'complete';
    return 'partial';
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
            {sections.map((section) => {
              const details = getSectionDetails(section.id);
              const status = getSectionStatus(section.id);
              const isActive = currentSection === section.id;
              
              return (
                <div 
                  key={section.id}
                  className="relative group"
                >
                  <div className={`flex items-center justify-center w-10 h-10 bg-white rounded-full shadow-sm border-2 transition-all duration-300 group-hover:shadow-md ${
                    isActive ? 'border-blue-500' : 'border-gray-200'
                  }`}>
                    <span className="text-xs font-bold text-gray-700">{section.label}</span>
                  </div>
                  
                  {/* Section Counter */}
                  <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    status === 'complete' ? 'bg-green-500 text-white' : 
                    status === 'partial' ? 'bg-yellow-500 text-white' : 
                    'bg-gray-300 text-gray-600'
                  }`}>
                    {status === 'complete' ? '✓' : details.total - details.filled}
                  </div>
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                      <div className="font-semibold">{section.name}</div>
                      <div>{details.filled}/{details.total} sections completed</div>
                      {status !== 'complete' && (
                        <div className="mt-1 text-[11px]">{details.total - details.filled} remaining</div>
                      )}
                    </div>
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 -translate-y-1 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              );
            })}
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