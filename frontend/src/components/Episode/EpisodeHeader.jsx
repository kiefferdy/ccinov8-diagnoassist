import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Clock, Calendar, ChevronLeft, AlertCircle, Archive, CheckCircle } from 'lucide-react';
import { useEpisode } from '../../contexts/EpisodeContext';

const EpisodeHeader = ({ episode, patient }) => {
  const navigate = useNavigate();
  const { resolveEpisode } = useEpisode();
  
  const getStatusIcon = () => {
    switch (episode.status) {
      case 'active':
        return <Activity className="w-5 h-5 text-green-600" />;
      case 'resolved':
        return <CheckCircle className="w-5 h-5 text-gray-600" />;
      case 'chronic-management':
        return <Archive className="w-5 h-5 text-blue-600" />;
      default:
        return <Activity className="w-5 h-5 text-gray-600" />;
    }
  };
  
  const getStatusColor = () => {
    switch (episode.status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'resolved':
        return 'bg-gray-100 text-gray-800';
      case 'chronic-management':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
    if (window.confirm('Are you sure you want to mark this episode as resolved?')) {
      resolveEpisode(episode.id);
      navigate(`/patient/${patient.id}`);
    }
  };
  
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate(`/patient/${patient.id}`)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            Back to {patient.demographics.name}
          </button>
          
          {episode.status === 'active' && (
            <button
              onClick={handleResolveEpisode}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Mark as Resolved
            </button>
          )}
        </div>
        
        {/* Episode Info */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {episode.chiefComplaint}
            </h1>
            
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center">
                {getStatusIcon()}
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor()}`}>
                  {episode.status.replace('-', ' ')}
                </span>
              </div>
              
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                Started {new Date(episode.createdAt).toLocaleDateString()}
              </div>
              
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {getDuration()}
              </div>
            </div>
            
            {/* Tags */}
            {episode.tags && episode.tags.length > 0 && (
              <div className="flex gap-2 mt-3">
                {episode.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
          
          {/* Patient Allergies Alert */}
          {patient.medicalBackground?.allergies?.length > 0 && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 max-w-xs">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5 mr-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-orange-800">Allergies</p>
                  <p className="text-sm text-orange-700 mt-1">
                    {patient.medicalBackground.allergies.map(a => a.allergen).join(', ')}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EpisodeHeader;