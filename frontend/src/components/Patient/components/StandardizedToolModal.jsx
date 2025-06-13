import React, { useState } from 'react';
import { X, ChevronRight, ChevronLeft, CheckCircle, AlertCircle } from 'lucide-react';

const StandardizedToolModal = ({ tool, onClose, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  const responseOptions = [
    { value: 0, label: 'Not at all' },
    { value: 1, label: 'Several days' },
    { value: 2, label: 'More than half the days' },
    { value: 3, label: 'Nearly every day' }
  ];

  const handleAnswer = (value) => {
    const newAnswers = { ...answers, [currentQuestion]: value };
    setAnswers(newAnswers);

    if (currentQuestion < tool.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      calculateResults(newAnswers);
    }
  };

  const calculateResults = (allAnswers) => {
    const total = Object.values(allAnswers).reduce((sum, val) => sum + val, 0);
    let severity = '';
    let interpretation = '';
    let recommendations = [];

    if (tool.id === 'phq9') {
      if (total <= 4) {
        severity = 'Minimal';
        interpretation = 'No significant depressive symptoms';
        recommendations = ['Continue monitoring', 'Promote wellness activities'];
      } else if (total <= 9) {
        severity = 'Mild';
        interpretation = 'Mild depressive symptoms present';
        recommendations = ['Consider watchful waiting', 'Lifestyle modifications', 'Follow up in 2-4 weeks'];
      } else if (total <= 14) {
        severity = 'Moderate';
        interpretation = 'Moderate depression likely';
        recommendations = ['Consider therapy', 'Evaluate for antidepressants', 'Close follow-up needed'];
      } else if (total <= 19) {
        severity = 'Moderately Severe';
        interpretation = 'Moderately severe depression';
        recommendations = ['Therapy recommended', 'Antidepressants indicated', 'Consider psychiatry referral'];
      } else {
        severity = 'Severe';
        interpretation = 'Severe depression';
        recommendations = ['Urgent mental health referral', 'Immediate treatment needed', 'Assess safety'];
      }
    } else if (tool.id === 'gad7') {
      if (total <= 4) {
        severity = 'Minimal';
        interpretation = 'No significant anxiety';
        recommendations = ['Reassurance', 'Stress management education'];
      } else if (total <= 9) {
        severity = 'Mild';
        interpretation = 'Mild anxiety symptoms';
        recommendations = ['Self-help resources', 'Relaxation techniques', 'Monitor symptoms'];
      } else if (total <= 14) {
        severity = 'Moderate';
        interpretation = 'Moderate anxiety likely';
        recommendations = ['Consider therapy', 'Evaluate need for medication', 'Regular follow-up'];
      } else {
        severity = 'Severe';
        interpretation = 'Severe anxiety';
        recommendations = ['Therapy strongly recommended', 'Medication likely needed', 'Consider psychiatry'];
      }
    }

    setShowResults(true);
    
    // Store results
    const results = {
      toolId: tool.id,
      toolName: tool.name,
      score: total,
      severity,
      interpretation,
      recommendations,
      answers: allAnswers,
      completedAt: new Date().toISOString()
    };

    // Auto-complete after showing results
    setTimeout(() => {
      onComplete(results);
    }, 3000);
  };

  const progress = ((currentQuestion + 1) / tool.questions.length) * 100;

  if (showResults) {
    const total = Object.values(answers).reduce((sum, val) => sum + val, 0);
    const maxScore = tool.questions.length * 3;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">{tool.name} Results</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          <div className="p-6">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-4">
                <CheckCircle className="w-10 h-10 text-blue-600" />
              </div>
              <h4 className="text-2xl font-bold text-gray-900 mb-2">
                Score: {total}/{maxScore}
              </h4>
              <p className="text-lg text-gray-600">Assessment Complete</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h5 className="font-semibold text-gray-900 mb-2">Clinical Interpretation</h5>
              <p className="text-gray-700">
                Based on the responses, this indicates <strong>{getSeverityForTool(tool.id, total)}</strong> symptoms.
              </p>
            </div>

            <div className="bg-blue-50 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2">Recommended Actions</h5>
              <ul className="space-y-1">
                {getRecommendationsForScore(tool.id, total).map((rec, idx) => (
                  <li key={idx} className="text-blue-800 flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => onComplete({ score: total, answers })}
              className="mt-6 w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Save Results & Continue
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xl font-semibold text-gray-900">{tool.name}</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Question {currentQuestion + 1} of {tool.questions.length}
          </p>
        </div>

        <div className="p-6">
          <div className="mb-8">
            <p className="text-lg text-gray-900 mb-1">
              Over the last 2 weeks, how often has the patient been bothered by:
            </p>
            <h4 className="text-xl font-medium text-gray-900">
              {tool.questions[currentQuestion]}
            </h4>
          </div>

          <div className="space-y-3">
            {responseOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleAnswer(option.value)}
                className="w-full p-4 text-left rounded-lg border-2 border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full border-2 border-gray-300 mr-3 group-hover:border-blue-500" />
                    <span className="text-gray-900 font-medium">{option.label}</span>
                  </div>
                  <span className="text-gray-500">({option.value})</span>
                </div>
              </button>
            ))}
          </div>

          {currentQuestion > 0 && (
            <button
              onClick={() => setCurrentQuestion(currentQuestion - 1)}
              className="mt-6 px-4 py-2 text-gray-600 hover:text-gray-900 font-medium flex items-center"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous Question
            </button>
          )}
        </div>

        {/* Warning for concerning answers */}
        {tool.id === 'phq9' && currentQuestion === 8 && answers[8] > 0 && (
          <div className="px-6 pb-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-900">Important Notice</p>
                  <p className="text-sm text-red-800 mt-1">
                    The patient has indicated thoughts of self-harm. Please ensure immediate safety assessment and appropriate intervention.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper functions
const getSeverityForTool = (toolId, score) => {
  if (toolId === 'phq9') {
    if (score <= 4) return 'minimal depressive';
    if (score <= 9) return 'mild depressive';
    if (score <= 14) return 'moderate depressive';
    if (score <= 19) return 'moderately severe depressive';
    return 'severe depressive';
  } else if (toolId === 'gad7') {
    if (score <= 4) return 'minimal anxiety';
    if (score <= 9) return 'mild anxiety';
    if (score <= 14) return 'moderate anxiety';
    return 'severe anxiety';
  }
  return 'significant';
};

const getRecommendationsForScore = (toolId, score) => {
  if (toolId === 'phq9') {
    if (score <= 4) return ['Continue routine monitoring', 'Encourage healthy lifestyle'];
    if (score <= 9) return ['Consider watchful waiting', 'Provide self-help resources', 'Schedule follow-up in 2-4 weeks'];
    if (score <= 14) return ['Consider psychotherapy', 'Evaluate for antidepressant therapy', 'Schedule close follow-up'];
    if (score <= 19) return ['Psychotherapy recommended', 'Antidepressant therapy likely indicated', 'Consider psychiatry referral'];
    return ['Immediate intervention needed', 'Refer to mental health specialist', 'Assess safety and support system'];
  } else if (toolId === 'gad7') {
    if (score <= 4) return ['Provide reassurance', 'Basic stress management education'];
    if (score <= 9) return ['Self-help resources', 'Teach relaxation techniques', 'Monitor progress'];
    if (score <= 14) return ['Consider cognitive behavioral therapy', 'May benefit from medication', 'Regular follow-up'];
    return ['Therapy strongly recommended', 'Medication likely beneficial', 'Consider psychiatry consultation'];
  }
  return ['Further evaluation recommended'];
};

export default StandardizedToolModal;