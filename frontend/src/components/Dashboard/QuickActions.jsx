import React from 'react';
import { Plus, FolderOpen, Activity, Calendar } from 'lucide-react';

const QuickActions = ({ onNewEpisode, onViewAllRecords }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <button
        onClick={onNewEpisode}
        className="bg-white border-2 border-blue-200 rounded-lg p-4 hover:bg-blue-50 transition-colors group"
      >
        <div className="flex items-center justify-between mb-2">
          <Plus className="w-8 h-8 text-blue-600 group-hover:scale-110 transition-transform" />
          <span className="text-xs text-blue-600 font-medium">QUICK ACTION</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-900 text-left">New Episode</h3>
        <p className="text-xs text-gray-600 text-left mt-1">Start documenting a new health issue</p>
      </button>
      
      <button
        onClick={onViewAllRecords}
        className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors group"
      >
        <div className="flex items-center justify-between mb-2">
          <FolderOpen className="w-8 h-8 text-gray-600 group-hover:scale-110 transition-transform" />
          <span className="text-xs text-gray-500 font-medium">RECORDS</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-900 text-left">View All Records</h3>
        <p className="text-xs text-gray-600 text-left mt-1">Browse complete patient history</p>
      </button>
      
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <Activity className="w-8 h-8 text-green-600" />
          <span className="text-xs text-gray-500 font-medium">STATUS</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-900 text-left">Active Episodes</h3>
        <p className="text-2xl font-bold text-green-600 text-left mt-1">
          {/* This would be passed as a prop in a real implementation */}
          2
        </p>
      </div>
      
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <Calendar className="w-8 h-8 text-blue-600" />
          <span className="text-xs text-gray-500 font-medium">RECENT</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-900 text-left">Last Visit</h3>
        <p className="text-sm text-gray-600 text-left mt-1">
          {/* This would be calculated from actual data */}
          3 days ago
        </p>
      </div>
    </div>
  );
};

export default QuickActions;