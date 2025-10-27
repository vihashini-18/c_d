import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertTriangle, FiX, FiPhone, FiMapPin } from 'react-icons/fi';

const EmergencyAlert = ({ message, onClose }) => {
  if (!message || !message.is_emergency) return null;

  const { level, recommended_actions, confidence } = message;

  const getAlertColor = (level) => {
    switch (level) {
      case 'critical':
        return 'bg-red-600 border-red-700';
      case 'high':
        return 'bg-red-500 border-red-600';
      case 'medium':
        return 'bg-orange-500 border-orange-600';
      case 'low':
        return 'bg-yellow-500 border-yellow-600';
      default:
        return 'bg-red-500 border-red-600';
    }
  };

  const getAlertText = (level) => {
    switch (level) {
      case 'critical':
        return 'CRITICAL EMERGENCY';
      case 'high':
        return 'HIGH PRIORITY EMERGENCY';
      case 'medium':
        return 'MEDIUM PRIORITY EMERGENCY';
      case 'low':
        return 'LOW PRIORITY EMERGENCY';
      default:
        return 'EMERGENCY DETECTED';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -50, scale: 0.95 }}
        transition={{ duration: 0.3, type: "spring", stiffness: 300, damping: 30 }}
        className="fixed top-4 left-4 right-4 z-50 max-w-2xl mx-auto"
      >
        <div className={`${getAlertColor(level)} text-white rounded-lg shadow-2xl border-2`}>
          <div className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1 }}
                  className="flex-shrink-0"
                >
                  <FiAlertTriangle className="w-6 h-6" />
                </motion.div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-bold mb-2">
                    {getAlertText(level)}
                  </h3>
                  
                  <p className="text-sm mb-3 opacity-90">
                    The system has detected a potential medical emergency in your message.
                  </p>
                  
                  {recommended_actions && recommended_actions.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-semibold mb-2">Recommended Actions:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {recommended_actions.map((action, index) => (
                          <li key={index}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => window.open('tel:911')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white text-red-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                    >
                      <FiPhone className="w-4 h-4" />
                      <span>Call 911</span>
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => window.open('https://maps.google.com/?q=emergency+room+near+me')}
                      className="flex items-center space-x-2 px-4 py-2 bg-white text-red-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                    >
                      <FiMapPin className="w-4 h-4" />
                      <span>Find Hospital</span>
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={onClose}
                      className="flex items-center space-x-2 px-4 py-2 bg-red-700 text-white rounded-lg font-semibold hover:bg-red-800 transition-colors"
                    >
                      <FiX className="w-4 h-4" />
                      <span>Dismiss</span>
                    </motion.button>
                  </div>
                  
                  {confidence && (
                    <div className="mt-3 text-xs opacity-75">
                      Detection confidence: {(confidence * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default EmergencyAlert;
