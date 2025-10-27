#!/usr/bin/env python3
"""
Ingest medical data into the knowledge base
"""

import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.pinecone_manager import PineconeManager, VectorDocument
from src.database.mongodb_manager import MongoDBManager
from src.models.embeddings import EmbeddingModel
from config.settings import settings

def load_medical_data(file_path: str) -> List[Dict[str, Any]]:
    """Load medical data from various file formats"""
    
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
            # Split by paragraphs or sections
            sections = content.split('\n\n')
            for i, section in enumerate(sections):
                if section.strip():
                    data.append({
                        'content': section.strip(),
                        'metadata': {
                            'source': file_path.name,
                            'section': i + 1
                        }
                    })
    
    else:
        print(f"❌ Unsupported file format: {file_path.suffix}")
        return []
    
    print(f"✅ Loaded {len(data)} documents from {file_path}")
    return data

def process_documents(documents: List[Dict[str, Any]], embedding_model: EmbeddingModel) -> List[VectorDocument]:
    """Process documents and create vector embeddings"""
    
    vector_documents = []
    
    for i, doc in enumerate(documents):
        # Extract content and metadata
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        if not content.strip():
            continue
        
        # Generate embedding
        try:
            embedding = embedding_model.encode([content])[0]
        except Exception as e:
            print(f"❌ Failed to generate embedding for document {i}: {e}")
            continue
        
        # Create vector document
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
                **metadata
            }
        )
        
        vector_documents.append(vector_doc)
    
    return vector_documents

def ingest_to_pinecone(vector_documents: List[VectorDocument], batch_size: int = 100):
    """Ingest documents to Pinecone"""
    
    print("Ingesting documents to Pinecone...")
    
    pinecone_manager = PineconeManager()
    
    if not pinecone_manager.index:
        print("❌ Pinecone not initialized. Please run setup_databases.py first.")
        return False
    
    # Ingest in batches
    total_docs = len(vector_documents)
    success_count = 0
    
    for i in range(0, total_docs, batch_size):
        batch = vector_documents[i:i + batch_size]
        
        try:
            success = pinecone_manager.upsert_documents(batch)
            if success:
                success_count += len(batch)
                print(f"✅ Ingested batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1} ({len(batch)} documents)")
            else:
                print(f"❌ Failed to ingest batch {i//batch_size + 1}")
        except Exception as e:
            print(f"❌ Error ingesting batch {i//batch_size + 1}: {e}")
    
    print(f"✅ Successfully ingested {success_count}/{total_docs} documents to Pinecone")
    return success_count == total_docs

def ingest_to_mongodb(documents: List[Dict[str, Any]]):
    """Ingest documents to MongoDB"""
    
    print("Ingesting documents to MongoDB...")
    
    mongodb_manager = MongoDBManager()
    
    if not mongodb_manager.client:
        print("❌ MongoDB not initialized. Please run setup_databases.py first.")
        return False
    
    success_count = 0
    
    for doc in documents:
        try:
            doc_id = mongodb_manager.store_medical_data(doc, "medical_knowledge")
            if doc_id:
                success_count += 1
        except Exception as e:
            print(f"❌ Error storing document: {e}")
    
    print(f"✅ Successfully ingested {success_count}/{len(documents)} documents to MongoDB")
    return success_count == len(documents)

def create_sample_medical_data():
    """Create sample medical data for ingestion"""
    
    sample_data = [
        {
            "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
            "metadata": {
                "source": "medical_textbook",
                "category": "cardiology",
                "author": "Dr. Smith",
                "publication_date": "2023-01-01",
                "document_type": "textbook"
            }
        },
        {
            "content": "Fever is a common symptom of infection. Normal body temperature is around 98.6°F (37°C).",
            "metadata": {
                "source": "medical_guide",
                "category": "general_medicine",
                "author": "Dr. Johnson",
                "publication_date": "2023-02-01",
                "document_type": "guide"
            }
        },
        {
            "content": "Headaches can be caused by stress, dehydration, or underlying medical conditions. Severe headaches may require medical evaluation.",
            "metadata": {
                "source": "medical_journal",
                "category": "neurology",
                "author": "Dr. Brown",
                "publication_date": "2023-03-01",
                "document_type": "journal"
            }
        },
        {
            "content": "High blood pressure (hypertension) is a common condition that can lead to serious health problems if left untreated.",
            "metadata": {
                "source": "medical_textbook",
                "category": "cardiology",
                "author": "Dr. Wilson",
                "publication_date": "2023-04-01",
                "document_type": "textbook"
            }
        },
        {
            "content": "Diabetes is a chronic condition that affects how your body processes blood sugar. There are two main types: Type 1 and Type 2.",
            "metadata": {
                "source": "medical_guide",
                "category": "endocrinology",
                "author": "Dr. Davis",
                "publication_date": "2023-05-01",
                "document_type": "guide"
            }
        }
    ]
    
    return sample_data

def main():
    """Main ingestion function"""
    
    print("🚀 Ingesting Medical Data...")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        print(f"Loading data from: {data_file}")
        documents = load_medical_data(data_file)
    else:
        print("No data file specified. Creating sample data...")
        documents = create_sample_medical_data()
    
    if not documents:
        print("❌ No documents to ingest")
        return False
    
    print(f"📊 Processing {len(documents)} documents...")
    
    # Initialize embedding model
    print("Initializing embedding model...")
    embedding_model = EmbeddingModel()
    
    # Process documents
    print("Processing documents and generating embeddings...")
    vector_documents = process_documents(documents, embedding_model)
    
    if not vector_documents:
        print("❌ No documents processed successfully")
        return False
    
    print(f"✅ Processed {len(vector_documents)} documents")
    
    # Ingest to Pinecone
    pinecone_success = ingest_to_pinecone(vector_documents)
    
    # Ingest to MongoDB
    mongodb_success = ingest_to_mongodb(documents)
    
    print("\n" + "=" * 50)
    if pinecone_success and mongodb_success:
        print("✅ Data ingestion completed successfully!")
        print(f"📊 Ingested {len(documents)} documents")
        print("\nNext steps:")
        print("1. Test the knowledge base with queries")
        print("2. Start the API server")
        print("3. Test the chatbot functionality")
    else:
        print("❌ Data ingestion completed with errors")
        if not pinecone_success:
            print("   - Pinecone ingestion failed")
        if not mongodb_success:
            print("   - MongoDB ingestion failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
