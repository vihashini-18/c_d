import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiExternalLink, FiChevronDown, FiChevronUp, FiBookOpen } from 'react-icons/fi';

const CitationDisplay = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const visibleSources = isExpanded ? sources : sources.slice(0, 2);
  const hasMoreSources = sources.length > 2;

  return (
    <div className="mt-2">
      <div className="flex items-center space-x-2 text-xs text-gray-600 mb-2">
        <FiBookOpen className="w-4 h-4" />
        <span className="font-medium">Sources ({sources.length})</span>
      </div>
      
      <div className="space-y-2">
        {visibleSources.map((source, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start space-x-2 p-2 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
              {index + 1}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="text-sm text-gray-900 line-clamp-2">
                {source.content || source.text || 'Source content not available'}
              </div>
              
              {source.metadata && (
                <div className="mt-1 text-xs text-gray-500">
                  {source.metadata.source && (
                    <span className="font-medium">{source.metadata.source}</span>
                  )}
                  {source.metadata.category && (
                    <span className="ml-2 px-2 py-0.5 bg-gray-200 rounded text-xs">
                      {source.metadata.category}
                    </span>
                  )}
                  {source.score && (
                    <span className="ml-2 text-blue-600">
                      ({(source.score * 100).toFixed(1)}% match)
                    </span>
                  )}
                </div>
              )}
            </div>
            
            {source.url && (
              <motion.a
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-shrink-0 p-1 text-gray-400 hover:text-blue-600 transition-colors"
                title="Open source"
              >
                <FiExternalLink className="w-4 h-4" />
              </motion.a>
            )}
          </motion.div>
        ))}
      </div>
      
      {hasMoreSources && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-700 transition-colors"
        >
          <span>
            {isExpanded ? 'Show less' : `Show ${sources.length - 2} more sources`}
          </span>
          {isExpanded ? (
            <FiChevronUp className="w-3 h-3" />
          ) : (
            <FiChevronDown className="w-3 h-3" />
          )}
        </motion.button>
      )}
    </div>
  );
};

export default CitationDisplay;
