import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChat } from '../context/ChatContext';
import { useTheme } from '../context/ThemeContext';

// Components
import MessageList from './MessageList';
import InputSelector from './InputSelector';
import AudioRecorder from './AudioRecorder';
import ImageUploader from './ImageUploader';
import LanguageSelector from './LanguageSelector';
import ConfidenceDisplay from './ConfidenceDisplay';
import EmergencyAlert from './EmergencyAlert';
import TypingIndicator from './TypingIndicator';

// Icons
import { 
  FiSend, 
  FiMic, 
  FiImage, 
  FiFileText, 
  FiSettings,
  FiAlertTriangle,
  FiCheckCircle
} from 'react-icons/fi';

const ChatInterface = () => {
  const {
    messages,
    sendMessage,
    isTyping,
    currentConversation,
    createNewConversation,
    inputMode,
    setInputMode,
    selectedLanguage,
    setSelectedLanguage
  } = useChat();

  const { theme } = useTheme();
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showEmergencyAlert, setShowEmergencyAlert] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (lastMessage) {
      // Check if the last message indicates an emergency
      if (lastMessage.emergency?.is_emergency) {
        setShowEmergencyAlert(true);
      }
    }
  }, [lastMessage]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() && inputMode === 'text') return;

    const messageData = {
      content: inputValue,
      type: inputMode,
      language: selectedLanguage
    };

    try {
      const response = await sendMessage(messageData);
      setLastMessage(response);
      setInputValue('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleAudioTranscription = (transcribedText) => {
    setInputValue(transcribedText);
    setInputMode('text');
  };

  const handleImageAnalysis = (imageData) => {
    const messageData = {
      content: imageData.analysis,
      type: 'image',
      language: selectedLanguage,
      imageData: imageData
    };

    sendMessage(messageData);
  };

  const handleNewChat = () => {
    createNewConversation();
    setInputValue('');
    setShowEmergencyAlert(false);
  };

  const getInputPlaceholder = () => {
    switch (inputMode) {
      case 'text':
        return 'Type your medical question here...';
      case 'audio':
        return 'Click the microphone to start recording...';
      case 'image':
        return 'Upload an image for analysis...';
      default:
        return 'Select an input method...';
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">
            Medical Chatbot
          </h1>
          {currentConversation && (
            <span className="text-sm text-gray-500">
              Conversation {currentConversation.id}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onLanguageChange={setSelectedLanguage}
          />
          
          <button
            onClick={handleNewChat}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="New Chat"
          >
            <FiFileText className="w-5 h-5" />
          </button>
          
          <button
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <FiSettings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Emergency Alert */}
      <AnimatePresence>
        {showEmergencyAlert && (
          <EmergencyAlert
            onClose={() => setShowEmergencyAlert(false)}
            message={lastMessage?.emergency}
          />
        )}
      </AnimatePresence>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
        
        {isTyping && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        {/* Input Mode Selector */}
        <InputSelector
          selectedMode={inputMode}
          onModeChange={setInputMode}
        />

        {/* Main Input Area */}
        <div className="mt-4">
          {inputMode === 'text' && (
            <div className="flex items-end space-x-2">
              <div className="flex-1">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={getInputPlaceholder()}
                  className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <FiSend className="w-5 h-5" />
              </motion.button>
            </div>
          )}

          {inputMode === 'audio' && (
            <AudioRecorder
              onTranscription={handleAudioTranscription}
              onRecordingChange={setIsRecording}
              language={selectedLanguage}
            />
          )}

          {inputMode === 'image' && (
            <ImageUploader
              onImageAnalysis={handleImageAnalysis}
              language={selectedLanguage}
            />
          )}
        </div>

        {/* Input Mode Indicators */}
        <div className="mt-2 flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Mode: {inputMode}</span>
            <span>Language: {selectedLanguage}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {isRecording && (
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
                className="flex items-center space-x-1 text-red-500"
              >
                <FiMic className="w-4 h-4" />
                <span>Recording...</span>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
