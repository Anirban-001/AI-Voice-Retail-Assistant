"""
Master Orchestrator Agent for Agentic AI Retail System
Handles: Language detection, Mood analysis, Intent classification, Task routing
"""
import uuid
import logging
from typing import Dict, List, Optional, Any

from agents.base_agent import (
    BaseAgent, 
    AgentType, 
    AgentMessage, 
    AgentResponse,
    AgentRegistry
)
from services.llm_service import LLMService
from services.database import DatabaseService
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, MOOD_CATEGORIES


class OrchestratorAgent(BaseAgent):
    """
    Master Orchestrator Agent
    
    Responsibilities:
    1. Greet users in their language
    2. Detect and track user mood
    3. Classify user intent
    4. Route tasks to appropriate worker agents
    5. Maintain conversation context
    6. Handle edge cases and fallbacks
    """
    
    def __init__(self):
        super().__init__(AgentType.ORCHESTRATOR)
        self.supported_languages = SUPPORTED_LANGUAGES
        self.mood_categories = MOOD_CATEGORIES
    
    def _get_system_prompt(self) -> str:
        return """You are the Master Orchestrator for an AI-powered retail assistant. Your role is to:

1. GREET users warmly in their detected language
2. UNDERSTAND their needs through natural conversation
3. ANALYZE their mood and adapt your tone accordingly
4. ROUTE their requests to specialized agents when needed
5. MAINTAIN context throughout the conversation
6. HANDLE edge cases gracefully

Personality:
- Friendly and professional
- Emotionally intelligent - adapt to user's mood
- Helpful without being pushy
- Clear and concise in communication

When routing to agents:
- Recommendation Agent: product suggestions, browsing, personalization
- Inventory Agent: stock checks, availability, product details
- Payment Agent: checkout, payments, order completion

Always acknowledge the user's emotion and respond appropriately:
- Happy users: Be enthusiastic, suggest premium options
- Neutral users: Be professional, focus on efficiency
- Frustrated users: Be empathetic, prioritize quick resolution
- Confused users: Be patient, offer step-by-step guidance"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process incoming message and orchestrate response"""
        
        user_input = message.payload.get("user_message", "")
        session_id = message.context.get("session_id")
        
        self.log_action("Processing message", {"input": user_input[:100]})
        
        # Step 1: Detect language (if not already set)
        language = message.context.get("language")
        if not language or language == "auto":
            language_result = await self.detect_language(user_input)
            language = language_result.get("language_code", DEFAULT_LANGUAGE)
            message.context["language"] = language
            message.context["language_name"] = language_result.get("language_name", "English")
        
        # Step 2: Analyze mood
        mood_result = await self.analyze_mood(
            user_input, 
            message.context.get("conversation_history", [])
        )
        message.context["mood"] = mood_result.get("mood", "neutral")
        message.context["mood_confidence"] = mood_result.get("confidence", 0.5)
        message.context["suggested_tone"] = mood_result.get("suggested_tone", "professional")
        
        # Step 3: Classify intent with conversation context
        # Get recent conversation for context
        history = message.context.get("conversation_history", [])
        context_summary = ""
        if history:
            recent = history[-4:]  # Last 2 exchanges
            context_summary = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')[:100]}"
                for msg in recent
            ])
        
        intent_result = await self.classify_intent(user_input, context_summary)
        intent = intent_result.get("intent", "general_question")
        target_agent = intent_result.get("target_agent", "orchestrator")
        entities = intent_result.get("entities", {})
        
        # Handle confirm_action by looking at context to determine target
        if intent == "confirm_action":
            # Look at recent history to determine what action to confirm
            if context_summary:
                context_lower = context_summary.lower()
                if any(word in context_lower for word in ["checkout", "payment", "purchase", "proceed", "cart", "buy"]):
                    intent = "checkout"
                    target_agent = "payment"
                elif any(word in context_lower for word in ["add to cart", "add it", "take it"]):
                    intent = "add_to_cart"
                    target_agent = "payment"
                elif any(word in context_lower for word in ["stock", "available", "in stock"]):
                    intent = "add_to_cart"
                    target_agent = "payment"
        
        self.log_action("Analysis complete", {
            "language": language,
            "mood": mood_result.get("mood"),
            "intent": intent,
            "target_agent": target_agent
        })
        
        # Step 4: Route to appropriate agent or handle directly
        if target_agent == "orchestrator" or intent in ["greeting", "farewell", "general_question"]:
            # Handle directly
            response_text = await self.handle_direct(user_input, message.context, intent)
            
            return AgentResponse(
                success=True,
                message=response_text,
                data={
                    "language": language,
                    "mood": mood_result,
                    "intent": intent_result,
                    "handled_by": "orchestrator"
                }
            )
        else:
            # Route to worker agent
            return await self.route_to_agent(
                target_agent=target_agent,
                intent=intent,
                entities=entities,
                user_message=user_input,
                context=message.context
            )
    
    async def detect_language(self, text: str) -> Dict:
        """Detect the language of user input"""
        return self.llm.detect_language(text)
    
    async def analyze_mood(self, text: str, history: List[Dict] = None) -> Dict:
        """Analyze user's mood/sentiment"""
        return self.llm.analyze_mood(text, history)
    
    async def classify_intent(self, text: str, context_summary: str = None) -> Dict:
        """Classify user's intent with conversation context"""
        return self.llm.classify_intent(text, conversation_context=context_summary)
    
    async def handle_direct(self, user_message: str, context: Dict, intent: str) -> str:
        """Handle messages that don't need routing"""
        
        if intent == "greeting":
            return await self.generate_greeting(context)
        elif intent == "farewell":
            return await self.generate_farewell(context)
        else:
            return self.generate_response(user_message, context)
    
    async def generate_greeting(self, context: Dict) -> str:
        """Generate a personalized greeting"""
        
        language = context.get("language", "en")
        mood = context.get("mood", "neutral")
        
        greetings = {
            "en": "Hello! Welcome to our store. How can I help you today?",
            "es": "¡Hola! Bienvenido a nuestra tienda. ¿Cómo puedo ayudarte hoy?",
            "fr": "Bonjour! Bienvenue dans notre magasin. Comment puis-je vous aider?",
            "de": "Hallo! Willkommen in unserem Geschäft. Wie kann ich Ihnen helfen?",
            "hi": "नमस्ते! हमारी दुकान में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूं?",
        }
        
        base_greeting = greetings.get(language, greetings["en"])
        
        # Adjust based on mood
        if mood == "frustrated" or mood == "angry":
            return f"{base_greeting} I'm here to help make things easier for you."
        elif mood == "happy":
            return f"{base_greeting} 😊 Great to have you here!"
        
        return base_greeting
    
    async def generate_farewell(self, context: Dict) -> str:
        """Generate a personalized farewell"""
        
        language = context.get("language", "en")
        cart = context.get("cart", [])
        
        farewells = {
            "en": "Thank you for visiting! Have a wonderful day!",
            "es": "¡Gracias por visitarnos! ¡Que tengas un día maravilloso!",
            "fr": "Merci de votre visite! Passez une excellente journée!",
            "de": "Danke für Ihren Besuch! Haben Sie einen wunderschönen Tag!",
        }
        
        base_farewell = farewells.get(language, farewells["en"])
        
        if cart:
            return f"{base_farewell} Don't forget - you have {len(cart)} items in your cart! Feel free to return anytime to complete your purchase."
        
        return f"{base_farewell} Feel free to come back anytime - I'm always here to help! 👋"
    
    async def route_to_agent(
        self,
        target_agent: str,
        intent: str,
        entities: Dict,
        user_message: str,
        context: Dict
    ) -> AgentResponse:
        """Route request to appropriate worker agent"""
        
        # Map string to AgentType
        agent_map = {
            "recommendation": AgentType.RECOMMENDATION,
            "inventory": AgentType.INVENTORY,
            "payment": AgentType.PAYMENT,
        }
        
        agent_type = agent_map.get(target_agent)
        
        if not agent_type:
            return AgentResponse(
                success=False,
                message="I'm not sure how to help with that. Could you rephrase your request?",
                data={"error": f"Unknown agent: {target_agent}"}
            )
        
        # Create handoff message
        handoff = self.create_handoff_message(
            to_agent=agent_type,
            intent=intent,
            payload={
                "user_message": user_message,
                "entities": entities
            },
            context=context
        )
        
        self.log_action(f"Routing to {target_agent}", {"intent": intent})
        
        # Route through registry
        return await AgentRegistry.route_message(handoff)
    
    async def handle_edge_case(self, error_type: str, context: Dict) -> AgentResponse:
        """Handle edge cases and errors gracefully"""
        
        error_responses = {
            "agent_timeout": "I apologize for the delay. Let me try that again for you.",
            "agent_error": "I encountered an issue processing your request. Let me try a different approach.",
            "unknown_intent": "I'm not quite sure what you're looking for. Could you tell me more?",
            "out_of_scope": "I'm specialized in retail assistance. For other queries, I'd recommend contacting our general support."
        }
        
        message = error_responses.get(error_type, "Something went wrong. Please try again.")
        
        return AgentResponse(
            success=False,
            message=message,
            data={"error_type": error_type},
            suggested_actions=["retry", "rephrase", "contact_support"]
        )


# Create and register the orchestrator
orchestrator = OrchestratorAgent()
AgentRegistry.register(orchestrator)
