"""
REST API for Agentic AI Retail System
Provides endpoints for web, mobile, and kiosk interfaces
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agents import (
    AgentType,
    AgentMessage,
    AgentRegistry,
    orchestrator
)
from services.database import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Retail System",
    description="Multi-modal AI-powered retail assistant with mood detection and personalization",
    version="1.0.0-mvp"
)

# CORS middleware for web/mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    channel: str = Field("web", description="Channel: web, mobile, kiosk, voice")
    language: Optional[str] = Field(None, description="Preferred language (auto-detect if not set)")


class ChatResponse(BaseModel):
    """Chat message response"""
    success: bool
    message: str
    session_id: str
    data: Dict = {}
    suggested_actions: list = []
    context: Dict = {}


class SessionRequest(BaseModel):
    """Create session request"""
    user_id: Optional[str] = None
    channel: str = "web"


class CartRequest(BaseModel):
    """Add to cart request"""
    session_id: str
    product_id: str
    quantity: int = 1


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

# In-memory session store (use Redis in production)
sessions: Dict[str, Dict] = {}


def get_or_create_session(session_id: Optional[str], user_id: Optional[str], channel: str) -> Dict:
    """Get existing session or create new one"""
    
    if session_id and session_id in sessions:
        return sessions[session_id]
    
    # Create new session
    new_session_id = session_id or str(uuid.uuid4())
    
    session = {
        "id": new_session_id,
        "user_id": user_id or f"guest_{new_session_id[:8]}",
        "channel": channel,
        "language": "auto",
        "mood": "neutral",
        "mood_confidence": 0.0,
        "suggested_tone": "professional",
        "cart": [],
        "conversation_history": [],
        "context": {},
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat()
    }
    
    sessions[new_session_id] = session
    
    # Also create in database
    DatabaseService.create_session(session["user_id"], channel)
    
    return session


def update_session(session_id: str, updates: Dict):
    """Update session data"""
    if session_id in sessions:
        sessions[session_id].update(updates)
        sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Agentic AI Retail System",
        "version": "1.0.0-mvp",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/session", response_model=Dict)
async def create_session(request: SessionRequest):
    """Create a new chat session"""
    
    session = get_or_create_session(None, request.user_id, request.channel)
    
    return {
        "success": True,
        "session_id": session["id"],
        "user_id": session["user_id"],
        "channel": session["channel"]
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "session": sessions[session_id]
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user messages through the orchestrator
    """
    
    logger.info(f"Chat request: {request.message[:100]}")
    
    # Get or create session
    session = get_or_create_session(
        request.session_id,
        request.user_id,
        request.channel
    )
    
    # Build context from session
    context = {
        "session_id": session["id"],
        "user_id": session["user_id"],
        "channel": session["channel"],
        "language": request.language or session.get("language", "auto"),
        "mood": session.get("mood", "neutral"),
        "mood_confidence": session.get("mood_confidence", 0.0),
        "suggested_tone": session.get("suggested_tone", "professional"),
        "cart": session.get("cart", []),
        "conversation_history": session.get("conversation_history", [])
    }
    
    # Add user message to history
    context["conversation_history"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Create message for orchestrator
    agent_message = AgentMessage(
        message_id=str(uuid.uuid4()),
        from_agent=AgentType.ORCHESTRATOR,  # External request
        to_agent=AgentType.ORCHESTRATOR,
        intent="process_input",
        payload={"user_message": request.message},
        context=context
    )
    
    # Process through orchestrator
    try:
        response = await orchestrator.process(agent_message)
        
        # Update session with new context
        update_session(session["id"], {
            "language": response.data.get("language", context["language"]),
            "mood": response.data.get("mood", {}).get("mood", context["mood"]),
            "mood_confidence": response.data.get("mood", {}).get("confidence", 0.0),
            "suggested_tone": response.data.get("mood", {}).get("suggested_tone", "professional"),
            "conversation_history": context["conversation_history"] + [{
                "role": "assistant",
                "content": response.message,
                "timestamp": datetime.utcnow().isoformat()
            }]
        })
        
        return ChatResponse(
            success=response.success,
            message=response.message,
            session_id=session["id"],
            data=response.data,
            suggested_actions=response.suggested_actions,
            context={
                "language": response.data.get("language"),
                "mood": response.data.get("mood", {}).get("mood"),
                "intent": response.data.get("intent", {}).get("intent"),
                "handled_by": response.data.get("handled_by")
            }
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        return ChatResponse(
            success=False,
            message="I apologize, but I'm having trouble processing your request. Please try again.",
            session_id=session["id"],
            data={"error": str(e)},
            suggested_actions=["try_again"],
            context={}
        )


@app.post("/api/cart/add")
async def add_to_cart(request: CartRequest):
    """Add item to cart"""
    
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    
    # Get product details
    product = DatabaseService.get_product_by_id(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock
    stock = DatabaseService.check_stock(request.product_id)
    if not stock.get("in_stock"):
        raise HTTPException(status_code=400, detail="Product out of stock")
    
    # Add to cart
    cart = session.get("cart", [])
    
    # Check if already in cart
    for item in cart:
        if item["product_id"] == request.product_id:
            item["quantity"] += request.quantity
            break
    else:
        cart.append({
            "product_id": request.product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": request.quantity
        })
    
    update_session(request.session_id, {"cart": cart})
    
    return {
        "success": True,
        "cart": cart,
        "item_count": sum(i["quantity"] for i in cart)
    }


@app.get("/api/cart/{session_id}")
async def get_cart(session_id: str):
    """Get cart contents"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    cart = sessions[session_id].get("cart", [])
    
    subtotal = sum(item["price"] * item["quantity"] for item in cart)
    tax = subtotal * 0.08
    total = subtotal + tax
    
    return {
        "success": True,
        "cart": cart,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "item_count": sum(i["quantity"] for i in cart)
    }


@app.delete("/api/cart/{session_id}")
async def clear_cart(session_id: str):
    """Clear cart"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_session(session_id, {"cart": []})
    
    return {"success": True, "message": "Cart cleared"}


@app.get("/api/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = 20):
    """Get products with optional filtering"""
    
    if search:
        products = DatabaseService.search_products(search, category)
    elif category:
        products = DatabaseService.get_products_by_category(category)
    else:
        products = DatabaseService.get_all_products(limit=limit)
    
    return {
        "success": True,
        "products": products,
        "count": len(products)
    }


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product details"""
    
    product = DatabaseService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock = DatabaseService.check_stock(product_id)
    
    return {
        "success": True,
        "product": product,
        "stock": stock
    }


@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    
    categories = DatabaseService.get_categories()
    
    return {
        "success": True,
        "categories": categories
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    
    stats = DatabaseService.get_stats()
    stats["active_sessions"] = len(sessions)
    
    return {
        "success": True,
        "stats": stats
    }


# =============================================================================
# VOICE ENDPOINTS
# =============================================================================

class VoiceTextRequest(BaseModel):
    """Voice-to-AI request (client-side STT)"""
    session_id: str = Field(..., description="Session ID")
    transcription: str = Field(..., description="Transcribed text from client STT")
    language: Optional[str] = Field(None, description="Detected language")


@app.post("/api/voice/text")
async def voice_text(request: VoiceTextRequest):
    """
    Process transcribed voice input
    
    Use this endpoint when client handles STT and sends text.
    Response includes text that client should speak via TTS.
    """
    session = get_or_create_session(request.session_id, None, "voice")
    
    if request.language:
        session["language"] = request.language
    
    # Process through orchestrator
    session["conversation_history"].append({
        "role": "user",
        "content": request.transcription
    })
    
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        from_agent=AgentType.ORCHESTRATOR,
        to_agent=AgentType.ORCHESTRATOR,
        intent="process_input",
        payload={"user_message": request.transcription},
        context={
            "session_id": session["id"],
            "user_id": session["user_id"],
            "channel": "voice",
            "language": session.get("language", "auto"),
            "mood": session.get("mood", "neutral"),
            "cart": session.get("cart", []),
            "conversation_history": session.get("conversation_history", [])
        }
    )
    
    response = await orchestrator.process(message)
    
    # Update session
    mood_data = response.data.get("mood")
    if mood_data:
        if isinstance(mood_data, dict):
            session["mood"] = mood_data.get("mood", "neutral")
        else:
            session["mood"] = mood_data
    
    session["conversation_history"].append({
        "role": "assistant",
        "content": response.message
    })
    
    return {
        "success": True,
        "message": response.message,  # Text for TTS
        "session_id": session["id"],
        "data": response.data,
        "suggested_actions": response.suggested_actions,
        "context": {
            "mood": session.get("mood"),
            "language": session.get("language")
        }
    }


@app.websocket("/ws/voice/{session_id}")
async def voice_websocket(websocket, session_id: str):
    """
    WebSocket endpoint for real-time voice conversations
    
    Protocol:
    - Client → Server: {"type": "text", "content": "user message"}
    - Client → Server: {"type": "audio", "data": "base64_audio", "mime_type": "audio/wav"}
    - Server → Client: {"type": "response", "text": "...", "audio": "base64_audio"}
    - Server → Client: {"type": "transcript", "text": "...", "is_final": true/false}
    """
    from services.voice_service import handle_voice_websocket
    
    await websocket.accept()
    
    try:
        await handle_voice_websocket(websocket, session_id)
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


@app.post("/api/voice/session")
async def create_voice_session(user_id: Optional[str] = None):
    """Create a new voice session"""
    from agents.voice_agent import get_voice_agent
    
    voice_agent = get_voice_agent()
    session = voice_agent.create_session(user_id)
    
    return {
        "success": True,
        "session_id": session.session_id,
        "user_id": session.user_id,
        "state": session.state.value
    }


@app.post("/api/voice/audio")
async def process_voice_audio(
    session_id: str,
    audio_base64: str,
    mime_type: str = "audio/wav"
):
    """
    Process audio input and get voice response
    
    For REST API usage when WebSocket is not available.
    Audio should be base64 encoded.
    """
    from agents.voice_agent import get_voice_agent
    import base64
    
    voice_agent = get_voice_agent()
    
    try:
        audio_data = base64.b64decode(audio_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio: {e}")
    
    result = await voice_agent.process_audio(session_id, audio_data, mime_type)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
    
    return result


@app.get("/api/voice/session/{session_id}")
async def get_voice_session(session_id: str):
    """Get voice session info and state"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "channel": session.get("channel"),
        "mood": session.get("mood"),
        "language": session.get("language"),
        "cart_items": len(session.get("cart", [])),
        "message_count": len(session.get("conversation_history", []))
    }


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "Something went wrong. Please try again."
        }
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  🚀 Agentic AI Retail System - API Server")
    print("=" * 60)
    print("\n📡 API Documentation: http://localhost:8000/docs")
    print("📡 Health Check: http://localhost:8000/")
    print("\n🤖 Agents Loaded:")
    print("   • Orchestrator (Master)")
    print("   • Recommendation Agent")
    print("   • Inventory Agent")
    print("   • Payment Agent")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
