import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Calendar, Filter, Search, 
  TrendingUp, Users, Activity, Clock, BarChart3,
  ChevronRight, Eye, Printer, Mail, PieChart,
  AlertCircle, CheckCircle, XCircle, FileCheck
} from 'lucide-react';
import DashboardLayout from '../Layout/DashboardLayout';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { StorageManager } from '../../utils/storage';
import './reports-animations.css';

const Reports = () => {
  const { patients } = usePatient();
  const { episodes } = useEpisode();
  const { encounters } = useEncounter();
  
  const [selectedReportType, setSelectedReportType] = useState('patient-summary');
  const [dateRange, setDateRange] = useState('last-30-days');
  const [searchTerm, setSearchTerm] = useState('');
  const [generatedReports, setGeneratedReports] = useState([]);
  const [showPreview, setShowPreview] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  // Report types
  const reportTypes = [
    {
      id: 'patient-summary',
      name: 'Patient Summary',
      description: 'Comprehensive patient medical history and current status',
      icon: Users,
      color: 'blue'
    },    {
      id: 'clinical-activity',
      name: 'Clinical Activity',
      description: 'Overview of clinical activities and procedures',
      icon: Activity,
      color: 'green'
    },
    {
      id: 'diagnosis-trends',
      name: 'Diagnosis Trends',
      description: 'Analysis of diagnosis patterns and frequencies',
      icon: TrendingUp,
      color: 'purple'
    },
    {
      id: 'treatment-outcomes',
      name: 'Treatment Outcomes',
      description: 'Success rates and effectiveness of treatments',
      icon: BarChart3,
      color: 'orange'
    },
    {
      id: 'appointment-analytics',
      name: 'Appointment Analytics',
      description: 'Appointment statistics and no-show rates',
      icon: Calendar,
      color: 'red'
    }
  ];

  // Load generated reports from localStorage
  useEffect(() => {
    const storedReports = StorageManager.getGeneratedReports();
    if (storedReports.length === 0) {
      // Generate some sample reports
      const sampleReports = generateSampleReports();
      StorageManager.saveGeneratedReports(sampleReports);
      setGeneratedReports(sampleReports);
    } else {
      setGeneratedReports(storedReports);
    }
  }, []);

  // Generate sample reports
  const generateSampleReports = () => {
    const reports = [];
    const types = reportTypes.map(rt => rt.id);
    
    // Generate 10 sample reports
    for (let i = 0; i < 10; i++) {
      const date = new Date();
      date.setDate(date.getDate() - Math.floor(Math.random() * 30));
      
      const selectedType = types[Math.floor(Math.random() * types.length)];
      const reportTypeName = reportTypes.find(rt => rt.id === selectedType)?.name || 'Report';
      
      reports.push({
        id: `RPT-${Date.now()}-${i}`,
        type: selectedType,
        name: `${reportTypeName} - ${date.toLocaleDateString()}`,
        generatedDate: date.toISOString(),
        generatedBy: 'Dr. Sarah Chen',
        size: `${Math.floor(Math.random() * 500) + 100} KB`,
        status: 'completed'
      });
    }
    
    return reports;
  };

  // Calculate statistics
  const calculateStatistics = () => {
    const stats = {
      totalPatients: patients.length,
      activeEpisodes: episodes.filter(ep => ep.status === 'open').length,
      completedEncounters: encounters.filter(enc => enc.status === 'completed').length,
      avgEncountersPerPatient: patients.length > 0 ? (encounters.length / patients.length).toFixed(1) : 0
    };
    
    // Diagnosis frequency
    const diagnosisCounts = {};
    episodes.forEach(episode => {
      if (episode.diagnosis?.final) {
        const diagnosis = episode.diagnosis.final;
        diagnosisCounts[diagnosis] = (diagnosisCounts[diagnosis] || 0) + 1;
      }
    });
    
    stats.topDiagnoses = Object.entries(diagnosisCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([diagnosis, count]) => ({ diagnosis, count }));
    
    return stats;
  };

  // Generate new report
  const generateReport = () => {
    const newReport = {
      id: `RPT-${Date.now()}`,
      type: selectedReportType,
      name: `${reportTypes.find(rt => rt.id === selectedReportType).name} - ${new Date().toLocaleDateString()}`,
      generatedDate: new Date().toISOString(),
      generatedBy: 'Dr. Sarah Chen',
      size: `${Math.floor(Math.random() * 500) + 100} KB`,
      status: 'generating'
    };
    
    const updatedReports = [newReport, ...generatedReports];
    setGeneratedReports(updatedReports);
    
    // Simulate report generation
    setTimeout(() => {
      const finalReports = updatedReports.map(report =>
        report.id === newReport.id ? { ...report, status: 'completed' } : report
      );
      setGeneratedReports(finalReports);
      StorageManager.saveGeneratedReports(finalReports);
    }, 2000);
  };

  // Filter reports
  const filteredReports = generatedReports.filter(report => 
    report.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get date range filter
  const getDateRangeFilter = () => {
    const now = new Date();
    const ranges = {
      'last-7-days': 7,
      'last-30-days': 30,
      'last-90-days': 90,
      'all-time': 9999
    };
    
    const daysAgo = ranges[dateRange];
    const cutoffDate = new Date();
    cutoffDate.setDate(now.getDate() - daysAgo);
    
    return filteredReports.filter(report => 
      new Date(report.generatedDate) >= cutoffDate
    );
  };

  const stats = calculateStatistics();

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports & Analytics</h1>
              <p className="text-gray-600">Generate comprehensive medical reports and view practice analytics</p>
            </div>
          </div>
        </div>

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-200 p-6 transition-all hover:shadow-md stat-card">
            <div className="flex items-center justify-between mb-2">
              <Users className="w-10 h-10 text-blue-600" />
              <span className="text-3xl font-bold text-gray-900">{stats.totalPatients}</span>
            </div>
            <p className="text-sm font-medium text-gray-700">Total Patients</p>
            <p className="text-xs text-gray-600 mt-1">Active in system</p>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-sm border border-green-200 p-6 transition-all hover:shadow-md stat-card">
            <div className="flex items-center justify-between mb-2">
              <Activity className="w-10 h-10 text-green-600" />
              <span className="text-3xl font-bold text-gray-900">{stats.activeEpisodes}</span>
            </div>
            <p className="text-sm font-medium text-gray-700">Active Episodes</p>
            <p className="text-xs text-gray-600 mt-1">Currently open</p>
          </div>
          
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-sm border border-purple-200 p-6 transition-all hover:shadow-md stat-card">
            <div className="flex items-center justify-between mb-2">
              <FileCheck className="w-10 h-10 text-purple-600" />
              <span className="text-3xl font-bold text-gray-900">{stats.completedEncounters}</span>
            </div>
            <p className="text-sm font-medium text-gray-700">Completed Encounters</p>
            <p className="text-xs text-gray-600 mt-1">Successfully finished</p>
          </div>
          
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl shadow-sm border border-orange-200 p-6 transition-all hover:shadow-md stat-card">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-10 h-10 text-orange-600" />
              <span className="text-3xl font-bold text-gray-900">{stats.avgEncountersPerPatient}</span>
            </div>
            <p className="text-sm font-medium text-gray-700">Avg Encounters/Patient</p>
            <p className="text-xs text-gray-600 mt-1">Overall average</p>
          </div>
        </div>

        {/* Report Generation */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 mb-8 p-6 transition-all hover:shadow-xl">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Generate New Report</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {reportTypes.map(type => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setSelectedReportType(type.id)}
                  className={`p-5 rounded-xl border-2 transition-all transform hover:scale-105 ${
                    selectedReportType === type.id
                      ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-md'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-sm bg-white'
                  }`}
                >
                  <Icon className={`w-10 h-10 mb-3 mx-auto ${
                    type.color === 'blue' ? 'text-blue-600' :
                    type.color === 'green' ? 'text-green-600' :
                    type.color === 'purple' ? 'text-purple-600' :
                    type.color === 'orange' ? 'text-orange-600' :
                    type.color === 'red' ? 'text-red-600' : 'text-gray-600'
                  }`} />
                  <h3 className="font-medium text-gray-900 mb-1">{type.name}</h3>
                  <p className="text-xs text-gray-600">{type.description}</p>
                </button>
              );
            })}
          </div>
          
          <div className="mt-6 flex items-center gap-4">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="last-7-days">Last 7 days</option>
              <option value="last-30-days">Last 30 days</option>
              <option value="last-90-days">Last 90 days</option>
              <option value="all-time">All time</option>
            </select>
            
            <button
              onClick={generateReport}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Generate Report
            </button>
          </div>
        </div>

        {/* Generated Reports */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Generated Reports</h2>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search reports..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200">
            {getDateRangeFilter().length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                No reports found for the selected criteria
              </div>
            ) : (
              getDateRangeFilter().map(report => {
                const reportType = reportTypes.find(rt => rt.id === report.type);
                const Icon = reportType?.icon || FileText;
                
                return (
                  <div key={report.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-lg ${
                          reportType?.color === 'blue' ? 'bg-blue-100' :
                          reportType?.color === 'green' ? 'bg-green-100' :
                          reportType?.color === 'purple' ? 'bg-purple-100' :
                          reportType?.color === 'orange' ? 'bg-orange-100' :
                          reportType?.color === 'red' ? 'bg-red-100' : 'bg-gray-100'
                        }`}>
                          <Icon className={`w-6 h-6 ${
                            reportType?.color === 'blue' ? 'text-blue-600' :
                            reportType?.color === 'green' ? 'text-green-600' :
                            reportType?.color === 'purple' ? 'text-purple-600' :
                            reportType?.color === 'orange' ? 'text-orange-600' :
                            reportType?.color === 'red' ? 'text-red-600' : 'text-gray-600'
                          }`} />
                        </div>
                        
                        <div>
                          <h3 className="font-medium text-gray-900 mb-1">{report.name}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>Generated by {report.generatedBy}</span>
                            <span>•</span>
                            <span>{new Date(report.generatedDate).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>{report.size}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {report.status === 'generating' ? (
                          <div className="flex items-center gap-2 text-blue-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                            <span className="text-sm">Generating...</span>
                          </div>
                        ) : (
                          <>
                            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Preview">
                              <Eye className="w-5 h-5 text-gray-600" />
                            </button>
                            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Download">
                              <Download className="w-5 h-5 text-gray-600" />
                            </button>
                            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Print">
                              <Printer className="w-5 h-5 text-gray-600" />
                            </button>
                            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Email">
                              <Mail className="w-5 h-5 text-gray-600" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Reports;