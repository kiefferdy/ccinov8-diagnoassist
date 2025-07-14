import React, { useState, useEffect } from 'react';
import { 
  FileText, Clock, X, Eye, Edit, Trash2, 
  Calendar, Tag, User, Search, Filter
} from 'lucide-react';

const QuickNotesView = ({ patient, onClose }) => {
  const [notes, setNotes] = useState([]);
  const [filteredNotes, setFilteredNotes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [selectedNote, setSelectedNote] = useState(null);

  // Load notes from localStorage
  useEffect(() => {
    const allNotes = JSON.parse(localStorage.getItem('quickNotes') || '[]');
    const patientNotes = allNotes.filter(note => note.patientId === patient.id);
    setNotes(patientNotes);
    setFilteredNotes(patientNotes);
  }, [patient.id]);

  // Apply filters
  useEffect(() => {
    let filtered = [...notes];

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(note => note.type === filterType);
    }

    // Priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(note => note.priority === filterPriority);
    }

    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(note => 
        note.title.toLowerCase().includes(search) ||
        note.content.toLowerCase().includes(search) ||
        note.tags?.some(tag => tag.toLowerCase().includes(search))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'priority':
          const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    setFilteredNotes(filtered);
  }, [notes, filterType, filterPriority, searchTerm, sortBy]);

  const handleDeleteNote = (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      const allNotes = JSON.parse(localStorage.getItem('quickNotes') || '[]');
      const updatedNotes = allNotes.filter(note => note.id !== noteId);
      localStorage.setItem('quickNotes', JSON.stringify(updatedNotes));
      
      const patientNotes = updatedNotes.filter(note => note.patientId === patient.id);
      setNotes(patientNotes);
      setSelectedNote(null);
      
      if (window.showNotification) {
        window.showNotification('Note deleted successfully', 'success');
      }
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'normal': return 'text-blue-600 bg-blue-50';
      case 'low': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Quick Notes</h2>
            <p className="text-sm text-gray-600 mt-1">
              {patient.demographics.name} • {filteredNotes.length} notes
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Type Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            >
              <option value="all">All Types</option>
              <option value="clinical">Clinical Notes</option>
              <option value="telephone">Phone Calls</option>
              <option value="followup">Follow-ups</option>
              <option value="reminder">Reminders</option>
              <option value="administrative">Administrative</option>
            </select>

            {/* Priority Filter */}
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            >
              <option value="all">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
              <option value="low">Low</option>
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            >
              <option value="date">Sort by Date</option>
              <option value="priority">Sort by Priority</option>
              <option value="title">Sort by Title</option>
            </select>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Notes List */}
          <div className={`${selectedNote ? 'w-1/2' : 'w-full'} overflow-y-auto border-r border-gray-200`}>
            <div className="p-6">
              {filteredNotes.length > 0 ? (
                <div className="space-y-3">
                  {filteredNotes.map(note => (
                    <button
                      key={note.id}
                      onClick={() => setSelectedNote(note)}
                      className={`w-full text-left p-4 rounded-lg border transition-all hover:shadow-md ${
                        selectedNote?.id === note.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{note.title}</h4>
                        <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(note.priority)}`}>
                          {note.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2 mb-2">{note.content}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-3">
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {new Date(note.createdAt).toLocaleDateString()}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                            {new Date(note.createdAt).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <span className="capitalize">{note.type}</span>
                      </div>
                      {note.tags && note.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {note.tags.map((tag, idx) => (
                            <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                              <Tag className="w-2.5 h-2.5 mr-1" />
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-600">No notes found</p>
                  <p className="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
                </div>
              )}
            </div>
          </div>

          {/* Note Detail */}
          {selectedNote && (
            <div className="w-1/2 overflow-y-auto p-6 bg-gray-50">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedNote.title}</h3>
                    <div className="flex items-center space-x-3 mt-2 text-sm text-gray-600">
                      <span className="flex items-center">
                        <User className="w-4 h-4 mr-1" />
                        {selectedNote.createdBy}
                      </span>
                      <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {new Date(selectedNote.createdAt).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDeleteNote(selectedNote.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete note"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setSelectedNote(null)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Type</p>
                      <p className="text-gray-900 capitalize">{selectedNote.type}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Priority</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(selectedNote.priority)}`}>
                        {selectedNote.priority}
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Content</p>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-gray-900 whitespace-pre-wrap">{selectedNote.content}</p>
                    </div>
                  </div>

                  {selectedNote.tags && selectedNote.tags.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Tags</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedNote.tags.map((tag, idx) => (
                          <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700">
                            <Tag className="w-3 h-3 mr-1" />
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuickNotesView;