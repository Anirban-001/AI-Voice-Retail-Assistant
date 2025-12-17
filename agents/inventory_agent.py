"""
Inventory Agent for Agentic AI Retail System
Handles: Stock checks, Availability, Product details, Alternatives
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
from services.database import DatabaseService


class InventoryAgent(BaseAgent):
    """
    Inventory Agent
    
    Responsibilities:
    1. Check product availability/stock levels
    2. Provide detailed product information
    3. Find alternatives for out-of-stock items
    4. Handle stock-related queries
    5. Alert on low stock situations
    """
    
    def __init__(self):
        super().__init__(AgentType.INVENTORY)
    
    def _get_system_prompt(self) -> str:
        return """You are an Inventory Specialist for an AI-powered retail assistant.

Your expertise:
1. Real-time stock availability checking
2. Providing accurate product details
3. Suggesting alternatives when items are unavailable
4. Managing customer expectations about stock
5. Helping customers find what they need

Key behaviors:
- Always check actual stock before confirming availability
- If out of stock: immediately suggest similar alternatives
- If low stock: create urgency but don't pressure
- Provide accurate delivery/availability estimates
- Be transparent about stock limitations

Stock status responses:
- IN STOCK: "Great news! This item is available and ready to ship."
- LOW STOCK: "This item is in stock but selling fast - only X left!"
- OUT OF STOCK: "I'm sorry, this item is currently out of stock. Let me find you some alternatives..."
- COMING SOON: "This item is temporarily unavailable but expected back on [date]."

Always format stock info clearly:
✅ In Stock (X available)
⚠️ Low Stock (Only X left)
❌ Out of Stock
🔄 Checking availability..."""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process inventory requests"""
        
        user_message = message.payload.get("user_message", "")
        entities = message.payload.get("entities", {})
        intent = message.intent
        context = message.context
        
        self.log_action(f"Processing: {intent}", {"entities": entities})
        
        # Determine action based on intent
        if intent in ["check_stock", "check_availability"]:
            return await self.check_stock(user_message, entities, context)
        else:
            return await self.handle_general(user_message, entities, context)
    
    async def check_stock(
        self,
        user_message: str,
        entities: Dict,
        context: Dict
    ) -> AgentResponse:
        """Check stock for a specific product"""
        
        product_name = entities.get("product_name", "")
        
        # Search for the product
        if product_name:
            products = self.db.search_products(product_name)
        else:
            # Try to find product from message
            products = self.db.search_products(user_message)
        
        if not products:
            response_text = self.generate_response(
                user_message,
                context,
                additional_context="Could not find the requested product. Ask for clarification or suggest browsing categories."
            )
            return AgentResponse(
                success=True,
                message=response_text,
                data={"found": False},
                suggested_actions=["search_again", "browse_categories"]
            )
        
        # Check stock for found product(s)
        product = products[0]
        product_id = product.get("id")
        
        stock_info = self.db.check_stock(product_id)
        
        self.log_action("Stock check result", {
            "product": product.get("name"),
            "stock": stock_info
        })
        
        # Build response based on stock status
        stock_status = self._format_stock_status(stock_info)
        
        additional_context = f"""
Product: {product.get('name')}
Price: ${product.get('price', 0):.2f}
Category: {product.get('category', 'N/A')}

Stock Status: {stock_status}
Quantity Available: {stock_info.get('quantity', 0)}

"""
        
        # If out of stock, find alternatives
        alternatives = []
        if not stock_info.get("in_stock"):
            alternatives = await self._find_alternatives(product)
            if alternatives:
                alt_text = "\n".join([
                    f"- {a.get('name')} (${a.get('price', 0):.2f})"
                    for a in alternatives[:3]
                ])
                additional_context += f"\nAlternative products available:\n{alt_text}"
                additional_context += "\n\nOffer to show more details on alternatives or help them find something else."
        else:
            additional_context += "\n\nAsk if they'd like to add this to their cart, see more details, or continue browsing."
        
        response_text = self.generate_response(
            user_message,
            context,
            additional_context=additional_context
        )
        
        # Ensure follow-up for conversation continuity
        if "?" not in response_text[-80:]:
            if stock_info.get("in_stock"):
                response_text += "\n\n🛒 Would you like to add this to your cart, or do you have any questions about it?"
            else:
                response_text += "\n\n🔍 Would you like me to show you some alternatives, or search for something else?"
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "product": product,
                "stock": stock_info,
                "alternatives": alternatives,
                "continue_conversation": True
            },
            suggested_actions=self._get_suggested_actions(stock_info),
            next_agent=AgentType.PAYMENT if stock_info.get("in_stock") else None
        )
    
    async def handle_general(
        self,
        user_message: str,
        entities: Dict,
        context: Dict
    ) -> AgentResponse:
        """Handle general inventory queries"""
        
        product_name = entities.get("product_name")
        
        if product_name:
            # They're asking about a specific product
            return await self.check_stock(user_message, entities, context)
        
        # General inventory question
        response_text = self.generate_response(
            user_message,
            context,
            additional_context="User is asking about inventory/availability. Ask which product they want to check."
        )
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={},
            suggested_actions=["specify_product", "browse_products"]
        )
    
    async def _find_alternatives(self, product: Dict) -> List[Dict]:
        """Find alternative products in same category"""
        
        category = product.get("category")
        if not category:
            return []
        
        # Get products in same category
        alternatives = self.db.get_products_by_category(category)
        
        # Filter out the original product and out-of-stock items
        original_id = product.get("id")
        valid_alternatives = []
        
        for alt in alternatives:
            if str(alt.get("id")) == str(original_id):
                continue
            
            stock = self.db.check_stock(alt.get("id"))
            if stock.get("in_stock"):
                alt["stock_quantity"] = stock.get("quantity")
                valid_alternatives.append(alt)
        
        # Sort by price similarity
        original_price = product.get("price", 0)
        valid_alternatives.sort(
            key=lambda x: abs(x.get("price", 0) - original_price)
        )
        
        return valid_alternatives[:5]
    
    def _format_stock_status(self, stock_info: Dict) -> str:
        """Format stock status for display"""
        
        if stock_info.get("status") == "not_found":
            return "❓ Product not found in inventory"
        elif stock_info.get("status") == "error":
            return "⚠️ Unable to check stock"
        elif not stock_info.get("in_stock"):
            return "❌ Out of Stock"
        elif stock_info.get("low_stock"):
            qty = stock_info.get("quantity", 0)
            return f"⚠️ Low Stock (Only {qty} left!)"
        else:
            qty = stock_info.get("quantity", 0)
            return f"✅ In Stock ({qty} available)"
    
    def _get_suggested_actions(self, stock_info: Dict) -> List[str]:
        """Get suggested actions based on stock status"""
        
        if not stock_info.get("in_stock"):
            return ["view_alternatives", "notify_when_available", "search_similar"]
        elif stock_info.get("low_stock"):
            return ["add_to_cart_now", "view_details", "continue_shopping"]
        else:
            return ["add_to_cart", "view_details", "continue_shopping"]
    
    async def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve stock for a pending order"""
        # This would implement stock reservation logic
        # For MVP, we just check if enough stock exists
        stock = self.db.check_stock(product_id)
        return stock.get("quantity", 0) >= quantity
    
    async def release_stock(self, product_id: str, quantity: int) -> bool:
        """Release reserved stock (e.g., if payment fails)"""
        # For MVP, this is a placeholder
        return True


# Create and register the agent
inventory_agent = InventoryAgent()
AgentRegistry.register(inventory_agent)
