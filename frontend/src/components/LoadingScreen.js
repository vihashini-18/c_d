import React from 'react';
import { motion } from 'framer-motion';
import { FiHeart, FiActivity, FiShield, FiZap } from 'react-icons/fi';

const LoadingScreen = () => {
  const features = [
    { icon: FiHeart, text: 'Medical Expertise', delay: 0 },
    { icon: FiActivity, text: 'Real-time Analysis', delay: 0.2 },
    { icon: FiShield, text: 'Privacy Protected', delay: 0.4 },
    { icon: FiZap, text: 'AI-Powered', delay: 0.6 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
          className="mb-8"
        >
          <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">MC</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Chatbot</h1>
          <p className="text-gray-600">AI-Powered Healthcare Assistant</p>
        </motion.div>

        {/* Loading Animation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <div className="flex justify-center space-x-2">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className="w-3 h-3 bg-blue-600 rounded-full"
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
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="grid grid-cols-2 gap-4 max-w-md mx-auto"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 + feature.delay }}
                className="flex items-center space-x-2 p-3 bg-white rounded-lg shadow-sm"
              >
                <Icon className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">{feature.text}</span>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Loading Text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="mt-8"
        >
          <p className="text-gray-500 text-sm">Initializing AI models...</p>
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingScreen;
