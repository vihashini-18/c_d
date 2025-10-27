import React from 'react';
import { motion } from 'framer-motion';
import { 
  FiMessageSquare, 
  FiClock, 
  FiSettings, 
  FiHelpCircle, 
  FiInfo, 
  FiX,
  FiPlus,
  FiTrash2,
  FiEdit3
} from 'react-icons/fi';

const Sidebar = ({ onClose }) => {
  const conversations = [
    { id: '1', title: 'Chest Pain Discussion', timestamp: '2 hours ago', unread: 0 },
    { id: '2', title: 'Fever Symptoms', timestamp: '1 day ago', unread: 2 },
    { id: '3', title: 'Headache Analysis', timestamp: '2 days ago', unread: 0 },
    { id: '4', title: 'Skin Rash Question', timestamp: '3 days ago', unread: 1 },
    { id: '5', title: 'General Health Check', timestamp: '1 week ago', unread: 0 }
  ];

  const menuItems = [
    { icon: FiMessageSquare, label: 'New Chat', active: true },
    { icon: FiClock, label: 'Recent Chats', count: conversations.length },
    { icon: FiSettings, label: 'Settings' },
    { icon: FiHelpCircle, label: 'Help & Support' },
    { icon: FiInfo, label: 'About' }
  ];

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded lg:hidden"
          >
            <FiX className="w-5 h-5" />
          </motion.button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <FiPlus className="w-4 h-4" />
          <span className="font-medium">New Chat</span>
        </motion.button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Recent Conversations</h3>
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <motion.div
                key={conversation.id}
                whileHover={{ backgroundColor: '#f3f4f6' }}
                className="group flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <FiMessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {conversation.title}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {conversation.timestamp}
                  </p>
                </div>
                
                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {conversation.unread > 0 && (
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  )}
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete conversation"
                  >
                    <FiTrash2 className="w-3 h-3" />
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <div className="border-t border-gray-200 p-4">
        <div className="space-y-1">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.button
                key={index}
                whileHover={{ backgroundColor: '#f3f4f6' }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                  item.active ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                </div>
                {item.count && (
                  <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">
                    {item.count}
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4">
        <div className="text-xs text-gray-500 text-center">
          <p>Medical Chatbot v1.0.0</p>
          <p className="mt-1">AI-Powered Healthcare Assistant</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
