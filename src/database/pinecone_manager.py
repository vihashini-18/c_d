import pinecone
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import uuid
import json
from config.settings import settings

@dataclass
class VectorDocument:
    """Represents a document with vector embedding"""
    id: str
    content: str
    vector: List[float]
    metadata: Dict[str, Any]

class PineconeManager:
    """
    Manages Pinecone vector database operations
    """
    
    def __init__(self):
        """Initialize Pinecone manager"""
        self.api_key = settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENV
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        
        if self.api_key and self.environment:
            self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Check if index exists
            if self.index_name in pinecone.list_indexes():
                self.index = pinecone.Index(self.index_name)
            else:
                print(f"Index {self.index_name} not found. Please create it first.")
                
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
    
    def create_index(self, dimension: int = 384, metric: str = "cosine") -> bool:
        """
        Create a new Pinecone index
        
        Args:
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.index_name in pinecone.list_indexes():
                print(f"Index {self.index_name} already exists")
                return True
            
            pinecone.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric
            )
            
            # Wait for index to be ready
            import time
            time.sleep(10)
            
            self.index = pinecone.Index(self.index_name)
            return True
            
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def upsert_documents(self, documents: List[VectorDocument]) -> bool:
        """
        Upsert documents to Pinecone index
        
        Args:
            documents: List of VectorDocument objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for doc in documents:
                vector_data = {
                    'id': doc.id,
                    'values': doc.vector,
                    'metadata': {
                        'content': doc.content,
                        **doc.metadata
                    }
                }
                vectors.append(vector_data)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            return True
            
        except Exception as e:
            print(f"Error upserting documents: {e}")
            return False
    
    def search(self, query_vector: List[float], top_k: int = 5, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filter_dict: Metadata filter dictionary
            
        Returns:
            List of search results
        """
        if not self.index:
            print("Index not initialized")
            return []
        
        try:
            search_params = {
                'vector': query_vector,
                'top_k': top_k,
                'include_metadata': True
            }
            
            if filter_dict:
                search_params['filter'] = filter_dict
            
            results = self.index.query(**search_params)
            
            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'content': match['metadata'].get('content', ''),
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'content'}
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        if not self.index:
            print("Index not initialized")
            return None
        
        try:
            results = self.index.fetch(ids=[document_id])
            
            if document_id in results['vectors']:
                vector_data = results['vectors'][document_id]
                return {
                    'id': vector_data['id'],
                    'content': vector_data['metadata'].get('content', ''),
                    'metadata': {k: v for k, v in vector_data['metadata'].items() if k != 'content'}
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching document: {e}")
            return None
    
    def update_document(self, document_id: str, content: str = None, 
                       metadata: Dict[str, Any] = None) -> bool:
        """
        Update a document
        
        Args:
            document_id: Document ID
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            # Get existing document
            existing = self.get_document(document_id)
            if not existing:
                print(f"Document {document_id} not found")
                return False
            
            # Update fields
            if content is not None:
                existing['content'] = content
            
            if metadata is not None:
                existing['metadata'].update(metadata)
            
            # Note: Pinecone doesn't support partial updates, so we need to re-upsert
            # This requires the vector to be regenerated
            print("Warning: Document update requires vector regeneration")
            return False
            
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            self.index.delete(ids=[document_id])
            return True
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete multiple documents
        
        Args:
            document_ids: List of document IDs
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            self.index.delete(ids=document_ids)
            return True
            
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics
        
        Returns:
            Dictionary with index statistics
        """
        if not self.index:
            print("Index not initialized")
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'index_fullness': stats.get('index_fullness', 0),
                'namespaces': stats.get('namespaces', {})
            }
            
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
    
    def search_by_metadata(self, filter_dict: Dict[str, Any], 
                          top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search by metadata filters only
        
        Args:
            filter_dict: Metadata filter dictionary
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        if not self.index:
            print("Index not initialized")
            return []
        
        try:
            # Create a dummy vector for metadata-only search
            dummy_vector = [0.0] * 384  # Assuming 384 dimensions
            
            results = self.index.query(
                vector=dummy_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'content': match['metadata'].get('content', ''),
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'content'}
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching by metadata: {e}")
            return []
    
    def batch_upsert(self, documents: List[VectorDocument], 
                    batch_size: int = 100) -> bool:
        """
        Upsert documents in batches
        
        Args:
            documents: List of VectorDocument objects
            batch_size: Batch size for processing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Prepare batch vectors
                vectors = []
                for doc in batch:
                    vector_data = {
                        'id': doc.id,
                        'values': doc.vector,
                        'metadata': {
                            'content': doc.content,
                            **doc.metadata
                        }
                    }
                    vectors.append(vector_data)
                
                # Upsert batch
                self.index.upsert(vectors=vectors)
                
                print(f"Upserted batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            return True
            
        except Exception as e:
            print(f"Error in batch upsert: {e}")
            return False
    
    def create_namespace(self, namespace: str) -> bool:
        """
        Create a namespace (Pinecone supports namespaces for organization)
        
        Args:
            namespace: Namespace name
            
        Returns:
            True if successful, False otherwise
        """
        # Note: Namespaces are created implicitly when you upsert to them
        # This is just a placeholder for future namespace management
        return True
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespaces in the index
        
        Returns:
            List of namespace names
        """
        if not self.index:
            print("Index not initialized")
            return []
        
        try:
            stats = self.index.describe_index_stats()
            return list(stats.get('namespaces', {}).keys())
            
        except Exception as e:
            print(f"Error listing namespaces: {e}")
            return []
    
    def clear_index(self) -> bool:
        """
        Clear all vectors from the index
        
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            print("Index not initialized")
            return False
        
        try:
            # Delete all vectors by fetching all IDs and deleting them
            # Note: This is a simplified approach. In production, you might want to
            # use a more efficient method or recreate the index
            stats = self.get_index_stats()
            if stats.get('total_vector_count', 0) == 0:
                return True
            
            print("Warning: Clearing index will delete all vectors")
            # For safety, we'll not implement automatic clearing
            return False
            
        except Exception as e:
            print(f"Error clearing index: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Pinecone connection
        
        Returns:
            Health check results
        """
        try:
            if not self.index:
                return {
                    'status': 'error',
                    'message': 'Index not initialized',
                    'connected': False
                }
            
            # Try to get index stats
            stats = self.get_index_stats()
            
            return {
                'status': 'healthy',
                'message': 'Pinecone connection successful',
                'connected': True,
                'index_stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Pinecone connection failed: {e}',
                'connected': False
            }
