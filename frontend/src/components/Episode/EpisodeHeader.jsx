import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Clock, Calendar, ChevronLeft, AlertCircle, Archive, 
  CheckCircle, Tag, User, Sparkles, MoreVertical, X, Check
} from 'lucide-react';
import { useEpisode } from '../../contexts/EpisodeContext';

const EpisodeHeader = ({ episode, patient }) => {
  const navigate = useNavigate();
  const { resolveEpisode } = useEpisode();
  const [showResolveDialog, setShowResolveDialog] = useState(false);
  const [showMoreOptions, setShowMoreOptions] = useState(false);
  
  const getStatusIcon = () => {
    switch (episode.status) {
      case 'active':
        return <Activity className="w-5 h-5" />;
      case 'resolved':
        return <CheckCircle className="w-5 h-5" />;
      case 'chronic-management':
        return <Archive className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };
  
  const getStatusGradient = () => {
    switch (episode.status) {
      case 'active':
        return 'from-green-500 to-green-600';
      case 'resolved':
        return 'from-gray-500 to-gray-600';
      case 'chronic-management':
        return 'from-blue-500 to-blue-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };
  
  const getStatusLabel = () => {
    switch (episode.status) {
      case 'active':
        return 'Active';
      case 'resolved':
        return 'Resolved';
      case 'chronic-management':
        return 'Chronic Management';
      default:
        return episode.status;
    }
  };
  
  const getDuration = () => {
    const start = new Date(episode.createdAt);
    const end = episode.resolvedAt ? new Date(episode.resolvedAt) : new Date();
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Started today';
    if (days === 1) return '1 day';
    return `${days} days`;
  };
  
  const handleResolveEpisode = () => {
    resolveEpisode(episode.id);
    setShowResolveDialog(false);
    navigate(`/patient/${patient.id}`);
  };  
  return (
    <>
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl">
        <div className="px-6 py-4">
          {/* Top Navigation */}
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate(`/patient/${patient.id}`)}
              className="inline-flex items-center text-white/80 hover:text-white transition-colors group"
            >
              <ChevronLeft className="w-5 h-5 mr-1 group-hover:-translate-x-1 transition-transform" />
              <span>Back to {patient.name}</span>
            </button>
            
            <div className="flex items-center space-x-3">
              {episode.status === 'active' && (
                <button
                  onClick={() => setShowResolveDialog(true)}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg transition-all duration-300 flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span className="font-medium">Mark as Resolved</span>
                </button>
              )}
              
              <div className="relative">
                <button
                  onClick={() => setShowMoreOptions(!showMoreOptions)}
                  className="p-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg transition-all"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
                
                {showMoreOptions && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-10">
                    <button className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                      <Archive className="w-4 h-4" />
                      <span>Archive Episode</span>
                    </button>
                    <button className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                      <Tag className="w-4 h-4" />
                      <span>Manage Tags</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Episode Information */}
          <div className="space-y-4">
            <div>
              <h1 className="text-3xl font-bold flex items-center">
                <Sparkles className="w-8 h-8 mr-3" />
                {episode.chiefComplaint}
              </h1>
              
              {/* Tags */}
              {episode.tags && episode.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {episode.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>            
            {/* Status and Meta Information */}
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <div className={`inline-flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r ${getStatusGradient()} rounded-full shadow-md`}>
                {getStatusIcon()}
                <span className="font-medium">{getStatusLabel()}</span>
              </div>
              
              <div className="flex items-center space-x-2 text-white/80">
                <Calendar className="w-4 h-4" />
                <span>Started {new Date(episode.createdAt).toLocaleDateString()}</span>
              </div>
              
              <div className="flex items-center space-x-2 text-white/80">
                <Clock className="w-4 h-4" />
                <span>Duration: {getDuration()}</span>
              </div>
              
              {episode.encounterCount > 0 && (
                <div className="flex items-center space-x-2 text-white/80">
                  <Activity className="w-4 h-4" />
                  <span>{episode.encounterCount} Encounters</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Resolve Episode Dialog */}
      {showResolveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Resolve Episode</h3>
              <button
                onClick={() => setShowResolveDialog(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to mark this episode as resolved? This action will close the episode 
              and prevent further documentation.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-900 mb-1">Before resolving:</p>
                  <ul className="text-blue-800 space-y-1">
                    <li>• Ensure all encounters are documented</li>
                    <li>• Verify treatment plans are complete</li>
                    <li>• Sign any pending encounters</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowResolveDialog(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleResolveEpisode}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Check className="w-5 h-5" />
                <span>Resolve Episode</span>
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Click outside to close more options */}
      {showMoreOptions && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setShowMoreOptions(false)}
        />
      )}
    </>
  );
};

export default EpisodeHeader;