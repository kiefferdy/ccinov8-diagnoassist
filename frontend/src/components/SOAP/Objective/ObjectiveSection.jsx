import React, { useState } from 'react';
import { Activity, Stethoscope, FlaskConical, FileText } from 'lucide-react';

const ObjectiveSection = ({ data, patient, episode, encounter, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('vitals');
  
  const tabs = [
    { id: 'vitals', label: 'Vitals & Exam', icon: Stethoscope },
    { id: 'tests', label: 'Diagnostic Tests', icon: FlaskConical },
    { id: 'results', label: 'Test Results', icon: FileText }
  ];
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors
                    ${activeTab === tab.id
                      ? 'text-blue-600 border-blue-600'
                      : 'text-gray-500 border-transparent hover:text-gray-700'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          <p className="text-gray-600">Objective section - To be implemented</p>
        </div>
      </div>
    </div>
  );
};

export default ObjectiveSection;