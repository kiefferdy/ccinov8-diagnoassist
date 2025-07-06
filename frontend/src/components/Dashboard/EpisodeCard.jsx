import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Calendar, Clock, ChevronRight, FileText, AlertCircle, CheckCircle } from 'lucide-react';

const EpisodeCard = ({ episode, encounters, patientId }) => {
  const navigate = useNavigate();
  
  const getStatusColor = () => {
    switch (episode.status) {
      case 'active':
        return 'border-green-200 bg-green-50';
      case 'resolved':
        return 'border-gray-200 bg-gray-50';
      case 'chronic-management':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };
  
  const getStatusBadge = () => {
    switch (episode.status) {
      case 'active':
        return { color: 'bg-green-100 text-green-800', icon: Activity };
      case 'resolved':
        return { color: 'bg-gray-100 text-gray-800', icon: CheckCircle };
      case 'chronic-management':
        return { color: 'bg-blue-100 text-blue-800', icon: Activity };
      default:
        return { color: 'bg-gray-100 text-gray-800', icon: Activity };
    }
  };
  
  const getDuration = () => {
    const start = new Date(episode.createdAt);
    const end = episode.resolvedAt ? new Date(episode.resolvedAt) : new Date();
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Started today';
    if (days === 1) return '1 day';
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} years`;
  };
  
  const lastEncounter = encounters[0];
  const statusBadge = getStatusBadge();
  const StatusIcon = statusBadge.icon;
  
  const handleClick = () => {
    navigate(`/patient/${patientId}/episode/${episode.id}`);
  };
  
  return (
    <div 
      className={`rounded-lg border-2 p-6 hover:shadow-md transition-all cursor-pointer ${getStatusColor()}`}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {episode.chiefComplaint}
          </h3>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge.color}`}>
              <StatusIcon className="w-3 h-3 mr-1" />
              {episode.status.replace('-', ' ')}
            </span>
            <span className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {getDuration()}
            </span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
      </div>
      
      {/* Episode Info */}
      <div className="space-y-2 text-sm">
        <div className="flex items-center text-gray-600">
          <Calendar className="w-4 h-4 mr-2" />
          Started: {new Date(episode.createdAt).toLocaleDateString()}
        </div>
        
        <div className="flex items-center text-gray-600">
          <FileText className="w-4 h-4 mr-2" />
          {encounters.length} encounter{encounters.length !== 1 ? 's' : ''}
        </div>
        
        {lastEncounter && (
          <div className="flex items-center text-gray-600">
            <Activity className="w-4 h-4 mr-2" />
            Last visit: {new Date(lastEncounter.date).toLocaleDateString()}
          </div>
        )}
      </div>
      
      {/* Tags */}
      {episode.tags && episode.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {episode.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-0.5 bg-white bg-opacity-70 text-gray-600 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
      
      {/* Quick Status Indicators */}
      <div className="flex items-center gap-4 mt-4 pt-4 border-t border-opacity-30">
        {encounters.some(e => e.status === 'draft') && (
          <div className="flex items-center text-amber-600 text-xs">
            <AlertCircle className="w-3 h-3 mr-1" />
            Draft encounter
          </div>
        )}
        {encounters.some(e => e.soap?.objective?.diagnosticTests?.ordered?.some(t => t.status === 'pending')) && (
          <div className="flex items-center text-blue-600 text-xs">
            <Clock className="w-3 h-3 mr-1" />
            Tests pending
          </div>
        )}
      </div>
    </div>
  );
};

export default EpisodeCard;