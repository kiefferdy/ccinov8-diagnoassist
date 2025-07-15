import React, { useState } from 'react';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useNavigate } from 'react-router-dom';
import { 
  X, AlertCircle, ChevronDown, Search, Sparkles, 
  Clock, TrendingUp, Heart, Brain, Stethoscope, 
  Tag, Plus, AlertTriangle, Activity, Calendar,
  Shield, Zap, Info, CheckCircle, ChevronRight
} from 'lucide-react';

const NewEpisodeModal = ({ patientId, onClose, onSuccess }) => {
  const navigate = useNavigate();
  const { createEpisode } = useEpisode();
  
  const [formData, setFormData] = useState({
    chiefComplaint: '',
    category: 'acute',
    tags: [],
    urgency: 'normal',
    createEncounter: true
  });
  
  const [customTag, setCustomTag] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAISuggestions, setShowAISuggestions] = useState(false);

  // Categorized common complaints
  const complaintCategories = {
    'Common Urgent': {
      icon: AlertTriangle,
      color: 'red',
      complaints: ['Chest pain', 'Shortness of breath', 'Severe headache', 'Abdominal pain (severe)']
    },
    'Respiratory': {
      icon: Wind,
      color: 'blue',
      complaints: ['Cough', 'Sore throat', 'Nasal congestion', 'Wheezing']
    },
    'Neurological': {
      icon: Brain,
      color: 'purple',
      complaints: ['Headache', 'Dizziness', 'Numbness/Tingling', 'Memory problems']
    },
    'Musculoskeletal': {
      icon: Activity,
      color: 'green',
      complaints: ['Back pain', 'Joint pain', 'Muscle pain', 'Sports injury']
    },
    'Gastrointestinal': {
      icon: Shield,
      color: 'orange',
      complaints: ['Nausea/Vomiting', 'Diarrhea', 'Constipation', 'Heartburn']
    },
    'General': {
      icon: Heart,
      color: 'pink',
      complaints: ['Fatigue', 'Fever', 'Weight loss', 'General check-up']
    }
  };

  const categoryOptions = [
    { 
      value: 'acute', 
      label: 'Acute', 
      description: 'New or sudden onset',
      icon: Zap,
      color: 'red'
    },
    { 
      value: 'chronic', 
      label: 'Chronic', 
      description: 'Ongoing management',
      icon: Clock,
      color: 'blue'
    },
    { 
      value: 'preventive', 
      label: 'Preventive', 
      description: 'Routine check-up',
      icon: Shield,
      color: 'green'
    },
    { 
      value: 'follow-up', 
      label: 'Follow-up', 
      description: 'Related to previous',
      icon: Calendar,
      color: 'purple'
    }
  ];

  const urgencyLevels = [
    { value: 'normal', label: 'Normal', color: 'green' },
    { value: 'urgent', label: 'Urgent', color: 'orange' },
    { value: 'emergency', label: 'Emergency', color: 'red' }
  ];

  const systemTags = {
    'Body Systems': [
      { value: 'cardiovascular', icon: Heart, color: 'red' },
      { value: 'respiratory', icon: Wind, color: 'blue' },
      { value: 'neurological', icon: Brain, color: 'purple' },
      { value: 'gastrointestinal', icon: Shield, color: 'orange' },
      { value: 'musculoskeletal', icon: Activity, color: 'green' },
      { value: 'endocrine', icon: Activity, color: 'indigo' },
      { value: 'genitourinary', icon: Shield, color: 'pink' },
      { value: 'dermatological', icon: Shield, color: 'yellow' }
    ],
    'Clinical Context': [
      { value: 'infectious', icon: AlertTriangle, color: 'red' },
      { value: 'trauma', icon: AlertCircle, color: 'orange' },
      { value: 'mental-health', icon: Brain, color: 'purple' },
      { value: 'pediatric', icon: Heart, color: 'pink' },
      { value: 'geriatric', icon: Clock, color: 'gray' }
    ]
  };

  // Filter complaints based on search
  const filteredComplaints = searchTerm
    ? Object.entries(complaintCategories).reduce((acc, [category, data]) => {
        const filtered = data.complaints.filter(complaint =>
          complaint.toLowerCase().includes(searchTerm.toLowerCase())
        );
        if (filtered.length > 0) {
          acc[category] = { ...data, complaints: filtered };
        }
        return acc;
      }, {})
    : complaintCategories;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.chiefComplaint.trim()) {
      setError('Chief complaint is required');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const newEpisode = createEpisode(patientId, {
        chiefComplaint: formData.chiefComplaint.trim(),
        category: formData.category,
        tags: [...formData.tags, formData.urgency !== 'normal' ? formData.urgency : null].filter(Boolean)
      });
      
      if (formData.createEncounter) {
        navigate(`/patient/${patientId}/episode/${newEpisode.id}`);
      } else {
        onSuccess(newEpisode);
      }
    } catch {
      setError('Failed to create episode. Please try again.');
      setLoading(false);
    }
  };

  const handleAddTag = (tag) => {
    if (!formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleAddCustomTag = () => {
    if (customTag.trim() && !formData.tags.includes(customTag.trim())) {
      handleAddTag(customTag.trim().toLowerCase());
      setCustomTag('');
    }
  };

  const generateAISuggestions = () => {
    // Simulate AI suggestions based on chief complaint
    const complaint = formData.chiefComplaint.toLowerCase();
    const suggestions = [];
    
    if (complaint.includes('chest')) {
      suggestions.push('Consider cardiac workup', 'Rule out PE', 'Check for GERD');
    } else if (complaint.includes('headache')) {
      suggestions.push('Assess for migraine features', 'Check blood pressure', 'Neurological exam');
    }
    
    return suggestions;
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold flex items-center">
                <Plus className="w-7 h-7 mr-2" />
                New Clinical Episode
              </h2>
              <p className="text-blue-100 mt-1">Start documenting a new patient concern</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col h-full">
          <div className="p-6 space-y-6 overflow-y-auto flex-1" style={{ maxHeight: 'calc(90vh - 240px)' }}>
          {/* Chief Complaint */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Chief Complaint <span className="text-red-500">*</span>
            </label>
            
            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search common complaints..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Custom Input */}
            <input
              type="text"
              value={formData.chiefComplaint}
              onChange={(e) => setFormData(prev => ({ ...prev, chiefComplaint: e.target.value }))}
              placeholder="Or type a custom chief complaint..."
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              autoFocus
            />

            {/* Common Complaints Grid */}
            <div className="mt-4 space-y-3">
              {Object.entries(filteredComplaints).map(([category, data]) => {
                const Icon = data.icon;
                return (
                  <div key={category} className="bg-gray-50 rounded-xl p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <Icon className={`w-4 h-4 mr-2 text-${data.color}-500`} />
                      {category}
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {data.complaints.map((complaint) => (
                        <button
                          key={complaint}
                          type="button"
                          onClick={() => setFormData(prev => ({ ...prev, chiefComplaint: complaint }))}
                          className={`text-sm px-3 py-2 rounded-lg transition-all ${
                            formData.chiefComplaint === complaint
                              ? `bg-${data.color}-100 text-${data.color}-700 border-2 border-${data.color}-300`
                              : 'bg-white border border-gray-200 hover:bg-gray-100'
                          }`}
                        >
                          {complaint}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Urgency Level */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Urgency Level
            </label>
            <div className="grid grid-cols-3 gap-3">
              {urgencyLevels.map((level) => (
                <button
                  key={level.value}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, urgency: level.value }))}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    formData.urgency === level.value
                      ? `bg-${level.color}-50 border-${level.color}-500 text-${level.color}-700`
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <AlertCircle className={`w-5 h-5 mx-auto mb-2 ${
                    formData.urgency === level.value ? `text-${level.color}-500` : 'text-gray-400'
                  }`} />
                  <p className="font-medium">{level.label}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Episode Type
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {categoryOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, category: option.value }))}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.category === option.value
                        ? `bg-${option.color}-50 border-${option.color}-500`
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`w-6 h-6 mx-auto mb-2 ${
                      formData.category === option.value ? `text-${option.color}-600` : 'text-gray-400'
                    }`} />
                    <p className={`font-medium ${
                      formData.category === option.value ? `text-${option.color}-700` : 'text-gray-700'
                    }`}>{option.label}</p>
                    <p className="text-xs text-gray-500 mt-1">{option.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-3">
              Clinical Tags
            </label>
            
            {/* Selected Tags */}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4 p-3 bg-blue-50 rounded-xl">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1.5 rounded-full text-sm bg-blue-100 text-blue-700 border border-blue-200"
                  >
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
            
            {/* Tag Categories */}
            {Object.entries(systemTags).map(([category, tags]) => (
              <div key={category} className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2">{category}</h5>
                <div className="flex flex-wrap gap-2">
                  {tags.filter(tag => !formData.tags.includes(tag.value)).map((tag) => {
                    const Icon = tag.icon;
                    return (
                      <button
                        key={tag.value}
                        type="button"
                        onClick={() => handleAddTag(tag.value)}
                        className={`inline-flex items-center px-3 py-1.5 bg-${tag.color}-50 text-${tag.color}-700 border border-${tag.color}-200 rounded-lg hover:bg-${tag.color}-100 transition-colors text-sm`}
                      >
                        <Icon className="w-3 h-3 mr-1" />
                        <Plus className="w-3 h-3 mr-1" />
                        {tag.value}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
            
            {/* Custom Tag Input */}
            <div className="flex gap-2 mt-4">
              <input
                type="text"
                value={customTag}
                onChange={(e) => setCustomTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTag())}
                placeholder="Add custom tag..."
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={handleAddCustomTag}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium"
              >
                Add Tag
              </button>
            </div>
          </div>

          {/* AI Suggestions */}
          {formData.chiefComplaint && (
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-4 border border-purple-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-purple-900 flex items-center">
                  <Sparkles className="w-4 h-4 mr-2" />
                  AI Clinical Suggestions
                </h4>
                <button
                  type="button"
                  onClick={() => setShowAISuggestions(!showAISuggestions)}
                  className="text-sm text-purple-600 hover:text-purple-700"
                >
                  {showAISuggestions ? 'Hide' : 'Show'}
                </button>
              </div>
              {showAISuggestions && (
                <div className="space-y-2 mt-3">
                  {generateAISuggestions().map((suggestion, idx) => (
                    <div key={idx} className="flex items-start">
                      <ChevronRight className="w-4 h-4 text-purple-500 mt-0.5 mr-2 flex-shrink-0" />
                      <p className="text-sm text-purple-800">{suggestion}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Create Encounter Option */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={formData.createEncounter}
                onChange={(e) => setFormData(prev => ({ ...prev, createEncounter: e.target.checked }))}
                className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div className="ml-3">
                <p className="font-medium text-gray-900">Start documentation immediately</p>
                <p className="text-sm text-gray-600 mt-1">
                  Create the first encounter and begin SOAP documentation right away
                </p>
              </div>
            </label>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-xl">
              <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          </div>

          {/* Actions */}
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            <div className="flex justify-between items-center">
              <button
                type="button"
                className="text-gray-500 hover:text-gray-700 flex items-center"
              >
                <Info className="w-4 h-4 mr-1" />
                <span className="text-sm">Help</span>
              </button>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.chiefComplaint.trim()}
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Create Episode
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// Add missing icon import
const Wind = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5a2 2 0 110-4h5m9-4h1a2 2 0 110 4h-1m-9 8h10a2 2 0 110 4H10" />
  </svg>
);

const Loader2 = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

export default NewEpisodeModal;