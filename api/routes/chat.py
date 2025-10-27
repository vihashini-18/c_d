from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import uuid

from src.models.llm_handler import LLMHandler
from src.models.embeddings import EmbeddingModel
from src.rag.hybrid_search import HybridSearch
from src.analysis.confidence_scorer import ConfidenceScorer
from src.analysis.emotion_analyzer import EmotionAnalyzer
from src.analysis.emergency_detector import EmergencyDetector
from src.multimodal.text_processor import TextProcessor
from src.multimodal.image_processor import ImageProcessor
from src.multimodal.audio_processor import AudioProcessor
from src.translation.multilingual import MultilingualProcessor
from src.database.mongodb_manager import MongoDBManager
from src.database.pinecone_manager import PineconeManager

router = APIRouter()

# Initialize services
llm_handler = LLMHandler()
embedding_model = EmbeddingModel()
confidence_scorer = ConfidenceScorer()
emotion_analyzer = EmotionAnalyzer()
emergency_detector = EmergencyDetector()
text_processor = TextProcessor()
image_processor = ImageProcessor()
audio_processor = AudioProcessor()
multilingual_processor = MultilingualProcessor()
mongodb_manager = MongoDBManager()
pinecone_manager = PineconeManager()

# Initialize RAG system (this would be loaded from your knowledge base)
# For demo purposes, we'll use a simple in-memory system
sample_documents = [
    {
        "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
        "metadata": {"source": "medical_textbook", "category": "cardiology"},
        "source": "medical_knowledge"
    },
    {
        "content": "Fever is a common symptom of infection. Normal body temperature is around 98.6°F (37°C).",
        "metadata": {"source": "medical_guide", "category": "general_medicine"},
        "source": "medical_knowledge"
    },
    {
        "content": "Headaches can be caused by stress, dehydration, or underlying medical conditions. Severe headaches may require medical evaluation.",
        "metadata": {"source": "medical_journal", "category": "neurology"},
        "source": "medical_knowledge"
    }
]

# Initialize hybrid search with sample documents
hybrid_search = HybridSearch(embedding_model, sample_documents)

@router.post("/chat/text")
async def chat_with_text(
    message: str = Form(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    language: str = Form("en"),
    conversation_id: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Chat with text input
    """
    try:
        # Process text
        processed_text = text_processor.clean_text(message)
        
        # Detect language if not specified
        if language == "auto":
            lang_detection = multilingual_processor.detect_language(processed_text)
            language = lang_detection['primary_language']
        
        # Translate if needed
        if language != "en":
            translation_result = multilingual_processor.translate_text(processed_text, "en", language)
            processed_text = translation_result['translated_text']
        
        # Extract medical entities
        medical_entities = text_processor.extract_medical_entities(processed_text)
        
        # Search for relevant information
        query_vector = embedding_model.encode([processed_text])[0]
        search_results = hybrid_search.search(query_vector, top_k=3)
        
        # Extract context from search results
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
            confidence=1.0,  # Will be calculated below
            is_emergency=emergency_detection.is_emergency,
            language=language
        )
        
        # Calculate confidence
        confidence_score = confidence_scorer.calculate_confidence(
            retrieval_scores=retrieval_scores,
            response_text=response_data['response'],
            query_text=processed_text,
            sources=[{"content": result.content, "metadata": result.metadata} for result in search_results],
            medical_entities=medical_entities
        )
        
        # Translate response back if needed
        final_response = response_data['response']
        if language != "en":
            response_translation = multilingual_processor.translate_text(response_data['response'], language, "en")
            final_response = response_translation['translated_text']
        
        # Store conversation
        if not conversation_id:
            conversation_id = mongodb_manager.create_conversation(user_id, session_id, message)
        
        message_id = mongodb_manager.add_message(
            conversation_id,
            final_response,
            "assistant",
            {
                "confidence": confidence_score.score,
                "emergency_detected": emergency_detection.is_emergency,
                "emotion": emotion_analysis.primary_emotion,
                "medical_entities": medical_entities,
                "sources": [{"content": result.content, "score": result.score} for result in search_results]
            }
        )
        
        return {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "response": final_response,
            "confidence": {
                "score": confidence_score.score,
                "level": confidence_score.level,
                "recommendation": confidence_score.recommendation
            },
            "emergency": {
                "is_emergency": emergency_detection.is_emergency,
                "level": emergency_detection.level.value,
                "recommended_actions": emergency_detection.recommended_actions
            },
            "emotion": {
                "primary_emotion": emotion_analysis.primary_emotion,
                "intensity": emotion_analysis.intensity,
                "recommendations": emotion_analysis.recommendations
            },
            "medical_entities": medical_entities,
            "sources": [{"content": result.content, "score": result.score} for result in search_results],
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.post("/chat/audio")
async def chat_with_audio(
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    language: str = Form("auto"),
    conversation_id: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Chat with audio input
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Validate audio
        audio_validation = audio_processor.validate_audio(audio_data)
        if not audio_validation['valid']:
            raise HTTPException(status_code=400, detail=f"Invalid audio: {audio_validation['issues']}")
        
        # Detect language if auto
        if language == "auto":
            detected_language = audio_processor.detect_language(audio_data)
            language = detected_language
        
        # Transcribe audio
        transcription_result = audio_processor.transcribe_audio(audio_data, language)
        
        if transcription_result['error']:
            raise HTTPException(status_code=400, detail=f"Transcription failed: {transcription_result['error']}")
        
        # Process transcribed text
        text_message = transcription_result['text']
        
        # Use the text chat endpoint logic
        return await chat_with_text(
            message=text_message,
            user_id=user_id,
            session_id=session_id,
            language=language,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio chat: {str(e)}")

@router.post("/chat/image")
async def chat_with_image(
    image_file: UploadFile = File(...),
    message: str = Form(""),
    user_id: str = Form(...),
    session_id: str = Form(...),
    language: str = Form("en"),
    conversation_id: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Chat with image input
    """
    try:
        # Read image data
        image_data = await image_file.read()
        
        # Process image
        image_result = image_processor.process_image(image_data)
        
        if not image_result['success']:
            raise HTTPException(status_code=400, detail=f"Image processing failed: {image_result['error']}")
        
        # Extract body parts and medical information
        body_parts = image_result['body_parts']
        medical_conditions = image_processor.detect_medical_conditions(image_data)
        
        # Create context from image analysis
        image_context = f"Image analysis shows: {', '.join([part['name'] for part in body_parts])}"
        if medical_conditions:
            image_context += f" Potential conditions: {', '.join([cond['condition'] for cond in medical_conditions])}"
        
        # Combine with text message
        combined_message = f"{message} {image_context}".strip()
        
        # Use the text chat endpoint logic
        return await chat_with_text(
            message=combined_message,
            user_id=user_id,
            session_id=session_id,
            language=language,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image chat: {str(e)}")

@router.get("/chat/conversation/{conversation_id}")
async def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Get conversation history
    """
    try:
        conversation = mongodb_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

@router.get("/chat/conversation/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get messages from a conversation
    """
    try:
        messages = mongodb_manager.get_conversation_messages(conversation_id, limit, offset)
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "limit": limit,
            "offset": offset,
            "total": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@router.delete("/chat/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Delete a conversation
    """
    try:
        success = mongodb_manager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.post("/chat/feedback")
async def submit_feedback(
    conversation_id: str = Form(...),
    message_id: str = Form(...),
    feedback_type: str = Form(...),  # positive, negative, neutral
    rating: int = Form(..., ge=1, le=5),
    comments: str = Form("")
) -> Dict[str, Any]:
    """
    Submit feedback for a message
    """
    try:
        feedback_data = {
            "type": feedback_type,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        feedback_id = mongodb_manager.store_user_feedback(
            conversation_id, message_id, feedback_data
        )
        
        return {
            "feedback_id": feedback_id,
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/chat/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """
    Get supported languages
    """
    try:
        languages = multilingual_processor.get_supported_languages()
        return {
            "languages": languages,
            "total": len(languages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving languages: {str(e)}")

@router.post("/chat/analyze")
async def analyze_text(
    text: str = Form(...),
    analysis_type: str = Form("all")  # all, emotion, emergency, medical_entities
) -> Dict[str, Any]:
    """
    Analyze text without generating a response
    """
    try:
        result = {}
        
        if analysis_type in ["all", "emotion"]:
            emotion_analysis = emotion_analyzer.analyze_emotion(text)
            result["emotion"] = {
                "primary_emotion": emotion_analysis.primary_emotion,
                "intensity": emotion_analysis.intensity,
                "confidence": emotion_analysis.confidence,
                "recommendations": emotion_analysis.recommendations
            }
        
        if analysis_type in ["all", "emergency"]:
            emergency_detection = emergency_detector.detect_emergency(text)
            result["emergency"] = {
                "is_emergency": emergency_detection.is_emergency,
                "level": emergency_detection.level.value,
                "confidence": emergency_detection.confidence,
                "recommended_actions": emergency_detection.recommended_actions
            }
        
        if analysis_type in ["all", "medical_entities"]:
            medical_entities = text_processor.extract_medical_entities(text)
            result["medical_entities"] = medical_entities
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")
