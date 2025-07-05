import React from 'react';
import { Plus, Calendar, FileText, History } from 'lucide-react';

const QuickActions = ({ onNewEpisode, onViewAllRecords }) => {
  const actions = [
    {
      icon: Plus,
      label: 'New Episode',
      description: 'Start documenting a new health issue',
      onClick: onNewEpisode,
      color: 'blue',
      primary: true
    },
    {
      icon: Calendar,
      label: 'Schedule Follow-up',
      description: 'Plan next appointment',
      onClick: () => console.log('Schedule follow-up - to be implemented'),
      color: 'green'
    },
    {
      icon: FileText,
      label: 'View All Records',
      description: 'Complete patient history',
      onClick: onViewAllRecords,
      color: 'purple'
    },
    {
      icon: History,
      label: 'Timeline View',
      description: 'Visual health timeline',
      onClick: () => console.log('Timeline view - to be implemented'),
      color: 'gray'
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className={`
              p-4 rounded-lg border transition-all
              ${action.primary 
                ? 'bg-blue-50 border-blue-200 hover:bg-blue-100 hover:border-blue-300' 
                : 'bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
              }
            `}
          >
            <action.icon className={`
              w-6 h-6 mb-2 mx-auto
              ${action.primary ? 'text-blue-600' : 'text-gray-600'}
            `} />
            <p className={`text-sm font-medium ${action.primary ? 'text-blue-900' : 'text-gray-900'}`}>
              {action.label}
            </p>
            <p className="text-xs text-gray-500 mt-1">{action.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;