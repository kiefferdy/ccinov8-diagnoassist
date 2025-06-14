import React from 'react';
import { 
  Activity, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  Lightbulb,
  FileText,
  TestTube,
  Brain,
  User,
  Stethoscope,
  ClipboardCheck
} from 'lucide-react';

const DiagnosticSummaryPanel = ({ patientData, refinedDiagnoses, testResults }) => {
  // Get all key information
  const getAllFindings = () => {
    const findings = [];
    
    // Clinical Assessment findings
    if (patientData.chiefComplaintDetails && patientData.chiefComplaintDetails.length > 0) {
      const symptoms = patientData.chiefComplaintDetails
        .filter(q => q.answer && !q.skipped)
        .map(q => q.answer);
      
      if (symptoms.length > 0) {
        findings.push({
          category: 'Symptoms',
          items: symptoms.map(symptom => ({
            type: 'symptom',
            text: symptom,
            icon: ClipboardCheck
          }))
        });
      }
    }
    
    // Physical exam findings
    if (patientData.physicalExam) {
      const exam = patientData.physicalExam;
      const examFindings = [];
      
      if (exam.temperature && parseFloat(exam.temperature) > 37.5) {
        examFindings.push({ 
          type: 'warning', 
          text: `Elevated temperature: ${exam.temperature}°C`, 
          icon: AlertCircle 
        });
      }
      if (exam.bloodPressure) {
        const [systolic] = exam.bloodPressure.split('/').map(Number);
        if (systolic > 140) {
          examFindings.push({ 
            type: 'warning', 
            text: `Elevated blood pressure: ${exam.bloodPressure}`, 
            icon: AlertCircle 
          });
        } else {
          examFindings.push({ 
            type: 'normal', 
            text: `Blood pressure: ${exam.bloodPressure}`, 
            icon: Stethoscope 
          });
        }
      }
      if (exam.heartRate) {
        examFindings.push({ 
          type: 'info', 
          text: `Heart rate: ${exam.heartRate} bpm`, 
          icon: Activity 
        });
      }
      if (exam.oxygenSaturation) {
        examFindings.push({ 
          type: 'info', 
          text: `O2 saturation: ${exam.oxygenSaturation}%`, 
          icon: Activity 
        });
      }
      
      if (examFindings.length > 0) {
        findings.push({
          category: 'Physical Examination',
          items: examFindings
        });
      }
      
      if (exam.additionalFindings) {
        findings.push({
          category: 'Additional Exam Findings',
          items: [{
            type: 'info',
            text: exam.additionalFindings,
            icon: FileText
          }]
        });
      }
    }
    
    // Test results
    const testFindings = [];
    Object.values(testResults || {}).forEach(result => {
      if (result.status === 'completed') {
        testFindings.push({ 
          type: 'test', 
          text: `${result.testName}: ${result.value || 'Completed'} ${result.unit || ''} ${result.interpretation ? `(${result.interpretation})` : ''}`, 
          icon: TestTube 
        });
      }
    });
    
    if (testFindings.length > 0) {
      findings.push({
        category: 'Test Results',
        items: testFindings
      });
    }
    
    // Medical history if relevant
    if (patientData.medicalHistory && patientData.medicalHistory.length > 0) {
      findings.push({
        category: 'Relevant Medical History',
        items: patientData.medicalHistory.map(history => ({
          type: 'history',
          text: history,
          icon: User
        }))
      });
    }
    
    return findings;
  };
  
  const allFindings = getAllFindings();
  
  return (
    <div className="space-y-4">
      {/* Clinical Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <Lightbulb className="w-5 h-5 text-yellow-500 mr-2" />
          Clinical Summary
        </h3>
        
        {allFindings.length > 0 ? (
          <div className="space-y-4">
            {allFindings.map((category, catIdx) => (
              <div key={catIdx}>
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-2">
                  {category.category}
                </p>
                <div className="space-y-1">
                  {category.items.map((finding, idx) => {
                    const Icon = finding.icon;
                    return (
                      <div key={idx} className="flex items-start text-sm">
                        <Icon className={`w-4 h-4 mr-2 flex-shrink-0 mt-0.5 ${
                          finding.type === 'warning' ? 'text-amber-500' : 
                          finding.type === 'test' ? 'text-blue-500' :
                          finding.type === 'symptom' ? 'text-purple-500' :
                          finding.type === 'history' ? 'text-gray-500' :
                          'text-gray-400'
                        }`} />
                        <span className="text-gray-700">{finding.text}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No clinical findings documented</p>
        )}
      </div>
      
      {/* Possible Diagnoses */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <Brain className="w-5 h-5 text-blue-600 mr-2" />
          Possible Diagnoses
        </h3>
        
        <div className="space-y-2">
          {refinedDiagnoses.map((diagnosis, idx) => (
            <div key={diagnosis.id} className="flex items-center justify-between">
              <span className="text-xs text-gray-700 truncate flex-1 mr-2">
                {idx + 1}. {diagnosis.name}
              </span>
              <div className="flex items-center">
                <div className="w-16 bg-gray-200 rounded-full h-1.5 mr-2">
                  <div 
                    className={`h-1.5 rounded-full ${
                      diagnosis.probability > 0.7 ? 'bg-green-500' :
                      diagnosis.probability > 0.4 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${diagnosis.probability * 100}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-600 w-10 text-right">
                  {(diagnosis.probability * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <Activity className="w-5 h-5 text-purple-600 mr-2" />
          Assessment Progress
        </h3>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs text-gray-500 mb-1">Tests Completed</p>
            <p className="text-lg font-bold text-gray-900">
              {Object.values(testResults || {}).filter(t => t.status === 'completed').length}/
              {Object.keys(testResults || {}).length}
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs text-gray-500 mb-1">High Confidence</p>
            <p className="text-lg font-bold text-gray-900">
              {refinedDiagnoses.filter(d => d.confidence === 'High' || d.confidence === 'high').length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticSummaryPanel;