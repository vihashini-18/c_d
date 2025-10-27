#!/usr/bin/env python3
"""
Comprehensive dataset management for medical chatbot
"""

import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import argparse

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.pinecone_manager import PineconeManager, VectorDocument
from src.database.mongodb_manager import MongoDBManager
from src.models.embeddings import EmbeddingModel
from config.settings import settings

class DatasetManager:
    """Manages medical datasets for the chatbot"""
    
    def __init__(self):
        self.pinecone_manager = PineconeManager()
        self.mongodb_manager = MongoDBManager()
        self.embedding_model = EmbeddingModel()
    
    def load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """Load dataset from various formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return []
        
        data = []
        
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        elif file_path.suffix == '.jsonl':
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data.append(json.loads(line.strip()))
        
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
            data = df.to_dict('records')
        
        elif file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                sections = content.split('\n\n')
                for i, section in enumerate(sections):
                    if section.strip():
                        data.append({
                            'content': section.strip(),
                            'metadata': {
                                'source': file_path.name,
                                'section': i + 1,
                                'category': 'general'
                            }
                        })
        
        else:
            print(f"❌ Unsupported file format: {file_path.suffix}")
            return []
        
        print(f"✅ Loaded {len(data)} documents from {file_path}")
        return data
    
    def create_vector_documents(self, documents: List[Dict[str, Any]]) -> List[VectorDocument]:
        """Convert documents to vector documents"""
        vector_documents = []
        
        for i, doc in enumerate(documents):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            if not content.strip():
                continue
            
            try:
                embedding = self.embedding_model.encode([content])[0]
                
                vector_doc = VectorDocument(
                    id=str(uuid.uuid4()),
                    content=content,
                    vector=embedding.tolist(),
                    metadata={
                        'source': metadata.get('source', 'unknown'),
                        'category': metadata.get('category', 'general'),
                        'author': metadata.get('author', 'unknown'),
                        'publication_date': metadata.get('publication_date', 'unknown'),
                        'document_type': metadata.get('document_type', 'text'),
                        'dataset_version': metadata.get('dataset_version', '1.0'),
                        **metadata
                    }
                )
                
                vector_documents.append(vector_doc)
                
            except Exception as e:
                print(f"❌ Failed to process document {i}: {e}")
                continue
        
        return vector_documents
    
    def add_dataset(self, file_path: str, dataset_name: str = None) -> bool:
        """Add new dataset to existing knowledge base"""
        print(f"📥 Adding dataset: {file_path}")
        
        documents = self.load_dataset(file_path)
        if not documents:
            return False
        
        # Add dataset name to metadata
        if dataset_name:
            for doc in documents:
                if 'metadata' not in doc:
                    doc['metadata'] = {}
                doc['metadata']['dataset_name'] = dataset_name
        
        vector_documents = self.create_vector_documents(documents)
        
        # Add to Pinecone
        pinecone_success = self.pinecone_manager.upsert_documents(vector_documents)
        
        # Add to MongoDB
        mongodb_success = True
        for doc in documents:
            try:
                self.mongodb_manager.store_medical_data(doc, "medical_knowledge")
            except Exception as e:
                print(f"❌ Failed to store document in MongoDB: {e}")
                mongodb_success = False
        
        if pinecone_success and mongodb_success:
            print(f"✅ Successfully added {len(documents)} documents")
            return True
        else:
            print("❌ Failed to add some documents")
            return False
    
    def replace_dataset(self, file_path: str, dataset_name: str = None) -> bool:
        """Replace entire knowledge base with new dataset"""
        print(f"🔄 Replacing knowledge base with: {file_path}")
        
        # Clear existing data
        print("🗑️ Clearing existing data...")
        self.clear_all_data()
        
        # Add new dataset
        return self.add_dataset(file_path, dataset_name)
    
    def clear_all_data(self) -> bool:
        """Clear all data from both databases"""
        print("🗑️ Clearing all data...")
        
        # Clear Pinecone (this is destructive!)
        if self.pinecone_manager.index:
            try:
                # Get all vector IDs and delete them
                stats = self.pinecone_manager.get_index_stats()
                if stats.get('total_vector_count', 0) > 0:
                    print("⚠️ Warning: This will delete all vectors from Pinecone!")
                    # Note: In production, you might want to recreate the index
                    print("Consider recreating the Pinecone index manually")
            except Exception as e:
                print(f"❌ Error clearing Pinecone: {e}")
        
        # Clear MongoDB collections
        if self.mongodb_manager.database:
            try:
                # Clear medical data collection
                medical_collection = self.mongodb_manager.database['medical_data']
                medical_collection.delete_many({})
                
                # Clear conversations (optional)
                conversations_collection = self.mongodb_manager.database['conversations']
                conversations_collection.delete_many({})
                
                print("✅ Cleared MongoDB collections")
            except Exception as e:
                print(f"❌ Error clearing MongoDB: {e}")
                return False
        
        return True
    
    def list_datasets(self) -> Dict[str, Any]:
        """List all datasets in the knowledge base"""
        print("📋 Listing datasets...")
        
        datasets = {}
        
        # Get data from MongoDB
        if self.mongodb_manager.database:
            medical_collection = self.mongodb_manager.database['medical_data']
            
            # Group by dataset name
            pipeline = [
                {
                    "$group": {
                        "_id": "$metadata.dataset_name",
                        "count": {"$sum": 1},
                        "categories": {"$addToSet": "$metadata.category"},
                        "sources": {"$addToSet": "$metadata.source"},
                        "latest_date": {"$max": "$created_at"}
                    }
                }
            ]
            
            results = list(medical_collection.aggregate(pipeline))
            
            for result in results:
                dataset_name = result['_id'] or 'default'
                datasets[dataset_name] = {
                    'count': result['count'],
                    'categories': result['categories'],
                    'sources': result['sources'],
                    'latest_date': result['latest_date']
                }
        
        # Get Pinecone stats
        pinecone_stats = self.pinecone_manager.get_index_stats()
        
        return {
            'datasets': datasets,
            'pinecone_stats': pinecone_stats
        }
    
    def backup_dataset(self, backup_path: str) -> bool:
        """Backup current dataset to file"""
        print(f"💾 Creating backup: {backup_path}")
        
        if not self.mongodb_manager.database:
            print("❌ MongoDB not available")
            return False
        
        try:
            medical_collection = self.mongodb_manager.database['medical_data']
            documents = list(medical_collection.find({}, {'_id': 0}))
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=str)
            
            print(f"✅ Backup created: {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_dataset(self, backup_path: str) -> bool:
        """Restore dataset from backup"""
        print(f"🔄 Restoring from backup: {backup_path}")
        
        backup_path = Path(backup_path)
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Clear existing data
            self.clear_all_data()
            
            # Restore data
            return self.add_dataset_from_list(documents)
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def add_dataset_from_list(self, documents: List[Dict[str, Any]]) -> bool:
        """Add dataset from a list of documents"""
        vector_documents = self.create_vector_documents(documents)
        
        # Add to Pinecone
        pinecone_success = self.pinecone_manager.upsert_documents(vector_documents)
        
        # Add to MongoDB
        mongodb_success = True
        for doc in documents:
            try:
                self.mongodb_manager.store_medical_data(doc, "medical_knowledge")
            except Exception as e:
                print(f"❌ Failed to store document: {e}")
                mongodb_success = False
        
        return pinecone_success and mongodb_success

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Medical Chatbot Dataset Manager')
    parser.add_argument('action', choices=['add', 'replace', 'list', 'clear', 'backup', 'restore'],
                       help='Action to perform')
    parser.add_argument('--file', '-f', help='Dataset file path')
    parser.add_argument('--name', '-n', help='Dataset name')
    parser.add_argument('--backup-path', '-b', help='Backup file path')
    
    args = parser.parse_args()
    
    manager = DatasetManager()
    
    if args.action == 'add':
        if not args.file:
            print("❌ File path required for add action")
            return False
        return manager.add_dataset(args.file, args.name)
    
    elif args.action == 'replace':
        if not args.file:
            print("❌ File path required for replace action")
            return False
        return manager.replace_dataset(args.file, args.name)
    
    elif args.action == 'list':
        datasets = manager.list_datasets()
        print("\n📊 Dataset Summary:")
        for name, info in datasets['datasets'].items():
            print(f"  📁 {name}: {info['count']} documents")
            print(f"     Categories: {', '.join(info['categories'])}")
            print(f"     Sources: {', '.join(info['sources'])}")
            print(f"     Latest: {info['latest_date']}")
            print()
        
        pinecone_stats = datasets['pinecone_stats']
        print(f"🔍 Pinecone Stats:")
        print(f"  Total vectors: {pinecone_stats.get('total_vector_count', 0)}")
        print(f"  Index fullness: {pinecone_stats.get('index_fullness', 0)}")
        return True
    
    elif args.action == 'clear':
        confirm = input("⚠️ This will delete ALL data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            return manager.clear_all_data()
        else:
            print("❌ Operation cancelled")
            return False
    
    elif args.action == 'backup':
        backup_path = args.backup_path or f"backups/dataset_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        return manager.backup_dataset(backup_path)
    
    elif args.action == 'restore':
        if not args.backup_path:
            print("❌ Backup path required for restore action")
            return False
        return manager.restore_dataset(args.backup_path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
