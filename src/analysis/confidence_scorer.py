import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from config.settings import settings

@dataclass
class ConfidenceScore:
    """Represents a confidence score with metadata"""
    score: float
    level: str  # 'low', 'medium', 'high'
    factors: Dict[str, float]
    recommendation: str

class ConfidenceScorer:
    """
    Advanced confidence scoring for medical chatbot responses
    """
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.emergency_threshold = settings.EMERGENCY_CONFIDENCE_THRESHOLD
        
        # Weight factors for different confidence indicators
        self.weights = {
            'retrieval_similarity': 0.3,
            'source_quality': 0.2,
            'response_coherence': 0.2,
            'medical_term_match': 0.15,
            'context_relevance': 0.1,
            'response_length': 0.05
        }
    
    def calculate_confidence(self, 
                           retrieval_scores: List[float],
                           response_text: str,
                           query_text: str,
                           sources: List[Dict[str, Any]] = None,
                           medical_entities: Dict[str, List[str]] = None) -> ConfidenceScore:
        """
        Calculate overall confidence score
        
        Args:
            retrieval_scores: List of similarity scores from retrieval
            response_text: Generated response text
            query_text: Original query text
            sources: List of source documents
            medical_entities: Extracted medical entities
            
        Returns:
            ConfidenceScore object
        """
        factors = {}
        
        # Calculate retrieval similarity factor
        factors['retrieval_similarity'] = self._calculate_retrieval_confidence(retrieval_scores)
        
        # Calculate source quality factor
        factors['source_quality'] = self._calculate_source_quality(sources or [])
        
        # Calculate response coherence factor
        factors['response_coherence'] = self._calculate_response_coherence(response_text)
        
        # Calculate medical term match factor
        factors['medical_term_match'] = self._calculate_medical_term_match(
            query_text, response_text, medical_entities or {}
        )
        
        # Calculate context relevance factor
        factors['context_relevance'] = self._calculate_context_relevance(
            query_text, response_text, sources or []
        )
        
        # Calculate response length factor
        factors['response_length'] = self._calculate_response_length_factor(response_text)
        
        # Calculate weighted overall score
        overall_score = sum(
            factors[factor] * self.weights[factor] 
            for factor in factors
        )
        
        # Determine confidence level
        level = self._determine_confidence_level(overall_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score, factors)
        
        return ConfidenceScore(
            score=overall_score,
            level=level,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_retrieval_confidence(self, retrieval_scores: List[float]) -> float:
        """Calculate confidence based on retrieval scores"""
        if not retrieval_scores:
            return 0.0
        
        # Use the highest score as primary indicator
        max_score = max(retrieval_scores)
        
        # Consider score distribution
        if len(retrieval_scores) > 1:
            score_std = np.std(retrieval_scores)
            # Lower standard deviation indicates more consistent results
            consistency_factor = max(0.5, 1.0 - score_std)
        else:
            consistency_factor = 1.0
        
        # Combine max score with consistency
        confidence = max_score * consistency_factor
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_source_quality(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on source quality"""
        if not sources:
            return 0.0
        
        quality_scores = []
        
        for source in sources:
            score = 0.5  # Base score
            
            # Check source metadata
            metadata = source.get('metadata', {})
            
            # Medical source preference
            if metadata.get('source_type') == 'medical_journal':
                score += 0.3
            elif metadata.get('source_type') == 'medical_textbook':
                score += 0.25
            elif metadata.get('source_type') == 'medical_website':
                score += 0.2
            elif metadata.get('source_type') == 'general_web':
                score += 0.1
            
            # Author credibility
            if metadata.get('author_credentials') == 'medical_professional':
                score += 0.2
            elif metadata.get('author_credentials') == 'researcher':
                score += 0.15
            
            # Publication date (recent is better for medical info)
            if 'publication_date' in metadata:
                score += 0.1  # Assume recent if date is available
            
            # Content length (longer content often more comprehensive)
            content_length = len(source.get('content', ''))
            if content_length > 500:
                score += 0.1
            elif content_length < 100:
                score -= 0.1
            
            quality_scores.append(min(1.0, max(0.0, score)))
        
        return np.mean(quality_scores) if quality_scores else 0.0
    
    def _calculate_response_coherence(self, response_text: str) -> float:
        """Calculate response coherence score"""
        if not response_text.strip():
            return 0.0
        
        score = 0.5  # Base score
        
        # Length check (too short or too long reduces coherence)
        word_count = len(response_text.split())
        if 20 <= word_count <= 200:
            score += 0.2
        elif word_count < 10:
            score -= 0.3
        elif word_count > 500:
            score -= 0.1
        
        # Check for medical terminology usage
        medical_terms = [
            'symptom', 'diagnosis', 'treatment', 'condition', 'patient',
            'medical', 'health', 'doctor', 'physician', 'clinical'
        ]
        
        medical_term_count = sum(1 for term in medical_terms if term.lower() in response_text.lower())
        if medical_term_count > 0:
            score += min(0.2, medical_term_count * 0.05)
        
        # Check for proper sentence structure
        sentences = response_text.split('.')
        if len(sentences) > 1:
            avg_sentence_length = word_count / len(sentences)
            if 10 <= avg_sentence_length <= 25:
                score += 0.1
        
        # Check for uncertainty indicators (reduce confidence)
        uncertainty_words = ['maybe', 'possibly', 'might', 'could', 'perhaps', 'unclear']
        uncertainty_count = sum(1 for word in uncertainty_words if word.lower() in response_text.lower())
        if uncertainty_count > 2:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_medical_term_match(self, query_text: str, response_text: str, 
                                    medical_entities: Dict[str, List[str]]) -> float:
        """Calculate medical term matching score"""
        if not medical_entities:
            return 0.5  # Neutral score if no entities provided
        
        query_terms = set()
        response_terms = set()
        
        # Extract terms from query
        for category, terms in medical_entities.items():
            query_terms.update([term.lower() for term in terms])
        
        # Extract medical terms from response
        response_lower = response_text.lower()
        for category, terms in medical_entities.items():
            for term in terms:
                if term.lower() in response_lower:
                    response_terms.add(term.lower())
        
        # Calculate match ratio
        if not query_terms:
            return 0.5
        
        match_ratio = len(query_terms.intersection(response_terms)) / len(query_terms)
        
        # Bonus for additional relevant medical terms in response
        additional_terms = response_terms - query_terms
        if additional_terms:
            bonus = min(0.2, len(additional_terms) * 0.05)
            match_ratio += bonus
        
        return min(1.0, max(0.0, match_ratio))
    
    def _calculate_context_relevance(self, query_text: str, response_text: str, 
                                   sources: List[Dict[str, Any]]) -> float:
        """Calculate context relevance score"""
        if not sources:
            return 0.5
        
        # Check if response addresses the query
        query_words = set(query_text.lower().split())
        response_words = set(response_text.lower().split())
        
        # Calculate word overlap
        word_overlap = len(query_words.intersection(response_words))
        if query_words:
            word_relevance = word_overlap / len(query_words)
        else:
            word_relevance = 0.0
        
        # Check if response contains information from sources
        source_content = ' '.join([source.get('content', '') for source in sources])
        source_words = set(source_content.lower().split())
        
        response_source_overlap = len(response_words.intersection(source_words))
        if source_words:
            source_relevance = response_source_overlap / len(source_words)
        else:
            source_relevance = 0.0
        
        # Combine word relevance and source relevance
        relevance_score = 0.6 * word_relevance + 0.4 * source_relevance
        
        return min(1.0, max(0.0, relevance_score))
    
    def _calculate_response_length_factor(self, response_text: str) -> float:
        """Calculate response length appropriateness factor"""
        word_count = len(response_text.split())
        
        # Optimal length for medical responses is 50-150 words
        if 50 <= word_count <= 150:
            return 1.0
        elif 30 <= word_count < 50 or 150 < word_count <= 200:
            return 0.8
        elif 20 <= word_count < 30 or 200 < word_count <= 300:
            return 0.6
        else:
            return 0.4
    
    def _determine_confidence_level(self, score: float) -> str:
        """Determine confidence level based on score"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(self, score: float, factors: Dict[str, float]) -> str:
        """Generate recommendation based on confidence score and factors"""
        if score >= 0.8:
            return "High confidence response. Information appears reliable and comprehensive."
        elif score >= 0.6:
            return "Medium confidence response. Consider consulting additional sources for verification."
        else:
            # Identify specific issues
            issues = []
            
            if factors.get('retrieval_similarity', 0) < 0.5:
                issues.append("limited relevant information found")
            
            if factors.get('source_quality', 0) < 0.5:
                issues.append("source quality concerns")
            
            if factors.get('response_coherence', 0) < 0.5:
                issues.append("response clarity issues")
            
            if factors.get('medical_term_match', 0) < 0.5:
                issues.append("limited medical terminology coverage")
            
            if issues:
                issue_text = ", ".join(issues)
                return f"Low confidence response due to {issue_text}. Please consult a healthcare professional for accurate medical advice."
            else:
                return "Low confidence response. Please consult a healthcare professional for accurate medical advice."
    
    def calculate_emergency_confidence(self, query_text: str, response_text: str,
                                     emergency_indicators: List[str]) -> ConfidenceScore:
        """Calculate confidence specifically for emergency situations"""
        factors = {}
        
        # Emergency keyword presence
        emergency_keywords = [
            'emergency', 'urgent', 'immediate', 'critical', 'severe',
            'chest pain', 'heart attack', 'stroke', 'unconscious',
            'bleeding', 'difficulty breathing', 'allergic reaction'
        ]
        
        query_lower = query_text.lower()
        response_lower = response_text.lower()
        
        query_emergency_count = sum(1 for keyword in emergency_keywords if keyword in query_lower)
        response_emergency_count = sum(1 for keyword in emergency_keywords if keyword in response_lower)
        
        factors['emergency_keyword_match'] = min(1.0, (query_emergency_count + response_emergency_count) / 3)
        
        # Response urgency level
        urgency_indicators = ['immediately', 'urgent', 'emergency', 'call 911', 'seek help']
        urgency_count = sum(1 for indicator in urgency_indicators if indicator in response_lower)
        factors['response_urgency'] = min(1.0, urgency_count / 2)
        
        # Response clarity for emergency
        factors['emergency_clarity'] = self._calculate_emergency_clarity(response_text)
        
        # Overall emergency confidence
        emergency_score = (
            0.4 * factors['emergency_keyword_match'] +
            0.3 * factors['response_urgency'] +
            0.3 * factors['emergency_clarity']
        )
        
        level = 'high' if emergency_score >= 0.7 else 'medium' if emergency_score >= 0.5 else 'low'
        
        recommendation = self._generate_emergency_recommendation(emergency_score, factors)
        
        return ConfidenceScore(
            score=emergency_score,
            level=level,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_emergency_clarity(self, response_text: str) -> float:
        """Calculate clarity of emergency response"""
        score = 0.5
        
        # Check for clear action instructions
        action_words = ['call', 'go to', 'visit', 'seek', 'contact', 'immediately']
        action_count = sum(1 for word in action_words if word in response_text.lower())
        if action_count > 0:
            score += 0.3
        
        # Check for specific emergency services mention
        if any(service in response_text.lower() for service in ['911', 'emergency room', 'ambulance', 'paramedic']):
            score += 0.2
        
        # Check for clear, direct language
        if len(response_text.split()) > 10:  # Sufficient detail
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _generate_emergency_recommendation(self, score: float, factors: Dict[str, float]) -> str:
        """Generate emergency-specific recommendation"""
        if score >= 0.7:
            return "High confidence emergency response. Follow the provided instructions immediately."
        elif score >= 0.5:
            return "Medium confidence emergency response. Consider seeking additional emergency guidance."
        else:
            return "Low confidence emergency response. Please call emergency services immediately for urgent medical situations."
    
    def get_confidence_breakdown(self, confidence_score: ConfidenceScore) -> Dict[str, Any]:
        """Get detailed breakdown of confidence score"""
        return {
            'overall_score': confidence_score.score,
            'confidence_level': confidence_score.level,
            'factor_scores': confidence_score.factors,
            'factor_weights': self.weights,
            'weighted_contributions': {
                factor: score * self.weights[factor]
                for factor, score in confidence_score.factors.items()
            },
            'recommendation': confidence_score.recommendation,
            'thresholds': {
                'low': 0.0,
                'medium': 0.6,
                'high': 0.8
            }
        }

