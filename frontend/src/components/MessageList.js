import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '../context/ThemeContext';

// Components
import MessageBubble from './MessageBubble';
import ConfidenceDisplay from './ConfidenceDisplay';
import CitationDisplay from './CitationDisplay';
import EmergencyAlert from './EmergencyAlert';

// Icons
import { FiUser, FiBot, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';

const MessageList = ({ messages }) => {
  const { theme } = useTheme();

  const getMessageIcon = (message) => {
    if (message.type === 'user') {
      return <FiUser className="w-5 h-5" />;
    } else if (message.emergency?.is_emergency) {
      return <FiAlertTriangle className="w-5 h-5 text-red-500" />;
    } else {
      return <FiBot className="w-5 h-5" />;
    }
  };

  const getMessageVariant = (message) => {
    if (message.type === 'user') {
      return 'user';
    } else if (message.emergency?.is_emergency) {
      return 'emergency';
    } else if (message.confidence?.level === 'high') {
      return 'assistant-high';
    } else if (message.confidence?.level === 'medium') {
      return 'assistant-medium';
    } else {
      return 'assistant-low';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : message.emergency?.is_emergency
                    ? 'bg-red-100 text-red-600'
                    : 'bg-gray-100 text-gray-600'
              }`}>
                {getMessageIcon(message)}
              </div>

              {/* Message Content */}
              <div className={`flex-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                <MessageBubble
                  message={message}
                  variant={getMessageVariant(message)}
                />

                {/* Message Metadata */}
                <div className={`mt-2 text-xs text-gray-500 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className="flex items-center space-x-2">
                    <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                    
                    {message.type === 'assistant' && (
                      <>
                        {message.confidence && (
                          <ConfidenceDisplay confidence={message.confidence} />
                        )}
                        
                        {message.emergency?.is_emergency && (
                          <span className="text-red-500 font-medium">
                            Emergency Detected
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Citations */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2">
                    <CitationDisplay sources={message.sources} />
                  </div>
                )}

                {/* Emergency Actions */}
                {message.emergency?.is_emergency && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <FiAlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-red-800">Emergency Detected</h4>
                        <p className="text-sm text-red-700 mt-1">
                          {message.emergency.recommended_actions?.join(', ')}
                        </p>
                        <div className="mt-2 flex space-x-2">
                          <button className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors">
                            Call 911
                          </button>
                          <button className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 transition-colors">
                            Find Hospital
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Emotion Analysis */}
                {message.emotion && (
                  <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                    <span className="font-medium text-blue-800">Emotion: </span>
                    <span className="text-blue-700">{message.emotion.primary_emotion}</span>
                    {message.emotion.intensity > 0.7 && (
                      <span className="ml-2 text-orange-600 font-medium">(High Intensity)</span>
                    )}
                  </div>
                )}

                {/* Medical Entities */}
                {message.medical_entities && Object.keys(message.medical_entities).length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs text-gray-600 mb-1">Detected Medical Terms:</div>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(message.medical_entities).map(([category, terms]) => (
                        terms.length > 0 && (
                          <div key={category} className="text-xs">
                            <span className="font-medium text-gray-700">{category}:</span>
                            <span className="text-gray-600 ml-1">
                              {terms.slice(0, 3).join(', ')}
                              {terms.length > 3 && ` +${terms.length - 3} more`}
                            </span>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default MessageList;
