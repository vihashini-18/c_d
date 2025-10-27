from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
from datetime import datetime

from src.database.pinecone_manager import PineconeManager
from src.database.mongodb_manager import MongoDBManager
from src.audio.whisper_stt import WhisperSTT
from src.audio.elevenlabs_tts import ElevenLabsTTS
from src.translation.multilingual import MultilingualProcessor

router = APIRouter()

# Initialize services
pinecone_manager = PineconeManager()
mongodb_manager = MongoDBManager()
whisper_stt = WhisperSTT()
elevenlabs_tts = ElevenLabsTTS()
multilingual_processor = MultilingualProcessor()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "medical-chatbot-api",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check for all services
    """
    health_status = {
        "overall_status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check Pinecone
    try:
        pinecone_health = pinecone_manager.health_check()
        health_status["services"]["pinecone"] = pinecone_health
    except Exception as e:
        health_status["services"]["pinecone"] = {
            "status": "error",
            "message": str(e),
            "connected": False
        }
    
    # Check MongoDB
    try:
        mongodb_health = mongodb_manager.health_check()
        health_status["services"]["mongodb"] = mongodb_health
    except Exception as e:
        health_status["services"]["mongodb"] = {
            "status": "error",
            "message": str(e),
            "connected": False
        }
    
    # Check Whisper STT
    try:
        whisper_health = whisper_stt.health_check()
        health_status["services"]["whisper_stt"] = whisper_health
    except Exception as e:
        health_status["services"]["whisper_stt"] = {
            "status": "error",
            "message": str(e),
            "ready": False
        }
    
    # Check ElevenLabs TTS
    try:
        elevenlabs_health = elevenlabs_tts.health_check()
        health_status["services"]["elevenlabs_tts"] = elevenlabs_health
    except Exception as e:
        health_status["services"]["elevenlabs_tts"] = {
            "status": "error",
            "message": str(e),
            "ready": False
        }
    
    # Check Multilingual Processor
    try:
        multilingual_health = multilingual_processor.health_check()
        health_status["services"]["multilingual"] = multilingual_health
    except Exception as e:
        health_status["services"]["multilingual"] = {
            "status": "error",
            "message": str(e),
            "ready": False
        }
    
    # Determine overall status
    service_statuses = [service.get("status", "error") for service in health_status["services"].values()]
    if "error" in service_statuses:
        health_status["overall_status"] = "degraded"
    if all(status == "error" for status in service_statuses):
        health_status["overall_status"] = "unhealthy"
    
    return health_status

@router.get("/health/services")
async def services_status() -> Dict[str, Any]:
    """
    Get status of individual services
    """
    services = {}
    
    # Pinecone status
    try:
        pinecone_stats = pinecone_manager.get_index_stats()
        services["pinecone"] = {
            "status": "connected",
            "index_stats": pinecone_stats
        }
    except Exception as e:
        services["pinecone"] = {
            "status": "error",
            "error": str(e)
        }
    
    # MongoDB status
    try:
        mongodb_stats = mongodb_manager.get_database_stats()
        services["mongodb"] = {
            "status": "connected",
            "database_stats": mongodb_stats
        }
    except Exception as e:
        services["mongodb"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Whisper STT status
    try:
        whisper_info = whisper_stt.get_model_info()
        services["whisper_stt"] = {
            "status": "ready",
            "model_info": whisper_info
        }
    except Exception as e:
        services["whisper_stt"] = {
            "status": "error",
            "error": str(e)
        }
    
    # ElevenLabs TTS status
    try:
        elevenlabs_usage = elevenlabs_tts.get_usage_info()
        services["elevenlabs_tts"] = {
            "status": "ready",
            "usage_info": elevenlabs_usage
        }
    except Exception as e:
        services["elevenlabs_tts"] = {
            "status": "error",
            "error": str(e)
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }

@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes-style readiness check
    """
    try:
        # Check if critical services are ready
        critical_services = ["mongodb", "pinecone"]
        
        for service in critical_services:
            if service == "mongodb":
                health = mongodb_manager.health_check()
            elif service == "pinecone":
                health = pinecone_manager.health_check()
            
            if not health.get("connected", False):
                raise HTTPException(
                    status_code=503,
                    detail=f"Service {service} is not ready"
                )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes-style liveness check
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get basic metrics for monitoring
    """
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "calculated_by_monitoring_system",
        "requests": {
            "total": "tracked_by_monitoring_system",
            "successful": "tracked_by_monitoring_system",
            "failed": "tracked_by_monitoring_system"
        },
        "services": {}
    }
    
    # Add service-specific metrics
    try:
        # Pinecone metrics
        pinecone_stats = pinecone_manager.get_index_stats()
        metrics["services"]["pinecone"] = {
            "total_vectors": pinecone_stats.get("total_vector_count", 0),
            "index_fullness": pinecone_stats.get("index_fullness", 0)
        }
    except:
        metrics["services"]["pinecone"] = {"error": "unavailable"}
    
    try:
        # MongoDB metrics
        mongodb_stats = mongodb_manager.get_database_stats()
        metrics["services"]["mongodb"] = {
            "collections": mongodb_stats.get("collections", 0),
            "documents": mongodb_stats.get("objects", 0),
            "data_size": mongodb_stats.get("data_size", 0)
        }
    except:
        metrics["services"]["mongodb"] = {"error": "unavailable"}
    
    return metrics
