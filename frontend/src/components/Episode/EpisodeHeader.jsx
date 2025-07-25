import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Clock, Calendar, ChevronLeft, AlertCircle, Archive, 
  CheckCircle, Tag, User, Sparkles, MoreVertical, X, Check, Trash2
} from 'lucide-react';
import { useEpisode } from '../../contexts/EpisodeContext';

const EpisodeHeader = ({ episode, patient }) => {
  const navigate = useNavigate();
  const { resolveEpisode, updateEpisode, deleteEpisode } = useEpisode();
  const [showResolveDialog, setShowResolveDialog] = useState(false);
  const [showMoreOptions, setShowMoreOptions] = useState(false);
  const [showArchiveDialog, setShowArchiveDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showTagsModal, setShowTagsModal] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [episodeTags, setEpisodeTags] = useState(episode.tags || []);
  
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
  
  const handleArchiveEpisode = () => {
    updateEpisode(episode.id, { status: 'archived', archivedAt: new Date().toISOString() });
    setShowArchiveDialog(false);
    if (window.showNotification) {
      window.showNotification('Episode archived successfully', 'success');
    }
    navigate(`/patient/${patient.id}`);
  };

  const handleDeleteEpisode = async () => {
    try {
      console.log('Starting episode deletion...');
      await deleteEpisode(episode.id);
      setShowDeleteDialog(false);
      if (window.showNotification) {
        window.showNotification('Episode deleted successfully', 'success');
      }
      console.log('Navigating back to patient dashboard...');
      navigate(`/patient/${patient.id}`);
    } catch (error) {
      console.error('Delete episode failed:', error);
      setShowDeleteDialog(false);
      if (window.showNotification) {
        window.showNotification(`Failed to delete episode: ${error.message}`, 'error');
      }
      // Don't navigate away if delete failed
    }
  };
  
  const handleAddTag = () => {
    if (newTag.trim() && !episodeTags.includes(newTag.trim())) {
      const updatedTags = [...episodeTags, newTag.trim()];
      setEpisodeTags(updatedTags);
      updateEpisode(episode.id, { tags: updatedTags });
      setNewTag('');
      if (window.showNotification) {
        window.showNotification(`Tag "${newTag.trim()}" added successfully`, 'success');
      }
    }
  };
  
  const handleRemoveTag = (tagToRemove) => {
    const updatedTags = episodeTags.filter(tag => tag !== tagToRemove);
    setEpisodeTags(updatedTags);
    updateEpisode(episode.id, { tags: updatedTags });
    if (window.showNotification) {
      window.showNotification(`Tag "${tagToRemove}" removed`, 'info');
    }
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
                    <button 
                      onClick={() => {
                        setShowArchiveDialog(true);
                        setShowMoreOptions(false);
                      }}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <Archive className="w-4 h-4" />
                      <span>Archive Episode</span>
                    </button>
                    <button 
                      onClick={() => {
                        setShowTagsModal(true);
                        setShowMoreOptions(false);
                      }}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <Tag className="w-4 h-4" />
                      <span>Manage Tags</span>
                    </button>
                    <div className="border-t border-gray-200 my-1"></div>
                    <button 
                      onClick={() => {
                        setShowDeleteDialog(true);
                        setShowMoreOptions(false);
                      }}
                      className="w-full px-4 py-2 text-left text-red-700 hover:bg-red-50 flex items-center space-x-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>Delete Episode</span>
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
      
      {/* Archive Episode Dialog */}
      {showArchiveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Archive Episode</h3>
              <button
                onClick={() => setShowArchiveDialog(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-6">
              Archiving this episode will move it to the archived section. You can still view it but won't be able to add new encounters. The episode can be unarchived later if needed.
            </p>
            
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <Archive className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-amber-900 mb-1">Archive when:</p>
                  <ul className="text-amber-800 space-y-1">
                    <li>• Episode is no longer active but not resolved</li>
                    <li>• Patient moved or transferred care</li>
                    <li>• Need to declutter active episodes</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowArchiveDialog(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleArchiveEpisode}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-amber-600 to-amber-700 text-white rounded-lg hover:from-amber-700 hover:to-amber-800 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Archive className="w-5 h-5" />
                <span>Archive Episode</span>
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Delete Episode Dialog */}
      {showDeleteDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-red-900">Delete Episode</h3>
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to permanently delete this episode? This action cannot be undone and will remove all associated data including encounters and notes.
            </p>
            
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-red-900 mb-1">This will permanently delete:</p>
                  <ul className="text-red-800 space-y-1">
                    <li>• Episode record and all clinical notes</li>
                    <li>• All associated encounters and SOAP notes</li>
                    <li>• Any uploaded documents or attachments</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteEpisode}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Trash2 className="w-5 h-5" />
                <span>Delete Episode</span>
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Manage Tags Modal */}
      {showTagsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Manage Episode Tags</h3>
              <button
                onClick={() => setShowTagsModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">
              Add tags to help categorize and find this episode easily.
            </p>
            
            {/* Current Tags */}
            {episodeTags.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Current tags:</p>
                <div className="flex flex-wrap gap-2">
                  {episodeTags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      #{tag}
                      <button
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-2 hover:text-blue-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Add New Tag */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Add new tag:
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  placeholder="Enter tag name"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleAddTag}
                  disabled={!newTag.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
            
            {/* Suggested Tags */}
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 mb-2">Suggested tags:</p>
              <div className="flex flex-wrap gap-2">
                {['chronic', 'acute', 'follow-up', 'urgent', 'preventive', 'diagnostic'].map(tag => (
                  !episodeTags.includes(tag) && (
                    <button
                      key={tag}
                      onClick={() => {
                        setNewTag(tag);
                        handleAddTag();
                      }}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                    >
                      + {tag}
                    </button>
                  )
                ))}
              </div>
            </div>
            
            <button
              onClick={() => setShowTagsModal(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Done
            </button>
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