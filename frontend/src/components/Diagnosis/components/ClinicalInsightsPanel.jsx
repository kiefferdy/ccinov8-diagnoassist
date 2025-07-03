import React, { useState } from 'react';
import { 
  Brain, 
  AlertTriangle, 
  CheckCircle, 
  AlertCircle,
  Lightbulb,
  Search,
  Target,
  Shield,
  Activity,
  TrendingUp,
  Info
} from 'lucide-react';

const ClinicalInsightsPanel = ({ patientData, isAnalyzing, onRefresh }) => {
  const [expandedSection, setExpandedSection] = useState(null);
  
  // Generate clinical insights based on subjective and objective data
  const generateInsights = () => {
    const insights = {
      keyFindings: [],
      redFlags: [],
      differentialConsiderations: [],
      diagnosticSuggestions: [],
      clinicalPearls: []
    };
    
    // Analyze chief complaint and history
    if (patientData.chiefComplaint?.toLowerCase().includes('chest') || 
        patientData.chiefComplaint?.toLowerCase().includes('breath')) {
      insights.redFlags.push({
        icon: AlertTriangle,
        text: "Consider cardiac causes - check for risk factors",
        severity: "high"
      });
      insights.differentialConsiderations.push({
        category: "Cardiovascular",
        items: ["Acute coronary syndrome", "Pulmonary embolism", "Aortic dissection"]
      });
    }
    
    // Analyze vital signs
    const exam = patientData.physicalExam || {};
    if (exam.heartRate && parseInt(exam.heartRate) > 100) {
      insights.keyFindings.push({
        icon: Activity,
        text: "Tachycardia present - consider underlying causes",
        type: "vital"
      });
    }
    
    if (exam.temperature && parseFloat(exam.temperature) > 38) {
      insights.keyFindings.push({
        icon: AlertCircle,
        text: "Fever present - suggests infectious/inflammatory process",
        type: "vital"
      });
      insights.differentialConsiderations.push({
        category: "Infectious",
        items: ["Pneumonia", "Sepsis", "Viral syndrome"]
      });
    }
    
    // Add diagnostic suggestions
    insights.diagnosticSuggestions = [
      {
        category: "Laboratory",
        rationale: "Based on presentation",
        tests: ["CBC with differential", "Basic metabolic panel", "Inflammatory markers"]
      },
      {
        category: "Imaging",
        rationale: "To evaluate structural causes",
        tests: ["Chest X-ray", "Consider CT if indicated"]
      }
    ];
    
    // Add clinical pearls
    insights.clinicalPearls = [
      "Remember to consider patient's age and comorbidities in your differential",
      "Document pertinent negatives to support your clinical reasoning",
      "Consider social factors that may impact diagnosis and treatment"
    ];
    
    return insights;
  };
  
  const insights = generateInsights();
  
  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Brain className="w-5 h-5 text-purple-600 mr-2" />
          Clinical Reasoning Assistant
        </h3>
        <button
          onClick={onRefresh}
          disabled={isAnalyzing}
          className="text-sm text-purple-600 hover:text-purple-700 disabled:text-gray-400"
        >
          {isAnalyzing ? 'Analyzing...' : 'Refresh insights'}
        </button>
      </div>
      
      <div className="space-y-4">
        {/* Red Flags Section */}
        {insights.redFlags.length > 0 && (
          <div className="border border-red-200 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('redFlags')}
              className="w-full px-4 py-3 bg-red-50 hover:bg-red-100 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                <span className="font-medium text-red-900">Red Flags to Consider</span>
                <span className="ml-2 text-sm text-red-700">({insights.redFlags.length})</span>
              </div>
              <Info className="w-4 h-4 text-red-600" />
            </button>
            {expandedSection === 'redFlags' && (
              <div className="p-4 space-y-2">
                {insights.redFlags.map((flag, idx) => (
                  <div key={idx} className="flex items-start space-x-2">
                    <flag.icon className="w-4 h-4 text-red-600 mt-0.5" />
                    <p className="text-sm text-gray-700">{flag.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Key Findings */}
        {insights.keyFindings.length > 0 && (
          <div className="border border-blue-200 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('keyFindings')}
              className="w-full px-4 py-3 bg-blue-50 hover:bg-blue-100 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center">
                <Target className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-medium text-blue-900">Key Clinical Findings</span>
                <span className="ml-2 text-sm text-blue-700">({insights.keyFindings.length})</span>
              </div>
              <Info className="w-4 h-4 text-blue-600" />
            </button>
            {expandedSection === 'keyFindings' && (
              <div className="p-4 space-y-2">
                {insights.keyFindings.map((finding, idx) => (
                  <div key={idx} className="flex items-start space-x-2">
                    <finding.icon className="w-4 h-4 text-blue-600 mt-0.5" />
                    <p className="text-sm text-gray-700">{finding.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Differential Considerations */}
        <div className="border border-purple-200 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('differential')}
            className="w-full px-4 py-3 bg-purple-50 hover:bg-purple-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center">
              <Search className="w-5 h-5 text-purple-600 mr-2" />
              <span className="font-medium text-purple-900">Differential Considerations</span>
            </div>
            <Info className="w-4 h-4 text-purple-600" />
          </button>
          {expandedSection === 'differential' && (
            <div className="p-4 space-y-3">
              {insights.differentialConsiderations.map((category, idx) => (
                <div key={idx}>
                  <p className="text-sm font-medium text-gray-700 mb-1">{category.category}:</p>
                  <ul className="ml-4 space-y-1">
                    {category.items.map((item, itemIdx) => (
                      <li key={itemIdx} className="text-sm text-gray-600">• {item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Diagnostic Approach */}
        <div className="border border-green-200 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('diagnostic')}
            className="w-full px-4 py-3 bg-green-50 hover:bg-green-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-green-600 mr-2" />
              <span className="font-medium text-green-900">Diagnostic Approach</span>
            </div>
            <Info className="w-4 h-4 text-green-600" />
          </button>
          {expandedSection === 'diagnostic' && (
            <div className="p-4 space-y-3">
              {insights.diagnosticSuggestions.map((suggestion, idx) => (
                <div key={idx}>
                  <p className="text-sm font-medium text-gray-700">{suggestion.category}</p>
                  <p className="text-xs text-gray-500 mb-1">{suggestion.rationale}</p>
                  <ul className="ml-4 space-y-1">
                    {suggestion.tests.map((test, testIdx) => (
                      <li key={testIdx} className="text-sm text-gray-600">• {test}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Clinical Pearls */}
        <div className="border border-yellow-200 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('pearls')}
            className="w-full px-4 py-3 bg-yellow-50 hover:bg-yellow-100 transition-colors flex items-center justify-between"
          >
            <div className="flex items-center">
              <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
              <span className="font-medium text-yellow-900">Clinical Pearls</span>
            </div>
            <Info className="w-4 h-4 text-yellow-600" />
          </button>
          {expandedSection === 'pearls' && (
            <div className="p-4 space-y-2">
              {insights.clinicalPearls.map((pearl, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-yellow-600">💡</span>
                  <p className="text-sm text-gray-700">{pearl}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600 text-center">
          These insights are AI-generated suggestions to support clinical reasoning. 
          Always use your clinical judgment.
        </p>
      </div>
    </div>
  );
};

export default ClinicalInsightsPanel;