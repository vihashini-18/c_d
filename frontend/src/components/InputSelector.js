import React from 'react';
import { motion } from 'framer-motion';
import { FiFileText, FiMic, FiImage, FiVideo } from 'react-icons/fi';

const InputSelector = ({ selectedMode, onModeChange }) => {
  const inputModes = [
    {
      id: 'text',
      name: 'Text',
      icon: FiFileText,
      description: 'Type your message',
      color: 'blue'
    },
    {
      id: 'audio',
      name: 'Voice',
      icon: FiMic,
      description: 'Speak your message',
      color: 'green'
    },
    {
      id: 'image',
      name: 'Image',
      icon: FiImage,
      description: 'Upload an image',
      color: 'purple'
    }
  ];

  const getColorClasses = (color, isSelected) => {
    const colorMap = {
      blue: isSelected 
        ? 'bg-blue-100 border-blue-500 text-blue-700' 
        : 'hover:bg-blue-50 border-blue-200 text-blue-600',
      green: isSelected 
        ? 'bg-green-100 border-green-500 text-green-700' 
        : 'hover:bg-green-50 border-green-200 text-green-600',
      purple: isSelected 
        ? 'bg-purple-100 border-purple-500 text-purple-700' 
        : 'hover:bg-purple-50 border-purple-200 text-purple-600'
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className="flex space-x-2">
      {inputModes.map((mode) => {
        const Icon = mode.icon;
        const isSelected = selectedMode === mode.id;
        
        return (
          <motion.button
            key={mode.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onModeChange(mode.id)}
            className={`
              flex items-center space-x-2 px-4 py-2 rounded-lg border-2 transition-all duration-200
              ${getColorClasses(mode.color, isSelected)}
            `}
          >
            <Icon className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium text-sm">{mode.name}</div>
              <div className="text-xs opacity-75">{mode.description}</div>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
};

export default InputSelector;
