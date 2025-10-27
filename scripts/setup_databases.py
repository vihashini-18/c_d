#!/usr/bin/env python3
"""
Setup script for medical chatbot databases
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.pinecone_manager import PineconeManager
from src.database.mongodb_manager import MongoDBManager
from config.settings import settings

async def setup_pinecone():
    """Setup Pinecone vector database"""
    print("Setting up Pinecone...")
    
    pinecone_manager = PineconeManager()
    
    # Check if index exists
    if pinecone_manager.index is None:
        print("Creating Pinecone index...")
        success = pinecone_manager.create_index(dimension=384, metric="cosine")
        if success:
            print("✅ Pinecone index created successfully")
        else:
            print("❌ Failed to create Pinecone index")
            return False
    else:
        print("✅ Pinecone index already exists")
    
    # Health check
    health = pinecone_manager.health_check()
    if health['connected']:
        print("✅ Pinecone connection successful")
    else:
        print("❌ Pinecone connection failed")
        return False
    
    return True

async def setup_mongodb():
    """Setup MongoDB database"""
    print("Setting up MongoDB...")
    
    mongodb_manager = MongoDBManager()
    
    # Health check
    health = mongodb_manager.health_check()
    if health['connected']:
        print("✅ MongoDB connection successful")
        
        # Create indexes
        print("Creating MongoDB indexes...")
        mongodb_manager.create_indexes()
        print("✅ MongoDB indexes created")
        
        return True
    else:
        print("❌ MongoDB connection failed")
        return False

async def create_sample_data():
    """Create sample medical data"""
    print("Creating sample medical data...")
    
    sample_documents = [
        {
            "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
            "metadata": {
                "source": "medical_textbook",
                "category": "cardiology",
                "author": "Dr. Smith",
                "publication_date": "2023-01-01"
            }
        },
        {
            "content": "Fever is a common symptom of infection. Normal body temperature is around 98.6°F (37°C).",
            "metadata": {
                "source": "medical_guide",
                "category": "general_medicine",
                "author": "Dr. Johnson",
                "publication_date": "2023-02-01"
            }
        },
        {
            "content": "Headaches can be caused by stress, dehydration, or underlying medical conditions. Severe headaches may require medical evaluation.",
            "metadata": {
                "source": "medical_journal",
                "category": "neurology",
                "author": "Dr. Brown",
                "publication_date": "2023-03-01"
            }
        },
        {
            "content": "High blood pressure (hypertension) is a common condition that can lead to serious health problems if left untreated.",
            "metadata": {
                "source": "medical_textbook",
                "category": "cardiology",
                "author": "Dr. Wilson",
                "publication_date": "2023-04-01"
            }
        },
        {
            "content": "Diabetes is a chronic condition that affects how your body processes blood sugar. There are two main types: Type 1 and Type 2.",
            "metadata": {
                "source": "medical_guide",
                "category": "endocrinology",
                "author": "Dr. Davis",
                "publication_date": "2023-05-01"
            }
        }
    ]
    
    # Add to Pinecone
    pinecone_manager = PineconeManager()
    if pinecone_manager.index:
        from src.database.pinecone_manager import VectorDocument
        import uuid
        
        vector_docs = []
        for i, doc in enumerate(sample_documents):
            # Generate a simple embedding (in practice, use your embedding model)
            import numpy as np
            embedding = np.random.rand(384).tolist()  # Replace with actual embedding
            
            vector_doc = VectorDocument(
                id=str(uuid.uuid4()),
                content=doc['content'],
                vector=embedding,
                metadata=doc['metadata']
            )
            vector_docs.append(vector_doc)
        
        success = pinecone_manager.upsert_documents(vector_docs)
        if success:
            print("✅ Sample data added to Pinecone")
        else:
            print("❌ Failed to add sample data to Pinecone")
    
    # Add to MongoDB
    mongodb_manager = MongoDBManager()
    if mongodb_manager.client:
        for doc in sample_documents:
            mongodb_manager.store_medical_data(doc, "medical_knowledge")
        print("✅ Sample data added to MongoDB")
    
    return True

async def main():
    """Main setup function"""
    print("🚀 Setting up Medical Chatbot Databases...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['PINECONE_API_KEY', 'PINECONE_ENV', 'MONGO_URI']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        return False
    
    # Setup databases
    pinecone_success = await setup_pinecone()
    mongodb_success = await setup_mongodb()
    
    if not (pinecone_success and mongodb_success):
        print("\n❌ Database setup failed")
        return False
    
    # Create sample data
    sample_success = await create_sample_data()
    
    print("\n" + "=" * 50)
    if pinecone_success and mongodb_success and sample_success:
        print("✅ All databases setup successfully!")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn api.main:app --reload")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("❌ Setup completed with errors")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
