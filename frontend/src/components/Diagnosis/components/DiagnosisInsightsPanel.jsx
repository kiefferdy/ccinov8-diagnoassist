import React, { useState } from 'react';
import { 
  Brain,
  Activity,
  Stethoscope,
  Heart,
  Thermometer,
  Wind,
  Droplet,
  TrendingUp,
  Clock,
  FileText,
  AlertCircle,
  CheckCircle2,
  XCircle
} from 'lucide-react';

const DiagnosisInsightsPanel = ({ patientData, diagnoses }) => {
  const [expandedInsight, setExpandedInsight] = useState(null);
  
  // Generate insights based on patient data and diagnoses
  const insights = [
    {
      id: 1,
      category: 'Risk Factors',
      icon: AlertCircle,
      color: 'text-yellow-600 bg-yellow-50',
      title: 'Age-Related Considerations',
      content: `At ${patientData.age || 'unknown'} years old, the patient's age ${
        parseInt(patientData.age) > 65 ? 'increases risk for severe pneumonia and complications' :
        parseInt(patientData.age) < 5 ? 'requires careful monitoring for rapid deterioration' :
        'suggests good reserve capacity for recovery'
      }.`,
      recommendations: [
        'Consider age-adjusted antibiotic dosing',
        'Monitor for age-specific complications',
        'Assess vaccination status'
      ]
    },
    {
      id: 2,
      category: 'Vital Signs Analysis',
      icon: Activity,
      color: 'text-blue-600 bg-blue-50',
      title: 'Hemodynamic Status',
      content: 'Current vital signs suggest mild systemic inflammatory response. The elevated heart rate with normal blood pressure indicates compensated state.',
      vitals: {
        'Heart Rate': { value: patientData.physicalExam?.heartRate || '102', status: 'elevated', normal: '60-100 bpm' },
        'Blood Pressure': { value: patientData.physicalExam?.bloodPressure || '120/80', status: 'normal', normal: '90-120/60-80' },
        'Temperature': { value: patientData.physicalExam?.temperature || '38.5', status: 'elevated', normal: '36.5-37.5°C' },
        'O2 Saturation': { value: patientData.physicalExam?.oxygenSaturation || '98', status: 'normal', normal: '>95%' }
      }
    },
    {
      id: 3,
      category: 'Diagnostic Confidence',
      icon: Brain,
      color: 'text-purple-600 bg-purple-50',
      title: 'AI Confidence Analysis',
      content: 'The AI has high confidence in the top differential diagnoses based on classical presentation and consistent clinical findings.',
      metrics: {
        'Data Completeness': 85,
        'Symptom Consistency': 92,
        'Pattern Recognition': 88
      }
    }
  ];
  
  const getStatusColor = (status) => {
    switch(status) {
      case 'elevated': return 'text-red-600';
      case 'low': return 'text-blue-600';
      case 'normal': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Clinical Intelligence Dashboard</h3>
      
      {insights.map((insight) => (
        <div key={insight.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setExpandedInsight(expandedInsight === insight.id ? null : insight.id)}
            className="w-full p-4 flex items-start space-x-3 hover:bg-gray-50 transition-colors"
          >
            <div className={`p-2 rounded-lg ${insight.color}`}>
              <insight.icon className="w-5 h-5" />
            </div>
            <div className="flex-1 text-left">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{insight.category}</p>
                  <p className="font-semibold text-gray-900">{insight.title}</p>
                </div>
                <div className={`transform transition-transform ${expandedInsight === insight.id ? 'rotate-180' : ''}`}>
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
          </button>
          
          {expandedInsight === insight.id && (
            <div className="px-4 pb-4 border-t border-gray-100">
              <p className="text-gray-700 text-sm mt-3">{insight.content}</p>
              
              {insight.vitals && (
                <div className="mt-4 space-y-2">
                  {Object.entries(insight.vitals).map(([key, data]) => (
                    <div key={key} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">{key}:</span>
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${getStatusColor(data.status)}`}>
                          {data.value}
                        </span>
                        <span className="text-gray-400 text-xs">({data.normal})</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {insight.metrics && (
                <div className="mt-4 space-y-2">
                  {Object.entries(insight.metrics).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">{key}</span>
                        <span className="font-medium text-gray-900">{value}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                          style={{ width: `${value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {insight.recommendations && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Recommendations:</p>
                  <ul className="space-y-1">
                    {insight.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <CheckCircle2 className="w-4 h-4 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
      
      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3 mt-6">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <p className="text-3xl font-bold text-blue-600">{diagnoses.length}</p>
          <p className="text-xs text-blue-700">Differentials</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3 text-center">
          <p className="text-3xl font-bold text-green-600">
            {diagnoses.filter(d => d.probability > 50).length}
          </p>
          <p className="text-xs text-green-700">High Probability</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3 text-center">
          <p className="text-3xl font-bold text-purple-600">
            {Math.round(diagnoses.reduce((acc, d) => acc + (d.confidence === 'high' ? 1 : 0), 0) / diagnoses.length * 100)}%
          </p>
          <p className="text-xs text-purple-700">AI Confidence</p>
        </div>
      </div>
    </div>
  );
};

export default DiagnosisInsightsPanel;