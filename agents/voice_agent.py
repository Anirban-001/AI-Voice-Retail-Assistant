"""
Voice Agent for Agentic AI Retail System
Uses Deepgram for STT/TTS, routes ALL requests through Master Orchestrator

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                        VOICE AGENT                               │
│  (Interface Layer - No Decision Making)                         │
│                                                                  │
│  🎤 Audio In → [Deepgram STT] → Text                            │
│                                  ↓                               │
│                         ┌───────────────┐                        │
│                         │    MASTER     │                        │
│                         │ ORCHESTRATOR  │                        │
│                         └───────────────┘                        │
│                          ↓    ↓    ↓                             │
│                    ┌─────┴────┴────┴─────┐                       │
│                    │  Worker Agents      │                       │
│                    │  - Recommendation   │                       │
│                    │  - Inventory        │                       │
│                    │  - Payment          │                       │
│                    └─────────────────────┘                       │
│                                  ↓                               │
│  🔊 Audio Out ← [Deepgram TTS] ← Response Text                  │
└─────────────────────────────────────────────────────────────────┘
"""
import asyncio
import uuid
import logging
import json
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceState(Enum):
    """Voice session states"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceSession:
    """Voice session data"""
    session_id: str
    user_id: str = "voice_user"
    channel: str = "voice"
    language: str = "en"
    mood: str = "neutral"
    cart: list = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    state: VoiceState = VoiceState.DISCONNECTED
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_context(self) -> Dict:
        """Convert to orchestrator context format"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "channel": self.channel,
            "language": self.language,
            "mood": self.mood,
            "cart": self.cart,
            "conversation_history": self.conversation_history
        }


class VoiceAgent:
    """
    Voice Agent - Interface layer for voice interactions
    
    This agent does NOT make decisions. It:
    1. Converts speech to text (Deepgram STT)
    2. Sends ALL text to the Master Orchestrator
    3. Receives response from Master Orchestrator
    4. Converts response to speech (Deepgram TTS)
    
    All intelligence, routing, and decision-making happens
    in the Master Orchestrator and its worker agents.
    """
    
    def __init__(self):
        self.sessions: Dict[str, VoiceSession] = {}
        self._deepgram = None
        self._streaming_connections: Dict[str, Any] = {}
        
        logger.info("VoiceAgent initialized - routes to Master Orchestrator")
    
    @property
    def deepgram(self):
        """Lazy load Deepgram service"""
        if self._deepgram is None:
            from services.deepgram_service import get_deepgram_service
            self._deepgram = get_deepgram_service()
        return self._deepgram
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def create_session(self, user_id: str = None) -> VoiceSession:
        """Create a new voice session"""
        session = VoiceSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id or f"voice_user_{uuid.uuid4().hex[:8]}",
            state=VoiceState.CONNECTED
        )
        self.sessions[session.session_id] = session
        logger.info(f"Voice session created: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str):
        """End and cleanup a voice session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Voice session ended: {session_id}")
        
        # Cleanup streaming connection if exists
        if session_id in self._streaming_connections:
            del self._streaming_connections[session_id]
    
    # =========================================================================
    # CORE VOICE PROCESSING
    # =========================================================================
    
    async def process_audio(
        self, 
        session_id: str, 
        audio_data: bytes,
        mime_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Process audio input and get voice response
        
        Flow:
        1. Audio → Deepgram STT → Text
        2. Text → Master Orchestrator → Response
        3. Response → Deepgram TTS → Audio
        
        Args:
            session_id: Voice session ID
            audio_data: Raw audio bytes
            mime_type: Audio format
            
        Returns:
            Dict with transcript, response_text, response_audio, etc.
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        if not self.deepgram:
            return {"success": False, "error": "Deepgram service not configured"}
        
        session.state = VoiceState.PROCESSING
        
        try:
            # Step 1: Speech to Text
            stt_result = await self.deepgram.transcribe_audio(audio_data, mime_type)
            
            if not stt_result["success"]:
                session.state = VoiceState.ERROR
                return {
                    "success": False,
                    "error": f"STT failed: {stt_result.get('error')}",
                    "session_id": session_id
                }
            
            transcript = stt_result["transcript"]
            
            if not transcript.strip():
                session.state = VoiceState.LISTENING
                return {
                    "success": True,
                    "transcript": "",
                    "response_text": "I didn't catch that. Could you please repeat?",
                    "session_id": session_id
                }
            
            logger.info(f"[Voice] Transcribed: {transcript[:50]}...")
            
            # Step 2: Process through Master Orchestrator
            response = await self._route_to_orchestrator(session, transcript)
            
            # Step 3: Text to Speech
            session.state = VoiceState.SPEAKING
            tts_result = await self.deepgram.synthesize_speech_base64(response["message"])
            
            session.state = VoiceState.LISTENING
            
            return {
                "success": True,
                "session_id": session_id,
                "transcript": transcript,
                "response_text": response["message"],
                "response_audio_base64": tts_result.get("audio_base64") if tts_result["success"] else None,
                "audio_content_type": tts_result.get("content_type", "audio/wav"),
                "data": response.get("data", {}),
                "suggested_actions": response.get("suggested_actions", []),
                "context": {
                    "mood": session.mood,
                    "language": session.language
                }
            }
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            session.state = VoiceState.ERROR
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def process_text(
        self, 
        session_id: str, 
        text: str,
        generate_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Process text input (when client handles STT)
        
        Args:
            session_id: Voice session ID
            text: Transcribed text from client
            generate_audio: Whether to generate TTS audio
            
        Returns:
            Dict with response_text, response_audio, etc.
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        session.state = VoiceState.PROCESSING
        
        try:
            # Process through Master Orchestrator
            response = await self._route_to_orchestrator(session, text)
            
            result = {
                "success": True,
                "session_id": session_id,
                "response_text": response["message"],
                "data": response.get("data", {}),
                "suggested_actions": response.get("suggested_actions", []),
                "context": {
                    "mood": session.mood,
                    "language": session.language
                }
            }
            
            # Generate TTS if requested and Deepgram is available
            if generate_audio and self.deepgram:
                session.state = VoiceState.SPEAKING
                tts_result = await self.deepgram.synthesize_speech_base64(response["message"])
                
                if tts_result["success"]:
                    result["response_audio_base64"] = tts_result.get("audio_base64")
                    result["audio_content_type"] = tts_result.get("content_type", "audio/wav")
            
            session.state = VoiceState.LISTENING
            return result
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            session.state = VoiceState.ERROR
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def _route_to_orchestrator(
        self, 
        session: VoiceSession, 
        user_input: str
    ) -> Dict[str, Any]:
        """
        Route user input to the Master Orchestrator
        
        The Orchestrator handles:
        - Language detection
        - Mood analysis
        - Intent classification
        - Routing to worker agents (Recommendation, Inventory, Payment)
        - Response generation
        """
        from agents import orchestrator, AgentMessage, AgentType
        
        # Add to conversation history
        session.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Create message for Master Orchestrator
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=AgentType.ORCHESTRATOR,
            to_agent=AgentType.ORCHESTRATOR,
            intent="process_input",
            payload={"user_message": user_input},
            context=session.to_context()
        )
        
        # Process through Orchestrator (which may route to workers)
        response = await orchestrator.process(message)
        
        # Update session with response data
        mood_data = response.data.get("mood")
        if mood_data:
            if isinstance(mood_data, dict):
                session.mood = mood_data.get("mood", "neutral")
            else:
                session.mood = mood_data
        
        if response.data.get("language"):
            session.language = response.data["language"]
        
        # Update cart if changed
        if "cart" in response.data:
            session.cart = response.data["cart"]
        
        # Add assistant response to history
        session.conversation_history.append({
            "role": "assistant",
            "content": response.message
        })
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "suggested_actions": response.suggested_actions
        }
    
    # =========================================================================
    # STREAMING VOICE (Real-time)
    # =========================================================================
    
    async def start_streaming(
        self,
        session_id: str,
        on_transcript: Callable[[str, bool], None] = None,
        on_response: Callable[[str, bytes], None] = None
    ) -> bool:
        """
        Start real-time streaming voice conversation
        
        Args:
            session_id: Voice session ID
            on_transcript: Callback(text, is_final) for interim transcripts
            on_response: Callback(text, audio_bytes) for AI responses
            
        Returns:
            True if streaming started successfully
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        if not self.deepgram:
            logger.error("Deepgram service not configured")
            return False
        
        from services.deepgram_service import DeepgramStreamingSTT, DeepgramConfig
        from config import DEEPGRAM_API_KEY
        
        # Create callback for when user finishes speaking
        async def handle_utterance(text: str):
            """Process complete utterance through orchestrator"""
            response = await self._route_to_orchestrator(session, text)
            
            # Generate TTS
            tts_result = await self.deepgram.synthesize_speech(response["message"])
            
            if on_response:
                audio = tts_result.get("audio") if tts_result["success"] else None
                on_response(response["message"], audio)
        
        def on_utterance_end(text: str):
            """Wrapper to run async handler"""
            asyncio.create_task(handle_utterance(text))
        
        # Create streaming STT
        config = DeepgramConfig(api_key=DEEPGRAM_API_KEY)
        streaming = DeepgramStreamingSTT(
            config=config,
            on_transcript=on_transcript,
            on_utterance_end=on_utterance_end
        )
        
        # Connect
        success = await streaming.connect()
        
        if success:
            self._streaming_connections[session_id] = streaming
            session.state = VoiceState.LISTENING
            logger.info(f"Streaming started for session: {session_id}")
        
        return success
    
    async def send_audio_chunk(self, session_id: str, audio_chunk: bytes):
        """Send audio chunk for real-time streaming"""
        streaming = self._streaming_connections.get(session_id)
        if streaming:
            await streaming.send_audio(audio_chunk)
    
    async def stop_streaming(self, session_id: str):
        """Stop streaming for a session"""
        streaming = self._streaming_connections.get(session_id)
        if streaming:
            await streaming.close()
            del self._streaming_connections[session_id]
            
            session = self.get_session(session_id)
            if session:
                session.state = VoiceState.CONNECTED
            
            logger.info(f"Streaming stopped for session: {session_id}")
    
    # =========================================================================
    # PROACTIVE SPEAKING
    # =========================================================================
    
    async def speak(
        self, 
        session_id: str, 
        text: str
    ) -> Dict[str, Any]:
        """
        Proactively speak to the user (not in response to input)
        
        Args:
            session_id: Voice session ID
            text: Text to speak
            
        Returns:
            Dict with audio data
        """
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        if not self.deepgram:
            return {"success": False, "error": "Deepgram not configured"}
        
        session.state = VoiceState.SPEAKING
        
        tts_result = await self.deepgram.synthesize_speech_base64(text)
        
        session.state = VoiceState.LISTENING
        
        if tts_result["success"]:
            return {
                "success": True,
                "text": text,
                "audio_base64": tts_result.get("audio_base64"),
                "content_type": tts_result.get("content_type", "audio/wav")
            }
        else:
            return {
                "success": False,
                "error": tts_result.get("error"),
                "text": text
            }
    
    async def generate_welcome(self, session_id: str) -> Dict[str, Any]:
        """Generate and speak a welcome message"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        
        # Get welcome from orchestrator
        response = await self._route_to_orchestrator(session, "hello")
        
        # Generate audio
        return await self.speak(session_id, response["message"])


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Create global voice agent instance
voice_agent = VoiceAgent()


def get_voice_agent() -> VoiceAgent:
    """Get the global voice agent instance"""
    return voice_agent
