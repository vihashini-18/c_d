import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Database
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/medical_chatbot")
    
    # Application Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    USE_CUDA: bool = os.getenv("USE_CUDA", "0") == "1"
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    
    # Model Settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "alloy")
    
    # Confidence Thresholds
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
    EMERGENCY_CONFIDENCE_THRESHOLD: float = float(os.getenv("EMERGENCY_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Pinecone Settings
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "medical-knowledge")
    
    # MongoDB Settings
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "medical_chatbot")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "conversations")

settings = Settings()

