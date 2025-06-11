import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles,
  Loader,
  Paperclip,
  Mic,
  Image as ImageIcon,
  FileText,
  AlertCircle
} from 'lucide-react';

const AIChat = ({ messages, onSendMessage, diagnoses }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputMessage]);
  
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const newMessage = {
        id: Date.now(),
        sender: 'user',
        message: inputMessage.trim(),
        timestamp: new Date().toISOString()
      };
      
      onSendMessage(newMessage);
      setInputMessage('');
      setIsTyping(true);
      
      // Simulate typing indicator
      setTimeout(() => setIsTyping(false), 1500);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const suggestedQuestions = [
    "What additional tests would help narrow down the diagnosis?",
    "Are there any red flags I should be concerned about?",
    "What's the typical treatment approach for the most likely diagnosis?",
    "Could this be a presentation of something more serious?"
  ];
  
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };
  
  return (
    <div 
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col resize-y" 
      style={{ 
        height: '700px', 
        minHeight: '500px', 
        maxHeight: '900px',
        position: 'relative'
      }}
    >
      {/* Resize Handle Indicator */}
      <div className="absolute bottom-0 right-0 w-6 h-6 cursor-ns-resize opacity-50 hover:opacity-100 transition-opacity">
        <svg className="w-full h-full text-gray-400" viewBox="0 0 24 24" fill="none">
          <path d="M8 15h8M8 19h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </div>
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold">AI Diagnostic Assistant</h3>
              <p className="text-xs text-blue-100">Always here to help refine diagnoses</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-yellow-300" />
            <span className="text-sm text-blue-100">Advanced AI</span>
          </div>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 custom-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                message.sender === 'user' ? 'bg-blue-600' : 'bg-gray-600'
              }`}>
                {message.sender === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>
              
              {/* Message Content */}
              <div className="flex flex-col">
                <div className={`rounded-lg px-4 py-2.5 ${
                  message.sender === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}>
                  {message.isSystemGenerated && (
                    <div className="flex items-center mb-1">
                      <AlertCircle className="w-3 h-3 mr-1" />
                      <span className="text-xs opacity-75">System Action</span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed">{message.message}</p>
                </div>
                <span className={`text-xs text-gray-500 mt-1 ${
                  message.sender === 'user' ? 'text-right' : 'text-left'
                }`}>
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
            </div>
          </div>
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Suggested Questions */}
      {messages.length <= 2 && (
        <div className="px-4 py-3 bg-gray-100 border-t border-gray-200">
          <p className="text-xs text-gray-600 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.slice(0, 2).map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInputMessage(question)}
                className="text-xs bg-white border border-gray-300 rounded-full px-3 py-1.5 hover:bg-gray-50 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about diagnoses, symptoms, or provide additional information..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none overflow-hidden"
              rows="1"
              style={{ maxHeight: '120px' }}
            />
            
            {/* Action Buttons */}
            <div className="absolute right-2 bottom-2 flex items-center space-x-1">
              <button className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors" title="Attach file">
                <Paperclip className="w-4 h-4" />
              </button>
              <button className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors" title="Voice input">
                <Mic className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className={`p-3 rounded-lg transition-all ${
              inputMessage.trim()
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* Context Info */}
        <div className="mt-2 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            AI has access to patient data and {diagnoses.length} differential diagnoses
          </p>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span className="flex items-center">
              <FileText className="w-3 h-3 mr-1" />
              Clinical data
            </span>
            <span className="flex items-center">
              <ImageIcon className="w-3 h-3 mr-1" />
              Lab results
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;