import re
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

@dataclass
class EmotionAnalysis:
    """Represents emotion analysis results"""
    primary_emotion: str
    emotion_scores: Dict[str, float]
    intensity: float
    confidence: float
    indicators: List[str]
    recommendations: List[str]

class EmotionAnalyzer:
    """
    Advanced emotion analysis for medical chatbot interactions
    """
    
    def __init__(self):
        """Initialize emotion analyzer"""
        self.sia = SentimentIntensityAnalyzer()
        
        # Medical-specific emotion indicators
        self.emotion_indicators = {
            'anxiety': {
                'keywords': ['worried', 'anxious', 'nervous', 'scared', 'fearful', 'panic', 'concerned'],
                'phrases': ['what if', 'afraid', 'terrified', 'worried about', 'scared of'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'frustration': {
                'keywords': ['frustrated', 'annoyed', 'irritated', 'angry', 'mad', 'upset'],
                'phrases': ['fed up', 'can\'t stand', 'so annoying', 'this is ridiculous'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'sadness': {
                'keywords': ['sad', 'depressed', 'down', 'blue', 'miserable', 'hopeless'],
                'phrases': ['feeling down', 'not myself', 'can\'t cope', 'overwhelmed'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'confusion': {
                'keywords': ['confused', 'unclear', 'don\'t understand', 'puzzled', 'lost'],
                'phrases': ['not sure', 'don\'t know', 'unclear about', 'can\'t figure out'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'relief': {
                'keywords': ['relieved', 'better', 'good news', 'thankful', 'grateful'],
                'phrases': ['that\'s good', 'feeling better', 'much better', 'so relieved'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'urgency': {
                'keywords': ['urgent', 'immediate', 'asap', 'quickly', 'fast', 'emergency'],
                'phrases': ['right now', 'immediately', 'can\'t wait', 'need help now'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            },
            'pain': {
                'keywords': ['pain', 'hurt', 'ache', 'sore', 'uncomfortable', 'agony'],
                'phrases': ['in pain', 'hurts so much', 'can\'t bear', 'excruciating'],
                'intensity_modifiers': ['severe', 'intense', 'sharp', 'throbbing', 'burning']
            },
            'hope': {
                'keywords': ['hopeful', 'optimistic', 'positive', 'encouraged', 'confident'],
                'phrases': ['feeling hopeful', 'good outlook', 'positive attitude', 'encouraged'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'quite']
            }
        }
        
        # Medical context modifiers
        self.medical_context_modifiers = {
            'diagnosis': 1.2,
            'treatment': 1.1,
            'symptoms': 1.3,
            'medication': 1.1,
            'surgery': 1.4,
            'cancer': 1.5,
            'chronic': 1.2,
            'acute': 1.3
        }
    
    def analyze_emotion(self, text: str, context: str = "") -> EmotionAnalysis:
        """
        Analyze emotion in text
        
        Args:
            text: Text to analyze
            context: Additional context for analysis
            
        Returns:
            EmotionAnalysis object
        """
        text_lower = text.lower()
        
        # Calculate emotion scores
        emotion_scores = self._calculate_emotion_scores(text_lower)
        
        # Apply medical context modifiers
        if context:
            emotion_scores = self._apply_context_modifiers(emotion_scores, context)
        
        # Calculate VADER sentiment
        vader_scores = self.sia.polarity_scores(text)
        
        # Combine emotion and sentiment scores
        combined_scores = self._combine_scores(emotion_scores, vader_scores)
        
        # Determine primary emotion
        primary_emotion = max(combined_scores, key=combined_scores.get)
        
        # Calculate intensity
        intensity = self._calculate_intensity(combined_scores, text_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(combined_scores, text_lower)
        
        # Extract indicators
        indicators = self._extract_indicators(text_lower, primary_emotion)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(primary_emotion, intensity, context)
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            emotion_scores=combined_scores,
            intensity=intensity,
            confidence=confidence,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def _calculate_emotion_scores(self, text: str) -> Dict[str, float]:
        """Calculate emotion scores based on keywords and phrases"""
        scores = {emotion: 0.0 for emotion in self.emotion_indicators.keys()}
        
        for emotion, indicators in self.emotion_indicators.items():
            # Check keywords
            keyword_matches = sum(1 for keyword in indicators['keywords'] if keyword in text)
            
            # Check phrases
            phrase_matches = sum(1 for phrase in indicators['phrases'] if phrase in text)
            
            # Check intensity modifiers
            intensity_matches = sum(1 for modifier in indicators['intensity_modifiers'] if modifier in text)
            
            # Calculate base score
            base_score = (keyword_matches * 0.3 + phrase_matches * 0.5 + intensity_matches * 0.2)
            
            # Normalize by text length
            word_count = len(text.split())
            if word_count > 0:
                scores[emotion] = min(1.0, base_score / (word_count / 10))
        
        return scores
    
    def _apply_context_modifiers(self, emotion_scores: Dict[str, float], context: str) -> Dict[str, float]:
        """Apply medical context modifiers to emotion scores"""
        context_lower = context.lower()
        
        for emotion in emotion_scores:
            modifier = 1.0
            
            for medical_term, multiplier in self.medical_context_modifiers.items():
                if medical_term in context_lower:
                    modifier *= multiplier
            
            emotion_scores[emotion] = min(1.0, emotion_scores[emotion] * modifier)
        
        return emotion_scores
    
    def _combine_scores(self, emotion_scores: Dict[str, float], vader_scores: Dict[str, float]) -> Dict[str, float]:
        """Combine emotion scores with VADER sentiment scores"""
        combined = emotion_scores.copy()
        
        # Map VADER scores to emotions
        vader_mapping = {
            'anxiety': vader_scores['neg'] * 0.7,
            'frustration': vader_scores['neg'] * 0.8,
            'sadness': vader_scores['neg'] * 0.9,
            'confusion': vader_scores['neu'] * 0.5,
            'relief': vader_scores['pos'] * 0.8,
            'urgency': vader_scores['compound'] * 0.6,
            'pain': vader_scores['neg'] * 0.6,
            'hope': vader_scores['pos'] * 0.9
        }
        
        # Combine with weights
        for emotion in combined:
            emotion_weight = 0.7
            vader_weight = 0.3
            
            combined[emotion] = (
                emotion_weight * combined[emotion] + 
                vader_weight * vader_mapping.get(emotion, 0)
            )
        
        return combined
    
    def _calculate_intensity(self, emotion_scores: Dict[str, float], text: str) -> float:
        """Calculate emotion intensity"""
        # Base intensity from highest emotion score
        max_score = max(emotion_scores.values())
        
        # Intensity modifiers in text
        intensity_words = ['very', 'extremely', 'really', 'so', 'quite', 'incredibly', 'absolutely']
        intensity_count = sum(1 for word in intensity_words if word in text)
        
        # Exclamation marks
        exclamation_count = text.count('!')
        
        # Caps lock usage
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Calculate intensity
        intensity = max_score + (intensity_count * 0.1) + (exclamation_count * 0.05) + (caps_ratio * 0.2)
        
        return min(1.0, max(0.0, intensity))
    
    def _calculate_confidence(self, emotion_scores: Dict[str, float], text: str) -> float:
        """Calculate confidence in emotion detection"""
        # Check if any emotion has a clear lead
        sorted_scores = sorted(emotion_scores.values(), reverse=True)
        
        if len(sorted_scores) < 2:
            return 0.5
        
        # Calculate score difference
        score_diff = sorted_scores[0] - sorted_scores[1]
        
        # Base confidence on score difference
        confidence = min(1.0, score_diff * 2)
        
        # Adjust based on text length and clarity
        word_count = len(text.split())
        if word_count > 5:
            confidence += 0.1
        
        # Check for clear emotional indicators
        emotional_indicators = sum(1 for emotion, indicators in self.emotion_indicators.items()
                                for keyword in indicators['keywords'] if keyword in text)
        
        if emotional_indicators > 0:
            confidence += 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _extract_indicators(self, text: str, primary_emotion: str) -> List[str]:
        """Extract specific emotion indicators from text"""
        indicators = []
        
        if primary_emotion in self.emotion_indicators:
            emotion_data = self.emotion_indicators[primary_emotion]
            
            # Find matching keywords
            for keyword in emotion_data['keywords']:
                if keyword in text:
                    indicators.append(f"Keyword: '{keyword}'")
            
            # Find matching phrases
            for phrase in emotion_data['phrases']:
                if phrase in text:
                    indicators.append(f"Phrase: '{phrase}'")
            
            # Find intensity modifiers
            for modifier in emotion_data['intensity_modifiers']:
                if modifier in text:
                    indicators.append(f"Intensity: '{modifier}'")
        
        return indicators
    
    def _generate_recommendations(self, primary_emotion: str, intensity: float, context: str) -> List[str]:
        """Generate recommendations based on emotion analysis"""
        recommendations = []
        
        if primary_emotion == 'anxiety':
            if intensity > 0.7:
                recommendations.append("Consider suggesting relaxation techniques or breathing exercises")
                recommendations.append("Recommend speaking with a mental health professional")
            else:
                recommendations.append("Provide reassurance and clear information")
                recommendations.append("Suggest discussing concerns with a healthcare provider")
        
        elif primary_emotion == 'frustration':
            recommendations.append("Acknowledge the frustration and validate feelings")
            recommendations.append("Provide clear, step-by-step guidance")
            if intensity > 0.6:
                recommendations.append("Suggest taking a break and returning when calmer")
        
        elif primary_emotion == 'sadness':
            if intensity > 0.7:
                recommendations.append("Strongly recommend mental health support")
                recommendations.append("Provide crisis resources if needed")
            else:
                recommendations.append("Offer emotional support and understanding")
                recommendations.append("Suggest discussing feelings with a healthcare provider")
        
        elif primary_emotion == 'confusion':
            recommendations.append("Provide clear, simple explanations")
            recommendations.append("Break down complex information into smaller parts")
            recommendations.append("Encourage asking follow-up questions")
        
        elif primary_emotion == 'urgency':
            if intensity > 0.6:
                recommendations.append("Prioritize immediate medical attention")
                recommendations.append("Provide emergency contact information")
            else:
                recommendations.append("Schedule prompt medical consultation")
        
        elif primary_emotion == 'pain':
            if intensity > 0.7:
                recommendations.append("Recommend immediate medical evaluation")
                recommendations.append("Suggest pain management strategies")
            else:
                recommendations.append("Provide pain assessment guidance")
                recommendations.append("Suggest discussing pain with healthcare provider")
        
        elif primary_emotion == 'hope':
            recommendations.append("Encourage maintaining positive outlook")
            recommendations.append("Provide supportive information")
        
        # General recommendations
        if intensity > 0.8:
            recommendations.append("Consider escalating to human healthcare provider")
        
        return recommendations
    
    def analyze_emotion_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emotion trends across multiple texts"""
        if not texts:
            return {}
        
        emotions = []
        intensities = []
        confidences = []
        
        for text in texts:
            analysis = self.analyze_emotion(text)
            emotions.append(analysis.primary_emotion)
            intensities.append(analysis.intensity)
            confidences.append(analysis.confidence)
        
        # Calculate trends
        emotion_counts = Counter(emotions)
        avg_intensity = np.mean(intensities)
        avg_confidence = np.mean(confidences)
        
        # Identify dominant emotion
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else 'neutral'
        
        # Calculate emotion stability
        emotion_stability = len(set(emotions)) / len(emotions) if emotions else 0
        
        return {
            'emotion_distribution': dict(emotion_counts),
            'dominant_emotion': dominant_emotion,
            'average_intensity': float(avg_intensity),
            'average_confidence': float(avg_confidence),
            'emotion_stability': float(emotion_stability),
            'trend_analysis': self._analyze_emotion_trend(emotions, intensities)
        }
    
    def _analyze_emotion_trend(self, emotions: List[str], intensities: List[float]) -> str:
        """Analyze the trend of emotions over time"""
        if len(emotions) < 2:
            return "insufficient_data"
        
        # Simple trend analysis
        positive_emotions = ['relief', 'hope']
        negative_emotions = ['anxiety', 'frustration', 'sadness', 'pain']
        
        recent_emotions = emotions[-3:]  # Last 3 emotions
        recent_intensities = intensities[-3:]
        
        positive_count = sum(1 for emotion in recent_emotions if emotion in positive_emotions)
        negative_count = sum(1 for emotion in recent_emotions if emotion in negative_emotions)
        
        avg_recent_intensity = np.mean(recent_intensities)
        
        if positive_count > negative_count and avg_recent_intensity < 0.6:
            return "improving"
        elif negative_count > positive_count and avg_recent_intensity > 0.7:
            return "worsening"
        else:
            return "stable"
    
    def get_emotion_summary(self, analysis: EmotionAnalysis) -> Dict[str, Any]:
        """Get a summary of emotion analysis"""
        return {
            'primary_emotion': analysis.primary_emotion,
            'intensity_level': self._get_intensity_level(analysis.intensity),
            'confidence_level': self._get_confidence_level(analysis.confidence),
            'key_indicators': analysis.indicators[:3],  # Top 3 indicators
            'recommendations': analysis.recommendations,
            'emotion_scores': {k: round(v, 3) for k, v in analysis.emotion_scores.items()},
            'requires_attention': analysis.intensity > 0.7 or analysis.primary_emotion in ['anxiety', 'sadness', 'urgency', 'pain']
        }
    
    def _get_intensity_level(self, intensity: float) -> str:
        """Get intensity level description"""
        if intensity >= 0.8:
            return 'very_high'
        elif intensity >= 0.6:
            return 'high'
        elif intensity >= 0.4:
            return 'medium'
        elif intensity >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        else:
            return 'low'

