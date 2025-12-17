"""
Deepgram Voice Service for Agentic AI Retail System
Provides real-time STT (Speech-to-Text) and TTS (Text-to-Speech)
"""
import asyncio
import base64
import json
import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class DeepgramVoice(Enum):
    """Available Deepgram Aura TTS voices"""
    # Female voices
    ASTERIA = "aura-asteria-en"      # Warm, professional
    LUNA = "aura-luna-en"            # Friendly, casual
    STELLA = "aura-stella-en"        # Clear, articulate
    ATHENA = "aura-athena-en"        # Confident
    HERA = "aura-hera-en"            # Soft, gentle
    # Male voices
    ORION = "aura-orion-en"          # Professional
    ARCAS = "aura-arcas-en"          # Friendly
    PERSEUS = "aura-perseus-en"      # Deep, authoritative
    ANGUS = "aura-angus-en"          # Scottish accent
    ORPHEUS = "aura-orpheus-en"      # Warm male


@dataclass
class DeepgramConfig:
    """Deepgram service configuration"""
    api_key: str
    # STT settings
    stt_model: str = "nova-2"        # Best accuracy
    stt_language: str = "en"
    smart_format: bool = True        # Punctuation, formatting
    diarize: bool = False            # Speaker identification
    # TTS settings
    tts_voice: DeepgramVoice = DeepgramVoice.ASTERIA
    tts_sample_rate: int = 24000     # 24kHz for good quality
    tts_encoding: str = "linear16"   # PCM audio


