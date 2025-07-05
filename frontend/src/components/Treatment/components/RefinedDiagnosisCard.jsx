import React from 'react';
import { 
  Check, 
  AlertCircle, 
  TrendingUp, 
  Brain,
  Sparkles,
  ChevronRight
} from 'lucide-react';

const RefinedDiagnosisCard = ({ diagnosis, index, isSelected, onSelect, testResults }) => {
  const getConfidenceColor = (confidence) => {
    switch (confidence?.toLowerCase()) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200';
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };
  
  const getProbabilityColor = (probability) => {
    const prob = probability * 100;
    if (prob >= 70) return 'from-green-500 to-green-600';
    if (prob >= 40) return 'from-yellow-500 to-yellow-600';
    return 'from-red-500 to-red-600';
  };
  
  // Check if test results support this diagnosis
  const getSupportingTests = () => {
    if (!testResults || Object.keys(testResults).length === 0) return [];
    
    // Mock logic - in real app, this would be more sophisticated
    const supporting = [];
    Object.entries(testResults).forEach(([, result]) => {
      if (result.status === 'completed' && result.interpretation) {
        if (diagnosis.name.includes('Pneumonia') && result.testName?.includes('Chest X-ray')) {
          supporting.push({
            name: result.testName,
            supports: result.interpretation.includes('consolidation') || result.interpretation.includes('infiltrate')
          });
        }
        // Add more test-diagnosis correlations
      }
    });
    return supporting;
  };
  
  const supportingTests = getSupportingTests();
  
  return (
    <div
      onClick={onSelect}
      className={`
        relative p-6 border-2 rounded-xl cursor-pointer transition-all duration-200
        ${isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-lg' 
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md bg-white'
        }
      `}
    >
      {/* Selection indicator */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center shadow-md">
          <Check className="w-5 h-5 text-white" />
        </div>
      )}
      
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center mb-1">
            <span className="text-lg font-semibold text-gray-900 mr-2">
              {index + 1}. {diagnosis.name}
            </span>
            {index === 0 && (
              <span className="px-2 py-0.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-medium rounded-full">
                Most Likely
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">ICD-10: {diagnosis.icd10}</p>
        </div>
        
        {/* Confidence Badge */}
        <div className={`px-3 py-1.5 rounded-lg border ${getConfidenceColor(diagnosis.confidence)}`}>
          <p className="text-xs font-medium">{diagnosis.confidence || 'Moderate'}</p>
        </div>
      </div>
      
      {/* Probability Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">Probability</span>
          <span className="text-sm font-bold text-gray-900">
            {(diagnosis.probability * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className={`h-full bg-gradient-to-r ${getProbabilityColor(diagnosis.probability)} rounded-full transition-all duration-500`}
            style={{ width: `${diagnosis.probability * 100}%` }}
          />
        </div>
      </div>
      
      {/* AI Insights */}
      {diagnosis.clinicalPearls && (
        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="flex items-start">
            <Sparkles className="w-4 h-4 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-medium text-purple-900 mb-1">AI Clinical Insight</p>
              <p className="text-xs text-purple-800">{diagnosis.clinicalPearls}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Supporting Test Results */}
      {supportingTests.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-medium text-gray-700 mb-2">Test Result Correlation:</p>
          <div className="space-y-1">
            {supportingTests.map((test, idx) => (
              <div key={idx} className="flex items-center text-xs">
                {test.supports ? (
                  <Check className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <AlertCircle className="w-3 h-3 text-yellow-500 mr-1" />
                )}
                <span className={test.supports ? 'text-green-700' : 'text-yellow-700'}>
                  {test.name} {test.supports ? 'supports' : 'questions'} this diagnosis
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Key Factors */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">Supporting Factors</p>
          <ul className="space-y-1">
            {diagnosis.supportingFactors?.slice(0, 2).map((factor, idx) => (
              <li key={idx} className="text-xs text-gray-700 flex items-start">
                <TrendingUp className="w-3 h-3 text-green-500 mr-1 flex-shrink-0 mt-0.5" />
                {factor}
              </li>
            ))}
          </ul>
        </div>
        {diagnosis.contradictingFactors && diagnosis.contradictingFactors.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">Considerations</p>
            <ul className="space-y-1">
              {diagnosis.contradictingFactors.slice(0, 2).map((factor, idx) => (
                <li key={idx} className="text-xs text-gray-700 flex items-start">
                  <AlertCircle className="w-3 h-3 text-yellow-500 mr-1 flex-shrink-0 mt-0.5" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {/* Select button hint */}
      <div className="mt-4 flex items-center justify-end text-xs text-gray-500">
        <span>Click to select</span>
        <ChevronRight className="w-3 h-3 ml-1" />
      </div>
    </div>
  );
};

export default RefinedDiagnosisCard;