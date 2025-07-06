import React, { useState } from 'react';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useNavigate } from 'react-router-dom';
import { X, AlertCircle, ChevronDown } from 'lucide-react';

const NewEpisodeModal = ({ patientId, onClose, onSuccess }) => {
  const navigate = useNavigate();
  const { createEpisode } = useEpisode();
  
  const [formData, setFormData] = useState({
    chiefComplaint: '',
    category: 'acute',
    tags: [],
    createEncounter: true
  });
  
  const [customTag, setCustomTag] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const commonComplaints = [
    'Chest pain',
    'Shortness of breath',
    'Abdominal pain',
    'Headache',
    'Back pain',
    'Cough',
    'Fever',
    'Fatigue',
    'Dizziness',
    'Nausea/Vomiting'
  ];

  const categoryOptions = [
    { value: 'acute', label: 'Acute', description: 'New or sudden onset condition' },
    { value: 'chronic', label: 'Chronic', description: 'Ongoing management of existing condition' },
    { value: 'preventive', label: 'Preventive', description: 'Routine check-up or screening' },
    { value: 'follow-up', label: 'Follow-up', description: 'Related to previous episode' }
  ];

  const commonTags = [
    'respiratory',
    'cardiovascular',
    'gastrointestinal',
    'neurological',
    'musculoskeletal',
    'endocrine',
    'infectious',
    'mental-health',
    'dermatological',
    'urological'
  ];
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
        tags: formData.tags
      });
      
      if (formData.createEncounter) {
        // Navigate to episode workspace to create first encounter
        navigate(`/patient/${patientId}/episode/${newEpisode.id}`);
      } else {
        // Just create episode and close modal
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">New Episode</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Chief Complaint */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chief Complaint <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.chiefComplaint}
              onChange={(e) => setFormData(prev => ({ ...prev, chiefComplaint: e.target.value }))}
              placeholder="Enter the main reason for this visit..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
            {commonComplaints.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-1">Common complaints:</p>
                <div className="flex flex-wrap gap-1">
                  {commonComplaints.map((complaint, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, chiefComplaint: complaint }))}
                      className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      {complaint}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Episode Category
            </label>
            <div className="grid grid-cols-2 gap-3">
              {categoryOptions.map((option) => (
                <label
                  key={option.value}
                  className={`
                    relative flex items-start p-3 border rounded-lg cursor-pointer transition-all
                    ${formData.category === option.value 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="category"
                    value={option.value}
                    checked={formData.category === option.value}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    className="sr-only"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{option.label}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{option.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (Optional)
            </label>
            <div className="space-y-3">
              {/* Selected Tags */}
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700"
                    >
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
              
              {/* Common Tags */}
              <div className="flex flex-wrap gap-2">
                {commonTags.filter(tag => !formData.tags.includes(tag)).map((tag, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleAddTag(tag)}
                    className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                  >
                    + {tag}
                  </button>
                ))}
              </div>
              
              {/* Custom Tag Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customTag}
                  onChange={(e) => setCustomTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTag())}
                  placeholder="Add custom tag..."
                  className="flex-1 px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={handleAddCustomTag}
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Create Encounter Option */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="createEncounter"
              checked={formData.createEncounter}
              onChange={(e) => setFormData(prev => ({ ...prev, createEncounter: e.target.checked }))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="createEncounter" className="ml-2 text-sm text-gray-700">
              Start documenting first encounter immediately
            </label>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Creating...' : 'Create Episode'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewEpisodeModal;