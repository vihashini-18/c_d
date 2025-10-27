#!/usr/bin/env python3
"""
Test the medical chatbot pipeline
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.llm_handler import LLMHandler
from src.models.embeddings import EmbeddingModel
from src.rag.hybrid_search import HybridSearch
from src.analysis.confidence_scorer import ConfidenceScorer
from src.analysis.emotion_analyzer import EmotionAnalyzer
from src.analysis.emergency_detector import EmergencyDetector
from src.multimodal.text_processor import TextProcessor
from src.audio.whisper_stt import WhisperSTT
from src.audio.elevenlabs_tts import ElevenLabsTTS
from src.translation.multilingual import MultilingualProcessor
from src.database.pinecone_manager import PineconeManager
from src.database.mongodb_manager import MongoDBManager

async def test_embedding_model():
    """Test embedding model"""
    print("Testing embedding model...")
    
    try:
        embedding_model = EmbeddingModel()
        test_text = "I have chest pain and shortness of breath"
        embedding = embedding_model.encode([test_text])
        
        print(f"✅ Embedding model working - generated {len(embedding[0])} dimensional vector")
        return True
    except Exception as e:
        print(f"❌ Embedding model failed: {e}")
        return False

async def test_llm_handler():
    """Test LLM handler"""
    print("Testing LLM handler...")
    
    try:
        llm_handler = LLMHandler()
        test_prompt = "What are the symptoms of a heart attack?"
        response = llm_handler.generate_response_gemini(test_prompt)
        
        print(f"✅ LLM handler working - generated response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM handler failed: {e}")
        return False

async def test_rag_system():
    """Test RAG system"""
    print("Testing RAG system...")
    
    try:
        embedding_model = EmbeddingModel()
        
        # Sample documents
        sample_docs = [
            {
                "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
                "metadata": {"source": "medical_textbook", "category": "cardiology"}
            },
            {
                "content": "Fever is a common symptom of infection. Normal body temperature is around 98.6°F (37°C).",
                "metadata": {"source": "medical_guide", "category": "general_medicine"}
            }
        ]
        
        hybrid_search = HybridSearch(embedding_model, sample_docs)
        query = "What should I do if I have chest pain?"
        query_vector = embedding_model.encode([query])[0]
        results = hybrid_search.search(query_vector, top_k=2)
        
        print(f"✅ RAG system working - found {len(results)} relevant documents")
        return True
    except Exception as e:
        print(f"❌ RAG system failed: {e}")
        return False

async def test_analysis_modules():
    """Test analysis modules"""
    print("Testing analysis modules...")
    
    try:
        # Test confidence scorer
        confidence_scorer = ConfidenceScorer()
        test_scores = [0.8, 0.7, 0.9]
        confidence = confidence_scorer.calculate_confidence(
            retrieval_scores=test_scores,
            response_text="This is a test response",
            query_text="test query"
        )
        print(f"✅ Confidence scorer working - score: {confidence.score}")
        
        # Test emotion analyzer
        emotion_analyzer = EmotionAnalyzer()
        emotion_result = emotion_analyzer.analyze_emotion("I'm worried about my health")
        print(f"✅ Emotion analyzer working - detected: {emotion_result.primary_emotion}")
        
        # Test emergency detector
        emergency_detector = EmergencyDetector()
        emergency_result = emergency_detector.detect_emergency("I'm having severe chest pain")
        print(f"✅ Emergency detector working - emergency: {emergency_result.is_emergency}")
        
        return True
    except Exception as e:
        print(f"❌ Analysis modules failed: {e}")
        return False

async def test_multimodal_processors():
    """Test multimodal processors"""
    print("Testing multimodal processors...")
    
    try:
        # Test text processor
        text_processor = TextProcessor()
        medical_entities = text_processor.extract_medical_entities("I have chest pain and fever")
        print(f"✅ Text processor working - extracted {len(medical_entities)} entity categories")
        
        # Test multilingual processor
        multilingual_processor = MultilingualProcessor()
        lang_detection = multilingual_processor.detect_language("Hello, how are you?")
        print(f"✅ Multilingual processor working - detected language: {lang_detection['primary_language']}")
        
        return True
    except Exception as e:
        print(f"❌ Multimodal processors failed: {e}")
        return False

async def test_audio_services():
    """Test audio services"""
    print("Testing audio services...")
    
    try:
        # Test Whisper STT
        whisper_stt = WhisperSTT()
        health_check = whisper_stt.health_check()
        print(f"✅ Whisper STT working - status: {health_check['status']}")
        
        # Test ElevenLabs TTS
        elevenlabs_tts = ElevenLabsTTS()
        health_check = elevenlabs_tts.health_check()
        print(f"✅ ElevenLabs TTS working - status: {health_check['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Audio services failed: {e}")
        return False

async def test_database_connections():
    """Test database connections"""
    print("Testing database connections...")
    
    try:
        # Test Pinecone
        pinecone_manager = PineconeManager()
        health_check = pinecone_manager.health_check()
        print(f"✅ Pinecone working - status: {health_check['status']}")
        
        # Test MongoDB
        mongodb_manager = MongoDBManager()
        health_check = mongodb_manager.health_check()
        print(f"✅ MongoDB working - status: {health_check['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Database connections failed: {e}")
        return False

async def test_full_pipeline():
    """Test the full pipeline"""
    print("Testing full pipeline...")
    
    try:
        # Initialize components
        embedding_model = EmbeddingModel()
        llm_handler = LLMHandler()
        confidence_scorer = ConfidenceScorer()
        emotion_analyzer = EmotionAnalyzer()
        emergency_detector = EmergencyDetector()
        text_processor = TextProcessor()
        
        # Sample documents
        sample_docs = [
            {
                "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
                "metadata": {"source": "medical_textbook", "category": "cardiology"}
            }
        ]
        
        hybrid_search = HybridSearch(embedding_model, sample_docs)
        
        # Test query
        query = "I'm having chest pain, what should I do?"
        
        # Process query
        processed_text = text_processor.clean_text(query)
        medical_entities = text_processor.extract_medical_entities(processed_text)
        
        # Search for relevant information
        query_vector = embedding_model.encode([processed_text])[0]
        search_results = hybrid_search.search(query_vector, top_k=2)
        
        # Extract context
        context = " ".join([result.content for result in search_results])
        retrieval_scores = [result.score for result in search_results]
        
        # Detect emergency
        emergency_detection = emergency_detector.detect_emergency(processed_text)
        
        # Analyze emotion
        emotion_analysis = emotion_analyzer.analyze_emotion(processed_text)
        
        # Generate response
        response_data = llm_handler.generate_medical_response(
            question=processed_text,
            context=context,
            confidence=1.0,
            is_emergency=emergency_detection.is_emergency,
            language="en"
        )
        
        # Calculate confidence
        confidence_score = confidence_scorer.calculate_confidence(
            retrieval_scores=retrieval_scores,
            response_text=response_data['response'],
            query_text=processed_text,
            sources=[{"content": result.content, "metadata": result.metadata} for result in search_results],
            medical_entities=medical_entities
        )
        
        print(f"✅ Full pipeline working")
        print(f"   - Query: {query}")
        print(f"   - Response: {response_data['response'][:100]}...")
        print(f"   - Confidence: {confidence_score.score:.2f}")
        print(f"   - Emergency: {emergency_detection.is_emergency}")
        print(f"   - Emotion: {emotion_analysis.primary_emotion}")
        
        return True
    except Exception as e:
        print(f"❌ Full pipeline failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🚀 Testing Medical Chatbot Pipeline...")
    print("=" * 50)
    
    tests = [
        ("Embedding Model", test_embedding_model),
        ("LLM Handler", test_llm_handler),
        ("RAG System", test_rag_system),
        ("Analysis Modules", test_analysis_modules),
        ("Multimodal Processors", test_multimodal_processors),
        ("Audio Services", test_audio_services),
        ("Database Connections", test_database_connections),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn api.main:app --reload")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all environment variables are set")
        print("2. Check that all services are running")
        print("3. Verify API keys are valid")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
