import React, { useState } from 'react';
import { 
  X, FileText, Save, Calendar, Clock, Tag, 
  AlertCircle, Sparkles, Mic, MicOff, Paperclip,
  Phone, Archive, Zap
} from 'lucide-react';
import { generateId } from '../../utils/storage';

const QuickNoteModal = ({ patient, onClose, onSave }) => {
  const [noteType, setNoteType] = useState('clinical');
  const [noteContent, setNoteContent] = useState('');
  const [noteTitle, setNoteTitle] = useState('');
  const [noteTags, setNoteTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [priority, setPriority] = useState('normal');
  const [isRecording, setIsRecording] = useState(false);
  const [errors, setErrors] = useState({});

  const noteTypes = [
    { id: 'clinical', label: 'Clinical Note', icon: FileText, color: 'blue' },
    { id: 'telephone', label: 'Phone Call', icon: Phone, color: 'green' },
    { id: 'followup', label: 'Follow-up', icon: Calendar, color: 'purple' },
    { id: 'reminder', label: 'Reminder', icon: Clock, color: 'orange' },
    { id: 'administrative', label: 'Administrative', icon: Archive, color: 'gray' }
  ];

  const priorities = [
    { id: 'low', label: 'Low', color: 'gray' },
    { id: 'normal', label: 'Normal', color: 'blue' },
    { id: 'high', label: 'High', color: 'orange' },
    { id: 'urgent', label: 'Urgent', color: 'red' }
  ];

  const suggestedTags = [
    'medication-change', 'lab-review', 'phone-consult', 
    'patient-education', 'referral', 'follow-up-needed'
  ];

  const noteTemplates = {
    telephone: {
      title: 'Telephone Consultation - [Date]',
      content: `Phone call with patient regarding: [Chief concern]

Patient reported: [Symptoms/concerns]

Advice given:
- [Advice point 1]
- [Advice point 2]

Follow-up: [Instructions]

Call duration: [X] minutes`
    },
    followup: {
      title: 'Follow-up Note - [Condition]',
      content: `Follow-up for: [Condition/Episode]

Current status:
- Symptoms: [Improved/Unchanged/Worsened]
- Medications: [Compliance status]
- Side effects: [None/List]

Plan:
- [Next steps]
- Next follow-up: [Timeframe]`
    },
    referral: {
      title: 'Referral - [Specialty]',
      content: `Referral to: [Specialist/Department]

Reason for referral: [Clinical indication]

Clinical summary:
- [Key findings]
- [Relevant test results]

Urgency: [Routine/Urgent/Emergency]

Patient informed and agrees to referral.`
    },
    medication: {
      title: 'Medication Change - [Date]',
      content: `Medication adjustment:

Stopped: [Medication name, dose, reason]
Started: [Medication name, dose, frequency]

Indication: [Clinical reason]

Patient counseled on:
- Dosing instructions
- Potential side effects
- When to seek help

Follow-up: [Timeframe]`
    }
  };

  const handleAddTag = (tag) => {
    if (tag && !noteTags.includes(tag)) {
      setNoteTags([...noteTags, tag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setNoteTags(noteTags.filter(tag => tag !== tagToRemove));
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    if (isRecording) {
      // Stop recording
      if (window.currentRecognition) {
        window.currentRecognition.stop();
      }
      setIsRecording(false);
    } else {
      // Start recording
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }
        if (finalTranscript) {
          setNoteContent(prev => prev + finalTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      window.currentRecognition = recognition;
      recognition.start();
    }
  };

  const validate = () => {
    const newErrors = {};
    
    if (!noteTitle.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!noteContent.trim()) {
      newErrors.content = 'Note content is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;

    const quickNote = {
      id: generateId(),
      patientId: patient.id,
      type: noteType,
      title: noteTitle,
      content: noteContent,
      tags: noteTags,
      priority: priority,
      createdAt: new Date().toISOString(),
      createdBy: 'Current User', // Would come from auth context
      status: 'active'
    };

    onSave(quickNote);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Quick Note</h2>
            <p className="text-sm text-gray-600 mt-1">
              {patient.demographics.name} • {new Date().toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Note Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Note Type
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {noteTypes.map(type => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => setNoteType(type.id)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      noteType === type.id
                        ? `border-${type.color}-500 bg-${type.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`w-5 h-5 mx-auto mb-1 ${
                      noteType === type.id ? `text-${type.color}-600` : 'text-gray-600'
                    }`} />
                    <p className={`text-sm font-medium ${
                      noteType === type.id ? `text-${type.color}-700` : 'text-gray-700'
                    }`}>
                      {type.label}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Priority
            </label>
            <div className="flex space-x-2">
              {priorities.map(p => (
                <button
                  key={p.id}
                  onClick={() => setPriority(p.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    priority === p.id
                      ? `bg-${p.color}-100 text-${p.color}-700 border-2 border-${p.color}-500`
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={noteTitle}
              onChange={(e) => {
                setNoteTitle(e.target.value);
                if (errors.title) setErrors({ ...errors, title: null });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter a brief title for this note"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.title}
              </p>
            )}
          </div>

          {/* Templates */}
          {noteType && noteTemplates[noteType] && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-blue-900 flex items-center">
                  <Zap className="w-4 h-4 mr-1" />
                  Quick Template Available
                </p>
                <button
                  onClick={() => {
                    setNoteTitle(noteTemplates[noteType].title);
                    setNoteContent(noteTemplates[noteType].content);
                  }}
                  className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Use Template
                </button>
              </div>
              <p className="text-xs text-blue-700">
                Click "Use Template" to pre-fill with a {noteType} note template
              </p>
            </div>
          )}

          {/* Note Content */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Note Content <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleVoiceInput}
                  className={`p-2 rounded-lg transition-all ${
                    isRecording
                      ? 'bg-red-100 text-red-600 hover:bg-red-200'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  title={isRecording ? 'Stop recording' : 'Start voice input'}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
                <button
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-all"
                  title="Attach files"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
              </div>
            </div>
            <textarea
              value={noteContent}
              onChange={(e) => {
                setNoteContent(e.target.value);
                if (errors.content) setErrors({ ...errors, content: null });
              }}
              rows={6}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.content ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your clinical note here..."
            />
            {errors.content && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.content}
              </p>
            )}
            <div className="mt-2 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                {noteContent.length} characters
              </p>
              <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center">
                <Sparkles className="w-4 h-4 mr-1" />
                AI Assist
              </button>
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {noteTags.map(tag => (
                <span
                  key={tag}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700"
                >
                  <Tag className="w-3 h-3 mr-1" />
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag(tagInput);
                  }
                }}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Add a tag..."
              />
              <button
                onClick={() => handleAddTag(tagInput)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                Add
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <p className="text-xs text-gray-500 w-full">Suggested:</p>
              {suggestedTags.filter(tag => !noteTags.includes(tag)).map(tag => (
                <button
                  key={tag}
                  onClick={() => handleAddTag(tag)}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="w-4 h-4 mr-1" />
            {new Date().toLocaleTimeString()}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Note
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickNoteModal;