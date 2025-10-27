from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
from bson import ObjectId
from config.settings import settings

class MongoDBManager:
    """
    Manages MongoDB operations for medical chatbot
    """
    
    def __init__(self):
        """Initialize MongoDB manager"""
        self.uri = settings.MONGO_URI
        self.database_name = settings.MONGO_DATABASE
        self.collection_name = settings.MONGO_COLLECTION
        self.client = None
        self.database = None
        self.collection = None
        
        if self.uri:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(self.uri)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {self.database_name}")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.database = None
            self.collection = None
    
    def create_conversation(self, user_id: str, session_id: str, 
                          initial_message: str = None) -> str:
        """
        Create a new conversation
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            initial_message: Initial message (optional)
            
        Returns:
            Conversation ID
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        conversation = {
            'user_id': user_id,
            'session_id': session_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'messages': [],
            'metadata': {
                'language': 'en',
                'total_messages': 0,
                'last_activity': datetime.utcnow()
            }
        }
        
        if initial_message:
            conversation['messages'].append({
                'message_id': str(ObjectId()),
                'content': initial_message,
                'type': 'user',
                'timestamp': datetime.utcnow(),
                'metadata': {}
            })
            conversation['metadata']['total_messages'] = 1
        
        result = self.collection.insert_one(conversation)
        return str(result.inserted_id)
    
    def add_message(self, conversation_id: str, content: str, message_type: str,
                   metadata: Dict[str, Any] = None) -> str:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            message_type: Type of message (user, assistant, system)
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        message = {
            'message_id': str(ObjectId()),
            'content': content,
            'type': message_type,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$push': {'messages': message},
                '$set': {
                    'updated_at': datetime.utcnow(),
                    'metadata.last_activity': datetime.utcnow(),
                    'metadata.total_messages': {'$add': ['$metadata.total_messages', 1]}
                }
            }
        )
        
        if result.matched_count == 0:
            raise Exception(f"Conversation {conversation_id} not found")
        
        return message['message_id']
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None if not found
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        conversation = self.collection.find_one({'_id': ObjectId(conversation_id)})
        
        if conversation:
            conversation['_id'] = str(conversation['_id'])
            return conversation
        
        return None
    
    def get_conversation_messages(self, conversation_id: str, 
                                 limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of messages
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        conversation = self.collection.find_one(
            {'_id': ObjectId(conversation_id)},
            {'messages': {'$slice': [offset, limit]}}
        )
        
        if conversation and 'messages' in conversation:
            return conversation['messages']
        
        return []
    
    def update_conversation_metadata(self, conversation_id: str, 
                                   metadata: Dict[str, Any]) -> bool:
        """
        Update conversation metadata
        
        Args:
            conversation_id: Conversation ID
            metadata: Metadata to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        result = self.collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$set': {
                    'updated_at': datetime.utcnow(),
                    'metadata': {**metadata, 'last_activity': datetime.utcnow()}
                }
            }
        )
        
        return result.matched_count > 0
    
    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get conversations for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        conversations = self.collection.find(
            {'user_id': user_id}
        ).sort('updated_at', -1).limit(limit)
        
        result = []
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
            result.append(conv)
        
        return result
    
    def search_conversations(self, query: Dict[str, Any], 
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversations by query
        
        Args:
            query: MongoDB query dictionary
            limit: Maximum number of results
            
        Returns:
            List of matching conversations
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        conversations = self.collection.find(query).limit(limit)
        
        result = []
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
            result.append(conv)
        
        return result
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        result = self.collection.delete_one({'_id': ObjectId(conversation_id)})
        return result.deleted_count > 0
    
    def store_medical_data(self, data: Dict[str, Any], 
                          data_type: str = "medical_knowledge") -> str:
        """
        Store medical data in a separate collection
        
        Args:
            data: Medical data to store
            data_type: Type of medical data
            
        Returns:
            Document ID
        """
        if not self.database:
            raise Exception("MongoDB not initialized")
        
        medical_collection = self.database['medical_data']
        
        document = {
            'data_type': data_type,
            'content': data.get('content', ''),
            'metadata': data.get('metadata', {}),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = medical_collection.insert_one(document)
        return str(result.inserted_id)
    
    def get_medical_data(self, data_type: str = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get medical data
        
        Args:
            data_type: Type of medical data to filter by
            limit: Maximum number of documents to return
            
        Returns:
            List of medical data documents
        """
        if not self.database:
            raise Exception("MongoDB not initialized")
        
        medical_collection = self.database['medical_data']
        
        query = {}
        if data_type:
            query['data_type'] = data_type
        
        documents = medical_collection.find(query).limit(limit)
        
        result = []
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            result.append(doc)
        
        return result
    
    def store_user_feedback(self, conversation_id: str, message_id: str,
                          feedback: Dict[str, Any]) -> str:
        """
        Store user feedback for a message
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            feedback: Feedback data
            
        Returns:
            Feedback ID
        """
        if not self.database:
            raise Exception("MongoDB not initialized")
        
        feedback_collection = self.database['user_feedback']
        
        feedback_doc = {
            'conversation_id': conversation_id,
            'message_id': message_id,
            'feedback': feedback,
            'created_at': datetime.utcnow()
        }
        
        result = feedback_collection.insert_one(feedback_doc)
        return str(result.inserted_id)
    
    def get_user_feedback(self, conversation_id: str = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user feedback
        
        Args:
            conversation_id: Filter by conversation ID
            limit: Maximum number of feedback entries to return
            
        Returns:
            List of feedback entries
        """
        if not self.database:
            raise Exception("MongoDB not initialized")
        
        feedback_collection = self.database['user_feedback']
        
        query = {}
        if conversation_id:
            query['conversation_id'] = conversation_id
        
        feedback_entries = feedback_collection.find(query).limit(limit)
        
        result = []
        for entry in feedback_entries:
            entry['_id'] = str(entry['_id'])
            result.append(entry)
        
        return result
    
    def create_indexes(self):
        """Create useful indexes for better performance"""
        if not self.collection:
            raise Exception("MongoDB not initialized")
        
        try:
            # Create indexes
            self.collection.create_index("user_id")
            self.collection.create_index("session_id")
            self.collection.create_index("created_at")
            self.collection.create_index("updated_at")
            self.collection.create_index([("user_id", 1), ("updated_at", -1)])
            
            # Create text index for message content search
            self.collection.create_index([("messages.content", "text")])
            
            print("Indexes created successfully")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        if not self.database:
            return {"error": "MongoDB not initialized"}
        
        try:
            stats = self.database.command("dbStats")
            
            return {
                'database_name': stats['db'],
                'collections': stats['collections'],
                'data_size': stats['dataSize'],
                'storage_size': stats['storageSize'],
                'indexes': stats['indexes'],
                'objects': stats['objects']
            }
            
        except Exception as e:
            return {"error": f"Error getting database stats: {e}"}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on MongoDB connection
        
        Returns:
            Health check results
        """
        try:
            if not self.client:
                return {
                    'status': 'error',
                    'message': 'MongoDB client not initialized',
                    'connected': False
                }
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get basic stats
            stats = self.get_database_stats()
            
            return {
                'status': 'healthy',
                'message': 'MongoDB connection successful',
                'connected': True,
                'database_stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'MongoDB connection failed: {e}',
                'connected': False
            }
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def __del__(self):
        """Destructor to close connection"""
        self.close_connection()
