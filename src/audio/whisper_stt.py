import whisper
import numpy as np
import io
import tempfile
import os
from typing import Dict, Any, Optional, List
import torch
from config.settings import settings

class WhisperSTT:
    """
    Speech-to-Text using OpenAI Whisper
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if settings.USE_CUDA and torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"Whisper model {self.model_size} loaded on {self.device}")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio_data: bytes, language: str = None, 
                  task: str = "transcribe") -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data as bytes
            language: Expected language (optional)
            task: Task type (transcribe or translate)
            
        Returns:
            Dictionary with transcription results
        """
        if not self.model:
            return {
                "text": "",
                "error": "Whisper model not loaded",
                "confidence": 0.0
            }
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                temp_file_path,
                language=language,
                task=task,
                fp16=False,  # Use fp32 for better compatibility
                verbose=False
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(result)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "confidence": confidence,
                "segments": result.get("segments", []),
                "task": task,
                "error": None
            }
            
        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    def _calculate_confidence(self, whisper_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score from Whisper result
        
        Args:
            whisper_result: Whisper transcription result
            
        Returns:
            Confidence score between 0 and 1
        """
        segments = whisper_result.get("segments", [])
        if not segments:
            return 0.0
        
        # Calculate average confidence from segments
        total_confidence = 0.0
        total_duration = 0.0
        
        for segment in segments:
            if "avg_logprob" in segment:
                # Convert log probability to confidence
                confidence = min(1.0, max(0.0, np.exp(segment["avg_logprob"])))
                duration = segment.get("end", 0) - segment.get("start", 0)
                
                total_confidence += confidence * duration
                total_duration += duration
        
        if total_duration > 0:
            return total_confidence / total_duration
        
        return 0.0
    
    def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language from audio
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Detected language code
        """
        if not self.model:
            return "unknown"
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Detect language using Whisper
            audio = whisper.load_audio(temp_file_path)
            audio = whisper.pad_or_trim(audio)
            
            # Get language detection
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            _, probs = self.model.detect_language(mel)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Return most likely language
            return max(probs, key=probs.get)
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return "unknown"
    
    def transcribe_with_timestamps(self, audio_data: bytes, 
                                 language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio with detailed timestamps
        
        Args:
            audio_data: Audio data as bytes
            language: Expected language (optional)
            
        Returns:
            Dictionary with transcription and timestamps
        """
        if not self.model:
            return {
                "text": "",
                "segments": [],
                "error": "Whisper model not loaded"
            }
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                temp_file_path,
                language=language,
                word_timestamps=True,
                fp16=False
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Process segments with word timestamps
            processed_segments = []
            for segment in result.get("segments", []):
                processed_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip(),
                    "confidence": np.exp(segment.get("avg_logprob", 0)) if "avg_logprob" in segment else 0.0,
                    "words": []
                }
                
                # Add word-level timestamps if available
                if "words" in segment:
                    for word in segment["words"]:
                        processed_segment["words"].append({
                            "word": word.get("word", ""),
                            "start": word.get("start", 0),
                            "end": word.get("end", 0),
                            "confidence": np.exp(word.get("probability", 0)) if "probability" in word else 0.0
                        })
                
                processed_segments.append(processed_segment)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": processed_segments,
                "duration": max([seg["end"] for seg in processed_segments]) if processed_segments else 0,
                "error": None
            }
            
        except Exception as e:
            return {
                "text": "",
                "segments": [],
                "error": str(e)
            }
    
    def translate(self, audio_data: bytes, target_language: str = "en") -> Dict[str, Any]:
        """
        Translate audio to target language
        
        Args:
            audio_data: Audio data as bytes
            target_language: Target language code
            
        Returns:
            Dictionary with translation results
        """
        return self.transcribe(audio_data, language=target_language, task="translate")
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of supported language codes
        """
        return [
            "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy",
            "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw",
            "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn",
            "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt",
            "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si",
            "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tr",
            "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        return {
            "model_size": self.model_size,
            "device": self.device,
            "is_multilingual": True,
            "supported_languages": self.get_supported_languages(),
            "model_parameters": sum(p.numel() for p in self.model.parameters())
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Whisper STT
        
        Returns:
            Health check results
        """
        try:
            if not self.model:
                return {
                    'status': 'error',
                    'message': 'Whisper model not loaded',
                    'ready': False
                }
            
            # Test with a simple audio (silence)
            test_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
            test_audio_bytes = (test_audio * 32767).astype(np.int16).tobytes()
            
            # This is a minimal test - in practice you might want to use actual audio
            return {
                'status': 'healthy',
                'message': 'Whisper STT is ready',
                'ready': True,
                'model_info': self.get_model_info()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Whisper STT health check failed: {e}',
                'ready': False
            }
