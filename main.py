"""
Main Entry Point for Agentic AI Retail System
"""
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🛒 AGENTIC AI RETAIL SYSTEM                                ║
    ║   ─────────────────────────────────────────────              ║
    ║   Multi-Modal • Mood-Aware • Personalized                    ║
    ║                                                               ║
    ║   Agents:                                                     ║
    ║   🎯 Orchestrator   - Language, Mood, Routing                ║
    ║   📦 Recommendation - Product Suggestions                    ║
    ║   📊 Inventory      - Stock Management                       ║
    ║   💳 Payment        - Checkout & Orders                      ║
    ║   🎤 Voice          - Speech Interface                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_api():
    """Run the FastAPI server"""
    import uvicorn
    from api.app import app
    
    print("\n🚀 Starting API Server...")
    print("📡 API Docs: http://localhost:8000/docs")
    print("📡 Health:   http://localhost:8000/")
    print("🎤 Voice WS: ws://localhost:8000/ws/voice/{session_id}")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_voice():
    """Run the LiveKit voice agent server"""
    from services.voice_service import run_voice_server
    run_voice_server()


async def run_console():
    """Run interactive console mode for testing"""
    from agents import orchestrator, AgentMessage, AgentType
    import uuid
    
    print("\n💬 Interactive Console Mode")
    print("Type your message and press Enter. Type 'quit' to exit.\n")
    
    # Create session context
    context = {
        "session_id": str(uuid.uuid4()),
        "user_id": "console_user",
        "channel": "console",
        "language": "auto",
        "mood": "neutral",
        "cart": [],
        "conversation_history": []
    }
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Add to history
            context["conversation_history"].append({
                "role": "user",
                "content": user_input
            })
            
            # Process through orchestrator
            message = AgentMessage(
                message_id=str(uuid.uuid4()),
                from_agent=AgentType.ORCHESTRATOR,
                to_agent=AgentType.ORCHESTRATOR,
                intent="process_input",
                payload={"user_message": user_input},
                context=context
            )
            
            response = await orchestrator.process(message)
            
            # Update context
            mood_data = response.data.get("mood")
            if mood_data:
                if isinstance(mood_data, dict):
                    context["mood"] = mood_data.get("mood", "neutral")
                else:
                    context["mood"] = mood_data
            if response.data.get("language"):
                context["language"] = response.data["language"]
            
            context["conversation_history"].append({
                "role": "assistant",
                "content": response.message
            })
            
            # Display response
            print(f"\n🤖 Assistant: {response.message}")
            
            # Show debug info
            mood_data = response.data.get("mood")
            if mood_data:
                if isinstance(mood_data, dict):
                    print(f"   📊 Mood: {mood_data.get('mood')} ({mood_data.get('confidence', 0):.0%})")
                else:
                    print(f"   📊 Mood: {mood_data}")
            intent_data = response.data.get("intent")
            if intent_data:
                if isinstance(intent_data, dict):
                    print(f"   🎯 Intent: {intent_data.get('intent')} → {intent_data.get('target_agent')}")
                else:
                    print(f"   🎯 Intent: {intent_data}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    print_banner()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "api":
            run_api()
        elif mode == "console":
            asyncio.run(run_console())
        elif mode == "voice":
            run_voice()
        elif mode == "seed":
            from seed_data import seed_data
            seed_data()
        else:
            print(f"Unknown mode: {mode}")
            print("\nUsage:")
            print("  python main.py api      - Start API server")
            print("  python main.py console  - Interactive console")
            print("  python main.py voice    - Start voice agent server")
            print("  python main.py seed     - Seed demo data")
    else:
        # Default: start API
        run_api()


if __name__ == "__main__":
    main()
