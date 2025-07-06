import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, Clock, FileText, ChevronRight, AlertCircle, 
  CheckCircle, Activity, Tag, User, Stethoscope,
  TrendingUp, Heart, Brain, Pill
} from 'lucide-react';

const EpisodeCard = ({ episode, encounters = [], patientId }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(`/patient/${patientId}/episode/${episode.id}`);
  };
  
  // Calculate episode duration
  const calculateDuration = () => {
    const start = new Date(episode.createdAt);
    const end = episode.resolvedAt ? new Date(episode.resolvedAt) : new Date();
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return '1 day';
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} years`;
  };
  
  // Get status config
  const getStatusConfig = () => {
    const configs = {
      active: {
        color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        icon: Activity,
        label: 'Active',
        borderColor: 'border-l-emerald-500',
        bgGradient: 'from-emerald-50 to-green-50'
      },
      resolved: {
        color: 'bg-gray-100 text-gray-600 border-gray-200',
        icon: CheckCircle,
        label: 'Resolved',
        borderColor: 'border-l-gray-400',
        bgGradient: 'from-gray-50 to-slate-50'
      },
      'chronic-management': {
        color: 'bg-amber-100 text-amber-800 border-amber-200',
        icon: TrendingUp,
        label: 'Chronic',
        borderColor: 'border-l-amber-500',
        bgGradient: 'from-amber-50 to-orange-50'
      }
    };
    
    return configs[episode.status] || configs.active;
  };
  
  // Get category icon
  const getCategoryIcon = () => {
    const icons = {
      acute: { icon: AlertCircle, color: 'text-red-500' },
      chronic: { icon: Heart, color: 'text-purple-500' },
      preventive: { icon: Stethoscope, color: 'text-blue-500' },
      'follow-up': { icon: FileText, color: 'text-green-500' }
    };
    
    return icons[episode.category] || icons.acute;
  };
  
  const statusConfig = getStatusConfig();
  const categoryIcon = getCategoryIcon();
  const StatusIcon = statusConfig.icon;
  const CategoryIcon = categoryIcon.icon;
  
  // Get last encounter info
  const lastEncounter = encounters[0];
  const totalEncounters = encounters.length;
  
  // Check if urgent
  const isUrgent = episode.tags?.includes('urgent');
  
  return (
    <div
      onClick={handleClick}
      className={`
        relative bg-white rounded-2xl shadow-lg hover:shadow-xl 
        transition-all duration-300 cursor-pointer overflow-hidden
        border-l-4 ${statusConfig.borderColor} group
        transform hover:scale-[1.02] hover:-translate-y-1
      `}
    >
      {/* Background Gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${statusConfig.bgGradient} opacity-30`} />
      
      {/* Content */}
      <div className="relative p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <CategoryIcon className={`w-5 h-5 ${categoryIcon.color}`} />
              <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-1">
                {episode.chiefComplaint}
              </h3>
            </div>
            
            {/* Status Badge */}
            <div className="flex items-center space-x-2">
              <span className={`
                inline-flex items-center px-3 py-1 rounded-full text-xs font-medium
                ${statusConfig.color} border
              `}>
                <StatusIcon className="w-3 h-3 mr-1" />
                {statusConfig.label}
              </span>
              
              {isUrgent && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                  <AlertCircle className="w-3 h-3 mr-1" />
                  Urgent
                </span>
              )}
            </div>
          </div>
          
          <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors transform group-hover:translate-x-1" />
        </div>
        
        {/* Episode Info */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white/70 rounded-lg p-3 border border-gray-100">
            <div className="flex items-center space-x-2 text-gray-600 mb-1">
              <Calendar className="w-4 h-4" />
              <span className="text-xs font-medium">Started</span>
            </div>
            <p className="text-sm font-semibold text-gray-900">
              {new Date(episode.createdAt).toLocaleDateString()}
            </p>
          </div>
          
          <div className="bg-white/70 rounded-lg p-3 border border-gray-100">
            <div className="flex items-center space-x-2 text-gray-600 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Duration</span>
            </div>
            <p className="text-sm font-semibold text-gray-900">
              {calculateDuration()}
            </p>
          </div>
        </div>
        
        {/* Encounters Summary */}
        <div className="bg-blue-50/50 rounded-lg p-4 mb-4 border border-blue-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">
                  {totalEncounters} Encounter{totalEncounters !== 1 ? 's' : ''}
                </p>
                {lastEncounter && (
                  <p className="text-xs text-gray-600">
                    Last: {new Date(lastEncounter.date).toLocaleDateString()} - {lastEncounter.type}
                  </p>
                )}
              </div>
            </div>
            
            {lastEncounter && (
              <div className={`
                px-2 py-1 rounded-full text-xs font-medium
                ${lastEncounter.status === 'signed' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-yellow-100 text-yellow-700'}
              `}>
                {lastEncounter.status === 'signed' ? 'Signed' : 'Draft'}
              </div>
            )}
          </div>
        </div>
        
        {/* Tags */}
        {episode.tags && episode.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {episode.tags.filter(tag => tag !== 'urgent').map((tag, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200"
              >
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
          </div>
        )}
        
        {/* Last Provider */}
        {lastEncounter?.provider && (
          <div className="flex items-center text-xs text-gray-600">
            <User className="w-3 h-3 mr-1" />
            <span>Last seen by {lastEncounter.provider.name}</span>
          </div>
        )}
        
        {/* Quick Stats */}
        {episode.status === 'active' && (
          <div className="absolute bottom-2 right-2">
            <div className="flex space-x-1">
              {encounters.some(e => e.soap?.objective?.diagnosticTests?.ordered?.length > 0) && (
                <div className="p-1.5 bg-purple-100 rounded-lg" title="Has pending tests">
                  <Brain className="w-3 h-3 text-purple-600" />
                </div>
              )}
              {encounters.some(e => e.soap?.plan?.medications?.length > 0) && (
                <div className="p-1.5 bg-green-100 rounded-lg" title="Medications prescribed">
                  <Pill className="w-3 h-3 text-green-600" />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Hover Effect Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/0 to-indigo-600/0 group-hover:from-blue-600/5 group-hover:to-indigo-600/5 transition-all duration-300 pointer-events-none" />
    </div>
  );
};

export default EpisodeCard;