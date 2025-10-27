import whisper
import librosa
import numpy as np
from typing import Dict, Any, Optional, Tuple
import io
import tempfile
import os
from config.settings import settings

class AudioProcessor:
    """
    Audio processing for speech-to-text and audio analysis
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize audio processor
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.whisper_model = None
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model"""
        try:
            self.whisper_model = whisper.load_model(self.model_size)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, audio_data: bytes, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: Audio data as bytes
            language: Expected language (optional)
            
        Returns:
            Dictionary with transcription and metadata
        """
        if not self.whisper_model:
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
            result = self.whisper_model.transcribe(
                temp_file_path,
                language=language,
                fp16=False  # Use fp32 for better compatibility
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "confidence": self._calculate_confidence(result),
                "segments": result.get("segments", []),
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
        if not self.whisper_model:
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
            mel = whisper.log_mel_spectrogram(audio).to(self.whisper_model.device)
            _, probs = self.whisper_model.detect_language(mel)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Return most likely language
            return max(probs, key=probs.get)
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return "unknown"
    
    def extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extract audio features for analysis
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Dictionary of audio features
        """
        try:
            # Load audio using librosa
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            # Extract features
            features = {
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "rms_energy": float(np.sqrt(np.mean(audio**2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))),
                "mfcc": librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).mean(axis=1).tolist(),
                "tempo": float(librosa.beat.tempo(y=audio, sr=sr)[0]) if len(audio) > 0 else 0.0
            }
            
            return features
            
        except Exception as e:
            return {
                "error": str(e),
                "duration": 0.0,
                "sample_rate": 0
            }
    
    def detect_emotion_from_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Detect emotion from audio features
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Dictionary with emotion analysis
        """
        features = self.extract_audio_features(audio_data)
        
        if "error" in features:
            return {"error": features["error"]}
        
        # Simple emotion detection based on audio features
        emotion_scores = {
            "calm": 0.0,
            "stressed": 0.0,
            "excited": 0.0,
            "sad": 0.0,
            "angry": 0.0
        }
        
        # Analyze features for emotion indicators
        rms_energy = features["rms_energy"]
        zero_crossing_rate = features["zero_crossing_rate"]
        spectral_centroid = features["spectral_centroid"]
        tempo = features["tempo"]
        
        # High energy and tempo might indicate excitement or stress
        if rms_energy > 0.1 and tempo > 120:
            emotion_scores["excited"] += 0.3
            emotion_scores["stressed"] += 0.2
        
        # Low energy might indicate sadness or calmness
        if rms_energy < 0.05:
            emotion_scores["sad"] += 0.3
            emotion_scores["calm"] += 0.2
        
        # High zero crossing rate might indicate stress or anger
        if zero_crossing_rate > 0.1:
            emotion_scores["stressed"] += 0.2
            emotion_scores["angry"] += 0.1
        
        # High spectral centroid might indicate excitement
        if spectral_centroid > 2000:
            emotion_scores["excited"] += 0.2
        
        # Normalize scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
        
        # Get dominant emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        
        return {
            "emotions": emotion_scores,
            "dominant_emotion": dominant_emotion,
            "confidence": emotion_scores[dominant_emotion]
        }
    
    def detect_voice_characteristics(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Detect voice characteristics
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Dictionary with voice characteristics
        """
        features = self.extract_audio_features(audio_data)
        
        if "error" in features:
            return {"error": features["error"]}
        
        # Analyze voice characteristics
        characteristics = {
            "pitch_range": "unknown",
            "speech_rate": "unknown",
            "volume_level": "unknown",
            "voice_quality": "unknown"
        }
        
        # Analyze pitch (using spectral centroid as proxy)
        spectral_centroid = features["spectral_centroid"]
        if spectral_centroid > 2500:
            characteristics["pitch_range"] = "high"
        elif spectral_centroid < 1500:
            characteristics["pitch_range"] = "low"
        else:
            characteristics["pitch_range"] = "medium"
        
        # Analyze speech rate (using tempo as proxy)
        tempo = features["tempo"]
        if tempo > 150:
            characteristics["speech_rate"] = "fast"
        elif tempo < 100:
            characteristics["speech_rate"] = "slow"
        else:
            characteristics["speech_rate"] = "normal"
        
        # Analyze volume
        rms_energy = features["rms_energy"]
        if rms_energy > 0.1:
            characteristics["volume_level"] = "loud"
        elif rms_energy < 0.05:
            characteristics["volume_level"] = "quiet"
        else:
            characteristics["volume_level"] = "normal"
        
        # Analyze voice quality
        zero_crossing_rate = features["zero_crossing_rate"]
        if zero_crossing_rate > 0.1:
            characteristics["voice_quality"] = "rough"
        else:
            characteristics["voice_quality"] = "smooth"
        
        return characteristics
    
    def preprocess_audio(self, audio_data: bytes, target_sr: int = 16000) -> bytes:
        """
        Preprocess audio for better transcription
        
        Args:
            audio_data: Input audio data
            target_sr: Target sample rate
            
        Returns:
            Preprocessed audio data
        """
        try:
            # Load audio
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=target_sr)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Remove silence
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Convert back to bytes
            audio_bytes = (audio * 32767).astype(np.int16).tobytes()
            
            return audio_bytes
            
        except Exception as e:
            print(f"Audio preprocessing error: {e}")
            return audio_data
    
    def validate_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate audio data quality
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            Validation results
        """
        try:
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            validation = {
                "valid": True,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "channels": 1,  # Assuming mono
                "issues": []
            }
            
            # Check duration
            if validation["duration"] < 0.5:
                validation["issues"].append("Audio too short (less than 0.5 seconds)")
                validation["valid"] = False
            
            if validation["duration"] > 300:  # 5 minutes
                validation["issues"].append("Audio too long (more than 5 minutes)")
            
            # Check sample rate
            if sr < 8000:
                validation["issues"].append("Sample rate too low (less than 8kHz)")
                validation["valid"] = False
            
            # Check for silence
            rms_energy = np.sqrt(np.mean(audio**2))
            if rms_energy < 0.001:
                validation["issues"].append("Audio appears to be silent")
                validation["valid"] = False
            
            return validation
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "issues": ["Invalid audio format"]
            }

