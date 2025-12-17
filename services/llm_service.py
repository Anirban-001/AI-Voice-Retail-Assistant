"""
Groq LLM Service for Agentic AI Retail System
Provides LLM capabilities for all agents using Groq's fast inference
"""
import logging
from typing import Dict, List, Optional, Any
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODELS, AGENT_MODELS

logger = logging.getLogger(__name__)

# Initialize Groq client
client: Groq = None

def get_groq_client() -> Groq:
    """Get or create Groq client"""
    global client
    if client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY must be set in .env")
        client = Groq(api_key=GROQ_API_KEY)
    return client


class LLMService:
    """Service for LLM operations using Groq"""
    
    @staticmethod
    def chat(
        messages: List[Dict[str, str]],
        model: str = None,
        agent_type: str = "orchestrator",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False
    ) -> Optional[str]:
        """
        Send chat completion request to Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Specific model to use (overrides agent_type default)
            agent_type: Type of agent (orchestrator, recommendation, inventory, payment)
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            json_mode: If True, expect JSON response
        
        Returns:
            Response text or None on error
        """
        try:
            groq = get_groq_client()
            
            # Select model
            if model:
                selected_model = model
            else:
                selected_model = AGENT_MODELS.get(agent_type, GROQ_MODELS["balanced"])
            
            # Build request
            request_params = {
                "model": selected_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            response = groq.chat.completions.create(**request_params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    @staticmethod
    def detect_language(text: str) -> Dict[str, Any]:
        """
        Detect language of input text
        
        Returns:
            Dict with 'language_code', 'language_name', 'confidence'
        """
        messages = [
            {
                "role": "system",
                "content": """You are a language detection system. Analyze the input text and respond with JSON:
{
    "language_code": "en",
    "language_name": "English", 
    "confidence": 0.95
}
Use ISO 639-1 codes (en, es, fr, de, hi, zh, ar, etc.)"""
            },
            {
                "role": "user",
                "content": f"Detect language: {text}"
            }
        ]
        
        response = LLMService.chat(
            messages=messages,
            agent_type="orchestrator",
            temperature=0.1,
            max_tokens=100,
            json_mode=True
        )
        
        if response:
            import json
            try:
                return json.loads(response)
            except:
                pass
        
        return {"language_code": "en", "language_name": "English", "confidence": 0.5}
    
    @staticmethod
    def analyze_mood(text: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Analyze mood/sentiment of user message
        
        Returns:
            Dict with 'mood', 'confidence', 'indicators'
        """
        history_context = ""
        if conversation_history:
            history_context = "Recent conversation:\n" + "\n".join([
                f"{m['role']}: {m['content']}" for m in conversation_history[-5:]
            ])
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a mood/sentiment analyzer for customer service. Analyze the user's emotional state.

{history_context}

Respond with JSON:
{{
    "mood": "happy|neutral|confused|frustrated|angry",
    "confidence": 0.0-1.0,
    "indicators": ["list", "of", "mood", "indicators"],
    "suggested_tone": "enthusiastic|professional|helpful|empathetic|calm_supportive"
}}"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
        
        response = LLMService.chat(
            messages=messages,
            agent_type="orchestrator",
            temperature=0.3,
            max_tokens=200,
            json_mode=True
        )
        
        if response:
            import json
            try:
                return json.loads(response)
            except:
                pass
        
        return {
            "mood": "neutral",
            "confidence": 0.5,
            "indicators": [],
            "suggested_tone": "professional"
        }
    
    @staticmethod
    def classify_intent(text: str, available_intents: List[str] = None, conversation_context: str = None) -> Dict[str, Any]:
        """
        Classify user intent for routing to appropriate agent
        
        Returns:
            Dict with 'intent', 'confidence', 'entities'
        """
        if not available_intents:
            available_intents = [
                "browse_products",
                "search_product",
                "get_recommendation",
                "check_availability",
                "check_stock",
                "add_to_cart",
                "view_cart",
                "checkout",
                "make_payment",
                "confirm_action",
                "track_order",
                "general_question",
                "greeting",
                "farewell"
            ]
        
        context_hint = ""
        if conversation_context:
            context_hint = f"\n\nRecent conversation context:\n{conversation_context}\n\nUse this context to understand confirmations like 'yes', 'proceed', 'do it', etc."
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an intent classifier for a retail AI system. Classify the user's intent.

Available intents: {', '.join(available_intents)}

IMPORTANT RULES:
1. If user says "yes", "proceed", "go ahead", "confirm", "do it" - look at context to determine the action
2. If context mentions checkout/payment/purchase → intent is "checkout" or "make_payment"
3. If context mentions adding to cart → intent is "add_to_cart"
4. If context mentions product selection → intent is "add_to_cart"
5. Simple greetings like "hi", "hello" → "greeting"
6. But "yes" or "proceed" after a product offer → NOT a greeting!
{context_hint}

Respond with JSON:
{{
    "intent": "one_of_available_intents",
    "confidence": 0.0-1.0,
    "entities": {{
        "product_name": "if mentioned",
        "category": "if mentioned",
        "quantity": "if mentioned",
        "price_range": "if mentioned"
    }},
    "target_agent": "recommendation|inventory|payment|orchestrator"
}}"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
        
        response = LLMService.chat(
            messages=messages,
            agent_type="orchestrator",
            temperature=0.2,
            max_tokens=300,
            json_mode=True
        )
        
        if response:
            import json
            try:
                return json.loads(response)
            except:
                pass
        
        return {
            "intent": "general_question",
            "confidence": 0.5,
            "entities": {},
            "target_agent": "orchestrator"
        }
    
    @staticmethod
    def generate_response(
        user_message: str,
        context: Dict,
        agent_type: str,
        system_prompt: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate a contextual response for the user
        
        Args:
            user_message: The user's message
            context: Additional context (mood, language, cart, etc.)
            agent_type: Which agent is responding
            system_prompt: Agent-specific system prompt
            conversation_history: Previous messages
        
        Returns:
            Generated response text
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add context as system message
        context_str = f"""
Current Context:
- User Mood: {context.get('mood', 'neutral')}
- Language: {context.get('language', 'en')}
- Cart Items: {len(context.get('cart', []))}
- Response Tone: {context.get('suggested_tone', 'professional')}
"""
        messages.append({"role": "system", "content": context_str})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = LLMService.chat(
            messages=messages,
            agent_type=agent_type,
            temperature=0.7,
            max_tokens=500
        )
        
        return response or "I apologize, but I'm having trouble processing your request. Please try again."
    
    @staticmethod
    def get_product_recommendations(
        user_preferences: Dict,
        mood: str,
        available_products: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get AI-powered product recommendations based on mood and preferences
        
        Returns:
            List of recommended product IDs with reasoning
        """
        products_summary = "\n".join([
            f"- ID: {p['id']}, Name: {p['name']}, Category: {p['category']}, Price: ${p['price']}"
            for p in available_products[:20]  # Limit for token efficiency
        ])
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a retail recommendation engine. Based on the user's mood and preferences, recommend products.

Available Products:
{products_summary}

User Mood: {mood}
User Preferences: {user_preferences}

Respond with JSON array of recommendations:
[
    {{
        "product_id": "id",
        "reason": "why this product fits",
        "mood_match": "how it relates to their mood"
    }}
]

Limit to {limit} recommendations. Consider mood:
- happy: suggest premium/exciting items
- neutral: suggest popular/practical items
- frustrated: suggest simple/reliable items with good reviews
- confused: suggest bestsellers or starter items"""
            },
            {
                "role": "user",
                "content": f"Recommend products for a {mood} customer interested in: {user_preferences}"
            }
        ]
        
        response = LLMService.chat(
            messages=messages,
            agent_type="recommendation",
            temperature=0.6,
            max_tokens=500,
            json_mode=True
        )
        
        if response:
            import json
            try:
                parsed = json.loads(response)
                # Ensure we have a list of dicts
                if isinstance(parsed, list):
                    # Filter to only valid recommendation dicts
                    valid_recs = []
                    for item in parsed:
                        if isinstance(item, dict) and "product_id" in item:
                            valid_recs.append(item)
                    return valid_recs
                elif isinstance(parsed, dict) and "recommendations" in parsed:
                    return parsed["recommendations"]
            except json.JSONDecodeError:
                logger.error(f"Failed to parse recommendations JSON: {response[:200]}")
        
        return []
