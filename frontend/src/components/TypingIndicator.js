import React from 'react';
import { motion } from 'framer-motion';
import { FiBot } from 'react-icons/fi';

const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex items-start space-x-3 max-w-3xl"
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center">
        <FiBot className="w-5 h-5" />
      </div>

      {/* Typing Animation */}
      <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl mr-12">
        <div className="flex items-center space-x-1">
          <span className="text-sm text-gray-600">AI is thinking</span>
          <div className="flex space-x-1">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className="w-2 h-2 bg-gray-400 rounded-full"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: index * 0.2
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TypingIndicator;
