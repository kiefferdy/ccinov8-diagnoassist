import React from 'react';
import { 
  Calendar, Clock, User, FileText, Edit3, CheckCircle, 
  Activity, Plus, Sparkles, ChevronRight, AlertCircle,
  Video, Phone, Stethoscope
} from 'lucide-react';

const EncounterList = ({ encounters, currentEncounter, onSelectEncounter }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };
  
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };
  
  const getEncounterTypeLabel = (type) => {
    const labels = {
      'initial': 'Initial Visit',
      'follow-up': 'Follow-up',
      'urgent': 'Urgent Visit',
      'telemedicine': 'Telemedicine',
      'phone': 'Phone Consult',
      'lab-review': 'Lab Review'
    };
    return labels[type] || type;
  };
  
  const getEncounterTypeIcon = (type) => {
    const icons = {
      'initial': Stethoscope,
      'follow-up': Activity,
      'urgent': AlertCircle,
      'telemedicine': Video,
      'phone': Phone,
      'lab-review': FileText
    };
    const Icon = icons[type] || FileText;
    return <Icon className="w-4 h-4" />;
  };
  
  const getEncounterTypeColor = (type) => {
    const colors = {
      'initial': 'from-blue-500 to-blue-600',
      'follow-up': 'from-green-500 to-green-600',
      'urgent': 'from-red-500 to-red-600',
      'telemedicine': 'from-purple-500 to-purple-600',
      'phone': 'from-yellow-500 to-yellow-600',
      'lab-review': 'from-gray-500 to-gray-600'
    };
    return colors[type] || 'from-gray-500 to-gray-600';
  };
  
  const getCompletionPercentage = (encounter) => {
    // Handle both backend completion_percentage and frontend calculation
    if (encounter.completionPercentage !== undefined) {
      return encounter.completionPercentage;
    }

    const { soap } = encounter;
    if (!soap) return 0;
    
    let completed = 0;
    const total = 4;
    
    // Check Subjective - more comprehensive check
    if (soap.subjective?.hpi || soap.subjective?.ros || soap.subjective?.chiefComplaint) completed += 1;
    
    // Check Objective - handle different data structures
    if (Object.values(soap.objective?.vitals || {}).some(v => v) || 
        soap.objective?.physicalExam?.general ||
        (soap.objective?.diagnosticTests?.ordered || []).length > 0) completed += 1;
    
    // Check Assessment
    if (soap.assessment?.clinicalImpression || 
        (soap.assessment?.differentialDiagnosis || []).length > 0 ||
        soap.assessment?.workingDiagnosis?.diagnosis) completed += 1;
    
    // Check Plan
    if ((soap.plan?.medications || []).length > 0 || 
        soap.plan?.followUp?.timeframe ||
        (soap.plan?.procedures || []).length > 0 ||
        (soap.plan?.patientEducation || []).length > 0) completed += 1;
    
    return Math.round((completed / total) * 100);
  };
  
  if (encounters.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-gray-400" />
        </div>
        <p className="text-gray-600 font-medium mb-2">No encounters yet</p>
        <p className="text-sm text-gray-500">Create your first encounter to begin documentation</p>
      </div>
    );
  }  
  return (
    <div className="divide-y divide-gray-100">
      {encounters.map((encounter, index) => {
        const isSelected = currentEncounter?.id === encounter.id;
        const isSigned = encounter.status === 'signed' || encounter.isSigned;
        const completionPercentage = getCompletionPercentage(encounter);
        const encounterDate = encounter.date || encounter.createdAt || new Date().toISOString();
        
        return (
          <button
            key={encounter.id}
            onClick={() => onSelectEncounter(encounter)}
            className={`
              w-full text-left p-4 transition-all duration-300 relative overflow-hidden group
              ${isSelected 
                ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 shadow-md' 
                : 'hover:bg-gray-50 hover:shadow-sm'
              }
            `}
          >
            {/* Background Animation */}
            <div className={`
              absolute inset-0 bg-gradient-to-r ${getEncounterTypeColor(encounter.type)} 
              opacity-0 group-hover:opacity-5 transition-opacity duration-300
            `} />
            
            {/* Encounter Header */}
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`
                    p-2 rounded-xl bg-gradient-to-r ${getEncounterTypeColor(encounter.type)}
                    text-white shadow-md ${isSelected ? 'animate-pulse' : ''}
                  `}>
                    {getEncounterTypeIcon(encounter.type)}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">
                      Encounter #{encounters.length - index}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {getEncounterTypeLabel(encounter.type)}
                    </p>
                  </div>
                </div>
                {isSigned && (
                  <div className="flex items-center space-x-1 bg-green-100 px-2 py-1 rounded-full">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                    <span className="text-xs font-medium text-green-700">
                      Signed
                      {encounter.signedBy && ` by ${encounter.signedBy}`}
                      {encounter.signed_by && !encounter.signedBy && ` by ${encounter.signed_by}`}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Date, Time and Provider */}
              <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
                <div className="flex items-center text-gray-600">
                  <Calendar className="w-3 h-3 mr-1.5 text-gray-400" />
                  {formatDate(encounterDate)}
                </div>
                <div className="flex items-center text-gray-600">
                  <Clock className="w-3 h-3 mr-1.5 text-gray-400" />
                  {formatTime(encounterDate)}
                </div>
                {(encounter.provider?.name || encounter.provider_name) && (
                  <div className="flex items-center text-gray-600 col-span-2">
                    <User className="w-3 h-3 mr-1.5 text-gray-400" />
                    {encounter.provider?.name || encounter.provider_name || 'Unknown Provider'}
                  </div>
                )}
              </div>              
              {/* Progress Indicator */}
              {!isSigned && (
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-600">Documentation Progress</span>
                    <span className="text-xs font-bold text-gray-900">{completionPercentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div 
                      className={`h-full bg-gradient-to-r transition-all duration-500 ease-out
                        ${completionPercentage === 100 
                          ? 'from-green-500 to-green-600' 
                          : completionPercentage >= 75 
                          ? 'from-blue-500 to-blue-600'
                          : completionPercentage >= 50
                          ? 'from-yellow-500 to-yellow-600'
                          : 'from-orange-500 to-red-500'
                        }
                      `}
                      style={{ width: `${completionPercentage}%` }}
                    />
                  </div>
                </div>
              )}
              
              {/* Hover Effect - View Indicator */}
              <div className={`
                absolute right-4 top-1/2 -translate-y-1/2 transition-all duration-300
                ${isSelected ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2 group-hover:opacity-100 group-hover:translate-x-0'}
              `}>
                <ChevronRight className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default EncounterList;