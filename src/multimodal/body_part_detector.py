import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class BodyPart:
    """Represents a detected body part"""
    name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: Tuple[int, int]
    area: int
    features: Dict[str, Any]

class BodyPartDetector:
    """
    Advanced body part detection for medical images
    """
    
    def __init__(self):
        """Initialize body part detector"""
        # Define anatomical regions with more precise coordinates
        self.anatomical_regions = {
            'head': {
                'region': (0.25, 0.0, 0.75, 0.25),
                'features': ['circular_shape', 'high_contrast', 'symmetrical'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]  # Skin tone range
            },
            'neck': {
                'region': (0.3, 0.2, 0.7, 0.35),
                'features': ['vertical_orientation', 'medium_contrast'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'chest': {
                'region': (0.15, 0.25, 0.85, 0.55),
                'features': ['broad_area', 'symmetrical', 'medium_contrast'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'abdomen': {
                'region': (0.2, 0.45, 0.8, 0.75),
                'features': ['broad_area', 'medium_contrast'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'left_arm': {
                'region': (0.0, 0.15, 0.25, 0.7),
                'features': ['vertical_orientation', 'limb_shape'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'right_arm': {
                'region': (0.75, 0.15, 1.0, 0.7),
                'features': ['vertical_orientation', 'limb_shape'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'left_leg': {
                'region': (0.2, 0.65, 0.5, 1.0),
                'features': ['vertical_orientation', 'limb_shape'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            },
            'right_leg': {
                'region': (0.5, 0.65, 0.8, 1.0),
                'features': ['vertical_orientation', 'limb_shape'],
                'color_ranges': [(0, 0, 100), (180, 255, 255)]
            }
        }
        
        # Medical imaging specific regions
        self.medical_regions = {
            'heart_area': {
                'region': (0.3, 0.3, 0.7, 0.5),
                'features': ['central_location', 'medium_contrast'],
                'importance': 'high'
            },
            'lung_area': {
                'region': (0.2, 0.25, 0.8, 0.55),
                'features': ['broad_area', 'low_contrast'],
                'importance': 'high'
            },
            'liver_area': {
                'region': (0.4, 0.45, 0.8, 0.65),
                'features': ['right_side', 'medium_contrast'],
                'importance': 'medium'
            },
            'kidney_area': {
                'region': (0.2, 0.5, 0.8, 0.7),
                'features': ['bilateral', 'medium_contrast'],
                'importance': 'medium'
            }
        }
    
    def detect_body_parts(self, image: np.ndarray, 
                         include_medical: bool = True) -> List[BodyPart]:
        """
        Detect body parts in medical image
        
        Args:
            image: Input image array
            include_medical: Whether to include medical-specific regions
            
        Returns:
            List of detected body parts
        """
        detected_parts = []
        h, w = image.shape[:2]
        
        # Detect anatomical regions
        for part_name, part_info in self.anatomical_regions.items():
            body_part = self._detect_single_body_part(image, part_name, part_info, w, h)
            if body_part and body_part.confidence > 0.3:
                detected_parts.append(body_part)
        
        # Detect medical regions if requested
        if include_medical:
            for region_name, region_info in self.medical_regions.items():
                body_part = self._detect_medical_region(image, region_name, region_info, w, h)
                if body_part and body_part.confidence > 0.4:
                    detected_parts.append(body_part)
        
        # Sort by confidence
        detected_parts.sort(key=lambda x: x.confidence, reverse=True)
        
        return detected_parts
    
    def _detect_single_body_part(self, image: np.ndarray, part_name: str, 
                                part_info: Dict[str, Any], w: int, h: int) -> Optional[BodyPart]:
        """Detect a single body part"""
        region = part_info['region']
        x1 = int(region[0] * w)
        y1 = int(region[1] * h)
        x2 = int(region[2] * w)
        y2 = int(region[3] * h)
        
        # Ensure coordinates are within image bounds
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        # Extract region
        region_image = image[y1:y2, x1:x2]
        
        # Analyze region
        analysis = self._analyze_body_part_region(region_image, part_name, part_info)
        
        if analysis['confidence'] > 0.3:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            area = (x2 - x1) * (y2 - y1)
            
            return BodyPart(
                name=part_name,
                confidence=analysis['confidence'],
                bbox=(x1, y1, x2, y2),
                center=(center_x, center_y),
                area=area,
                features=analysis['features']
            )
        
        return None
    
    def _detect_medical_region(self, image: np.ndarray, region_name: str,
                              region_info: Dict[str, Any], w: int, h: int) -> Optional[BodyPart]:
        """Detect medical-specific regions"""
        region = region_info['region']
        x1 = int(region[0] * w)
        y1 = int(region[1] * h)
        x2 = int(region[2] * w)
        y2 = int(region[3] * h)
        
        # Ensure coordinates are within image bounds
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        # Extract region
        region_image = image[y1:y2, x1:x2]
        
        # Analyze medical region
        analysis = self._analyze_medical_region(region_image, region_name, region_info)
        
        if analysis['confidence'] > 0.4:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            area = (x2 - x1) * (y2 - y1)
            
            return BodyPart(
                name=region_name,
                confidence=analysis['confidence'],
                bbox=(x1, y1, x2, y2),
                center=(center_x, center_y),
                area=area,
                features=analysis['features']
            )
        
        return None
    
    def _analyze_body_part_region(self, region: np.ndarray, part_name: str,
                                 part_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a body part region"""
        if region.size == 0:
            return {'confidence': 0.0, 'features': {}}
        
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY) if len(region.shape) == 3 else region
        hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV) if len(region.shape) == 3 else None
        
        # Calculate features
        features = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'edge_density': self._calculate_edge_density(gray),
            'texture_uniformity': self._calculate_texture_uniformity(gray),
            'shape_analysis': self._analyze_shape(region),
            'color_analysis': self._analyze_color_distribution(region) if hsv is not None else {}
        }
        
        # Calculate confidence based on features and expected characteristics
        confidence = self._calculate_body_part_confidence(features, part_name, part_info)
        
        return {
            'confidence': confidence,
            'features': features
        }
    
    def _analyze_medical_region(self, region: np.ndarray, region_name: str,
                               region_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a medical region"""
        if region.size == 0:
            return {'confidence': 0.0, 'features': {}}
        
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY) if len(region.shape) == 3 else region
        
        # Medical-specific analysis
        features = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'contrast_ratio': self._calculate_contrast_ratio(gray),
            'texture_analysis': self._analyze_medical_texture(gray),
            'symmetry_score': self._calculate_symmetry_score(region),
            'density_analysis': self._analyze_tissue_density(gray)
        }
        
        # Calculate confidence for medical regions
        confidence = self._calculate_medical_region_confidence(features, region_name, region_info)
        
        return {
            'confidence': confidence,
            'features': features
        }
    
    def _calculate_edge_density(self, gray: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection"""
        edges = cv2.Canny(gray, 50, 150)
        return float(np.sum(edges > 0) / edges.size)
    
    def _calculate_texture_uniformity(self, gray: np.ndarray) -> float:
        """Calculate texture uniformity using local binary patterns"""
        # Simplified LBP calculation
        h, w = gray.shape
        if h < 3 or w < 3:
            return 0.0
        
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
    
    def _analyze_shape(self, region: np.ndarray) -> Dict[str, Any]:
        """Analyze shape characteristics"""
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY) if len(region.shape) == 3 else region
        
        # Find contours
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {'circularity': 0.0, 'aspect_ratio': 1.0, 'area_ratio': 0.0}
        
        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        # Calculate shape features
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Calculate aspect ratio
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = w / h if h > 0 else 1.0
        
        # Calculate area ratio
        total_area = region.shape[0] * region.shape[1]
        area_ratio = area / total_area if total_area > 0 else 0.0
        
        return {
            'circularity': float(circularity),
            'aspect_ratio': float(aspect_ratio),
            'area_ratio': float(area_ratio)
        }
    
    def _analyze_color_distribution(self, region: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution in region"""
        hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
        
        # Calculate color statistics
        h_mean = np.mean(hsv[:, :, 0])
        s_mean = np.mean(hsv[:, :, 1])
        v_mean = np.mean(hsv[:, :, 2])
        
        # Calculate color variance
        h_var = np.var(hsv[:, :, 0])
        s_var = np.var(hsv[:, :, 1])
        v_var = np.var(hsv[:, :, 2])
        
        return {
            'hue_mean': float(h_mean),
            'saturation_mean': float(s_mean),
            'value_mean': float(v_mean),
            'hue_variance': float(h_var),
            'saturation_variance': float(s_var),
            'value_variance': float(v_var)
        }
    
    def _calculate_contrast_ratio(self, gray: np.ndarray) -> float:
        """Calculate contrast ratio"""
        min_val = np.min(gray)
        max_val = np.max(gray)
        
        if min_val == max_val:
            return 0.0
        
        return float((max_val - min_val) / (max_val + min_val))
    
    def _analyze_medical_texture(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze medical texture patterns"""
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate texture features
        mean_gradient = np.mean(gradient_magnitude)
        std_gradient = np.std(gradient_magnitude)
        
        # Calculate local binary pattern variance
        lbp_variance = self._calculate_lbp_variance(gray)
        
        return {
            'mean_gradient': float(mean_gradient),
            'std_gradient': float(std_gradient),
            'lbp_variance': float(lbp_variance)
        }
    
    def _calculate_lbp_variance(self, gray: np.ndarray) -> float:
        """Calculate Local Binary Pattern variance"""
        h, w = gray.shape
        if h < 3 or w < 3:
            return 0.0
        
        lbp_values = []
        
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
                
                lbp_values.append(pattern)
        
        return float(np.var(lbp_values)) if lbp_values else 0.0
    
    def _calculate_symmetry_score(self, region: np.ndarray) -> float:
        """Calculate symmetry score"""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        else:
            gray = region
        
        h, w = gray.shape
        if w < 2:
            return 0.0
        
        # Calculate horizontal symmetry
        left_half = gray[:, :w//2]
        right_half = gray[:, w//2:]
        
        # Flip right half to compare with left
        right_half_flipped = cv2.flip(right_half, 1)
        
        # Resize to match dimensions
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]
        
        # Calculate similarity
        if left_half.size > 0 and right_half_flipped.size > 0:
            correlation = cv2.matchTemplate(left_half, right_half_flipped, cv2.TM_CCOEFF_NORMED)[0][0]
            return float(max(0, correlation))
        
        return 0.0
    
    def _analyze_tissue_density(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze tissue density patterns"""
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Find peaks in histogram
        peaks = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 100:
                peaks.append(i)
        
        # Calculate density metrics
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Calculate density distribution
        low_density = np.sum(gray < mean_intensity - std_intensity) / gray.size
        medium_density = np.sum((gray >= mean_intensity - std_intensity) & 
                               (gray <= mean_intensity + std_intensity)) / gray.size
        high_density = np.sum(gray > mean_intensity + std_intensity) / gray.size
        
        return {
            'mean_intensity': float(mean_intensity),
            'std_intensity': float(std_intensity),
            'peak_count': len(peaks),
            'low_density_ratio': float(low_density),
            'medium_density_ratio': float(medium_density),
            'high_density_ratio': float(high_density)
        }
    
    def _calculate_body_part_confidence(self, features: Dict[str, Any], 
                                      part_name: str, part_info: Dict[str, Any]) -> float:
        """Calculate confidence for body part detection"""
        confidence = 0.5  # Base confidence
        
        # Adjust based on intensity
        mean_intensity = features['mean_intensity']
        if 80 < mean_intensity < 200:  # Typical skin tone range
            confidence += 0.2
        
        # Adjust based on texture uniformity
        texture_uniformity = features['texture_uniformity']
        if texture_uniformity > 0.6:
            confidence += 0.1
        
        # Adjust based on shape analysis
        shape_analysis = features['shape_analysis']
        if part_name in ['head'] and shape_analysis['circularity'] > 0.7:
            confidence += 0.2
        elif part_name in ['left_arm', 'right_arm', 'left_leg', 'right_leg']:
            aspect_ratio = shape_analysis['aspect_ratio']
            if 0.3 < aspect_ratio < 0.7:  # Vertical orientation
                confidence += 0.2
        
        # Adjust based on edge density
        edge_density = features['edge_density']
        if 0.1 < edge_density < 0.4:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_medical_region_confidence(self, features: Dict[str, Any],
                                           region_name: str, region_info: Dict[str, Any]) -> float:
        """Calculate confidence for medical region detection"""
        confidence = 0.4  # Base confidence for medical regions
        
        # Adjust based on contrast ratio
        contrast_ratio = features['contrast_ratio']
        if contrast_ratio > 0.3:
            confidence += 0.2
        
        # Adjust based on texture analysis
        texture_analysis = features['texture_analysis']
        if texture_analysis['mean_gradient'] > 10:
            confidence += 0.1
        
        # Adjust based on symmetry (important for medical regions)
        symmetry_score = features['symmetry_score']
        if symmetry_score > 0.5:
            confidence += 0.2
        
        # Adjust based on tissue density
        density_analysis = features['density_analysis']
        if density_analysis['peak_count'] > 2:  # Multiple tissue types
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def get_body_part_relationships(self, detected_parts: List[BodyPart]) -> List[Dict[str, Any]]:
        """Analyze relationships between detected body parts"""
        relationships = []
        
        for i, part1 in enumerate(detected_parts):
            for j, part2 in enumerate(detected_parts[i+1:], i+1):
                # Calculate distance between centers
                center1 = part1.center
                center2 = part2.center
                distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
                
                # Calculate overlap
                overlap = self._calculate_bbox_overlap(part1.bbox, part2.bbox)
                
                # Determine relationship type
                relationship_type = self._determine_relationship_type(part1.name, part2.name, distance, overlap)
                
                if relationship_type:
                    relationships.append({
                        'part1': part1.name,
                        'part2': part2.name,
                        'distance': float(distance),
                        'overlap': float(overlap),
                        'relationship': relationship_type
                    })
        
        return relationships
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
                               bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = area1 + area2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0
    
    def _determine_relationship_type(self, part1_name: str, part2_name: str, 
                                   distance: float, overlap: float) -> Optional[str]:
        """Determine the type of relationship between two body parts"""
        # Define anatomical relationships
        relationships = {
            ('head', 'neck'): 'connected',
            ('neck', 'chest'): 'connected',
            ('chest', 'abdomen'): 'connected',
            ('left_arm', 'chest'): 'attached',
            ('right_arm', 'chest'): 'attached',
            ('left_leg', 'abdomen'): 'attached',
            ('right_leg', 'abdomen'): 'attached',
            ('left_arm', 'right_arm'): 'symmetric',
            ('left_leg', 'right_leg'): 'symmetric'
        }
        
        # Check direct relationships
        if (part1_name, part2_name) in relationships:
            return relationships[(part1_name, part2_name)]
        if (part2_name, part1_name) in relationships:
            return relationships[(part2_name, part1_name)]
        
        # Check for proximity
        if distance < 100 and overlap > 0.1:
            return 'proximate'
        
        return None

