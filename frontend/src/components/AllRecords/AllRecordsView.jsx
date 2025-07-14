import React, { useState, useEffect } from 'react';
import { 
  FileText, Calendar, Clock, Activity, Filter, Download,
  ChevronRight, X, Search, Printer, Share2, Archive,
  Heart, Pill, TestTube, Stethoscope, Brain, Shield,
  TrendingUp, AlertCircle, CheckCircle, Eye
} from 'lucide-react';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';

const AllRecordsView = ({ patient, onClose }) => {
  const { getPatientEpisodes } = useEpisode();
  const { getEpisodeEncounters } = useEncounter();
  
  const [activeTab, setActiveTab] = useState('timeline');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // Get all episodes and encounters
  const episodes = getPatientEpisodes(patient.id, true);
  const allRecords = [];
  
  // Compile all records from episodes and encounters
  episodes.forEach(episode => {
    // Add episode as a record
    allRecords.push({
      id: episode.id,
      type: 'episode',
      title: episode.chiefComplaint,
      date: episode.createdAt,
      status: episode.status,
      category: episode.type,
      data: episode
    });
    
    // Add encounters as records
    const encounters = getEpisodeEncounters(episode.id);
    encounters.forEach(encounter => {
      allRecords.push({
        id: encounter.id,
        type: 'encounter',
        title: `${encounter.type} Visit - ${episode.chiefComplaint}`,
        date: encounter.date,
        status: encounter.status,
        category: encounter.type,
        data: encounter,
        episodeId: episode.id
      });
    });
  });
  
  // Add quick notes from localStorage
  const quickNotes = JSON.parse(localStorage.getItem('quickNotes') || '[]');
  const patientNotes = quickNotes.filter(note => note.patientId === patient.id);
  patientNotes.forEach(note => {
    allRecords.push({
      id: note.id,
      type: 'note',
      title: note.title,
      date: note.createdAt,
      status: 'active',
      category: note.type,
      data: note
    });
  });
  
  // Sort by date (newest first)
  allRecords.sort((a, b) => new Date(b.date) - new Date(a.date));
  
  // Filter records
  const filteredRecords = allRecords.filter(record => {
    // Type filter
    if (filterType !== 'all' && record.type !== filterType) return false;
    
    // Date range filter
    if (dateRange !== 'all') {
      const recordDate = new Date(record.date);
      const now = new Date();
      
      switch (dateRange) {
        case 'week':
          const oneWeekAgo = new Date(now.setDate(now.getDate() - 7));
          if (recordDate < oneWeekAgo) return false;
          break;
        case 'month':
          const oneMonthAgo = new Date(now.setMonth(now.getMonth() - 1));
          if (recordDate < oneMonthAgo) return false;
          break;
        case 'year':
          const oneYearAgo = new Date(now.setFullYear(now.getFullYear() - 1));
          if (recordDate < oneYearAgo) return false;
          break;
      }
    }
    
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return record.title.toLowerCase().includes(search) ||
             record.category?.toLowerCase().includes(search);
    }
    
    return true;
  });
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
      case 'in-progress':
        return 'text-yellow-600 bg-yellow-50';
      case 'resolved':
      case 'signed':
        return 'text-green-600 bg-green-50';
      case 'archived':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-blue-600 bg-blue-50';
    }
  };
  
  const getRecordIcon = (record) => {
    if (record.type === 'episode') {
      switch (record.category) {
        case 'acute': return Activity;
        case 'chronic': return Heart;
        case 'preventive': return Shield;
        default: return FileText;
      }
    } else if (record.type === 'note') {
      return FileText;
    }
    return Stethoscope;
  };
  
  const handleExport = () => {
    // Implement export functionality
    console.log('Exporting records...');
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-gray-900">Medical Records</h2>
            <span className="text-sm text-gray-600">
              {patient.demographics.name} • {filteredRecords.length} records
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleExport}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Export records"
            >
              <Download className="w-5 h-5" />
            </button>
            <button
              onClick={handlePrint}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Print records"
            >
              <Printer className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Filters and Search */}
        <div className="px-6 py-4 border-b border-gray-200 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search records..."
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
              <option value="episode">Episodes Only</option>
              <option value="encounter">Visits Only</option>
              <option value="note">Quick Notes Only</option>
            </select>
            
            {/* Date Range */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            >
              <option value="all">All Time</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="year">Last Year</option>
            </select>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-1 border-b border-gray-200">
            {[
              { id: 'timeline', label: 'Timeline View', icon: Clock },
              { id: 'categories', label: 'By Category', icon: Archive },
              { id: 'summary', label: 'Summary', icon: TrendingUp }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Records List */}
          <div className={`${selectedRecord ? 'w-1/2' : 'w-full'} overflow-y-auto border-r border-gray-200`}>
            {activeTab === 'timeline' && (
              <div className="p-6 space-y-4">
                {filteredRecords.length > 0 ? (
                  filteredRecords.map((record, index) => {
                    const Icon = getRecordIcon(record);
                    const isNewDay = index === 0 || 
                      new Date(record.date).toDateString() !== 
                      new Date(filteredRecords[index - 1].date).toDateString();
                    
                    return (
                      <div key={record.id}>
                        {isNewDay && (
                          <div className="flex items-center space-x-2 mb-3">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-600">
                              {new Date(record.date).toLocaleDateString('en-US', {
                                weekday: 'long',
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </span>
                          </div>
                        )}
                        
                        <button
                          onClick={() => setSelectedRecord(record)}
                          className={`w-full text-left p-4 rounded-lg border transition-all hover:shadow-md ${
                            selectedRecord?.id === record.id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 bg-white hover:border-gray-300'
                          }`}
                        >
                          <div className="flex items-start space-x-3">
                            <div className={`p-2 rounded-lg ${
                              record.type === 'episode' ? 'bg-purple-100' : 
                              record.type === 'note' ? 'bg-orange-100' : 'bg-blue-100'
                            }`}>
                              <Icon className={`w-5 h-5 ${
                                record.type === 'episode' ? 'text-purple-600' : 
                                record.type === 'note' ? 'text-orange-600' : 'text-blue-600'
                              }`} />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h4 className="font-medium text-gray-900">{record.title}</h4>
                                  <p className="text-sm text-gray-600 mt-1">
                                    {new Date(record.date).toLocaleTimeString('en-US', {
                                      hour: '2-digit',
                                      minute: '2-digit'
                                    })}
                                    {record.category && ` • ${record.category}`}
                                  </p>
                                </div>
                                <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(record.status)}`}>
                                  {record.status}
                                </span>
                              </div>
                            </div>
                            <ChevronRight className="w-4 h-4 text-gray-400 mt-1" />
                          </div>
                        </button>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-600">No records found</p>
                    <p className="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'categories' && (
              <div className="p-6">
                {/* Group records by category */}
                {['acute', 'chronic', 'preventive', 'follow-up'].map(category => {
                  const categoryRecords = filteredRecords.filter(r => r.category === category && r.type !== 'note');
                  if (categoryRecords.length === 0) return null;
                  
                  return (
                    <div key={category} className="mb-6">
                      <h3 className="font-medium text-gray-900 mb-3 capitalize">
                        {category} ({categoryRecords.length})
                      </h3>
                      <div className="space-y-2">
                        {categoryRecords.map(record => {
                          const Icon = getRecordIcon(record);
                          return (
                            <button
                              key={record.id}
                              onClick={() => setSelectedRecord(record)}
                              className={`w-full text-left p-3 rounded-lg border transition-all hover:shadow-sm ${
                                selectedRecord?.id === record.id
                                  ? 'border-blue-500 bg-blue-50'
                                  : 'border-gray-200 bg-white hover:border-gray-300'
                              }`}
                            >
                              <div className="flex items-center space-x-3">
                                <Icon className="w-4 h-4 text-gray-600" />
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900">{record.title}</p>
                                  <p className="text-xs text-gray-600">
                                    {new Date(record.date).toLocaleDateString()}
                                  </p>
                                </div>
                                <Eye className="w-4 h-4 text-gray-400" />
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
                
                {/* Quick Notes Section */}
                {(() => {
                  const noteRecords = filteredRecords.filter(r => r.type === 'note');
                  if (noteRecords.length === 0) return null;
                  
                  return (
                    <div className="mb-6">
                      <h3 className="font-medium text-gray-900 mb-3">
                        Quick Notes ({noteRecords.length})
                      </h3>
                      <div className="space-y-2">
                        {noteRecords.map(record => {
                          const Icon = getRecordIcon(record);
                          return (
                            <button
                              key={record.id}
                              onClick={() => setSelectedRecord(record)}
                              className={`w-full text-left p-3 rounded-lg border transition-all hover:shadow-sm ${
                                selectedRecord?.id === record.id
                                  ? 'border-blue-500 bg-blue-50'
                                  : 'border-gray-200 bg-white hover:border-gray-300'
                              }`}
                            >
                              <div className="flex items-center space-x-3">
                                <Icon className="w-4 h-4 text-orange-600" />
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900">{record.title}</p>
                                  <p className="text-xs text-gray-600">
                                    {new Date(record.date).toLocaleDateString()} • {record.category}
                                  </p>
                                </div>
                                <Eye className="w-4 h-4 text-gray-400" />
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
            
            {activeTab === 'summary' && (
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Total Episodes</span>
                      <Activity className="w-4 h-4 text-blue-600" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {episodes.length}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {episodes.filter(e => e.status === 'active').length} active
                    </p>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Total Visits</span>
                      <Stethoscope className="w-4 h-4 text-green-600" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {allRecords.filter(r => r.type === 'encounter').length}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Across all episodes
                    </p>
                  </div>
                  
                  <div className="bg-orange-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Quick Notes</span>
                      <FileText className="w-4 h-4 text-orange-600" />
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {allRecords.filter(r => r.type === 'note').length}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Clinical notes
                    </p>
                  </div>
                </div>
                
                {/* Recent Conditions */}
                <div className="mb-6">
                  <h3 className="font-medium text-gray-900 mb-3">Recent Conditions</h3>
                  <div className="space-y-2">
                    {episodes.slice(0, 5).map(episode => (
                      <div key={episode.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{episode.chiefComplaint}</p>
                          <p className="text-xs text-gray-600">
                            {new Date(episode.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(episode.status)}`}>
                          {episode.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Record Detail */}
          {selectedRecord && (
            <div className="w-1/2 overflow-y-auto p-6 bg-gray-50">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedRecord.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(selectedRecord.date).toLocaleString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedRecord(null)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                
                {selectedRecord.type === 'episode' && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Chief Complaint</p>
                      <p className="text-gray-900">{selectedRecord.data.chiefComplaint}</p>
                    </div>
                    
                    {selectedRecord.data.clinicalNotes && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Clinical Notes</p>
                        <p className="text-gray-900">{selectedRecord.data.clinicalNotes}</p>
                      </div>
                    )}
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Type</p>
                      <p className="text-gray-900 capitalize">{selectedRecord.data.type}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Status</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedRecord.data.status)}`}>
                        {selectedRecord.data.status}
                      </span>
                    </div>
                  </div>
                )}
                
                {selectedRecord.type === 'encounter' && selectedRecord.data.soap && (
                  <div className="space-y-6">
                    {/* SOAP Sections */}
                    {['subjective', 'objective', 'assessment', 'plan'].map(section => {
                      const soapData = selectedRecord.data.soap[section];
                      if (!soapData) return null;
                      
                      return (
                        <div key={section}>
                          <h4 className="font-medium text-gray-900 mb-2 capitalize">{section}</h4>
                          <div className="bg-gray-50 rounded-lg p-4 text-sm">
                            {section === 'subjective' && (
                              <>
                                {soapData.hpi && (
                                  <div className="mb-3">
                                    <p className="font-medium text-gray-700 mb-1">History of Present Illness</p>
                                    <p className="text-gray-900">{soapData.hpi}</p>
                                  </div>
                                )}
                                {soapData.ros && Object.keys(soapData.ros).length > 0 && (
                                  <div>
                                    <p className="font-medium text-gray-700 mb-1">Review of Systems</p>
                                    <div className="space-y-1">
                                      {Object.entries(soapData.ros).map(([system, value]) => (
                                        <p key={system} className="text-gray-900">
                                          <span className="font-medium capitalize">{system}:</span> {value}
                                        </p>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </>
                            )}
                            
                            {section === 'objective' && (
                              <>
                                {soapData.vitals && (
                                  <div className="mb-3">
                                    <p className="font-medium text-gray-700 mb-1">Vital Signs</p>
                                    <div className="grid grid-cols-2 gap-2">
                                      {Object.entries(soapData.vitals).map(([vital, value]) => value && (
                                        <p key={vital} className="text-gray-900">
                                          <span className="font-medium capitalize">{vital}:</span> {value}
                                        </p>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {soapData.physicalExam?.general && (
                                  <div>
                                    <p className="font-medium text-gray-700 mb-1">Physical Exam</p>
                                    <p className="text-gray-900">{soapData.physicalExam.general}</p>
                                  </div>
                                )}
                              </>
                            )}
                            
                            {section === 'assessment' && (
                              <>
                                {soapData.clinicalImpression && (
                                  <div className="mb-3">
                                    <p className="font-medium text-gray-700 mb-1">Clinical Impression</p>
                                    <p className="text-gray-900">{soapData.clinicalImpression}</p>
                                  </div>
                                )}
                                {soapData.differentialDiagnosis?.length > 0 && (
                                  <div>
                                    <p className="font-medium text-gray-700 mb-1">Differential Diagnosis</p>
                                    <ul className="list-disc list-inside space-y-1">
                                      {soapData.differentialDiagnosis.map((dx, idx) => (
                                        <li key={idx} className="text-gray-900">
                                          {dx.name} {dx.icdCode && `(${dx.icdCode})`}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </>
                            )}
                            
                            {section === 'plan' && (
                              <>
                                {soapData.medications?.length > 0 && (
                                  <div className="mb-3">
                                    <p className="font-medium text-gray-700 mb-1">Medications</p>
                                    <ul className="space-y-1">
                                      {soapData.medications.map((med, idx) => (
                                        <li key={idx} className="text-gray-900">
                                          {med.name} - {med.dosage} ({med.instructions})
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                {soapData.followUp?.timeframe && (
                                  <div>
                                    <p className="font-medium text-gray-700 mb-1">Follow-up</p>
                                    <p className="text-gray-900">{soapData.followUp.timeframe}</p>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                
                {selectedRecord.type === 'note' && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Note Type</p>
                      <p className="text-gray-900 capitalize">{selectedRecord.data.type}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Priority</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        selectedRecord.data.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                        selectedRecord.data.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                        selectedRecord.data.priority === 'normal' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {selectedRecord.data.priority}
                      </span>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Content</p>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-900 whitespace-pre-wrap">{selectedRecord.data.content}</p>
                      </div>
                    </div>
                    
                    {selectedRecord.data.tags && selectedRecord.data.tags.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Tags</p>
                        <div className="flex flex-wrap gap-2">
                          {selectedRecord.data.tags.map((tag, idx) => (
                            <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Created By</p>
                      <p className="text-gray-900">{selectedRecord.data.createdBy}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AllRecordsView;