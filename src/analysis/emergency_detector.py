import re
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EmergencyLevel(Enum):
    """Emergency severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EmergencyDetection:
    """Represents emergency detection results"""
    is_emergency: bool
    level: EmergencyLevel
    confidence: float
    indicators: List[str]
    recommended_actions: List[str]
    urgency_score: float
    medical_priority: str

class EmergencyDetector:
    """
    Advanced emergency detection for medical chatbot
    """
    
    def __init__(self):
        """Initialize emergency detector"""
        # Critical emergency keywords and patterns
        self.critical_patterns = {
            'cardiac_emergency': {
                'keywords': ['chest pain', 'heart attack', 'cardiac arrest', 'heart failure'],
                'phrases': ['crushing chest pain', 'severe chest pain', 'can\'t breathe', 'heart racing'],
                'symptoms': ['chest pressure', 'chest tightness', 'chest discomfort', 'arm pain'],
                'severity_indicators': ['severe', 'intense', 'crushing', 'unbearable', 'worst pain ever']
            },
            'stroke_indicators': {
                'keywords': ['stroke', 'paralysis', 'numbness', 'weakness', 'speech problems'],
                'phrases': ['can\'t move', 'face drooping', 'slurred speech', 'confusion', 'severe headache'],
                'symptoms': ['sudden weakness', 'vision problems', 'balance issues', 'dizziness'],
                'severity_indicators': ['sudden', 'severe', 'can\'t speak', 'can\'t move']
            },
            'respiratory_emergency': {
                'keywords': ['can\'t breathe', 'shortness of breath', 'choking', 'suffocating'],
                'phrases': ['struggling to breathe', 'gasping for air', 'turning blue', 'chest tightness'],
                'symptoms': ['wheezing', 'coughing blood', 'severe cough', 'chest pain'],
                'severity_indicators': ['severe', 'extreme', 'can\'t catch breath', 'emergency']
            },
            'trauma_emergency': {
                'keywords': ['bleeding', 'blood', 'injury', 'accident', 'fall', 'hit'],
                'phrases': ['lots of blood', 'bleeding heavily', 'severe injury', 'head injury'],
                'symptoms': ['unconscious', 'confusion', 'severe pain', 'broken bone'],
                'severity_indicators': ['severe', 'heavy', 'unconscious', 'can\'t move']
            },
            'allergic_reaction': {
                'keywords': ['allergic reaction', 'anaphylaxis', 'swelling', 'hives', 'rash'],
                'phrases': ['throat swelling', 'can\'t swallow', 'difficulty breathing', 'severe rash'],
                'symptoms': ['face swelling', 'tongue swelling', 'wheezing', 'dizziness'],
                'severity_indicators': ['severe', 'throat closing', 'can\'t breathe', 'emergency']
            },
            'poisoning_overdose': {
                'keywords': ['overdose', 'poisoning', 'took too much', 'accidental ingestion'],
                'phrases': ['unconscious', 'not responding', 'seizures', 'vomiting blood'],
                'symptoms': ['confusion', 'drowsiness', 'difficulty breathing', 'irregular heartbeat'],
                'severity_indicators': ['unconscious', 'not breathing', 'seizures', 'emergency']
            }
        }
        
        # High priority medical conditions
        self.high_priority_conditions = {
            'severe_pain': {
                'keywords': ['severe pain', 'excruciating', 'unbearable', 'worst pain'],
                'body_parts': ['chest', 'head', 'abdomen', 'back'],
                'severity': 0.8
            },
            'high_fever': {
                'keywords': ['high fever', 'very hot', 'burning up', 'temperature'],
                'indicators': ['over 103', '104', '105', 'severe fever'],
                'severity': 0.7
            },
            'severe_nausea': {
                'keywords': ['severe nausea', 'can\'t stop vomiting', 'vomiting blood'],
                'indicators': ['dehydrated', 'can\'t keep down', 'blood in vomit'],
                'severity': 0.6
            },
            'mental_health_crisis': {
                'keywords': ['suicidal', 'want to die', 'self harm', 'crisis'],
                'indicators': ['hopeless', 'can\'t cope', 'emergency', 'help me'],
                'severity': 0.9
            }
        }
        
        # Urgency modifiers
        self.urgency_modifiers = {
            'time_indicators': ['now', 'immediately', 'asap', 'right now', 'urgent'],
            'intensity_indicators': ['severe', 'extreme', 'worst', 'unbearable', 'critical'],
            'action_indicators': ['call 911', 'emergency room', 'ambulance', 'help me'],
            'symptom_combinations': ['chest pain and shortness of breath', 'headache and fever']
        }
    
    def detect_emergency(self, text: str, context: str = "") -> EmergencyDetection:
        """
        Detect emergency situations in text
        
        Args:
            text: Input text to analyze
            context: Additional context
            
        Returns:
            EmergencyDetection object
        """
        text_lower = text.lower()
        
        # Analyze critical patterns
        critical_scores = self._analyze_critical_patterns(text_lower)
        
        # Analyze high priority conditions
        priority_scores = self._analyze_priority_conditions(text_lower)
        
        # Calculate urgency modifiers
        urgency_modifiers = self._calculate_urgency_modifiers(text_lower)
        
        # Combine scores
        emergency_score = self._combine_emergency_scores(
            critical_scores, priority_scores, urgency_modifiers
        )
        
        # Determine emergency level
        level = self._determine_emergency_level(emergency_score)
        
        # Calculate confidence
        confidence = self._calculate_emergency_confidence(
            critical_scores, priority_scores, urgency_modifiers
        )
        
        # Extract indicators
        indicators = self._extract_emergency_indicators(text_lower, critical_scores, priority_scores)
        
        # Generate recommended actions
        recommended_actions = self._generate_emergency_actions(level, indicators, context)
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(emergency_score, urgency_modifiers)
        
        # Determine medical priority
        medical_priority = self._determine_medical_priority(level, indicators)
        
        return EmergencyDetection(
            is_emergency=level != EmergencyLevel.NONE,
            level=level,
            confidence=confidence,
            indicators=indicators,
            recommended_actions=recommended_actions,
            urgency_score=urgency_score,
            medical_priority=medical_priority
        )
    
    def _analyze_critical_patterns(self, text: str) -> Dict[str, float]:
        """Analyze critical emergency patterns"""
        scores = {}
        
        for pattern_name, pattern_data in self.critical_patterns.items():
            score = 0.0
            
            # Check keywords
            keyword_matches = sum(1 for keyword in pattern_data['keywords'] if keyword in text)
            score += keyword_matches * 0.3
            
            # Check phrases
            phrase_matches = sum(1 for phrase in pattern_data['phrases'] if phrase in text)
            score += phrase_matches * 0.4
            
            # Check symptoms
            symptom_matches = sum(1 for symptom in pattern_data['symptoms'] if symptom in text)
            score += symptom_matches * 0.2
            
            # Check severity indicators
            severity_matches = sum(1 for indicator in pattern_data['severity_indicators'] if indicator in text)
            score += severity_matches * 0.1
            
            # Normalize score
            scores[pattern_name] = min(1.0, score)
        
        return scores
    
    def _analyze_priority_conditions(self, text: str) -> Dict[str, float]:
        """Analyze high priority medical conditions"""
        scores = {}
        
        for condition_name, condition_data in self.high_priority_conditions.items():
            score = 0.0
            
            # Check keywords
            keyword_matches = sum(1 for keyword in condition_data['keywords'] if keyword in text)
            score += keyword_matches * 0.4
            
            # Check specific indicators
            if 'indicators' in condition_data:
                indicator_matches = sum(1 for indicator in condition_data['indicators'] if indicator in text)
                score += indicator_matches * 0.3
            
            # Check body parts for pain conditions
            if 'body_parts' in condition_data:
                body_part_matches = sum(1 for part in condition_data['body_parts'] if part in text)
                score += body_part_matches * 0.2
            
            # Apply severity multiplier
            score *= condition_data['severity']
            
            scores[condition_name] = min(1.0, score)
        
        return scores
    
    def _calculate_urgency_modifiers(self, text: str) -> Dict[str, float]:
        """Calculate urgency modifiers"""
        modifiers = {}
        
        # Time indicators
        time_matches = sum(1 for indicator in self.urgency_modifiers['time_indicators'] if indicator in text)
        modifiers['time_urgency'] = min(1.0, time_matches * 0.3)
        
        # Intensity indicators
        intensity_matches = sum(1 for indicator in self.urgency_modifiers['intensity_indicators'] if indicator in text)
        modifiers['intensity_urgency'] = min(1.0, intensity_matches * 0.3)
        
        # Action indicators
        action_matches = sum(1 for indicator in self.urgency_modifiers['action_indicators'] if indicator in text)
        modifiers['action_urgency'] = min(1.0, action_matches * 0.4)
        
        # Symptom combinations
        combo_matches = sum(1 for combo in self.urgency_modifiers['symptom_combinations'] if combo in text)
        modifiers['combo_urgency'] = min(1.0, combo_matches * 0.5)
        
        return modifiers
    
    def _combine_emergency_scores(self, critical_scores: Dict[str, float], 
                                 priority_scores: Dict[str, float],
                                 urgency_modifiers: Dict[str, float]) -> float:
        """Combine all emergency scores"""
        # Get maximum critical score
        max_critical = max(critical_scores.values()) if critical_scores else 0.0
        
        # Get maximum priority score
        max_priority = max(priority_scores.values()) if priority_scores else 0.0
        
        # Calculate urgency modifier
        urgency_modifier = sum(urgency_modifiers.values()) / len(urgency_modifiers) if urgency_modifiers else 0.0
        
        # Combine with weights
        emergency_score = (
            0.5 * max_critical +
            0.3 * max_priority +
            0.2 * urgency_modifier
        )
        
        return min(1.0, max(0.0, emergency_score))
    
    def _determine_emergency_level(self, emergency_score: float) -> EmergencyLevel:
        """Determine emergency level based on score"""
        if emergency_score >= 0.9:
            return EmergencyLevel.CRITICAL
        elif emergency_score >= 0.7:
            return EmergencyLevel.HIGH
        elif emergency_score >= 0.5:
            return EmergencyLevel.MEDIUM
        elif emergency_score >= 0.3:
            return EmergencyLevel.LOW
        else:
            return EmergencyLevel.NONE
    
    def _calculate_emergency_confidence(self, critical_scores: Dict[str, float],
                                      priority_scores: Dict[str, float],
                                      urgency_modifiers: Dict[str, float]) -> float:
        """Calculate confidence in emergency detection"""
        # Check if any pattern has high confidence
        max_critical = max(critical_scores.values()) if critical_scores else 0.0
        max_priority = max(priority_scores.values()) if priority_scores else 0.0
        
        # Check for multiple indicators
        indicator_count = sum(1 for score in critical_scores.values() if score > 0.3)
        indicator_count += sum(1 for score in priority_scores.values() if score > 0.3)
        
        # Calculate confidence
        confidence = max(max_critical, max_priority)
        
        # Boost confidence for multiple indicators
        if indicator_count > 1:
            confidence += 0.2
        
        # Boost confidence for urgency modifiers
        urgency_boost = sum(urgency_modifiers.values()) * 0.1
        confidence += urgency_boost
        
        return min(1.0, max(0.0, confidence))
    
    def _extract_emergency_indicators(self, text: str, critical_scores: Dict[str, float],
                                    priority_scores: Dict[str, float]) -> List[str]:
        """Extract specific emergency indicators"""
        indicators = []
        
        # Extract critical pattern indicators
        for pattern_name, score in critical_scores.items():
            if score > 0.3:
                pattern_data = self.critical_patterns[pattern_name]
                
                # Find matching keywords
                for keyword in pattern_data['keywords']:
                    if keyword in text:
                        indicators.append(f"Critical: {keyword}")
                
                # Find matching phrases
                for phrase in pattern_data['phrases']:
                    if phrase in text:
                        indicators.append(f"Critical phrase: {phrase}")
        
        # Extract priority condition indicators
        for condition_name, score in priority_scores.items():
            if score > 0.3:
                condition_data = self.high_priority_conditions[condition_name]
                
                # Find matching keywords
                for keyword in condition_data['keywords']:
                    if keyword in text:
                        indicators.append(f"Priority: {keyword}")
        
        return indicators[:10]  # Limit to top 10 indicators
    
    def _generate_emergency_actions(self, level: EmergencyLevel, indicators: List[str], 
                                  context: str) -> List[str]:
        """Generate recommended emergency actions"""
        actions = []
        
        if level == EmergencyLevel.CRITICAL:
            actions.append("Call 911 immediately")
            actions.append("Do not delay seeking emergency medical care")
            actions.append("If unconscious, check for breathing and pulse")
            actions.append("Stay with the person until help arrives")
        
        elif level == EmergencyLevel.HIGH:
            actions.append("Seek immediate medical attention")
            actions.append("Go to the nearest emergency room")
            actions.append("Call emergency services if symptoms worsen")
            actions.append("Do not drive yourself if experiencing severe symptoms")
        
        elif level == EmergencyLevel.MEDIUM:
            actions.append("Schedule urgent medical consultation")
            actions.append("Contact your healthcare provider immediately")
            actions.append("Monitor symptoms closely")
            actions.append("Go to urgent care if symptoms persist or worsen")
        
        elif level == EmergencyLevel.LOW:
            actions.append("Monitor symptoms")
            actions.append("Contact healthcare provider if symptoms worsen")
            actions.append("Consider urgent care if symptoms persist")
        
        # Add specific actions based on indicators
        if any('chest pain' in indicator.lower() for indicator in indicators):
            actions.append("If chest pain, sit down and rest")
            actions.append("Take prescribed heart medication if available")
        
        if any('breathing' in indicator.lower() for indicator in indicators):
            actions.append("Try to stay calm and breathe slowly")
            actions.append("Sit upright if possible")
        
        if any('bleeding' in indicator.lower() for indicator in indicators):
            actions.append("Apply direct pressure to stop bleeding")
            actions.append("Elevate the injured area if possible")
        
        return actions
    
    def _calculate_urgency_score(self, emergency_score: float, urgency_modifiers: Dict[str, float]) -> float:
        """Calculate overall urgency score"""
        urgency_modifier = sum(urgency_modifiers.values()) / len(urgency_modifiers) if urgency_modifiers else 0.0
        
        # Combine emergency score with urgency modifiers
        urgency_score = 0.7 * emergency_score + 0.3 * urgency_modifier
        
        return min(1.0, max(0.0, urgency_score))
    
    def _determine_medical_priority(self, level: EmergencyLevel, indicators: List[str]) -> str:
        """Determine medical priority level"""
        if level == EmergencyLevel.CRITICAL:
            return "immediate"
        elif level == EmergencyLevel.HIGH:
            return "urgent"
        elif level == EmergencyLevel.MEDIUM:
            return "priority"
        elif level == EmergencyLevel.LOW:
            return "routine"
        else:
            return "non_urgent"
    
    def analyze_emergency_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emergency trends across multiple texts"""
        if not texts:
            return {}
        
        emergency_levels = []
        urgency_scores = []
        confidence_scores = []
        
        for text in texts:
            detection = self.detect_emergency(text)
            emergency_levels.append(detection.level.value)
            urgency_scores.append(detection.urgency_score)
            confidence_scores.append(detection.confidence)
        
        # Calculate trends
        level_counts = {}
        for level in emergency_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        avg_urgency = np.mean(urgency_scores)
        avg_confidence = np.mean(confidence_scores)
        
        # Determine trend
        recent_levels = emergency_levels[-3:] if len(emergency_levels) >= 3 else emergency_levels
        trend = self._analyze_emergency_trend(recent_levels)
        
        return {
            'level_distribution': level_counts,
            'average_urgency': float(avg_urgency),
            'average_confidence': float(avg_confidence),
            'trend': trend,
            'requires_immediate_attention': any(level in ['critical', 'high'] for level in recent_levels)
        }
    
    def _analyze_emergency_trend(self, levels: List[str]) -> str:
        """Analyze emergency trend over time"""
        if len(levels) < 2:
            return "insufficient_data"
        
        # Map levels to numeric values
        level_values = {
            'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        
        numeric_levels = [level_values.get(level, 0) for level in levels]
        
        # Calculate trend
        if len(numeric_levels) >= 2:
            if numeric_levels[-1] > numeric_levels[0]:
                return "escalating"
            elif numeric_levels[-1] < numeric_levels[0]:
                return "de-escalating"
            else:
                return "stable"
        
        return "stable"
    
    def get_emergency_summary(self, detection: EmergencyDetection) -> Dict[str, Any]:
        """Get a summary of emergency detection"""
        return {
            'is_emergency': detection.is_emergency,
            'emergency_level': detection.level.value,
            'confidence': detection.confidence,
            'urgency_score': detection.urgency_score,
            'medical_priority': detection.medical_priority,
            'key_indicators': detection.indicators[:5],  # Top 5 indicators
            'recommended_actions': detection.recommended_actions,
            'requires_immediate_action': detection.level in [EmergencyLevel.CRITICAL, EmergencyLevel.HIGH]
        }
