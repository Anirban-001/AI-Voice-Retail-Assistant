"""
Recommendation Agent for Agentic AI Retail System
Handles: Product recommendations, Mood-based personalization, Product search
"""
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


class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent
    
    Responsibilities:
    1. Provide personalized product recommendations
    2. Mood-based product suggestions
    3. Product search and discovery
    4. Cross-selling and upselling
    5. Category browsing assistance
    """
    
    def __init__(self):
        super().__init__(AgentType.RECOMMENDATION)
    
    def _get_system_prompt(self) -> str:
        return """You are a Product Recommendation Specialist for an AI-powered retail assistant.

Your expertise:
1. Understanding customer preferences from conversation
2. Making mood-appropriate product suggestions
3. Explaining product benefits clearly
4. Cross-selling complementary items
5. Helping customers discover new products

Mood-based recommendations:
- HAPPY customers: Suggest premium, exciting, or new arrivals. Be enthusiastic!
- NEUTRAL customers: Focus on bestsellers, practical choices, good value
- FRUSTRATED customers: Suggest simple, reliable, well-reviewed items. Be empathetic.
- CONFUSED customers: Recommend starter kits, bundles, or top-rated basics. Guide them step by step.

Always:
- Be helpful, not pushy
- Explain WHY you're recommending something
- Offer alternatives at different price points
- Mention if items are on sale or low in stock
- Ask clarifying questions if needed

Format product recommendations clearly:
📦 Product Name - $XX.XX
   Brief description and why it fits their needs"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process recommendation requests"""
        
        user_message = message.payload.get("user_message", "")
        entities = message.payload.get("entities", {})
        intent = message.intent
        context = message.context
        
        self.log_action(f"Processing: {intent}", {"entities": entities})
        
        # Determine action based on intent
        if intent in ["search_product", "browse_products"]:
            return await self.handle_search(user_message, entities, context)
        elif intent == "get_recommendation":
            return await self.handle_recommendation(user_message, entities, context)
        else:
            return await self.handle_general(user_message, context)
    
    async def handle_search(
        self, 
        user_message: str, 
        entities: Dict, 
        context: Dict
    ) -> AgentResponse:
        """Handle product search requests"""
        
        # Extract search parameters
        query = entities.get("product_name", "")
        category = entities.get("category")
        
        if not query and not category:
            # Extract from user message
            query = user_message
        
        self.log_action("Searching products", {"query": query, "category": category})
        
        # Search database
        if category:
            products = self.db.get_products_by_category(category)
        elif query:
            products = self.db.search_products(query)
        else:
            products = self.db.get_all_products(limit=10)
        
        if not products:
            response_text = self.generate_response(
                user_message,
                context,
                additional_context=f"No products found for query: {query or category}. Suggest alternatives or ask for clarification."
            )
            return AgentResponse(
                success=True,
                message=response_text,
                data={"products": [], "search_query": query},
                suggested_actions=["try_different_search", "browse_categories"]
            )
        
        # Format products for display
        products_formatted = self._format_products(products[:5])
        
        response_text = self.generate_response(
            user_message,
            context,
            additional_context=f"Found {len(products)} products:\n{products_formatted}\n\nPresent these naturally and offer to help further."
        )
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "products": products[:5],
                "total_found": len(products),
                "search_query": query
            },
            suggested_actions=["view_details", "add_to_cart", "see_more"]
        )
    
    async def handle_recommendation(
        self,
        user_message: str,
        entities: Dict,
        context: Dict
    ) -> AgentResponse:
        """Handle personalized recommendation requests"""
        
        mood = context.get("mood", "neutral")
        preferences = entities.copy()
        
        # Add any mentioned categories/products as preferences
        if "category" in entities:
            preferences["interested_in"] = entities["category"]
        
        self.log_action("Generating recommendations", {"mood": mood, "preferences": preferences})
        
        # Get available products
        products = self.db.get_all_products(limit=20)
        
        if not products:
            return AgentResponse(
                success=False,
                message="I'm having trouble accessing our product catalog right now. Please try again in a moment.",
                data={"error": "no_products"}
            )
        
        # Get AI recommendations
        recommendations = self.llm.get_product_recommendations(
            user_preferences=preferences,
            mood=mood,
            available_products=products,
            limit=5
        )
        
        # Match recommendations to actual products
        recommended_products = []
        for rec in recommendations:
            # Handle case where rec might be a string or malformed
            if not isinstance(rec, dict):
                self.logger.warning(f"Skipping invalid recommendation: {rec}")
                continue
            
            product_id = rec.get("product_id")
            if not product_id:
                continue
                
            product = next((p for p in products if str(p.get("id")) == str(product_id)), None)
            if product:
                # Create a copy to avoid modifying original
                product_copy = product.copy()
                product_copy["recommendation_reason"] = rec.get("reason", "")
                product_copy["mood_match"] = rec.get("mood_match", "")
                recommended_products.append(product_copy)
        
        if not recommended_products:
            # Fallback to top products
            recommended_products = products[:3]
        
        products_formatted = self._format_recommendations(recommended_products)
        
        response_text = self.generate_response(
            user_message,
            context,
            additional_context=f"""Mood: {mood}

Recommendations:
{products_formatted}

Present these with enthusiasm appropriate to mood.
After presenting, ask engaging follow-up questions like:
- Would you like more details on any of these?
- Should I check availability on something specific?
- Would you like me to add any to your cart?
- Want to see more options in a specific category?

Keep the conversation flowing naturally!"""
        )
        
        # Ensure there's a follow-up question
        if "?" not in response_text[-100:]:
            response_text += "\n\n💬 Would you like more details on any of these, or shall I check availability?"
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "recommendations": recommended_products,
                "mood": mood,
                "personalized": True,
                "continue_conversation": True
            },
            suggested_actions=["view_details", "add_to_cart", "check_availability", "different_recommendations"],
            next_agent=AgentType.INVENTORY  # Suggest checking stock next
        )
    
    async def handle_general(self, user_message: str, context: Dict) -> AgentResponse:
        """Handle general browsing/discovery requests"""
        
        # Get categories
        categories = self.db.get_categories()
        
        # Get featured/popular products
        products = self.db.get_all_products(limit=6)
        
        categories_text = ", ".join(categories) if categories else "various categories"
        products_formatted = self._format_products(products[:3])
        
        response_text = self.generate_response(
            user_message,
            context,
            additional_context=f"""Available categories: {categories_text}

Featured products:
{products_formatted}

Help the customer explore our catalog based on their interests."""
        )
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "categories": categories,
                "featured_products": products[:3]
            },
            suggested_actions=["browse_category", "search", "get_recommendations"]
        )
    
    def _format_products(self, products: List[Dict]) -> str:
        """Format products for display in prompts"""
        formatted = []
        for p in products:
            price = p.get("price", 0)
            formatted.append(
                f"📦 {p.get('name', 'Unknown')} - ${price:.2f}\n"
                f"   Category: {p.get('category', 'N/A')}\n"
                f"   {p.get('description', '')[:100]}"
            )
        return "\n\n".join(formatted)
    
    def _format_recommendations(self, products: List[Dict]) -> str:
        """Format recommendations with reasons"""
        formatted = []
        for p in products:
            price = p.get("price", 0)
            reason = p.get("recommendation_reason", "Great choice!")
            formatted.append(
                f"⭐ {p.get('name', 'Unknown')} - ${price:.2f}\n"
                f"   {reason}\n"
                f"   {p.get('description', '')[:80]}"
            )
        return "\n\n".join(formatted)


# Create and register the agent
recommendation_agent = RecommendationAgent()
AgentRegistry.register(recommendation_agent)
