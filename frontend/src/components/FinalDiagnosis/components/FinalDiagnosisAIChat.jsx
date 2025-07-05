import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Stethoscope } from 'lucide-react';

const FinalDiagnosisAIChat = ({ messages, onSendMessage, selectedDiagnosis }) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      const message = {
        id: Date.now(),
        sender: 'user',
        message: inputMessage,
        timestamp: new Date().toISOString()
      };
      onSendMessage(message);
      setInputMessage('');
    }
  };
  
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit' 
    });
  };
  
  const suggestedQuestions = [
    "What additional tests might confirm this diagnosis?",
    "Are there any red flags I should watch for?",
    "What is the typical prognosis for this condition?",
    "Should I consider any specialist referrals?"
  ];
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-[600px]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Bot className="w-5 h-5 mr-2 text-blue-600" />
              AI Diagnostic Assistant
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Discuss the final diagnosis and clinical decision-making
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Sparkles className="w-4 h-4 text-yellow-500" />
            <span>AI-Powered</span>
          </div>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.sender === 'user' ? 'bg-blue-600' : 'bg-gradient-to-r from-blue-500 to-purple-500'
              }`}>
                {message.sender === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>
              <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`px-4 py-2 rounded-lg ${
                  message.sender === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                </div>
                <span className="text-xs text-gray-400 mt-1">
                  {formatTime(message.timestamp)}
                </span>
              </div>
            </div>
          </div>
        ))}
        
        {/* Selected Diagnosis Indicator */}
        {selectedDiagnosis && messages.length === 1 && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-start">
              <Stethoscope className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900 mb-1">Current Selection</p>
                <p className="text-sm text-blue-800">
                  You've selected <strong>{selectedDiagnosis.name}</strong> as the final diagnosis. 
                  Feel free to ask any questions about this diagnosis or discuss treatment considerations.
                </p>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Suggested Questions */}
      {messages.length <= 2 && (
        <div className="px-6 py-3 border-t border-gray-100 bg-gray-50">
          <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="text-xs px-3 py-1.5 bg-white border border-gray-300 rounded-full text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Input Area */}
      <form onSubmit={handleSubmit} className="px-6 py-4 border-t border-gray-200">
        <div className="flex space-x-3">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about the diagnosis, prognosis, or treatment considerations..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default FinalDiagnosisAIChat;