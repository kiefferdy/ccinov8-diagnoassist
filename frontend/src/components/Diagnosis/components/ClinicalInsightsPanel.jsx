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
  Info,
  Heart,
  Thermometer,
  Wind,
  Droplet,
  Clock,
  ChevronRight,
  FileText,
  Stethoscope,
  TestTube,
  BookOpen,
  XCircle,
  CheckSquare,
  Scale
} from 'lucide-react';

const ClinicalInsightsPanel = ({ patientData }) => {
  const [expandedSection, setExpandedSection] = useState('differential');
  const [selectedDifferential, setSelectedDifferential] = useState(null);
  
  // Generate more sophisticated clinical insights based on actual patient data
  const generateInsights = () => {
    const insights = {
      keyFindings: [],
      redFlags: [],
      differentialDiagnoses: [],
      evidenceAnalysis: {},
      diagnosticPlan: [],
      clinicalPearls: [],
      riskStratification: null
    };
    
    // Analyze chief complaint patterns
    const chiefComplaint = patientData.chiefComplaint?.toLowerCase() || '';
    const duration = patientData.chiefComplaintDuration?.toLowerCase() || '';
    const history = patientData.historyOfPresentIllness?.toLowerCase() || '';
    const exam = patientData.physicalExam || {};
    
    // Parse vital signs
    const vitals = {
      bp: exam.bloodPressure,
      hr: parseInt(exam.heartRate) || null,
      temp: parseFloat(exam.temperature) || null,
      rr: parseInt(exam.respiratoryRate) || null,
      o2: exam.oxygenSaturation
    };
    
    // Detect patterns and generate sophisticated differentials
    if (chiefComplaint.includes('cough') || chiefComplaint.includes('breath') || chiefComplaint.includes('chest')) {
      // Respiratory/Chest complaint analysis
      const differentials = [];
      
      // Check for pneumonia indicators
      if ((vitals.temp && vitals.temp > 38) || history.includes('fever')) {
        differentials.push({
          diagnosis: 'Community-Acquired Pneumonia',
          probability: 'High',
          supportingEvidence: [
            vitals.temp > 38 ? `Fever (${vitals.temp}°C)` : 'History of fever',
            chiefComplaint.includes('cough') ? 'Productive cough' : null,
            history.includes('phlegm') || history.includes('sputum') ? 'Sputum production' : null,
            exam.additionalFindings?.includes('crackles') ? 'Crackles on auscultation' : null
          ].filter(Boolean),
          againstEvidence: [
            vitals.o2 && parseInt(vitals.o2) > 95 ? 'Normal oxygen saturation' : null,
            !exam.additionalFindings?.includes('crackles') ? 'No crackles noted' : null
          ].filter(Boolean),
          criticalActions: [
            'Chest X-ray',
            'CBC with differential',
            'Consider sputum culture',
            'Blood cultures if severe'
          ]
        });
      }
      
      // Check for cardiac indicators
      if (chiefComplaint.includes('chest') && (patientData.age > 40 || history.includes('pressure') || history.includes('tight'))) {
        differentials.push({
          diagnosis: 'Acute Coronary Syndrome',
          probability: patientData.age > 50 ? 'Moderate-High' : 'Moderate',
          supportingEvidence: [
            'Chest discomfort',
            patientData.age > 50 ? `Age >50 (${patientData.age})` : null,
            vitals.bp && vitals.bp.includes('/') && parseInt(vitals.bp.split('/')[0]) > 140 ? 'Hypertension' : null,
            history.includes('pressure') || history.includes('tight') ? 'Pressure-like quality' : null
          ].filter(Boolean),
          againstEvidence: [
            !history.includes('radiat') ? 'No radiation mentioned' : null,
            !history.includes('sweat') && !history.includes('diaphor') ? 'No diaphoresis' : null,
            duration.includes('week') ? 'Prolonged duration (weeks)' : null
          ].filter(Boolean),
          criticalActions: [
            'STAT ECG',
            'Troponin levels',
            'Chest X-ray',
            'Consider cardiology consult'
          ]
        });
        
        insights.redFlags.push({
          icon: Heart,
          text: 'Cardiac etiology must be ruled out - obtain ECG',
          severity: 'critical',
          timeframe: 'Immediate'
        });
      }
      
      // Check for PE risk factors
      if (chiefComplaint.includes('breath') || chiefComplaint.includes('chest')) {
        const peRiskFactors = [
          history.includes('sudden') ? 'Sudden onset' : null,
          vitals.hr > 100 ? 'Tachycardia' : null,
          history.includes('leg') || history.includes('calf') ? 'Possible DVT symptoms' : null,
          history.includes('pill') || history.includes('contraceptive') ? 'OCP use' : null
        ].filter(Boolean);
        
        if (peRiskFactors.length > 0) {
          differentials.push({
            diagnosis: 'Pulmonary Embolism',
            probability: peRiskFactors.length > 2 ? 'Moderate' : 'Low-Moderate',
            supportingEvidence: peRiskFactors,
            againstEvidence: [
              vitals.o2 && parseInt(vitals.o2) > 95 ? 'Normal O2 saturation' : null,
              !history.includes('sudden') ? 'Gradual onset' : null
            ].filter(Boolean),
            criticalActions: [
              'Calculate Wells score',
              'D-dimer if low probability',
              'CTA chest if high probability',
              'ECG to assess RV strain'
            ]
          });
        }
      }
      
      // Always include bronchitis for cough
      if (chiefComplaint.includes('cough')) {
        differentials.push({
          diagnosis: 'Acute Bronchitis',
          probability: vitals.temp && vitals.temp > 38 ? 'Moderate' : 'High',
          supportingEvidence: [
            'Cough as primary symptom',
            duration.includes('week') ? `Duration: ${duration}` : null,
            history.includes('phlegm') || history.includes('sputum') ? 'Productive cough' : null
          ].filter(Boolean),
          againstEvidence: [
            vitals.temp > 38.5 ? 'High fever suggests pneumonia' : null,
            exam.additionalFindings?.includes('crackles') ? 'Focal findings suggest pneumonia' : null
          ].filter(Boolean),
          criticalActions: [
            'Consider chest X-ray if symptoms persist',
            'Symptomatic treatment',
            'Patient education on expected course'
          ]
        });
      }
      
      insights.differentialDiagnoses = differentials;
    }
    
    // Analyze vital sign abnormalities
    if (vitals.hr > 100) {
      insights.keyFindings.push({
        icon: Activity,
        text: `Tachycardia (${vitals.hr} bpm) - consider pain, anxiety, infection, or cardiac etiology`,
        type: 'vital',
        significance: 'moderate'
      });
    }
    
    if (vitals.temp > 38) {
      insights.keyFindings.push({
        icon: Thermometer,
        text: `Fever (${vitals.temp}°C) - suggests infectious or inflammatory process`,
        type: 'vital',
        significance: 'high'
      });
    }
    
    if (vitals.bp) {
      const [systolic, diastolic] = vitals.bp.split('/').map(v => parseInt(v));
      if (systolic > 140 || diastolic > 90) {
        insights.keyFindings.push({
          icon: Heart,
          text: `Hypertension (${vitals.bp} mmHg) - assess for end-organ damage if severe`,
          type: 'vital',
          significance: systolic > 180 || diastolic > 120 ? 'critical' : 'moderate'
        });
      }
    }
    
    // Generate risk stratification
    insights.riskStratification = calculateRiskLevel(patientData, vitals);
    
    // Generate evidence-based diagnostic plan
    insights.diagnosticPlan = generateDiagnosticPlan(insights.differentialDiagnoses);
    
    // Add specific red flags based on presentation
    insights.redFlags = [...insights.redFlags, ...generateRedFlags(patientData, vitals, chiefComplaint)];
    
    // Generate targeted clinical pearls
    insights.clinicalPearls = generateClinicalPearls(chiefComplaint, patientData, vitals);
    
    return insights;
  };
  
  const calculateRiskLevel = (patientData, vitals) => {
    let riskScore = 0;
    const factors = [];
    
    // Age risk
    if (patientData.age > 65) {
      riskScore += 2;
      factors.push('Age > 65');
    } else if (patientData.age > 50) {
      riskScore += 1;
      factors.push('Age > 50');
    }
    
    // Vital sign risks
    if (vitals.hr > 120 || vitals.hr < 50) {
      riskScore += 2;
      factors.push('Significant tachycardia/bradycardia');
    }
    
    if (vitals.temp > 39 || vitals.temp < 36) {
      riskScore += 2;
      factors.push('Significant fever/hypothermia');
    }
    
    if (vitals.o2 && parseInt(vitals.o2) < 92) {
      riskScore += 3;
      factors.push('Hypoxemia');
    }
    
    // Determine risk level
    let level, color, recommendations;
    if (riskScore >= 4) {
      level = 'High Risk';
      color = 'red';
      recommendations = 'Consider admission, close monitoring, aggressive workup';
    } else if (riskScore >= 2) {
      level = 'Moderate Risk';
      color = 'yellow';
      recommendations = 'Thorough evaluation needed, consider observation';
    } else {
      level = 'Low Risk';
      color = 'green';
      recommendations = 'Outpatient management likely appropriate with close follow-up';
    }
    
    return { level, color, factors, recommendations };
  };
  
  const generateRedFlags = (patientData, vitals, chiefComplaint) => {
    const redFlags = [];
    
    // Chest pain red flags
    if (chiefComplaint.includes('chest')) {
      if (patientData.age > 40) {
        redFlags.push({
          icon: Heart,
          text: 'Age >40 with chest pain - cardiac workup mandatory',
          severity: 'high',
          timeframe: 'Immediate'
        });
      }
    }
    
    // Respiratory red flags
    if (chiefComplaint.includes('breath') || chiefComplaint.includes('cough')) {
      if (vitals.o2 && parseInt(vitals.o2) < 92) {
        redFlags.push({
          icon: Wind,
          text: 'Hypoxemia present - immediate intervention needed',
          severity: 'critical',
          timeframe: 'STAT'
        });
      }
    }
    
    // Sepsis red flags
    if (vitals.temp > 38 || vitals.temp < 36) {
      if (vitals.hr > 90 || vitals.rr > 20) {
        redFlags.push({
          icon: AlertTriangle,
          text: 'SIRS criteria met - evaluate for sepsis',
          severity: 'high',
          timeframe: 'Within 1 hour'
        });
      }
    }
    
    return redFlags;
  };
  
  const generateDiagnosticPlan = (differentials) => {
    const plan = [];
    const testsAdded = new Set();
    
    // Priority tests based on differentials
    differentials.forEach(diff => {
      diff.criticalActions.forEach(action => {
        if (!testsAdded.has(action)) {
          testsAdded.add(action);
          
          // Categorize the test
          let category, urgency;
          if (action.includes('STAT') || action.includes('ECG')) {
            category = 'Immediate';
            urgency = 'critical';
          } else if (action.includes('X-ray') || action.includes('CT')) {
            category = 'Imaging';
            urgency = 'high';
          } else if (action.includes('CBC') || action.includes('troponin') || action.includes('culture')) {
            category = 'Laboratory';
            urgency = 'high';
          } else {
            category = 'Additional';
            urgency = 'moderate';
          }
          
          plan.push({
            test: action,
            category,
            urgency,
            rationale: `To evaluate for ${diff.diagnosis}`
          });
        }
      });
    });
    
    // Sort by urgency
    return plan.sort((a, b) => {
      const urgencyOrder = { critical: 0, high: 1, moderate: 2 };
      return urgencyOrder[a.urgency] - urgencyOrder[b.urgency];
    });
  };
  
  const generateClinicalPearls = (chiefComplaint, patientData, vitals) => {
    const pearls = [];
    
    if (chiefComplaint.includes('cough')) {
      pearls.push({
        icon: '💡',
        text: 'Duration >3 weeks warrants chest X-ray to rule out TB, malignancy',
        category: 'diagnostic'
      });
      pearls.push({
        icon: '📊',
        text: 'Viral bronchitis accounts for >90% of acute cough cases',
        category: 'epidemiology'
      });
    }
    
    if (chiefComplaint.includes('chest')) {
      pearls.push({
        icon: '⚡',
        text: 'HEART score can risk-stratify chest pain patients for ACS',
        category: 'tool'
      });
      pearls.push({
        icon: '🎯',
        text: 'Reproducible chest wall tenderness reduces ACS likelihood but doesn\'t exclude it',
        category: 'exam'
      });
    }
    
    if (vitals.temp > 38) {
      pearls.push({
        icon: '🌡️',
        text: 'Lack of fever doesn\'t exclude infection in elderly or immunocompromised',
        category: 'clinical'
      });
    }
    
    // Add general pearls
    pearls.push({
      icon: '📝',
      text: 'Document time course clearly - acute vs subacute vs chronic changes management',
      category: 'documentation'
    });
    
    return pearls;
  };
  
  const insights = generateInsights();
  
  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };
  
  return (
    <div className="space-y-6">
      {/* Risk Stratification Card */}
      {insights.riskStratification && (
        <div className={`bg-white rounded-xl shadow-sm border-2 ${
          insights.riskStratification.color === 'red' ? 'border-red-300' :
          insights.riskStratification.color === 'yellow' ? 'border-yellow-300' :
          'border-green-300'
        } p-6`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Scale className="w-5 h-5 mr-2" />
              Risk Stratification
            </h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              insights.riskStratification.color === 'red' ? 'bg-red-100 text-red-800' :
              insights.riskStratification.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {insights.riskStratification.level}
            </span>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Risk Factors:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                {insights.riskStratification.factors.map((factor, idx) => (
                  <li key={idx} className="flex items-center">
                    <CheckSquare className="w-3 h-3 mr-2 text-gray-400" />
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
            <div className="pt-3 border-t">
              <p className="text-sm font-medium text-gray-700 mb-1">Recommendation:</p>
              <p className="text-sm text-gray-600">{insights.riskStratification.recommendations}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Main Clinical Insights Panel */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Brain className="w-5 h-5 text-purple-600 mr-2" />
            Clinical Reasoning Assistant
          </h3>
          <span className="text-xs text-gray-500">Evidence-based analysis</span>
        </div>
        
        <div className="space-y-4">
          {/* Red Flags Section - Always show if present */}
          {insights.redFlags.length > 0 && (
            <div className="border-2 border-red-300 rounded-lg overflow-hidden bg-red-50">
              <div className="px-4 py-3 bg-red-100">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="font-medium text-red-900">Critical Considerations</span>
                  <span className="ml-2 text-sm text-red-700">({insights.redFlags.length})</span>
                </div>
              </div>
              <div className="p-4 space-y-3">
                {insights.redFlags.map((flag, idx) => (
                  <div key={idx} className="flex items-start space-x-3 bg-white p-3 rounded-lg border border-red-200">
                    <flag.icon className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{flag.text}</p>
                      <p className="text-xs text-red-600 mt-1">Action needed: {flag.timeframe}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Differential Diagnosis with Evidence */}
          {insights.differentialDiagnoses.length > 0 && (
            <div className="border border-purple-200 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('differential')}
                className="w-full px-4 py-3 bg-purple-50 hover:bg-purple-100 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <Search className="w-5 h-5 text-purple-600 mr-2" />
                  <span className="font-medium text-purple-900">Differential Diagnosis Analysis</span>
                </div>
                <ChevronRight className={`w-4 h-4 text-purple-600 transform transition-transform ${
                  expandedSection === 'differential' ? 'rotate-90' : ''
                }`} />
              </button>
              {expandedSection === 'differential' && (
                <div className="p-4 space-y-4">
                  {insights.differentialDiagnoses.map((diff, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h5 className="font-medium text-gray-900">{diff.diagnosis}</h5>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            diff.probability === 'High' ? 'bg-red-100 text-red-700' :
                            diff.probability.includes('Moderate') ? 'bg-yellow-100 text-yellow-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {diff.probability} Probability
                          </span>
                        </div>
                        <button
                          onClick={() => setSelectedDifferential(selectedDifferential === idx ? null : idx)}
                          className="text-purple-600 hover:text-purple-700"
                        >
                          {selectedDifferential === idx ? 'Hide' : 'Details'}
                        </button>
                      </div>
                      
                      {selectedDifferential === idx && (
                        <div className="space-y-3 mt-3 pt-3 border-t">
                          <div>
                            <p className="text-sm font-medium text-green-700 mb-1">Supporting Evidence:</p>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {diff.supportingEvidence.map((evidence, eIdx) => (
                                <li key={eIdx} className="flex items-start">
                                  <CheckCircle className="w-3 h-3 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                                  {evidence}
                                </li>
                              ))}
                            </ul>
                          </div>
                          
                          {diff.againstEvidence.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-red-700 mb-1">Against Evidence:</p>
                              <ul className="text-sm text-gray-600 space-y-1">
                                {diff.againstEvidence.map((evidence, eIdx) => (
                                  <li key={eIdx} className="flex items-start">
                                    <XCircle className="w-3 h-3 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                                    {evidence}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          <div>
                            <p className="text-sm font-medium text-blue-700 mb-1">Next Steps:</p>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {diff.criticalActions.map((action, aIdx) => (
                                <li key={aIdx} className="flex items-start">
                                  <ChevronRight className="w-3 h-3 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {/* Diagnostic Plan */}
          {insights.diagnosticPlan.length > 0 && (
            <div className="border border-green-200 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('diagnostic')}
                className="w-full px-4 py-3 bg-green-50 hover:bg-green-100 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <TestTube className="w-5 h-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-900">Recommended Diagnostic Plan</span>
                </div>
                <ChevronRight className={`w-4 h-4 text-green-600 transform transition-transform ${
                  expandedSection === 'diagnostic' ? 'rotate-90' : ''
                }`} />
              </button>
              {expandedSection === 'diagnostic' && (
                <div className="p-4">
                  <div className="space-y-3">
                    {['critical', 'high', 'moderate'].map(urgency => {
                      const urgencyTests = insights.diagnosticPlan.filter(test => test.urgency === urgency);
                      if (urgencyTests.length === 0) return null;
                      
                      return (
                        <div key={urgency}>
                          <h6 className={`text-sm font-medium mb-2 ${
                            urgency === 'critical' ? 'text-red-700' :
                            urgency === 'high' ? 'text-orange-700' :
                            'text-yellow-700'
                          }`}>
                            {urgency.charAt(0).toUpperCase() + urgency.slice(1)} Priority:
                          </h6>
                          <div className="space-y-2 ml-4">
                            {urgencyTests.map((test, idx) => (
                              <div key={idx} className="flex items-start">
                                <ChevronRight className="w-3 h-3 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{test.test}</p>
                                  <p className="text-xs text-gray-600">{test.rationale}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Clinical Pearls */}
          {insights.clinicalPearls.length > 0 && (
            <div className="border border-yellow-200 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('pearls')}
                className="w-full px-4 py-3 bg-yellow-50 hover:bg-yellow-100 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
                  <span className="font-medium text-yellow-900">Clinical Pearls & Evidence</span>
                </div>
                <ChevronRight className={`w-4 h-4 text-yellow-600 transform transition-transform ${
                  expandedSection === 'pearls' ? 'rotate-90' : ''
                }`} />
              </button>
              {expandedSection === 'pearls' && (
                <div className="p-4 space-y-3">
                  {insights.clinicalPearls.map((pearl, idx) => (
                    <div key={idx} className="flex items-start space-x-3">
                      <span className="text-lg">{pearl.icon}</span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-700">{pearl.text}</p>
                        <span className="text-xs text-gray-500 mt-1 inline-block">
                          Category: {pearl.category}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {/* Key Clinical Findings */}
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
                <ChevronRight className={`w-4 h-4 text-blue-600 transform transition-transform ${
                  expandedSection === 'keyFindings' ? 'rotate-90' : ''
                }`} />
              </button>
              {expandedSection === 'keyFindings' && (
                <div className="p-4 space-y-2">
                  {insights.keyFindings.map((finding, idx) => (
                    <div key={idx} className="flex items-start space-x-2">
                      <finding.icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                        finding.significance === 'high' ? 'text-red-600' :
                        finding.significance === 'moderate' ? 'text-yellow-600' :
                        'text-blue-600'
                      }`} />
                      <p className="text-sm text-gray-700">{finding.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600 text-center">
            AI-generated analysis based on current clinical data. Always correlate with clinical judgment and local guidelines.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ClinicalInsightsPanel;