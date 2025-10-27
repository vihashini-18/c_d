import React from 'react';
import { motion } from 'framer-motion';
import { FiCheckCircle, FiAlertTriangle, FiXCircle } from 'react-icons/fi';

const ConfidenceDisplay = ({ confidence }) => {
  if (!confidence) return null;

  const { score, level, recommendation } = confidence;

  const getConfidenceColor = (level) => {
    switch (level) {
      case 'high':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceIcon = (level) => {
    switch (level) {
      case 'high':
        return <FiCheckCircle className="w-4 h-4" />;
      case 'medium':
        return <FiAlertTriangle className="w-4 h-4" />;
      case 'low':
        return <FiXCircle className="w-4 h-4" />;
      default:
        return <FiAlertTriangle className="w-4 h-4" />;
    }
  };

  const getConfidenceText = (level) => {
    switch (level) {
      case 'high':
        return 'High Confidence';
      case 'medium':
        return 'Medium Confidence';
      case 'low':
        return 'Low Confidence';
      default:
        return 'Unknown Confidence';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(level)}`}
      title={recommendation}
    >
      {getConfidenceIcon(level)}
      <span>{getConfidenceText(level)}</span>
      <span className="font-mono">({(score * 100).toFixed(0)}%)</span>
    </motion.div>
  );
};

export default ConfidenceDisplay;
