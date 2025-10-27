import requests
import json
from typing import Dict, Any, Optional, List
import io
from config.settings import settings

class ElevenLabsTTS:
    """
    Text-to-Speech using ElevenLabs API
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize ElevenLabs TTS
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice = settings.TTS_VOICE
        
        # Available voices
        self.voices = {
            "alloy": "21m00Tcm4TlvDq8ikWAM",
            "echo": "AZnzlk1XvdvUeBnXmlld",
            "fable": "ErXwobaYiN019PkySvjV",
            "onyx": "2EiwWnXFnvU5JabPnv8n",
            "nova": "9BWtxz7Tgu7GRtdg9QkA",
            "shimmer": "pNInz6obpgDQGcFmaJgB"
        }
    
    def text_to_speech(self, text: str, voice: str = None, 
                      model_id: str = "eleven_multilingual_v2",
                      voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (optional)
            model_id: Model ID to use
            voice_settings: Voice settings (stability, similarity_boost, etc.)
            
        Returns:
            Dictionary with audio data and metadata
        """
        if not self.api_key:
            return {
                "audio_data": None,
                "error": "ElevenLabs API key not provided",
                "success": False
            }
        
        voice_id = self.voices.get(voice or self.default_voice, self.voices[self.default_voice])
        
        # Default voice settings
        default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        if voice_settings:
            default_settings.update(voice_settings)
        
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": default_settings
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return {
                    "audio_data": response.content,
                    "content_type": "audio/mpeg",
                    "voice_used": voice or self.default_voice,
                    "model_used": model_id,
                    "text_length": len(text),
                    "success": True,
                    "error": None
                }
            else:
                return {
                    "audio_data": None,
                    "error": f"API request failed: {response.status_code} - {response.text}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "audio_data": None,
                "error": f"TTS conversion failed: {e}",
                "success": False
            }
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get available voices
        
        Returns:
            List of available voices
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("voices", [])
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def get_voice_by_name(self, voice_name: str) -> Optional[Dict[str, Any]]:
        """
        Get voice information by name
        
        Args:
            voice_name: Name of the voice
            
        Returns:
            Voice information or None if not found
        """
        voices = self.get_voices()
        
        for voice in voices:
            if voice.get("name", "").lower() == voice_name.lower():
                return voice
        
        return None
    
    def create_custom_voice(self, name: str, description: str = "",
                           files: List[bytes] = None) -> Dict[str, Any]:
        """
        Create a custom voice (requires premium account)
        
        Args:
            name: Name for the custom voice
            description: Description of the voice
            files: List of audio files for training
            
        Returns:
            Creation result
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "ElevenLabs API key not provided"
            }
        
        try:
            url = f"{self.base_url}/voices/add"
            headers = {"xi-api-key": self.api_key}
            
            data = {
                "name": name,
                "description": description
            }
            
            files_data = []
            if files:
                for i, file_data in enumerate(files):
                    files_data.append(("files", (f"audio_{i}.wav", file_data, "audio/wav")))
            
            response = requests.post(url, data=data, files=files_data, headers=headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "voice_id": response.json().get("voice_id"),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": f"Voice creation failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Voice creation failed: {e}"
            }
    
    def get_voice_settings(self, voice_id: str) -> Dict[str, Any]:
        """
        Get voice settings for a specific voice
        
        Args:
            voice_id: Voice ID
            
        Returns:
            Voice settings
        """
        if not self.api_key:
            return {"error": "ElevenLabs API key not provided"}
        
        try:
            url = f"{self.base_url}/voices/{voice_id}/settings"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get voice settings: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error getting voice settings: {e}"}
    
    def update_voice_settings(self, voice_id: str, 
                             settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update voice settings
        
        Args:
            voice_id: Voice ID
            settings: New voice settings
            
        Returns:
            Update result
        """
        if not self.api_key:
            return {"success": False, "error": "ElevenLabs API key not provided"}
        
        try:
            url = f"{self.base_url}/voices/{voice_id}/settings"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=settings, headers=headers)
            
            if response.status_code == 200:
                return {"success": True, "error": None}
            else:
                return {
                    "success": False,
                    "error": f"Settings update failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Settings update failed: {e}"}
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get API usage information
        
        Returns:
            Usage information
        """
        if not self.api_key:
            return {"error": "ElevenLabs API key not provided"}
        
        try:
            url = f"{self.base_url}/user"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get usage info: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error getting usage info: {e}"}
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models
        
        Returns:
            List of available models
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/models"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def synthesize_speech_batch(self, texts: List[str], voice: str = None,
                               model_id: str = "eleven_multilingual_v2") -> List[Dict[str, Any]]:
        """
        Synthesize multiple texts to speech
        
        Args:
            texts: List of texts to convert
            voice: Voice to use
            model_id: Model ID to use
            
        Returns:
            List of synthesis results
        """
        results = []
        
        for text in texts:
            result = self.text_to_speech(text, voice, model_id)
            results.append(result)
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ElevenLabs TTS
        
        Returns:
            Health check results
        """
        try:
            if not self.api_key:
                return {
                    'status': 'error',
                    'message': 'ElevenLabs API key not provided',
                    'ready': False
                }
            
            # Test API connection
            usage_info = self.get_usage_info()
            
            if "error" in usage_info:
                return {
                    'status': 'error',
                    'message': f'API connection failed: {usage_info["error"]}',
                    'ready': False
                }
            
            return {
                'status': 'healthy',
                'message': 'ElevenLabs TTS is ready',
                'ready': True,
                'usage_info': usage_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'ElevenLabs TTS health check failed: {e}',
                'ready': False
            }
    
    def get_voice_recommendations(self, text: str) -> List[str]:
        """
        Get voice recommendations based on text content
        
        Args:
            text: Text to analyze
            
        Returns:
            List of recommended voices
        """
        text_lower = text.lower()
        
        recommendations = []
        
        # Medical/clinical content
        if any(word in text_lower for word in ['doctor', 'medical', 'health', 'patient', 'treatment']):
            recommendations.extend(['alloy', 'onyx'])  # Professional, clear voices
        
        # Emergency content
        elif any(word in text_lower for word in ['emergency', 'urgent', 'immediate', 'critical']):
            recommendations.extend(['echo', 'nova'])  # Authoritative voices
        
        # Emotional support content
        elif any(word in text_lower for word in ['comfort', 'support', 'care', 'help', 'understand']):
            recommendations.extend(['shimmer', 'fable'])  # Warm, empathetic voices
        
        # General content
        else:
            recommendations.extend(['alloy', 'echo', 'nova'])  # Versatile voices
        
        return list(set(recommendations))  # Remove duplicates
