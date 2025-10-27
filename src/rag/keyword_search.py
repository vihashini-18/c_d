import re
from typing import List, Dict, Any, Set
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class KeywordSearch:
    """
    Keyword-based search with TF-IDF scoring and medical term extraction
    """
    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words(language))
        self.documents = []
        self.vocabulary = set()
        self.term_frequencies = []
        self.document_frequencies = {}
        
        # Medical term patterns
        self.medical_patterns = [
            r'\b(?:pain|ache|hurt|sore)\b',
            r'\b(?:fever|temperature|hot|cold)\b',
            r'\b(?:cough|sneeze|breath|breathing)\b',
            r'\b(?:head|headache|migraine)\b',
            r'\b(?:chest|heart|cardiac)\b',
            r'\b(?:stomach|abdominal|belly)\b',
            r'\b(?:nausea|vomit|dizzy|dizziness)\b',
            r'\b(?:rash|skin|itch|itching)\b',
            r'\b(?:muscle|joint|bone|back)\b',
            r'\b(?:blood|bleeding|bruise)\b'
        ]
        
        # Compile medical patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.medical_patterns]
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for keyword extraction
        
        Args:
            text: Input text
            
        Returns:
            List of processed tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and stem
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return processed_tokens
    
    def extract_medical_terms(self, text: str) -> List[str]:
        """
        Extract medical terms from text using regex patterns
        
        Args:
            text: Input text
            
        Returns:
            List of medical terms found
        """
        medical_terms = []
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            medical_terms.extend(matches)
        
        return list(set(medical_terms))  # Remove duplicates
    
    def build_index(self, documents: List[Dict[str, Any]]):
        """
        Build keyword search index
        
        Args:
            documents: List of documents with 'content' field
        """
        self.documents = documents
        self.term_frequencies = []
        self.document_frequencies = {}
        
        # Process each document
        for doc in documents:
            content = doc.get('content', '')
            processed_tokens = self.preprocess_text(content)
            
            # Count term frequencies
            term_freq = Counter(processed_tokens)
            self.term_frequencies.append(term_freq)
            
            # Update vocabulary
            self.vocabulary.update(processed_tokens)
            
            # Update document frequencies
            for term in set(processed_tokens):
                self.document_frequencies[term] = self.document_frequencies.get(term, 0) + 1
    
    def calculate_tf_idf(self, term: str, doc_idx: int) -> float:
        """
        Calculate TF-IDF score for a term in a document
        
        Args:
            term: Term to calculate score for
            doc_idx: Document index
            
        Returns:
            TF-IDF score
        """
        if doc_idx >= len(self.term_frequencies):
            return 0.0
        
        # Term frequency
        term_freq = self.term_frequencies[doc_idx].get(term, 0)
        if term_freq == 0:
            return 0.0
        
        # Document frequency
        doc_freq = self.document_frequencies.get(term, 0)
        if doc_freq == 0:
            return 0.0
        
        # TF-IDF calculation
        tf = 1 + np.log(term_freq)  # Log normalization
        idf = np.log(len(self.documents) / doc_freq)
        
        return tf * idf
    
    def search(self, query: str, top_k: int = 5, use_medical_terms: bool = True) -> List[Dict[str, Any]]:
        """
        Search for documents using keyword matching
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_medical_terms: Whether to boost medical terms
            
        Returns:
            List of search results
        """
        if not self.documents:
            return []
        
        # Preprocess query
        query_tokens = self.preprocess_text(query)
        
        # Extract medical terms from query
        medical_terms = self.extract_medical_terms(query) if use_medical_terms else []
        
        # Calculate scores for each document
        doc_scores = []
        
        for doc_idx, doc in enumerate(self.documents):
            score = 0.0
            
            # Calculate TF-IDF scores for query terms
            for term in query_tokens:
                tf_idf = self.calculate_tf_idf(term, doc_idx)
                score += tf_idf
            
            # Boost score for medical terms
            if use_medical_terms:
                content = doc.get('content', '').lower()
                for medical_term in medical_terms:
                    if medical_term.lower() in content:
                        score += 2.0  # Boost medical terms
            
            # Normalize score by document length
            doc_length = len(self.term_frequencies[doc_idx])
            if doc_length > 0:
                score = score / doc_length
            
            doc_scores.append((doc_idx, score))
        
        # Sort by score and return top-k
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_idx, score in doc_scores[:top_k]:
            if score > 0:  # Only include documents with positive scores
                result = {
                    'content': self.documents[doc_idx].get('content', ''),
                    'score': float(score),
                    'metadata': self.documents[doc_idx].get('metadata', {}),
                    'source': self.documents[doc_idx].get('source', 'unknown'),
                    'matched_terms': self._get_matched_terms(query_tokens, doc_idx)
                }
                results.append(result)
        
        return results
    
    def _get_matched_terms(self, query_tokens: List[str], doc_idx: int) -> List[str]:
        """
        Get terms that matched between query and document
        
        Args:
            query_tokens: Processed query tokens
            doc_idx: Document index
            
        Returns:
            List of matched terms
        """
        if doc_idx >= len(self.term_frequencies):
            return []
        
        doc_terms = set(self.term_frequencies[doc_idx].keys())
        matched = [term for term in query_tokens if term in doc_terms]
        return matched
    
    def search_by_category(self, query: str, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search within a specific category
        
        Args:
            query: Search query
            category: Category to search in
            top_k: Number of results to return
            
        Returns:
            List of filtered search results
        """
        # Filter documents by category
        filtered_docs = []
        filtered_indices = []
        
        for i, doc in enumerate(self.documents):
            metadata = doc.get('metadata', {})
            if metadata.get('category', '').lower() == category.lower():
                filtered_docs.append(doc)
                filtered_indices.append(i)
        
        if not filtered_docs:
            return []
        
        # Create temporary search instance for filtered documents
        temp_search = KeywordSearch(self.language)
        temp_search.build_index(filtered_docs)
        
        # Search in filtered documents
        results = temp_search.search(query, top_k)
        
        # Map back to original indices
        for result in results:
            # Find the original index
            for i, orig_idx in enumerate(filtered_indices):
                if result['content'] == self.documents[orig_idx].get('content', ''):
                    result['original_index'] = orig_idx
                    break
        
        return results
    
    def get_medical_terms_in_document(self, doc_idx: int) -> List[str]:
        """
        Get medical terms found in a specific document
        
        Args:
            doc_idx: Document index
            
        Returns:
            List of medical terms
        """
        if doc_idx >= len(self.documents):
            return []
        
        content = self.documents[doc_idx].get('content', '')
        return self.extract_medical_terms(content)
    
    def add_documents(self, new_documents: List[Dict[str, Any]]):
        """
        Add new documents to the index
        
        Args:
            new_documents: List of new documents to add
        """
        if not new_documents:
            return
        
        # Add to documents list
        self.documents.extend(new_documents)
        
        # Process new documents
        for doc in new_documents:
            content = doc.get('content', '')
            processed_tokens = self.preprocess_text(content)
            
            # Count term frequencies
            term_freq = Counter(processed_tokens)
            self.term_frequencies.append(term_freq)
            
            # Update vocabulary
            self.vocabulary.update(processed_tokens)
            
            # Update document frequencies
            for term in set(processed_tokens):
                self.document_frequencies[term] = self.document_frequencies.get(term, 0) + 1

