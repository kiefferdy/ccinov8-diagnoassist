import React from 'react';
import { Save, Check, Clock } from 'lucide-react';

const AutoSaveIndicator = ({ hasUnsavedChanges, lastSaved }) => {
  const formatLastSaved = () => {
    if (!lastSaved) return null;
    
    const date = new Date(lastSaved);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just saved';
    if (diffMins === 1) return '1 minute ago';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1 hour ago';
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    return date.toLocaleDateString();
  };
  
  return (
    <div className="flex items-center text-sm">
      {hasUnsavedChanges ? (
        <div className="flex items-center text-amber-600">
          <Save className="w-4 h-4 mr-1" />
          <span>Unsaved changes</span>
        </div>
      ) : lastSaved ? (
        <div className="flex items-center text-gray-500">
          <Check className="w-4 h-4 mr-1" />
          <span>Saved {formatLastSaved()}</span>
        </div>
      ) : (
        <div className="flex items-center text-gray-400">
          <Clock className="w-4 h-4 mr-1" />
          <span>No changes</span>
        </div>
      )}
    </div>
  );
};

export default AutoSaveIndicator;