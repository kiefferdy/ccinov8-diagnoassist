import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Clock, 
  Activity, 
  ChevronRight, 
  FileText, 
  CheckCircle,
  AlertCircle,
  Link
} from 'lucide-react';

const EpisodeCard = ({ episode, encounters, patientId }) => {
  const navigate = useNavigate();
  
  // Get status color and icon
  const getStatusStyle = () => {
    switch (episode.status) {
      case 'active':
        return {
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          textColor: 'text-blue-700',
          icon: Activity
        };
      case 'resolved':
        return {
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-700',
          icon: CheckCircle
        };
      case 'chronic-management':
        return {
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          textColor: 'text-orange-700',
          icon: AlertCircle
        };
      default:
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-700',
          icon: Activity
        };
    }
  };

  const statusStyle = getStatusStyle();
  const StatusIcon = statusStyle.icon;
  const handleClick = () => {
    navigate(`/patient/${patientId}/episode/${episode.id}`);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDuration = () => {
    const start = new Date(episode.createdAt);
    const end = episode.resolvedAt ? new Date(episode.resolvedAt) : new Date();
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return '1 day';
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} years`;
  };

  const lastEncounter = encounters[0]; // Assumes encounters are sorted by date desc

  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border ${statusStyle.borderColor} p-6 hover:shadow-md transition-all cursor-pointer group`}
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start">
          <div className={`w-10 h-10 ${statusStyle.bgColor} rounded-lg flex items-center justify-center mr-3`}>
            <StatusIcon className={`w-5 h-5 ${statusStyle.textColor}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {episode.chiefComplaint}
            </h3>
            <div className="flex items-center text-sm text-gray-500">
              <Calendar className="w-4 h-4 mr-1" />
              <span>Started {formatDate(episode.createdAt)}</span>
              {episode.status === 'active' && (
                <>
                  <span className="mx-2">•</span>
                  <Clock className="w-4 h-4 mr-1" />
                  <span>{getDuration()}</span>
                </>
              )}
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
      </div>

      {/* Episode Info */}
      <div className="space-y-3">
        {/* Status Badge */}
        <div className="flex items-center justify-between">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyle.bgColor} ${statusStyle.textColor}`}>
            {episode.status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
          {episode.category && (
            <span className="text-xs text-gray-500">
              {episode.category.charAt(0).toUpperCase() + episode.category.slice(1)}
            </span>
          )}
        </div>

        {/* Encounters Summary */}
        <div className="flex items-center text-sm text-gray-600">
          <FileText className="w-4 h-4 mr-2" />
          <span>
            {encounters.length} encounter{encounters.length !== 1 ? 's' : ''}
            {lastEncounter && (
              <span className="text-gray-500">
                {' • Last visit: '}
                {formatDate(lastEncounter.date)}
              </span>
            )}
          </span>
        </div>

        {/* Related Episodes */}
        {episode.relatedEpisodeIds && episode.relatedEpisodeIds.length > 0 && (
          <div className="flex items-center text-sm text-blue-600">
            <Link className="w-4 h-4 mr-2" />
            <span>{episode.relatedEpisodeIds.length} related episode{episode.relatedEpisodeIds.length !== 1 ? 's' : ''}</span>
          </div>
        )}

        {/* Tags */}
        {episode.tags && episode.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {episode.tags.map((tag, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Quick Action */}
      {episode.status === 'active' && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <button 
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
            onClick={(e) => {
              e.stopPropagation();
              handleClick();
            }}
          >
            Continue Documentation →
          </button>
        </div>
      )}
    </div>
  );
};

export default EpisodeCard;