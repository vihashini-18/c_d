from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import io

from src.audio.whisper_stt import WhisperSTT
from src.audio.elevenlabs_tts import ElevenLabsTTS
from src.audio.audio_processor import AudioProcessor

router = APIRouter()

# Initialize services
whisper_stt = WhisperSTT()
elevenlabs_tts = ElevenLabsTTS()
audio_processor = AudioProcessor()

@router.post("/audio/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("auto"),
    include_timestamps: bool = Form(False)
) -> Dict[str, Any]:
    """
    Transcribe audio to text
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Validate audio
        validation = audio_processor.validate_audio(audio_data)
        if not validation['valid']:
            raise HTTPException(status_code=400, detail=f"Invalid audio: {validation['issues']}")
        
        # Detect language if auto
        if language == "auto":
            detected_language = audio_processor.detect_language(audio_data)
            language = detected_language
        
        # Transcribe audio
        if include_timestamps:
            result = whisper_stt.transcribe_with_timestamps(audio_data, language)
        else:
            result = whisper_stt.transcribe_audio(audio_data, language)
        
        if result.get('error'):
            raise HTTPException(status_code=400, detail=f"Transcription failed: {result['error']}")
        
        return {
            "text": result['text'],
            "language": result.get('language', 'unknown'),
            "confidence": result.get('confidence', 0.0),
            "segments": result.get('segments', []),
            "duration": result.get('duration', 0),
            "timestamp": result.get('timestamp', ''),
            "file_info": {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "size": len(audio_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

@router.post("/audio/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice: str = Form("alloy"),
    language: str = Form("en"),
    model: str = Form("eleven_multilingual_v2")
) -> StreamingResponse:
    """
    Synthesize text to speech
    """
    try:
        # Synthesize speech
        result = elevenlabs_tts.text_to_speech(
            text=text,
            voice=voice,
            model_id=model
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=f"Speech synthesis failed: {result['error']}")
        
        # Return audio as streaming response
        audio_stream = io.BytesIO(result['audio_data'])
        
        return StreamingResponse(
            io.BytesIO(result['audio_data']),
            media_type=result['content_type'],
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "X-Voice-Used": result['voice_used'],
                "X-Model-Used": result['model_used']
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {str(e)}")

@router.post("/audio/analyze")
async def analyze_audio(
    audio_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Analyze audio features and characteristics
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Extract audio features
        features = audio_processor.extract_audio_features(audio_data)
        
        # Detect emotion from audio
        emotion_analysis = audio_processor.detect_emotion_from_audio(audio_data)
        
        # Detect voice characteristics
        voice_characteristics = audio_processor.detect_voice_characteristics(audio_data)
        
        # Validate audio
        validation = audio_processor.validate_audio(audio_data)
        
        return {
            "features": features,
            "emotion_analysis": emotion_analysis,
            "voice_characteristics": voice_characteristics,
            "validation": validation,
            "file_info": {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "size": len(audio_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")

@router.get("/audio/voices")
async def get_available_voices() -> Dict[str, Any]:
    """
    Get available TTS voices
    """
    try:
        voices = elevenlabs_tts.get_voices()
        
        return {
            "voices": voices,
            "total": len(voices),
            "default_voice": "alloy"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voices: {str(e)}")

@router.get("/audio/voices/{voice_name}")
async def get_voice_info(voice_name: str) -> Dict[str, Any]:
    """
    Get information about a specific voice
    """
    try:
        voice_info = elevenlabs_tts.get_voice_by_name(voice_name)
        
        if not voice_info:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")
        
        return voice_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voice info: {str(e)}")

@router.get("/audio/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """
    Get supported languages for STT
    """
    try:
        languages = whisper_stt.get_supported_languages()
        
        return {
            "languages": languages,
            "total": len(languages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving languages: {str(e)}")

@router.post("/audio/voice-recommendations")
async def get_voice_recommendations(
    text: str = Form(...),
    context: str = Form("general")
) -> Dict[str, Any]:
    """
    Get voice recommendations based on text content
    """
    try:
        recommendations = elevenlabs_tts.get_voice_recommendations(text)
        
        return {
            "recommendations": recommendations,
            "text_analysis": {
                "length": len(text),
                "context": context,
                "medical_terms": any(term in text.lower() for term in [
                    'doctor', 'medical', 'health', 'patient', 'treatment', 'emergency'
                ])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting voice recommendations: {str(e)}")

@router.post("/audio/batch-transcribe")
async def batch_transcribe_audio(
    audio_files: list[UploadFile] = File(...),
    language: str = Form("auto")
) -> Dict[str, Any]:
    """
    Transcribe multiple audio files
    """
    try:
        results = []
        
        for audio_file in audio_files:
            try:
                audio_data = await audio_file.read()
                
                # Validate audio
                validation = audio_processor.validate_audio(audio_data)
                if not validation['valid']:
                    results.append({
                        "filename": audio_file.filename,
                        "error": f"Invalid audio: {validation['issues']}",
                        "success": False
                    })
                    continue
                
                # Transcribe
                result = whisper_stt.transcribe_audio(audio_data, language)
                
                results.append({
                    "filename": audio_file.filename,
                    "success": not bool(result.get('error')),
                    "text": result.get('text', ''),
                    "language": result.get('language', 'unknown'),
                    "confidence": result.get('confidence', 0.0),
                    "error": result.get('error')
                })
                
            except Exception as e:
                results.append({
                    "filename": audio_file.filename,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "results": results,
            "total_files": len(audio_files),
            "successful": sum(1 for r in results if r['success']),
            "failed": sum(1 for r in results if not r['success'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch transcription: {str(e)}")

@router.post("/audio/batch-synthesize")
async def batch_synthesize_speech(
    texts: list[str] = Form(...),
    voice: str = Form("alloy"),
    model: str = Form("eleven_multilingual_v2")
) -> Dict[str, Any]:
    """
    Synthesize multiple texts to speech
    """
    try:
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = elevenlabs_tts.text_to_speech(
                    text=text,
                    voice=voice,
                    model_id=model
                )
                
                results.append({
                    "index": i,
                    "text": text,
                    "success": result['success'],
                    "audio_size": len(result['audio_data']) if result['success'] else 0,
                    "error": result.get('error')
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "text": text,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "total_texts": len(texts),
            "successful": sum(1 for r in results if r['success']),
            "failed": sum(1 for r in results if not r['success'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch synthesis: {str(e)}")

@router.get("/audio/model-info")
async def get_model_info() -> Dict[str, Any]:
    """
    Get information about the loaded models
    """
    try:
        whisper_info = whisper_stt.get_model_info()
        elevenlabs_usage = elevenlabs_tts.get_usage_info()
        
        return {
            "whisper": whisper_info,
            "elevenlabs": elevenlabs_usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model info: {str(e)}")
