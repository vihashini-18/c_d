import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from config.settings import settings

class SemanticSearch:
    """
    Semantic search using sentence transformers and FAISS for efficient similarity search
    """
    
    def __init__(self, model_name: str = None, dimension: int = 384):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.dimension = dimension
        self.embedding_model = SentenceTransformer(self.model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
    def build_index(self, documents: List[Dict[str, Any]]):
        """
        Build FAISS index from documents
        
        Args:
            documents: List of documents with 'content' field
        """
        self.documents = documents
        
        # Extract text content
        texts = [doc.get('content', '') for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, normalize_embeddings=True)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata = [doc.get('metadata', {}) for doc in documents]
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of search results with content, score, and metadata
        """
        if self.index is None:
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= threshold and idx < len(self.documents):
                result = {
                    'content': self.documents[idx].get('content', ''),
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'source': self.documents[idx].get('source', 'unknown')
                }
                results.append(result)
        
        return results
    
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
        
        # Extract text content for new documents
        texts = [doc.get('content', '') for doc in new_documents]
        
        # Generate embeddings for new documents
        new_embeddings = self.embedding_model.encode(texts, normalize_embeddings=True)
        
        # Add to FAISS index
        if self.index is None:
            self.dimension = new_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)
        
        self.index.add(new_embeddings.astype('float32'))
        
        # Add metadata
        self.metadata.extend([doc.get('metadata', {}) for doc in new_documents])
    
    def get_similar_documents(self, doc_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a specific document
        
        Args:
            doc_id: Index of the document
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        if self.index is None or doc_id >= len(self.documents):
            return []
        
        # Get embedding for the document
        doc_embedding = self.embedding_model.encode([self.documents[doc_id].get('content', '')], 
                                                  normalize_embeddings=True)
        
        # Search for similar documents
        scores, indices = self.index.search(doc_embedding.astype('float32'), top_k + 1)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != doc_id and idx < len(self.documents):  # Exclude the document itself
                result = {
                    'content': self.documents[idx].get('content', ''),
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'source': self.documents[idx].get('source', 'unknown')
                }
                results.append(result)
        
        return results
    
    def search_by_metadata(self, query: str, metadata_filter: Dict[str, Any], 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search with metadata filtering
        
        Args:
            query: Search query
            metadata_filter: Dictionary of metadata filters
            top_k: Number of results to return
            
        Returns:
            List of filtered search results
        """
        # First get all results
        all_results = self.search(query, top_k * 2)  # Get more results for filtering
        
        # Filter by metadata
        filtered_results = []
        for result in all_results:
            metadata = result.get('metadata', {})
            match = True
            
            for key, value in metadata_filter.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_results.append(result)
                if len(filtered_results) >= top_k:
                    break
        
        return filtered_results
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_model.get_sentence_embedding_dimension()
    
    def save_index(self, filepath: str):
        """Save the FAISS index to disk"""
        if self.index is not None:
            faiss.write_index(self.index, filepath)
    
    def load_index(self, filepath: str):
        """Load the FAISS index from disk"""
        self.index = faiss.read_index(filepath)

