from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Represents a search result"""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str

class BaseRetriever(ABC):
    """Abstract base class for retrievers"""
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for relevant documents"""
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the retriever"""
        pass

class DenseRetriever(BaseRetriever):
    """Dense retrieval using embeddings"""
    
    def __init__(self, embedding_model, documents: List[Dict[str, Any]] = None):
        self.embedding_model = embedding_model
        self.documents = documents or []
        self.embeddings = None
        
        if self.documents:
            self._build_embeddings()
    
    def _build_embeddings(self):
        """Build embeddings for all documents"""
        texts = [doc.get('content', '') for doc in self.documents]
        self.embeddings = self.embedding_model.encode(texts)
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents and rebuild embeddings"""
        self.documents.extend(documents)
        self._build_embeddings()
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using dense embeddings"""
        if self.embeddings is None or len(self.documents) == 0:
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include positive similarities
                result = SearchResult(
                    content=self.documents[idx].get('content', ''),
                    score=float(similarities[idx]),
                    metadata=self.documents[idx].get('metadata', {}),
                    source=self.documents[idx].get('source', 'unknown')
                )
                results.append(result)
        
        return results

class SparseRetriever(BaseRetriever):
    """Sparse retrieval using keyword matching"""
    
    def __init__(self, documents: List[Dict[str, Any]] = None):
        self.documents = documents or []
        self._build_index()
    
    def _build_index(self):
        """Build keyword index"""
        self.keyword_index = {}
        
        for i, doc in enumerate(self.documents):
            content = doc.get('content', '').lower()
            words = content.split()
            
            for word in words:
                if word not in self.keyword_index:
                    self.keyword_index[word] = []
                self.keyword_index[word].append(i)
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents and rebuild index"""
        self.documents.extend(documents)
        self._build_index()
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using keyword matching"""
        query_words = query.lower().split()
        doc_scores = {}
        
        # Calculate TF-IDF-like scores
        for word in query_words:
            if word in self.keyword_index:
                for doc_idx in self.keyword_index[word]:
                    if doc_idx not in doc_scores:
                        doc_scores[doc_idx] = 0
                    doc_scores[doc_idx] += 1
        
        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_idx, score in sorted_docs[:top_k]:
            result = SearchResult(
                content=self.documents[doc_idx].get('content', ''),
                score=float(score),
                metadata=self.documents[doc_idx].get('metadata', {}),
                source=self.documents[doc_idx].get('source', 'unknown')
            )
            results.append(result)
        
        return results

class HybridRetriever(BaseRetriever):
    """Hybrid retrieval combining dense and sparse methods"""
    
    def __init__(self, embedding_model, documents: List[Dict[str, Any]] = None, 
                 dense_weight: float = 0.7, sparse_weight: float = 0.3):
        self.dense_retriever = DenseRetriever(embedding_model, documents)
        self.sparse_retriever = SparseRetriever(documents)
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to both retrievers"""
        self.dense_retriever.add_documents(documents)
        self.sparse_retriever.add_documents(documents)
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search using hybrid approach"""
        # Get results from both retrievers
        dense_results = self.dense_retriever.search(query, top_k * 2)
        sparse_results = self.sparse_retriever.search(query, top_k * 2)
        
        # Combine and re-rank results
        combined_results = {}
        
        # Add dense results
        for result in dense_results:
            key = result.content
            if key not in combined_results:
                combined_results[key] = {
                    'content': result.content,
                    'metadata': result.metadata,
                    'source': result.source,
                    'dense_score': 0,
                    'sparse_score': 0
                }
            combined_results[key]['dense_score'] = result.score
        
        # Add sparse results
        for result in sparse_results:
            key = result.content
            if key not in combined_results:
                combined_results[key] = {
                    'content': result.content,
                    'metadata': result.metadata,
                    'source': result.source,
                    'dense_score': 0,
                    'sparse_score': 0
                }
            combined_results[key]['sparse_score'] = result.score
        
        # Calculate hybrid scores
        final_results = []
        for result_data in combined_results.values():
            hybrid_score = (
                self.dense_weight * result_data['dense_score'] + 
                self.sparse_weight * result_data['sparse_score']
            )
            
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

