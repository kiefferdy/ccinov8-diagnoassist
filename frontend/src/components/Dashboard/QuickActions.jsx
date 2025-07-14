import React from 'react';
import { 
  Plus, FolderOpen, 
  FileText, Stethoscope, 
  Zap, ChevronRight, Sparkles,
  AlertCircle, Users, Star
} from 'lucide-react';

const QuickActions = ({ onNewEpisode, onViewAllRecords, onContinueCare, onQuickNote, stats = {}, quickNotesCount = 0 }) => {
  const quickActions = [
    {
      id: 'new-episode',
      title: 'New Episode',
      description: 'Start documenting a new health issue',
      icon: Plus,
      color: 'blue',
      bgGradient: 'from-blue-500 to-indigo-600',
      onClick: onNewEpisode,
      primary: true
    },
    {
      id: 'continue-care',
      title: 'Continue Care',
      description: 'Resume active episode documentation',
      icon: Stethoscope,
      color: 'purple',
      bgGradient: 'from-purple-500 to-pink-600',
      onClick: onContinueCare || (() => console.log('Continue care')),
      badge: stats.active > 0 ? stats.active : null
    },
    {
      id: 'view-records',
      title: 'All Records',
      description: 'Browse complete patient history',
      icon: FolderOpen,
      color: 'green',
      bgGradient: 'from-green-500 to-teal-600',
      onClick: onViewAllRecords
    },
    {
      id: 'quick-note',
      title: 'Quick Note',
      description: 'Add a quick clinical note',
      icon: FileText,
      color: 'orange',
      bgGradient: 'from-orange-500 to-red-600',
      onClick: onQuickNote || (() => console.log('Quick note')),
      badge: quickNotesCount > 0 ? quickNotesCount : null
    }
  ];

  return (
    <div className="space-y-6">
      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={action.onClick}
              className={`
                relative overflow-hidden group transition-all duration-300
                ${action.primary 
                  ? 'bg-gradient-to-br ' + action.bgGradient + ' text-white shadow-lg hover:shadow-xl transform hover:scale-105' 
                  : 'bg-white border-2 border-gray-200 hover:border-' + action.color + '-300 hover:shadow-lg'
                }
                rounded-2xl p-6
              `}
            >
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-white/20 blur-2xl" />
                <div className="absolute -left-8 -bottom-8 w-32 h-32 rounded-full bg-white/20 blur-2xl" />
              </div>
              
              {/* Content */}
              <div className="relative">
                <div className="flex items-start justify-between mb-4">
                  <div className={`
                    p-3 rounded-xl transition-all duration-300 group-hover:scale-110
                    ${action.primary 
                      ? 'bg-white/20 backdrop-blur-sm' 
                      : `bg-${action.color}-100 text-${action.color}-600`
                    }
                  `}>
                    <Icon className="w-6 h-6" />
                  </div>
                  {action.badge && (
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-bold
                      ${action.primary 
                        ? 'bg-white/20 text-white' 
                        : `bg-${action.color}-100 text-${action.color}-700`
                      }
                    `}>
                      {action.badge}
                    </span>
                  )}
                </div>
                
                <h3 className={`
                  text-lg font-bold text-left mb-1
                  ${action.primary ? 'text-white' : 'text-gray-900'}
                `}>
                  {action.title}
                </h3>
                <p className={`
                  text-sm text-left
                  ${action.primary ? 'text-white/80' : 'text-gray-600'}
                `}>
                  {action.description}
                </p>
                
                {/* Hover Arrow */}
                <div className={`
                  absolute bottom-4 right-4 transition-all duration-300 
                  opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0
                  ${action.primary ? 'text-white' : `text-${action.color}-600`}
                `}>
                  <ChevronRight className="w-5 h-5" />
                </div>
              </div>
              
              {/* Sparkle Effect for Primary */}
              {action.primary && (
                <Sparkles className="absolute top-4 right-4 w-5 h-5 text-white/50 animate-pulse" />
              )}
            </button>
          );
        })}
      </div>
      

      
      {/* Quick Insights */}
      {(stats.pendingTasks || stats.criticalAlerts) && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-lg mr-3">
                <Zap className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">Quick Insights</p>
                <p className="text-xs text-gray-600">
                  {stats.pendingTasks && `${stats.pendingTasks} pending tasks`}
                  {stats.pendingTasks && stats.criticalAlerts && ' • '}
                  {stats.criticalAlerts && `${stats.criticalAlerts} alerts`}
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </div>
        </div>
      )}
      
      {/* Favorites/Shortcuts */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700 flex items-center">
          <Star className="w-4 h-4 mr-1 text-yellow-500" />
          Quick Templates
        </h3>
        <div className="flex gap-2">
          {['URI', 'HTN Follow-up', 'Diabetes Check', 'Wellness'].map(template => (
            <button
              key={template}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-xs font-medium"
            >
              {template}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuickActions;