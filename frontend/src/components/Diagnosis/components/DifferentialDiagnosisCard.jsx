import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const DifferentialDiagnosisCard = ({ diagnosis, index, onFeedback }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [userVote, setUserVote] = useState(null);
  
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'mild':
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };
  
  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 'high':
        return 'high severity';
      case 'moderate':
        return 'moderate severity';
      case 'mild':
        return 'mild severity';
      default:
        return severity;
    }
  };
  
  const getProbabilityColor = (probability) => {
    if (probability >= 70) return 'text-red-600';
    if (probability >= 50) return 'text-yellow-600';
    return 'text-gray-600';
  };
  
  const handleVote = (voteType) => {
    const newVote = userVote === voteType ? null : voteType;
    setUserVote(newVote);
    
    if (newVote) {
      onFeedback(diagnosis.id, newVote === 'agree');
    }
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-4 flex-1">
            {/* Number Badge */}
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-semibold">{index + 1}</span>
              </div>
            </div>
            
            {/* Diagnosis Info */}
            <div className="flex-1">
              <div className="flex items-center flex-wrap gap-3 mb-2">
                <h3 className="text-lg font-semibold text-gray-900">
                  {diagnosis.name}
                </h3>
                <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getSeverityColor(diagnosis.severity)}`}>
                  {getSeverityLabel(diagnosis.severity)}
                </span>
                <span className="text-sm text-gray-500">
                  ICD-10: {diagnosis.icd10}
                </span>
              </div>
              
              <p className="text-gray-600 text-sm">
                {diagnosis.supportingFactors.length > 0 
                  ? `Patient presents with ${diagnosis.supportingFactors[0].toLowerCase()}. ` 
                  : ''}
                Physical exam findings are consistent with this diagnosis.
              </p>
            </div>
            
            {/* Probability */}
            <div className="flex-shrink-0 text-right">
              <div className={`text-3xl font-bold ${getProbabilityColor(diagnosis.probability * 100)}`}>
                {Math.round(diagnosis.probability * 100)}%
              </div>
              <div className="text-xs text-gray-500 uppercase tracking-wide">
                Probability
              </div>
            </div>
          </div>
        </div>
        
        {/* Supporting and Contradicting Factors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Supporting Factors */}
          <div>
            <div className="flex items-center mb-2">
              <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
              <h4 className="font-medium text-green-800">Supporting Factors</h4>
            </div>
            <ul className="space-y-1">
              {diagnosis.supportingFactors.map((factor, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Contradicting Factors */}
          <div>
            <div className="flex items-center mb-2">
              <XCircle className="w-4 h-4 text-red-600 mr-2" />
              <h4 className="font-medium text-red-800">Contradicting Factors</h4>
            </div>
            <ul className="space-y-1">
              {diagnosis.contradictingFactors.map((factor, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start">
                  <span className="text-red-600 mr-2">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        {/* Clinical Pearl */}
        {diagnosis.clinicalPearls && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="flex items-start">
              <Info className="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-blue-900">
                <span className="font-medium">Clinical Pearl:</span> {diagnosis.clinicalPearls}
              </p>
            </div>
          </div>
        )}
        
        {/* Feedback Section */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Is this diagnosis helpful?</span>
            <button
              onClick={() => handleVote('agree')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center space-x-2 ${
                userVote === 'agree'
                  ? 'bg-green-100 text-green-700 border-2 border-green-300'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-2 border-transparent'
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              <span>Agree</span>
            </button>
            <button
              onClick={() => handleVote('disagree')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center space-x-2 ${
                userVote === 'disagree'
                  ? 'bg-red-100 text-red-700 border-2 border-red-300'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-2 border-transparent'
              }`}
            >
              <ThumbsDown className="w-4 h-4" />
              <span>Disagree</span>
            </button>
          </div>
          
          {/* Expand/Collapse Button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Show Details
              </>
            )}
          </button>
        </div>
        
        {/* Expanded Details */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t space-y-4">
            {/* Confidence Level */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Diagnostic Confidence</h4>
              <div className="flex items-center space-x-4">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-full rounded-full ${
                      diagnosis.confidence === 'high' ? 'bg-green-500' :
                      diagnosis.confidence === 'moderate' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ 
                      width: diagnosis.confidence === 'high' ? '90%' :
                             diagnosis.confidence === 'moderate' ? '60%' :
                             '30%'
                    }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {diagnosis.confidence} confidence
                </span>
              </div>
            </div>
            
            {/* Recommended Actions */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Recommended Diagnostic Tests</h4>
              <div className="flex flex-wrap gap-2">
                {diagnosis.recommendedActions.map((action, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium"
                  >
                    {action}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DifferentialDiagnosisCard;