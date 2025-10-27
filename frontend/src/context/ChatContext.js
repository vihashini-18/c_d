import React, { createContext, useContext, useReducer, useCallback } from 'react';
import toast from 'react-hot-toast';

const ChatContext = createContext();

const initialState = {
  messages: [],
  currentConversation: null,
  conversations: [],
  isTyping: false,
  inputMode: 'text',
  selectedLanguage: 'en',
  isConnected: true
};

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    
    case 'SET_TYPING':
      return { ...state, isTyping: action.payload };
    
    case 'SET_CONVERSATION':
      return { ...state, currentConversation: action.payload };
    
    case 'SET_INPUT_MODE':
      return { ...state, inputMode: action.payload };
    
    case 'SET_LANGUAGE':
      return { ...state, selectedLanguage: action.payload };
    
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload };
    
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    
    default:
      return state;
  }
};

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const sendMessage = useCallback(async (messageData) => {
    const { content, type, language, imageData, audioData } = messageData;
    
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content,
      type: 'user',
      timestamp: new Date().toISOString(),
      inputType: type,
      language
    };
    
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_TYPING', payload: true });

    try {
      let response;
      
      if (type === 'text') {
        response = await sendTextMessage(content, language);
      } else if (type === 'audio') {
        response = await sendAudioMessage(audioData, language);
      } else if (type === 'image') {
        response = await sendImageMessage(imageData, language);
      }
      
      // Add assistant response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        type: 'assistant',
        timestamp: new Date().toISOString(),
        confidence: response.confidence,
        emergency: response.emergency,
        emotion: response.emotion,
        sources: response.sources,
        medical_entities: response.medical_entities,
        language: response.language
      };
      
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      
      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        type: 'assistant',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_TYPING', payload: false });
    }
  }, []);

  const sendTextMessage = async (content, language) => {
    const formData = new FormData();
    formData.append('message', content);
    formData.append('user_id', 'user_123'); // In real app, get from auth
    formData.append('session_id', 'session_123');
    formData.append('language', language);
    
    const response = await fetch('/api/v1/chat/text', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Failed to send text message');
    }
    
    return await response.json();
  };

  const sendAudioMessage = async (audioData, language) => {
    const formData = new FormData();
    formData.append('audio_file', audioData);
    formData.append('user_id', 'user_123');
    formData.append('session_id', 'session_123');
    formData.append('language', language);
    
    const response = await fetch('/api/v1/chat/audio', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Failed to send audio message');
    }
    
    return await response.json();
  };

  const sendImageMessage = async (imageData, language) => {
    const formData = new FormData();
    formData.append('image_file', imageData.file);
    formData.append('message', imageData.analysis);
    formData.append('user_id', 'user_123');
    formData.append('session_id', 'session_123');
    formData.append('language', language);
    
    const response = await fetch('/api/v1/chat/image', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Failed to send image message');
    }
    
    return await response.json();
  };

  const createNewConversation = useCallback(() => {
    const newConversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      createdAt: new Date().toISOString(),
      messageCount: 0
    };
    
    dispatch({ type: 'SET_CONVERSATION', payload: newConversation });
    dispatch({ type: 'CLEAR_MESSAGES' });
    
    toast.success('New conversation started');
  }, []);

  const setInputMode = useCallback((mode) => {
    dispatch({ type: 'SET_INPUT_MODE', payload: mode });
  }, []);

  const setSelectedLanguage = useCallback((language) => {
    dispatch({ type: 'SET_LANGUAGE', payload: language });
  }, []);

  const loadConversation = useCallback(async (conversationId) => {
    try {
      const response = await fetch(`/api/v1/chat/conversation/${conversationId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load conversation');
      }
      
      const conversation = await response.json();
      
      dispatch({ type: 'SET_CONVERSATION', payload: conversation });
      dispatch({ type: 'SET_MESSAGES', payload: conversation.messages || [] });
      
      toast.success('Conversation loaded');
    } catch (error) {
      console.error('Error loading conversation:', error);
      toast.error('Failed to load conversation');
    }
  }, []);

  const deleteConversation = useCallback(async (conversationId) => {
    try {
      const response = await fetch(`/api/v1/chat/conversation/${conversationId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete conversation');
      }
      
      // Remove from conversations list
      const updatedConversations = state.conversations.filter(
        conv => conv.id !== conversationId
      );
      
      dispatch({ type: 'SET_CONVERSATIONS', payload: updatedConversations });
      
      // If this was the current conversation, clear it
      if (state.currentConversation?.id === conversationId) {
        dispatch({ type: 'SET_CONVERSATION', payload: null });
        dispatch({ type: 'CLEAR_MESSAGES' });
      }
      
      toast.success('Conversation deleted');
    } catch (error) {
      console.error('Error deleting conversation:', error);
      toast.error('Failed to delete conversation');
    }
  }, [state.conversations, state.currentConversation]);

  const submitFeedback = useCallback(async (messageId, feedback) => {
    try {
      const response = await fetch('/api/v1/chat/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversation_id: state.currentConversation?.id,
          message_id: messageId,
          ...feedback
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      toast.success('Feedback submitted successfully');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error('Failed to submit feedback');
    }
  }, [state.currentConversation]);

  const value = {
    ...state,
    sendMessage,
    createNewConversation,
    setInputMode,
    setSelectedLanguage,
    loadConversation,
    deleteConversation,
    submitFeedback
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
