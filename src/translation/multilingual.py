from langdetect import detect, detect_langs, LangDetectException
from typing import Dict, Any, List, Optional, Tuple
import requests
import json
from config.settings import settings

class MultilingualProcessor:
    """
    Multilingual processing for medical chatbot
    """
    
    def __init__(self):
        """Initialize multilingual processor"""
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'tr': 'Turkish',
            'pl': 'Polish',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'uk': 'Ukrainian',
            'be': 'Belarusian',
            'mk': 'Macedonian',
            'sq': 'Albanian',
            'sr': 'Serbian',
            'bs': 'Bosnian',
            'me': 'Montenegrin',
            'is': 'Icelandic',
            'ga': 'Irish',
            'cy': 'Welsh',
            'mt': 'Maltese',
            'eu': 'Basque',
            'ca': 'Catalan',
            'gl': 'Galician'
        }
        
        # Medical terminology in different languages
        self.medical_terms = {
            'en': {
                'pain': 'pain', 'fever': 'fever', 'headache': 'headache',
                'cough': 'cough', 'nausea': 'nausea', 'dizziness': 'dizziness',
                'chest_pain': 'chest pain', 'shortness_of_breath': 'shortness of breath',
                'emergency': 'emergency', 'doctor': 'doctor', 'hospital': 'hospital'
            },
            'es': {
                'pain': 'dolor', 'fever': 'fiebre', 'headache': 'dolor de cabeza',
                'cough': 'tos', 'nausea': 'náusea', 'dizziness': 'mareo',
                'chest_pain': 'dolor de pecho', 'shortness_of_breath': 'dificultad para respirar',
                'emergency': 'emergencia', 'doctor': 'médico', 'hospital': 'hospital'
            },
            'fr': {
                'pain': 'douleur', 'fever': 'fièvre', 'headache': 'mal de tête',
                'cough': 'toux', 'nausea': 'nausée', 'dizziness': 'vertige',
                'chest_pain': 'douleur thoracique', 'shortness_of_breath': 'essoufflement',
                'emergency': 'urgence', 'doctor': 'médecin', 'hospital': 'hôpital'
            },
            'de': {
                'pain': 'Schmerz', 'fever': 'Fieber', 'headache': 'Kopfschmerz',
                'cough': 'Husten', 'nausea': 'Übelkeit', 'dizziness': 'Schwindel',
                'chest_pain': 'Brustschmerz', 'shortness_of_breath': 'Atemnot',
                'emergency': 'Notfall', 'doctor': 'Arzt', 'hospital': 'Krankenhaus'
            }
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with language detection results
        """
        try:
            # Detect primary language
            primary_lang = detect(text)
            
            # Get confidence scores for all detected languages
            lang_scores = detect_langs(text)
            
            # Format results
            results = {
                'primary_language': primary_lang,
                'language_name': self.supported_languages.get(primary_lang, 'Unknown'),
                'confidence': lang_scores[0].prob if lang_scores else 0.0,
                'all_detected': [
                    {
                        'language': lang.lang,
                        'name': self.supported_languages.get(lang.lang, 'Unknown'),
                        'confidence': lang.prob
                    }
                    for lang in lang_scores
                ],
                'is_medical_context': self._is_medical_context(text, primary_lang)
            }
            
            return results
            
        except LangDetectException as e:
            return {
                'primary_language': 'unknown',
                'language_name': 'Unknown',
                'confidence': 0.0,
                'all_detected': [],
                'error': str(e),
                'is_medical_context': False
            }
    
    def _is_medical_context(self, text: str, language: str) -> bool:
        """Check if text contains medical terminology"""
        text_lower = text.lower()
        
        if language in self.medical_terms:
            medical_terms = self.medical_terms[language]
            return any(term in text_lower for term in medical_terms.values())
        
        # Fallback to English medical terms
        english_terms = self.medical_terms['en']
        return any(term in text_lower for term in english_terms.values())
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = None) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Dictionary with translation results
        """
        try:
            # Auto-detect source language if not provided
            if not source_language:
                lang_detection = self.detect_language(text)
                source_language = lang_detection['primary_language']
            
            # If source and target are the same, return original text
            if source_language == target_language:
                return {
                    'original_text': text,
                    'translated_text': text,
                    'source_language': source_language,
                    'target_language': target_language,
                    'confidence': 1.0,
                    'method': 'no_translation_needed'
                }
            
            # Use Google Translate API (you would need to implement this)
            # For now, return a placeholder
            translated_text = self._translate_with_google(text, source_language, target_language)
            
            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence': 0.8,  # Placeholder confidence
                'method': 'google_translate'
            }
            
        except Exception as e:
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'confidence': 0.0,
                'error': str(e),
                'method': 'error'
            }
    
    def _translate_with_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Google Translate API
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        # This is a placeholder implementation
        # In practice, you would use the Google Translate API or another translation service
        
        # For demo purposes, return a simple translation
        if source_lang == 'en' and target_lang == 'es':
            return f"[ES] {text}"
        elif source_lang == 'en' and target_lang == 'fr':
            return f"[FR] {text}"
        elif source_lang == 'en' and target_lang == 'de':
            return f"[DE] {text}"
        else:
            return f"[{target_lang.upper()}] {text}"
    
    def get_medical_terms(self, language: str) -> Dict[str, str]:
        """
        Get medical terms for a specific language
        
        Args:
            language: Language code
            
        Returns:
            Dictionary of medical terms
        """
        return self.medical_terms.get(language, self.medical_terms['en'])
    
    def translate_medical_terms(self, terms: List[str], 
                              target_language: str) -> Dict[str, str]:
        """
        Translate medical terms to target language
        
        Args:
            terms: List of medical terms to translate
            target_language: Target language code
            
        Returns:
            Dictionary mapping original terms to translated terms
        """
        translated_terms = {}
        
        for term in terms:
            # Find the term in English medical terms
            english_terms = self.medical_terms['en']
            term_key = None
            
            for key, value in english_terms.items():
                if value.lower() == term.lower():
                    term_key = key
                    break
            
            if term_key and target_language in self.medical_terms:
                target_terms = self.medical_terms[target_language]
                translated_terms[term] = target_terms.get(term_key, term)
            else:
                translated_terms[term] = term
        
        return translated_terms
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if supported, False otherwise
        """
        return language_code in self.supported_languages
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get language name from language code
        
        Args:
            language_code: Language code
            
        Returns:
            Language name or 'Unknown' if not found
        """
        return self.supported_languages.get(language_code, 'Unknown')
    
    def process_multilingual_text(self, text: str, 
                                target_language: str = 'en') -> Dict[str, Any]:
        """
        Process text for multilingual support
        
        Args:
            text: Text to process
            target_language: Target language for processing
            
        Returns:
            Dictionary with processing results
        """
        # Detect language
        lang_detection = self.detect_language(text)
        
        # Translate if needed
        translation_result = None
        if lang_detection['primary_language'] != target_language:
            translation_result = self.translate_text(
                text, target_language, lang_detection['primary_language']
            )
        
        # Extract medical terms
        medical_terms = self._extract_medical_terms(text, lang_detection['primary_language'])
        
        return {
            'original_text': text,
            'language_detection': lang_detection,
            'translation': translation_result,
            'medical_terms': medical_terms,
            'processed_text': translation_result['translated_text'] if translation_result else text,
            'target_language': target_language
        }
    
    def _extract_medical_terms(self, text: str, language: str) -> List[str]:
        """Extract medical terms from text"""
        text_lower = text.lower()
        medical_terms = []
        
        if language in self.medical_terms:
            terms_dict = self.medical_terms[language]
            for term in terms_dict.values():
                if term.lower() in text_lower:
                    medical_terms.append(term)
        
        return medical_terms
    
    def get_emergency_phrases(self, language: str) -> List[str]:
        """
        Get emergency phrases in a specific language
        
        Args:
            language: Language code
            
        Returns:
            List of emergency phrases
        """
        emergency_phrases = {
            'en': [
                "Call 911 immediately",
                "This is a medical emergency",
                "Please seek immediate medical attention",
                "Go to the emergency room now"
            ],
            'es': [
                "Llame al 911 inmediatamente",
                "Esta es una emergencia médica",
                "Busque atención médica inmediata",
                "Vaya a la sala de emergencias ahora"
            ],
            'fr': [
                "Appelez le 911 immédiatement",
                "C'est une urgence médicale",
                "Veuillez consulter immédiatement un médecin",
                "Allez aux urgences maintenant"
            ],
            'de': [
                "Rufen Sie sofort 911 an",
                "Dies ist ein medizinischer Notfall",
                "Bitte suchen Sie sofort einen Arzt auf",
                "Gehen Sie jetzt in die Notaufnahme"
            ]
        }
        
        return emergency_phrases.get(language, emergency_phrases['en'])
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on multilingual processor
        
        Returns:
            Health check results
        """
        try:
            # Test language detection
            test_text = "Hello, this is a test message."
            lang_detection = self.detect_language(test_text)
            
            return {
                'status': 'healthy',
                'message': 'Multilingual processor is ready',
                'ready': True,
                'supported_languages_count': len(self.supported_languages),
                'test_detection': lang_detection
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Multilingual processor health check failed: {e}',
                'ready': False
            }
