import re
import string
from typing import List, Dict, Any, Optional
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from langdetect import detect, LangDetectException
import spacy

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

class TextProcessor:
    """
    Advanced text processing for medical chatbot
    """
    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words(language))
        
        # Try to load spaCy model for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Medical term patterns
        self.medical_patterns = {
            'symptoms': [
                r'\b(?:pain|ache|hurt|sore|tender)\b',
                r'\b(?:fever|temperature|hot|cold|chills)\b',
                r'\b(?:cough|sneeze|breath|breathing|shortness)\b',
                r'\b(?:headache|migraine|head pain)\b',
                r'\b(?:nausea|vomit|dizzy|dizziness|vertigo)\b',
                r'\b(?:rash|skin|itch|itching|redness)\b',
                r'\b(?:fatigue|tired|weak|weakness)\b',
                r'\b(?:swelling|inflammation|inflamed)\b'
            ],
            'body_parts': [
                r'\b(?:head|neck|shoulder|arm|hand|finger)\b',
                r'\b(?:chest|heart|lung|breast)\b',
                r'\b(?:stomach|abdomen|belly|gut)\b',
                r'\b(?:back|spine|spine|vertebrae)\b',
                r'\b(?:leg|thigh|knee|ankle|foot|toe)\b',
                r'\b(?:eye|ear|nose|mouth|throat)\b'
            ],
            'conditions': [
                r'\b(?:diabetes|hypertension|high blood pressure)\b',
                r'\b(?:cancer|tumor|malignancy)\b',
                r'\b(?:infection|bacterial|viral|fungal)\b',
                r'\b(?:inflammation|arthritis|rheumatoid)\b',
                r'\b(?:allergy|allergic|hypersensitivity)\b',
                r'\b(?:depression|anxiety|mental health)\b'
            ],
            'medications': [
                r'\b(?:aspirin|ibuprofen|acetaminophen|tylenol)\b',
                r'\b(?:antibiotic|penicillin|amoxicillin)\b',
                r'\b(?:insulin|metformin|glucose)\b',
                r'\b(?:antihistamine|benadryl|claritin)\b',
                r'\b(?:antidepressant|prozac|zoloft)\b'
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for category, patterns in self.medical_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text
        
        Args:
            text: Input text
            
        Returns:
            Detected language code
        """
        try:
            return detect(text)
        except LangDetectException:
            return 'en'  # Default to English
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep medical symbols
        text = re.sub(r'[^\w\s\-\.\,\!\?\(\)]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities by category
        """
        entities = {category: [] for category in self.medical_patterns.keys()}
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                entities[category].extend(matches)
        
        # Remove duplicates and empty strings
        for category in entities:
            entities[category] = list(set([entity for entity in entities[category] if entity.strip()]))
        
        return entities
    
    def extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using spaCy (if available)
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'EVENT': [],
            'WORK_OF_ART': [],
            'LAW': [],
            'LANGUAGE': [],
            'DATE': [],
            'TIME': [],
            'MONEY': [],
            'PERCENT': [],
            'QUANTITY': [],
            'ORDINAL': [],
            'CARDINAL': []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        return entities
    
    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text for embedding generation
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Clean text
        text = self.clean_text(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra punctuation but keep sentence structure
        text = re.sub(r'[^\w\s\.\,\!\?]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """
        Extract key phrases from text
        
        Args:
            text: Input text
            max_phrases: Maximum number of phrases to extract
            
        Returns:
            List of key phrases
        """
        # Tokenize and tag
        tokens = word_tokenize(text.lower())
        
        # Simple key phrase extraction based on medical terms
        phrases = []
        
        # Extract medical entities
        medical_entities = self.extract_medical_entities(text)
        for category, entities in medical_entities.items():
            phrases.extend(entities)
        
        # Extract noun phrases (simple approach)
        if self.nlp:
            doc = self.nlp(text)
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word phrases
                    phrases.append(chunk.text)
        
        # Remove duplicates and limit
        phrases = list(set(phrases))
        return phrases[:max_phrases]
    
    def segment_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        Segment long text into smaller chunks
        
        Args:
            text: Input text
            max_length: Maximum length of each segment
            
        Returns:
            List of text segments
        """
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences first
        sentences = sent_tokenize(text)
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment + " " + sentence) <= max_length:
                current_segment += " " + sentence if current_segment else sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def extract_symptoms(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract symptoms with context
        
        Args:
            text: Input text
            
        Returns:
            List of symptom dictionaries with context
        """
        symptoms = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            # Look for symptom patterns
            for pattern in self.compiled_patterns['symptoms']:
                matches = pattern.finditer(sentence)
                for match in matches:
                    symptom = {
                        'text': match.group(),
                        'sentence': sentence,
                        'start': match.start(),
                        'end': match.end(),
                        'context': sentence[max(0, match.start()-50):match.end()+50]
                    }
                    symptoms.append(symptom)
        
        return symptoms
    
    def extract_body_parts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract body parts with context
        
        Args:
            text: Input text
            
        Returns:
            List of body part dictionaries with context
        """
        body_parts = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            for pattern in self.compiled_patterns['body_parts']:
                matches = pattern.finditer(sentence)
                for match in matches:
                    body_part = {
                        'text': match.group(),
                        'sentence': sentence,
                        'start': match.start(),
                        'end': match.end(),
                        'context': sentence[max(0, match.start()-50):match.end()+50]
                    }
                    body_parts.append(body_part)
        
        return body_parts
    
    def extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medications with context
        
        Args:
            text: Input text
            
        Returns:
            List of medication dictionaries with context
        """
        medications = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            for pattern in self.compiled_patterns['medications']:
                matches = pattern.finditer(sentence)
                for match in matches:
                    medication = {
                        'text': match.group(),
                        'sentence': sentence,
                        'start': match.start(),
                        'end': match.end(),
                        'context': sentence[max(0, match.start()-50):match.end()+50]
                    }
                    medications.append(medication)
        
        return medications
    
    def extract_conditions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medical conditions with context
        
        Args:
            text: Input text
            
        Returns:
            List of condition dictionaries with context
        """
        conditions = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            for pattern in self.compiled_patterns['conditions']:
                matches = pattern.finditer(sentence)
                for match in matches:
                    condition = {
                        'text': match.group(),
                        'sentence': sentence,
                        'start': match.start(),
                        'end': match.end(),
                        'context': sentence[max(0, match.start()-50):match.end()+50]
                    }
                    conditions.append(condition)
        
        return conditions
    
    def get_text_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        Generate a summary of the text
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Text summary
        """
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple extractive summarization
        # Score sentences by medical term density
        scored_sentences = []
        
        for sentence in sentences:
            medical_entities = self.extract_medical_entities(sentence)
            total_entities = sum(len(entities) for entities in medical_entities.values())
            score = total_entities / len(sentence.split()) if sentence.split() else 0
            scored_sentences.append((sentence, score))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent for sent, _ in scored_sentences[:max_sentences]]
        
        return " ".join(top_sentences)
    
    def extract_emergency_keywords(self, text: str) -> List[str]:
        """
        Extract emergency-related keywords
        
        Args:
            text: Input text
            
        Returns:
            List of emergency keywords found
        """
        emergency_patterns = [
            r'\b(?:emergency|urgent|immediate|critical|severe)\b',
            r'\b(?:chest pain|heart attack|stroke)\b',
            r'\b(?:unconscious|unresponsive|coma)\b',
            r'\b(?:bleeding|hemorrhage|blood loss)\b',
            r'\b(?:difficulty breathing|can\'t breathe|choking)\b',
            r'\b(?:severe pain|excruciating|intense)\b',
            r'\b(?:allergic reaction|anaphylaxis)\b',
            r'\b(?:overdose|poisoning|toxic)\b'
        ]
        
        emergency_keywords = []
        for pattern in emergency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emergency_keywords.extend(matches)
        
        return list(set(emergency_keywords))

