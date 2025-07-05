import React from 'react';
import { Calendar, Clock, User, FileText, Edit3, CheckCircle } from 'lucide-react';

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
  
  const getEncounterTypeColor = (type) => {
    const colors = {
      'initial': 'bg-blue-100 text-blue-700',
      'follow-up': 'bg-green-100 text-green-700',
      'urgent': 'bg-red-100 text-red-700',
      'telemedicine': 'bg-purple-100 text-purple-700',
      'phone': 'bg-yellow-100 text-yellow-700',
      'lab-review': 'bg-gray-100 text-gray-700'
    };
    return colors[type] || 'bg-gray-100 text-gray-700';
  };
  
  if (encounters.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <FileText className="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <p className="text-sm">No encounters yet</p>
      </div>
    );
  }
  
  return (
    <div className="divide-y divide-gray-200">
      {encounters.map((encounter, index) => {
        const isSelected = currentEncounter?.id === encounter.id;
        const isSigned = encounter.status === 'signed';
        
        return (
          <button
            key={encounter.id}
            onClick={() => onSelectEncounter(encounter)}
            className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
              isSelected ? 'bg-blue-50 border-l-4 border-blue-600' : ''
            }`}
          >
            {/* Encounter Number and Type */}
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Encounter #{encounters.length - index}
                </p>
                <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full ${getEncounterTypeColor(encounter.type)}`}>
                  {getEncounterTypeLabel(encounter.type)}
                </span>
              </div>
              {isSigned && (
                <CheckCircle className="w-4 h-4 text-green-600" title="Signed" />
              )}
            </div>
            
            {/* Date and Time */}
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex items-center">
                <Calendar className="w-3 h-3 mr-1" />
                {formatDate(encounter.date)}
              </div>
              <div className="flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {formatTime(encounter.date)}
              </div>
              {encounter.provider && (
                <div className="flex items-center">
                  <User className="w-3 h-3 mr-1" />
                  {encounter.provider.name}
                </div>
              )}
            </div>
            
            {/* Status Indicator */}
            {!isSigned && (
              <div className="mt-2 flex items-center text-xs text-amber-600">
                <Edit3 className="w-3 h-3 mr-1" />
                Draft
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default EncounterList;