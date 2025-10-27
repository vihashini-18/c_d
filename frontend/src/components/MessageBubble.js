import React from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessageBubble = ({ message, variant = 'assistant' }) => {
  const getBubbleStyles = () => {
    const baseStyles = "px-4 py-3 rounded-2xl max-w-full break-words";
    
    switch (variant) {
      case 'user':
        return `${baseStyles} bg-blue-600 text-white ml-12`;
      case 'emergency':
        return `${baseStyles} bg-red-100 text-red-900 border-2 border-red-300 mr-12`;
      case 'assistant-high':
        return `${baseStyles} bg-green-50 text-gray-900 border border-green-200 mr-12`;
      case 'assistant-medium':
        return `${baseStyles} bg-yellow-50 text-gray-900 border border-yellow-200 mr-12`;
      case 'assistant-low':
        return `${baseStyles} bg-orange-50 text-gray-900 border border-orange-200 mr-12`;
      default:
        return `${baseStyles} bg-gray-100 text-gray-900 mr-12`;
    }
  };

  const getConfidenceIndicator = () => {
    if (message.type === 'user') return null;
    
    const confidence = message.confidence?.score || 0;
    const level = message.confidence?.level || 'low';
    
    let color = 'bg-red-500';
    if (level === 'high') color = 'bg-green-500';
    else if (level === 'medium') color = 'bg-yellow-500';
    
    return (
      <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white">
        <div className={`w-full h-full rounded-full ${color}`} />
      </div>
    );
  };

  const renderContent = () => {
    if (message.type === 'image' && message.imageData) {
      return (
        <div className="space-y-3">
          <div className="text-sm text-gray-600">
            <strong>Image Analysis:</strong>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm">
              <div><strong>Body Parts Detected:</strong> {message.imageData.body_parts?.map(part => part.name).join(', ') || 'None'}</div>
              <div><strong>Medical Conditions:</strong> {message.imageData.medical_conditions?.map(cond => cond.condition).join(', ') || 'None'}</div>
              <div><strong>Quality Score:</strong> {message.imageData.quality_metrics?.quality_score?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>
          <div className="text-sm">
            {message.content}
          </div>
        </div>
      );
    }

    if (message.type === 'audio' && message.audioData) {
      return (
        <div className="space-y-3">
          <div className="text-sm text-gray-600">
            <strong>Audio Transcription:</strong>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm">
              <div><strong>Language:</strong> {message.audioData.language}</div>
              <div><strong>Confidence:</strong> {(message.audioData.confidence * 100).toFixed(1)}%</div>
              <div><strong>Duration:</strong> {message.audioData.duration?.toFixed(1)}s</div>
            </div>
          </div>
          <div className="text-sm">
            {message.content}
          </div>
        </div>
      );
    }

    // Regular text content with markdown support
    return (
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={tomorrow}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-sm">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-700 my-2">
              {children}
            </blockquote>
          ),
          h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
        }}
      >
        {message.content}
      </ReactMarkdown>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      className={`relative ${getBubbleStyles()}`}
    >
      {getConfidenceIndicator()}
      
      <div className="text-sm leading-relaxed">
        {renderContent()}
      </div>
      
      {/* Emergency warning for low confidence */}
      {message.confidence?.level === 'low' && message.type === 'assistant' && (
        <div className="mt-2 p-2 bg-orange-100 border border-orange-300 rounded text-xs text-orange-800">
          <strong>⚠️ Low Confidence:</strong> {message.confidence.recommendation}
        </div>
      )}
    </motion.div>
  );
};

export default MessageBubble;
