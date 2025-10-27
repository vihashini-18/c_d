import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiImage, FiX, FiCheck, FiAlertCircle } from 'react-icons/fi';
import toast from 'react-hot-toast';

const ImageUploader = ({ onImageAnalysis, language = 'en' }) => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result);
      reader.readAsDataURL(file);
      
      toast.success('Image uploaded successfully');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  });

  const analyzeImage = async () => {
    if (!uploadedImage) return;
    
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('image_file', uploadedImage);
      formData.append('language', language);
      
      const response = await fetch('/api/v1/chat/image', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Image analysis failed');
      }
      
      const result = await response.json();
      
      if (result.response) {
        onImageAnalysis({
          analysis: result.response,
          bodyParts: result.body_parts || [],
          medicalConditions: result.medical_conditions || [],
          qualityMetrics: result.quality_metrics || {},
          confidence: result.confidence || {},
          emergency: result.emergency || {}
        });
        
        toast.success('Image analyzed successfully');
      } else {
        toast.error('Failed to analyze image');
      }
    } catch (error) {
      console.error('Image analysis error:', error);
      toast.error('Failed to analyze image');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearImage = () => {
    setUploadedImage(null);
    setPreview(null);
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <FiUpload className="w-8 h-8 text-gray-400" />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive ? 'Drop the image here' : 'Upload a medical image'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Drag & drop or click to select an image
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Supports: JPG, PNG, GIF, BMP, WebP (max 10MB)
            </p>
          </div>
        </div>
      </div>

      {/* Image Preview */}
      <AnimatePresence>
        {preview && uploadedImage && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <div className="relative">
              <img
                src={preview}
                alt="Uploaded medical image"
                className="w-full max-w-md mx-auto rounded-lg shadow-md"
              />
              
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
              >
                <FiX className="w-4 h-4" />
              </button>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">
                <strong>File:</strong> {uploadedImage.name} ({(uploadedImage.size / 1024 / 1024).toFixed(2)} MB)
              </p>
              
              <div className="flex justify-center space-x-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={analyzeImage}
                  disabled={isAnalyzing}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <FiImage className="w-4 h-4" />
                      <span>Analyze Image</span>
                    </>
                  )}
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Instructions */}
      <div className="text-center text-sm text-gray-500">
        <p className="mb-2">
          <strong>What can I analyze?</strong>
        </p>
        <ul className="text-left max-w-md mx-auto space-y-1">
          <li className="flex items-center space-x-2">
            <FiCheck className="w-4 h-4 text-green-500" />
            <span>Body parts and anatomical regions</span>
          </li>
          <li className="flex items-center space-x-2">
            <FiCheck className="w-4 h-4 text-green-500" />
            <span>Skin conditions and rashes</span>
          </li>
          <li className="flex items-center space-x-2">
            <FiCheck className="w-4 h-4 text-green-500" />
            <span>Wounds and injuries</span>
          </li>
          <li className="flex items-center space-x-2">
            <FiCheck className="w-4 h-4 text-green-500" />
            <span>Medical scans and X-rays</span>
          </li>
        </ul>
        
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <FiAlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="text-left">
              <p className="font-medium text-yellow-800">Important Disclaimer</p>
              <p className="text-sm text-yellow-700 mt-1">
                This is for educational purposes only. Always consult a healthcare professional for medical diagnosis and treatment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageUploader;
