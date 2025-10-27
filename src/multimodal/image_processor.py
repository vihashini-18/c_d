import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Tuple, Optional
import base64
from config.settings import settings

class ImageProcessor:
    """
    Image processing for medical image analysis and body part detection
    """
    
    def __init__(self):
        """Initialize image processor"""
        self.body_part_detector = BodyPartDetector()
        
        # Medical image enhancement parameters
        self.enhancement_params = {
            'contrast_alpha': 1.2,
            'brightness_beta': 10,
            'gamma': 1.1,
            'sharpen_kernel': np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        }
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process medical image for analysis
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Dictionary with processed image data and analysis
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            elif len(image_array.shape) == 2:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            
            # Enhance image
            enhanced_image = self._enhance_medical_image(image_array)
            
            # Detect body parts
            body_parts = self.body_part_detector.detect_body_parts(enhanced_image)
            
            # Extract features
            features = self._extract_image_features(enhanced_image)
            
            # Analyze image quality
            quality_metrics = self._analyze_image_quality(enhanced_image)
            
            return {
                "success": True,
                "body_parts": body_parts,
                "features": features,
                "quality_metrics": quality_metrics,
                "enhanced_image": self._encode_image(enhanced_image),
                "original_size": image.size,
                "processed_size": enhanced_image.shape[:2][::-1]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "body_parts": [],
                "features": {},
                "quality_metrics": {}
            }
    
    def _enhance_medical_image(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance medical image for better analysis
        
        Args:
            image: Input image array
            
        Returns:
            Enhanced image array
        """
        # Convert to float
        enhanced = image.astype(np.float32) / 255.0
        
        # Apply contrast enhancement
        enhanced = cv2.convertScaleAbs(enhanced * 255, 
                                     alpha=self.enhancement_params['contrast_alpha'],
                                     beta=self.enhancement_params['brightness_beta'])
        
        # Apply gamma correction
        enhanced = np.power(enhanced / 255.0, self.enhancement_params['gamma']) * 255.0
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        # Apply sharpening
        enhanced = cv2.filter2D(enhanced, -1, self.enhancement_params['sharpen_kernel'])
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        # Apply noise reduction
        enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        return enhanced
    
    def _extract_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract features from medical image
        
        Args:
            image: Input image array
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Basic image statistics
        features['mean_intensity'] = float(np.mean(gray))
        features['std_intensity'] = float(np.std(gray))
        features['min_intensity'] = int(np.min(gray))
        features['max_intensity'] = int(np.max(gray))
        
        # Histogram analysis
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        features['histogram_peaks'] = self._find_histogram_peaks(hist)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = float(np.sum(edges > 0) / edges.size)
        
        # Texture analysis using LBP (simplified)
        features['texture_uniformity'] = self._calculate_texture_uniformity(gray)
        
        # Color analysis (if color image)
        if len(image.shape) == 3:
            features['color_dominance'] = self._analyze_color_dominance(image)
        
        return features
    
    def _find_histogram_peaks(self, hist: np.ndarray) -> List[int]:
        """Find peaks in histogram"""
        peaks = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 100:
                peaks.append(int(i))
        return peaks
    
    def _calculate_texture_uniformity(self, gray: np.ndarray) -> float:
        """Calculate texture uniformity using local binary patterns"""
        # Simplified LBP calculation
        h, w = gray.shape
        uniform_count = 0
        total_pixels = 0
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = gray[i, j]
                pattern = 0
                
                # 8-neighborhood
                neighbors = [
                    gray[i-1, j-1], gray[i-1, j], gray[i-1, j+1],
                    gray[i, j+1], gray[i+1, j+1], gray[i+1, j],
                    gray[i+1, j-1], gray[i, j-1]
                ]
                
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        pattern |= (1 << k)
                
                # Count transitions
                transitions = 0
                pattern_str = format(pattern, '08b')
                for k in range(8):
                    if pattern_str[k] != pattern_str[(k+1) % 8]:
                        transitions += 1
                
                # Uniform pattern has <= 2 transitions
                if transitions <= 2:
                    uniform_count += 1
                total_pixels += 1
        
        return uniform_count / total_pixels if total_pixels > 0 else 0.0
    
    def _analyze_color_dominance(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze dominant colors in image"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Define color ranges
        color_ranges = {
            'red': [(0, 50, 50), (10, 255, 255)],
            'orange': [(10, 50, 50), (25, 255, 255)],
            'yellow': [(25, 50, 50), (35, 255, 255)],
            'green': [(35, 50, 50), (85, 255, 255)],
            'blue': [(85, 50, 50), (130, 255, 255)],
            'purple': [(130, 50, 50), (180, 255, 255)]
        }
        
        color_percentages = {}
        total_pixels = image.shape[0] * image.shape[1]
        
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            color_percentages[color] = float(np.sum(mask > 0) / total_pixels)
        
        return color_percentages
    
    def _analyze_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze image quality metrics
        
        Args:
            image: Input image array
            
        Returns:
            Dictionary of quality metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate Laplacian variance (sharpness)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        mean_gradient = np.mean(gradient_magnitude)
        
        # Calculate noise level (simplified)
        noise_level = np.std(cv2.GaussianBlur(gray, (5, 5), 0) - gray)
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        return {
            'sharpness': float(laplacian_var),
            'gradient_magnitude': float(mean_gradient),
            'noise_level': float(noise_level),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'quality_score': self._calculate_quality_score(laplacian_var, mean_gradient, noise_level)
        }
    
    def _calculate_quality_score(self, sharpness: float, gradient: float, noise: float) -> float:
        """Calculate overall quality score"""
        # Normalize metrics (simplified)
        sharpness_score = min(1.0, sharpness / 1000.0)
        gradient_score = min(1.0, gradient / 50.0)
        noise_score = max(0.0, 1.0 - noise / 30.0)
        
        # Weighted combination
        quality_score = (0.4 * sharpness_score + 0.4 * gradient_score + 0.2 * noise_score)
        return min(1.0, max(0.0, quality_score))
    
    def _encode_image(self, image: np.ndarray) -> str:
        """Encode image to base64 string"""
        # Convert to PIL Image
        pil_image = Image.fromarray(image)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Encode to base64
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def detect_medical_conditions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect potential medical conditions in image
        
        Args:
            image: Input image array
            
        Returns:
            List of detected conditions with confidence
        """
        conditions = []
        
        # This is a simplified example - in practice, you'd use trained models
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Example: Detect potential skin issues based on color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Look for redness (potential inflammation)
        red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        red_percentage = np.sum(red_mask > 0) / (image.shape[0] * image.shape[1])
        
        if red_percentage > 0.1:
            conditions.append({
                'condition': 'potential_inflammation',
                'confidence': min(0.8, red_percentage * 2),
                'description': 'Redness detected in image',
                'severity': 'low' if red_percentage < 0.2 else 'medium'
            })
        
        # Look for unusual patterns
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        if edge_density > 0.3:
            conditions.append({
                'condition': 'irregular_patterns',
                'confidence': min(0.7, edge_density),
                'description': 'Unusual patterns detected',
                'severity': 'low'
            })
        
        return conditions

class BodyPartDetector:
    """
    Body part detection for medical images
    """
    
    def __init__(self):
        """Initialize body part detector"""
        # Define body part regions (simplified)
        self.body_parts = {
            'head': {'region': (0.2, 0.0, 0.6, 0.3), 'confidence': 0.8},
            'chest': {'region': (0.1, 0.2, 0.8, 0.6), 'confidence': 0.9},
            'abdomen': {'region': (0.1, 0.4, 0.8, 0.8), 'confidence': 0.8},
            'arms': {'region': (0.0, 0.1, 1.0, 0.7), 'confidence': 0.7},
            'legs': {'region': (0.1, 0.6, 0.8, 1.0), 'confidence': 0.7}
        }
    
    def detect_body_parts(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect body parts in medical image
        
        Args:
            image: Input image array
            
        Returns:
            List of detected body parts
        """
        detected_parts = []
        h, w = image.shape[:2]
        
        for part_name, part_info in self.body_parts.items():
            region = part_info['region']
            x1 = int(region[0] * w)
            y1 = int(region[1] * h)
            x2 = int(region[2] * w)
            y2 = int(region[3] * h)
            
            # Extract region
            region_image = image[y1:y2, x1:x2]
            
            # Analyze region
            analysis = self._analyze_body_part_region(region_image, part_name)
            
            if analysis['confidence'] > 0.5:
                detected_parts.append({
                    'name': part_name,
                    'confidence': analysis['confidence'],
                    'region': (x1, y1, x2, y2),
                    'analysis': analysis
                })
        
        return detected_parts
    
    def _analyze_body_part_region(self, region: np.ndarray, part_name: str) -> Dict[str, Any]:
        """
        Analyze a specific body part region
        
        Args:
            region: Image region
            part_name: Name of the body part
            
        Returns:
            Analysis results
        """
        if region.size == 0:
            return {'confidence': 0.0, 'features': {}}
        
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY) if len(region.shape) == 3 else region
        
        # Calculate features
        features = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'edge_density': self._calculate_edge_density(gray),
            'texture_uniformity': self._calculate_texture_uniformity(gray)
        }
        
        # Calculate confidence based on features
        confidence = self._calculate_region_confidence(features, part_name)
        
        return {
            'confidence': confidence,
            'features': features
        }
    
    def _calculate_edge_density(self, gray: np.ndarray) -> float:
        """Calculate edge density in region"""
        edges = cv2.Canny(gray, 50, 150)
        return float(np.sum(edges > 0) / edges.size)
    
    def _calculate_texture_uniformity(self, gray: np.ndarray) -> float:
        """Calculate texture uniformity"""
        # Simplified texture analysis
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Lower variance in gradient magnitude indicates more uniform texture
        return 1.0 / (1.0 + np.var(gradient_magnitude))
    
    def _calculate_region_confidence(self, features: Dict[str, float], part_name: str) -> float:
        """Calculate confidence for body part detection"""
        # Simple heuristic-based confidence calculation
        confidence = 0.5  # Base confidence
        
        # Adjust based on intensity (different body parts have different typical intensities)
        mean_intensity = features['mean_intensity']
        if part_name == 'head' and 100 < mean_intensity < 200:
            confidence += 0.2
        elif part_name == 'chest' and 80 < mean_intensity < 180:
            confidence += 0.2
        elif part_name == 'abdomen' and 70 < mean_intensity < 170:
            confidence += 0.2
        
        # Adjust based on texture uniformity
        texture_uniformity = features['texture_uniformity']
        if texture_uniformity > 0.5:
            confidence += 0.1
        
        # Adjust based on edge density
        edge_density = features['edge_density']
        if 0.1 < edge_density < 0.4:  # Reasonable edge density
            confidence += 0.1
        
        return min(1.0, confidence)

