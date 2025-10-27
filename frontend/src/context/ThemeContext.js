import React, { createContext, useContext, useReducer, useEffect } from 'react';

const ThemeContext = createContext();

const themeReducer = (state, action) => {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' };
    case 'SET_FONT_SIZE':
      return { ...state, fontSize: action.payload };
    case 'SET_ANIMATIONS':
      return { ...state, animations: action.payload };
    default:
      return state;
  }
};

const initialState = {
  theme: 'light',
  fontSize: 'medium',
  animations: true,
  colors: {
    light: {
      primary: '#2563eb',
      secondary: '#64748b',
      background: '#ffffff',
      surface: '#f8fafc',
      text: '#1e293b',
      textSecondary: '#64748b',
      border: '#e2e8f0',
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#0ea5e9'
    },
    dark: {
      primary: '#3b82f6',
      secondary: '#94a3b8',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#f1f5f9',
      textSecondary: '#94a3b8',
      border: '#334155',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#06b6d4'
    }
  }
};

export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('medical-chatbot-theme');
    const savedFontSize = localStorage.getItem('medical-chatbot-font-size');
    const savedAnimations = localStorage.getItem('medical-chatbot-animations');

    if (savedTheme) {
      dispatch({ type: 'SET_THEME', payload: savedTheme });
    }
    if (savedFontSize) {
      dispatch({ type: 'SET_FONT_SIZE', payload: savedFontSize });
    }
    if (savedAnimations !== null) {
      dispatch({ type: 'SET_ANIMATIONS', payload: savedAnimations === 'true' });
    }
  }, []);

  // Save theme to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('medical-chatbot-theme', state.theme);
  }, [state.theme]);

  useEffect(() => {
    localStorage.setItem('medical-chatbot-font-size', state.fontSize);
  }, [state.fontSize]);

  useEffect(() => {
    localStorage.setItem('medical-chatbot-animations', state.animations.toString());
  }, [state.animations]);

  const setTheme = (theme) => {
    dispatch({ type: 'SET_THEME', payload: theme });
  };

  const toggleTheme = () => {
    dispatch({ type: 'TOGGLE_THEME' });
  };

  const setFontSize = (fontSize) => {
    dispatch({ type: 'SET_FONT_SIZE', payload: fontSize });
  };

  const setAnimations = (animations) => {
    dispatch({ type: 'SET_ANIMATIONS', payload: animations });
  };

  const getCurrentColors = () => {
    return state.colors[state.theme];
  };

  const getFontSizeClass = () => {
    const fontSizeMap = {
      small: 'text-sm',
      medium: 'text-base',
      large: 'text-lg',
      xlarge: 'text-xl'
    };
    return fontSizeMap[state.fontSize] || 'text-base';
  };

  const value = {
    ...state,
    setTheme,
    toggleTheme,
    setFontSize,
    setAnimations,
    getCurrentColors,
    getFontSizeClass
  };

  return (
    <ThemeContext.Provider value={value}>
      <div className={`${state.theme} ${getFontSizeClass()}`}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
