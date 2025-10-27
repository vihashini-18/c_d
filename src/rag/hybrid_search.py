from typing import List, Dict, Any, Optional
import numpy as np
from .semantic_search import SemanticSearch
from .keyword_search import KeywordSearch
from .retriever import SearchResult, HybridRetriever

class HybridSearch:
    """
    Hybrid search combining semantic and keyword search with intelligent ranking
    """
    
    def __init__(self, 
                 embedding_model,
                 documents: List[Dict[str, Any]] = None,
                 semantic_weight: float = 0.7,
                 keyword_weight: float = 0.3,
                 medical_boost: float = 1.5):
        """
        Initialize hybrid search
        
        Args:
            embedding_model: Sentence transformer model for embeddings
            documents: Initial documents to index
            semantic_weight: Weight for semantic search results
            keyword_weight: Weight for keyword search results
            medical_boost: Boost factor for medical terms
        """
        self.semantic_search = SemanticSearch(embedding_model=embedding_model)
        self.keyword_search = KeywordSearch()
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.medical_boost = medical_boost
        self.documents = documents or []
        
        if self.documents:
            self._build_indices()
    
    def _build_indices(self):
        """Build both semantic and keyword indices"""
        self.semantic_search.build_index(self.documents)
        self.keyword_search.build_index(self.documents)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to both search indices"""
        self.documents.extend(documents)
        self.semantic_search.add_documents(documents)
        self.keyword_search.add_documents(documents)
    
    def search(self, query: str, top_k: int = 5, 
               use_medical_boost: bool = True,
               semantic_threshold: float = 0.0,
               keyword_threshold: float = 0.0) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_medical_boost: Whether to apply medical term boosting
            semantic_threshold: Minimum similarity threshold for semantic search
            keyword_threshold: Minimum score threshold for keyword search
            
        Returns:
            List of SearchResult objects
        """
        # Get results from both search methods
        semantic_results = self.semantic_search.search(
            query, top_k * 2, threshold=semantic_threshold
        )
        keyword_results = self.keyword_search.search(
            query, top_k * 2, use_medical_terms=use_medical_boost
        )
        
        # Normalize scores
        semantic_scores = self._normalize_scores([r['score'] for r in semantic_results])
        keyword_scores = self._normalize_scores([r['score'] for r in keyword_results])
        
        # Create combined results dictionary
        combined_results = {}
        
        # Add semantic results
        for i, result in enumerate(semantic_results):
            content = result['content']
            if content not in combined_results:
                combined_results[content] = {
                    'content': content,
                    'metadata': result['metadata'],
                    'source': result['source'],
                    'semantic_score': 0.0,
                    'keyword_score': 0.0,
                    'medical_boost': 0.0
                }
            combined_results[content]['semantic_score'] = semantic_scores[i]
        
        # Add keyword results
        for i, result in enumerate(keyword_results):
            content = result['content']
            if content not in combined_results:
                combined_results[content] = {
                    'content': content,
                    'metadata': result['metadata'],
                    'source': result['source'],
                    'semantic_score': 0.0,
                    'keyword_score': 0.0,
                    'medical_boost': 0.0
                }
            combined_results[content]['keyword_score'] = keyword_scores[i]
            
            # Apply medical boost if enabled
            if use_medical_boost and 'matched_terms' in result:
                medical_terms = result['matched_terms']
                if medical_terms:
                    combined_results[content]['medical_boost'] = len(medical_terms) * 0.1
        
        # Calculate hybrid scores
        final_results = []
        for result_data in combined_results.values():
            hybrid_score = (
                self.semantic_weight * result_data['semantic_score'] +
                self.keyword_weight * result_data['keyword_score'] +
                result_data['medical_boost']
            )
            
            # Apply medical boost multiplier
            if use_medical_boost and result_data['medical_boost'] > 0:
                hybrid_score *= self.medical_boost
            
            result = SearchResult(
                content=result_data['content'],
                score=hybrid_score,
                metadata=result_data['metadata'],
                source=result_data['source']
            )
            final_results.append(result)
        
        # Sort by hybrid score and return top-k
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:top_k]
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to 0-1 range"""
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def search_by_category(self, query: str, category: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search within a specific category using hybrid approach
        
        Args:
            query: Search query
            category: Category to search in
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Filter documents by category
        filtered_docs = [
            doc for doc in self.documents 
            if doc.get('metadata', {}).get('category', '').lower() == category.lower()
        ]
        
        if not filtered_docs:
            return []
        
        # Create temporary hybrid search for filtered documents
        temp_search = HybridSearch(
            embedding_model=self.semantic_search.embedding_model,
            documents=filtered_docs,
            semantic_weight=self.semantic_weight,
            keyword_weight=self.keyword_weight,
            medical_boost=self.medical_boost
        )
        
        return temp_search.search(query, top_k)
    
    def search_with_filters(self, query: str, filters: Dict[str, Any], top_k: int = 5) -> List[SearchResult]:
        """
        Search with metadata filters
        
        Args:
            query: Search query
            filters: Dictionary of metadata filters
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Filter documents by metadata
        filtered_docs = []
        for doc in self.documents:
            metadata = doc.get('metadata', {})
            match = True
            
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_docs.append(doc)
        
        if not filtered_docs:
            return []
        
        # Create temporary hybrid search for filtered documents
        temp_search = HybridSearch(
            embedding_model=self.semantic_search.embedding_model,
            documents=filtered_docs,
            semantic_weight=self.semantic_weight,
            keyword_weight=self.keyword_weight,
            medical_boost=self.medical_boost
        )
        
        return temp_search.search(query, top_k)
    
    def get_similar_documents(self, doc_id: int, top_k: int = 5) -> List[SearchResult]:
        """
        Find documents similar to a specific document
        
        Args:
            doc_id: Index of the document
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        if doc_id >= len(self.documents):
            return []
        
        # Get the document content
        doc_content = self.documents[doc_id].get('content', '')
        
        # Use the document content as a query
        return self.search(doc_content, top_k + 1)[1:]  # Exclude the document itself
    
    def explain_search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Provide detailed explanation of search results
        
        Args:
            query: Search query
            top_k: Number of results to explain
            
        Returns:
            Dictionary with search explanation
        """
        # Get semantic and keyword results separately
        semantic_results = self.semantic_search.search(query, top_k)
        keyword_results = self.keyword_search.search(query, top_k)
        
        # Get hybrid results
        hybrid_results = self.search(query, top_k)
        
        # Extract medical terms from query
        medical_terms = self.keyword_search.extract_medical_terms(query)
        
        explanation = {
            'query': query,
            'medical_terms_found': medical_terms,
            'semantic_results': [
                {
                    'content': r['content'][:100] + '...',
                    'score': r['score'],
                    'source': r['source']
                } for r in semantic_results
            ],
            'keyword_results': [
                {
                    'content': r['content'][:100] + '...',
                    'score': r['score'],
                    'matched_terms': r.get('matched_terms', [])
                } for r in keyword_results
            ],
            'hybrid_results': [
                {
                    'content': r.content[:100] + '...',
                    'score': r.score,
                    'source': r.source
                } for r in hybrid_results
            ],
            'weights': {
                'semantic': self.semantic_weight,
                'keyword': self.keyword_weight,
                'medical_boost': self.medical_boost
            }
        }
        
        return explanation
    
    def update_weights(self, semantic_weight: float = None, keyword_weight: float = None, 
                      medical_boost: float = None):
        """
        Update search weights
        
        Args:
            semantic_weight: New semantic weight
            keyword_weight: New keyword weight
            medical_boost: New medical boost factor
        """
        if semantic_weight is not None:
            self.semantic_weight = semantic_weight
        if keyword_weight is not None:
            self.keyword_weight = keyword_weight
        if medical_boost is not None:
            self.medical_boost = medical_boost
        
        # Normalize weights
        total = self.semantic_weight + self.keyword_weight
        if total > 0:
            self.semantic_weight = self.semantic_weight / total
            self.keyword_weight = self.keyword_weight / total