class DeepgramService:
    """
    Deepgram Voice Service
    
    Provides:
    1. Real-time streaming STT via WebSocket
    2. Batch STT for audio files
    3. TTS for generating voice responses
    
    Architecture:
    - Voice input → STT → Master Orchestrator
    - Master Orchestrator response → TTS → Voice output
    """
    
    def __init__(self, config: DeepgramConfig):
        self.config = config
        self.base_url = "https://api.deepgram.com/v1"
        self._ws_connection = None
        
        logger.info(f"DeepgramService initialized with model: {config.stt_model}")
    
    # =========================================================================
    # SPEECH-TO-TEXT (STT)
    # =========================================================================
    
    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Transcribe audio data to text (batch/file mode)
        
        Args:
            audio_data: Raw audio bytes
            mime_type: Audio MIME type (audio/wav, audio/mp3, audio/webm, etc.)
            
        Returns:
            Dict with 'transcript', 'confidence', 'words', etc.
        """
        url = f"{self.base_url}/listen"
        
        params = {
            "model": self.config.stt_model,
            "language": self.config.stt_language,
            "smart_format": str(self.config.smart_format).lower(),
            "punctuate": "true",
        }
        
        headers = {
            "Authorization": f"Token {self.config.api_key}",
            "Content-Type": mime_type,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params=params,
                    headers=headers,
                    content=audio_data
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract transcript from response
                channels = result.get("results", {}).get("channels", [])
                if channels:
                    alternatives = channels[0].get("alternatives", [])
                    if alternatives:
                        return {
                            "success": True,
                            "transcript": alternatives[0].get("transcript", ""),
                            "confidence": alternatives[0].get("confidence", 0.0),
                            "words": alternatives[0].get("words", []),
                            "raw_response": result
                        }
                
                return {
                    "success": False,
                    "transcript": "",
                    "error": "No transcription in response"
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Deepgram STT HTTP error: {e.response.status_code}")
            return {
                "success": False,
                "transcript": "",
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f"Deepgram STT error: {e}")
            return {
                "success": False,
                "transcript": "",
                "error": str(e)
            }
    
    def get_streaming_url(self) -> str:
        """Get WebSocket URL for streaming STT"""
        params = [
            f"model={self.config.stt_model}",
            f"language={self.config.stt_language}",
            f"smart_format={str(self.config.smart_format).lower()}",
            "punctuate=true",
            "interim_results=true",
            "endpointing=300",  # 300ms silence = end of utterance
            "vad_events=true",  # Voice activity detection
        ]
        
        return f"wss://api.deepgram.com/v1/listen?{'&'.join(params)}"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for WebSocket"""
        return {"Authorization": f"Token {self.config.api_key}"}
    
    # =========================================================================
    # TEXT-TO-SPEECH (TTS)
    # =========================================================================
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice: DeepgramVoice = None
    ) -> Dict[str, Any]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to synthesize
            voice: Voice to use (default from config)
            
        Returns:
            Dict with 'audio' (bytes), 'content_type', etc.
        """
        voice = voice or self.config.tts_voice
        url = f"{self.base_url}/speak"
        
        params = {
            "model": voice.value,
            "encoding": self.config.tts_encoding,
            "sample_rate": self.config.tts_sample_rate,
        }
        
        headers = {
            "Authorization": f"Token {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params=params,
                    headers=headers,
                    json={"text": text}
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "audio": response.content,
                    "content_type": response.headers.get("content-type", "audio/wav"),
                    "sample_rate": self.config.tts_sample_rate,
                    "encoding": self.config.tts_encoding
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Deepgram TTS HTTP error: {e.response.status_code}")
            return {
                "success": False,
                "audio": None,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f"Deepgram TTS error: {e}")
            return {
                "success": False,
                "audio": None,
                "error": str(e)
            }
    
    async def synthesize_speech_base64(
        self, 
        text: str, 
        voice: DeepgramVoice = None
    ) -> Dict[str, Any]:
        """
        Convert text to base64-encoded speech audio
        Useful for sending audio over JSON/WebSocket
        """
        result = await self.synthesize_speech(text, voice)
        
        if result["success"] and result["audio"]:
            result["audio_base64"] = base64.b64encode(result["audio"]).decode("utf-8")
        
        return result


# =============================================================================
# STREAMING STT HANDLER
# =============================================================================

class DeepgramStreamingSTT:
    """
    Handles real-time streaming speech-to-text via WebSocket
    
    Usage:
        stt = DeepgramStreamingSTT(config, on_transcript=callback)
        await stt.connect()
        await stt.send_audio(audio_chunk)
        await stt.close()
    """
    
    def __init__(
        self, 
        config: DeepgramConfig,
        on_transcript: Callable[[str, bool], None] = None,
        on_utterance_end: Callable[[str], None] = None
    ):
        """
        Args:
            config: Deepgram configuration
            on_transcript: Callback(text, is_final) for transcripts
            on_utterance_end: Callback(final_text) when user stops speaking
        """
        self.config = config
        self.on_transcript = on_transcript
        self.on_utterance_end = on_utterance_end
        self._ws = None
        self._running = False
        self._current_transcript = ""
        
    async def connect(self):
        """Connect to Deepgram streaming API"""
        try:
            import websockets
            
            url = f"wss://api.deepgram.com/v1/listen?" + "&".join([
                f"model={self.config.stt_model}",
                f"language={self.config.stt_language}",
                "smart_format=true",
                "punctuate=true",
                "interim_results=true",
                "utterance_end_ms=1000",
                "vad_events=true",
            ])
            
            headers = {"Authorization": f"Token {self.config.api_key}"}
            
            self._ws = await websockets.connect(url, extra_headers=headers)
            self._running = True
            
            # Start listening for responses
            asyncio.create_task(self._receive_loop())
            
            logger.info("Connected to Deepgram streaming STT")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            return False
    
    async def send_audio(self, audio_data: bytes):
        """Send audio chunk to Deepgram"""
        if self._ws and self._running:
            try:
                await self._ws.send(audio_data)
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
    
    async def close(self):
        """Close the WebSocket connection"""
        self._running = False
        if self._ws:
            try:
                # Send close message
                await self._ws.send(json.dumps({"type": "CloseStream"}))
                await self._ws.close()
            except:
                pass
            self._ws = None
        logger.info("Disconnected from Deepgram")
    
    async def _receive_loop(self):
        """Receive and process transcription results"""
        while self._running and self._ws:
            try:
                message = await asyncio.wait_for(self._ws.recv(), timeout=30.0)
                data = json.loads(message)
                
                msg_type = data.get("type")
                
                if msg_type == "Results":
                    # Transcription result
                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "")
                        is_final = data.get("is_final", False)
                        
                        if transcript:
                            if is_final:
                                self._current_transcript = transcript
                            
                            if self.on_transcript:
                                self.on_transcript(transcript, is_final)
                
                elif msg_type == "UtteranceEnd":
                    # User stopped speaking
                    if self._current_transcript and self.on_utterance_end:
                        self.on_utterance_end(self._current_transcript)
                    self._current_transcript = ""
                
                elif msg_type == "SpeechStarted":
                    logger.debug("Speech started")
                
                elif msg_type == "Error":
                    logger.error(f"Deepgram error: {data}")
                    
            except asyncio.TimeoutError:
                # Send keepalive
                if self._ws:
                    try:
                        await self._ws.send(json.dumps({"type": "KeepAlive"}))
                    except:
                        pass
            except Exception as e:
                if self._running:
                    logger.error(f"Receive error: {e}")
                break


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_deepgram_service: Optional[DeepgramService] = None


def get_deepgram_service() -> Optional[DeepgramService]:
    """Get or create the global Deepgram service"""
    global _deepgram_service
    
    if _deepgram_service is None:
        from config import DEEPGRAM_API_KEY
        
        if not DEEPGRAM_API_KEY:
            logger.warning("DEEPGRAM_API_KEY not set - voice features disabled")
            return None
        
        config = DeepgramConfig(api_key=DEEPGRAM_API_KEY)
        _deepgram_service = DeepgramService(config)
    
    return _deepgram_service


def create_deepgram_service(api_key: str, **kwargs) -> DeepgramService:
    """Create a new Deepgram service with custom config"""
    config = DeepgramConfig(api_key=api_key, **kwargs)
    return DeepgramService(config)
