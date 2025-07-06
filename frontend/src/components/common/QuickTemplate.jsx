import React, { useState } from 'react';
import { Sparkles, ChevronDown, Check } from 'lucide-react';
import { applyTemplate } from '../../utils/templates';

const QuickTemplate = ({ onApplyTemplate, currentChiefComplaint }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  
  const templates = [
    { key: 'upper-respiratory', label: 'Upper Respiratory Infection', tags: ['respiratory', 'acute'] },
    { key: 'hypertension-followup', label: 'Hypertension Follow-up', tags: ['chronic', 'cardiovascular'] },
    { key: 'diabetes-followup', label: 'Diabetes Follow-up', tags: ['chronic', 'endocrine'] },
    { key: 'acute-back-pain', label: 'Acute Back Pain', tags: ['musculoskeletal', 'acute'] }
  ];
  
  const handleApplyTemplate = (templateKey) => {
    const template = applyTemplate(templateKey);
    if (template) {
      onApplyTemplate(template);
      setSelectedTemplate(templateKey);
      setShowDropdown(false);
    }
  };
  
  const suggestedTemplate = templates.find(t => 
    currentChiefComplaint && 
    t.label.toLowerCase().includes(currentChiefComplaint.toLowerCase())
  );
  
  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="inline-flex items-center px-3 py-1.5 text-sm bg-purple-50 text-purple-700 hover:bg-purple-100 rounded-lg transition-colors"
      >
        <Sparkles className="w-4 h-4 mr-1.5" />
        Quick Template
        <ChevronDown className="w-4 h-4 ml-1" />
      </button>
      
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
          <div className="p-2">
            <p className="text-xs text-gray-500 px-2 py-1">Select a template to pre-fill common documentation</p>
            
            {suggestedTemplate && (
              <div className="mb-2 p-2 bg-purple-50 rounded">
                <p className="text-xs font-medium text-purple-700 mb-1">Suggested based on chief complaint:</p>
                <button
                  onClick={() => handleApplyTemplate(suggestedTemplate.key)}
                  className="w-full text-left p-2 hover:bg-purple-100 rounded transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-purple-900">{suggestedTemplate.label}</span>
                    <Sparkles className="w-4 h-4 text-purple-600" />
                  </div>
                </button>
              </div>
            )}
            
            <div className="space-y-1">
              {templates.map((template) => (
                <button
                  key={template.key}
                  onClick={() => handleApplyTemplate(template.key)}
                  className="w-full text-left p-2 hover:bg-gray-50 rounded transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{template.label}</div>
                      <div className="flex gap-1 mt-1">
                        {template.tags.map((tag, idx) => (
                          <span key={idx} className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    {selectedTemplate === template.key && (
                      <Check className="w-4 h-4 text-green-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
          
          <div className="border-t border-gray-200 p-2">
            <p className="text-xs text-gray-500 px-2">Templates can be customized after applying</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickTemplate;