"""
Voice Service for Agentic AI Retail System
WebSocket handlers for real-time voice conversations using Deepgram
"""
import asyncio
import json
import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceWebSocketHandler:
    """
    WebSocket handler for real-time voice conversations
    
    Supports two modes:
    1. Client-side STT: Client sends transcribed text, server sends TTS audio
    2. Server-side STT: Client sends audio, server does STT + processing + TTS
    
    All intelligence flows through the Master Orchestrator.
    """
    
    def __init__(self):
        self.active_connections = {}
    
    async def handle_connection(self, websocket, session_id: str = None):
        """
        Handle a WebSocket voice connection
        
        Protocol:
        - Client → Server: {"type": "text", "content": "user message"}
        - Client → Server: {"type": "audio", "data": "base64_audio", "mime_type": "audio/wav"}
        - Server → Client: {"type": "response", "text": "...", "audio": "base64_audio"}
        - Server → Client: {"type": "transcript", "text": "...", "is_final": true/false}
        """
        from agents.voice_agent import get_voice_agent
        
        voice_agent = get_voice_agent()
        
        # Create or get session
        if session_id:
            session = voice_agent.get_session(session_id)
            if not session:
                session = voice_agent.create_session()
                session_id = session.session_id
        else:
            session = voice_agent.create_session()
            session_id = session.session_id
        
        self.active_connections[session_id] = websocket
        
        try:
            # Send session info
            await websocket.send_text(json.dumps({
                "type": "session_started",
                "session_id": session_id,
                "message": "Voice session connected"
            }))
            
            # Generate and send welcome
            welcome = await voice_agent.generate_welcome(session_id)
            await websocket.send_text(json.dumps({
                "type": "response",
                "text": welcome.get("text", "Hello! How can I help you?"),
                "audio": welcome.get("audio_base64"),
                "content_type": welcome.get("content_type", "audio/wav")
            }))
            
            # Handle messages
            async for message in websocket.iter_text():
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "text":
                        # Client-side STT - process text directly
                        text = data.get("content", "")
                        if text.strip():
                            result = await voice_agent.process_text(
                                session_id, 
                                text,
                                generate_audio=True
                            )
                            
                            await websocket.send_text(json.dumps({
                                "type": "response",
                                "text": result.get("response_text", ""),
                                "audio": result.get("response_audio_base64"),
                                "content_type": result.get("audio_content_type", "audio/wav"),
                                "data": result.get("data", {}),
                                "suggested_actions": result.get("suggested_actions", [])
                            }))
                    
                    elif msg_type == "audio":
                        # Server-side STT - process audio
                        audio_base64 = data.get("data", "")
                        mime_type = data.get("mime_type", "audio/wav")
                        
                        if audio_base64:
                            audio_data = base64.b64decode(audio_base64)
                            result = await voice_agent.process_audio(
                                session_id,
                                audio_data,
                                mime_type
                            )
                            
                            # Send transcript first
                            if result.get("transcript"):
                                await websocket.send_text(json.dumps({
                                    "type": "transcript",
                                    "text": result.get("transcript"),
                                    "is_final": True
                                }))
                            
                            # Then send response
                            await websocket.send_text(json.dumps({
                                "type": "response",
                                "text": result.get("response_text", ""),
                                "audio": result.get("response_audio_base64"),
                                "content_type": result.get("audio_content_type", "audio/wav"),
                                "data": result.get("data", {}),
                                "suggested_actions": result.get("suggested_actions", [])
                            }))
                    
                    elif msg_type == "end_session":
                        # End the session gracefully
                        farewell = await voice_agent.process_text(
                            session_id,
                            "goodbye",
                            generate_audio=True
                        )
                        
                        await websocket.send_text(json.dumps({
                            "type": "session_ended",
                            "text": farewell.get("response_text", "Goodbye!"),
                            "audio": farewell.get("response_audio_base64")
                        }))
                        break
                    
                    elif msg_type == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                        
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        
        finally:
            # Cleanup
            voice_agent.end_session(session_id)
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            logger.info(f"Voice WebSocket closed: {session_id}")


# Global handler instance
voice_websocket_handler = VoiceWebSocketHandler()


async def handle_voice_websocket(websocket, session_id: str = None):
    """Entry point for voice WebSocket connections"""
    await voice_websocket_handler.handle_connection(websocket, session_id)
