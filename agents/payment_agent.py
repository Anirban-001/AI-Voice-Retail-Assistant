"""
Payment Agent for Agentic AI Retail System
Handles: Checkout, Payment processing, Order completion, Error recovery
"""
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from agents.base_agent import (
    BaseAgent, 
    AgentType, 
    AgentMessage, 
    AgentResponse,
    AgentRegistry
)
from services.database import DatabaseService
from config import CURRENCY_SYMBOL, TAX_RATE, PAYMENT_METHODS


class PaymentAgent(BaseAgent):
    """
    Payment Agent
    
    Responsibilities:
    1. Process checkout flow
    2. Handle payment processing (mock for MVP)
    3. Create orders
    4. Handle payment failures gracefully
    5. Provide order confirmations
    """
    
    def __init__(self):
        super().__init__(AgentType.PAYMENT)
    
    def _get_system_prompt(self) -> str:
        return f"""You are a Payment & Checkout Specialist for an AI-powered retail assistant.

Your expertise:
1. Guiding customers through checkout smoothly
2. Processing payments securely
3. Handling payment issues with empathy
4. Providing clear order confirmations
5. Answering payment-related questions

Checkout flow:
1. Review cart items and totals
2. Confirm shipping details
3. Present payment options
4. Process payment
5. Confirm order

Payment methods supported: {', '.join(PAYMENT_METHODS)}
Tax rate: {TAX_RATE * 100}%
Currency: USD ({CURRENCY_SYMBOL})

Key behaviors:
- Always confirm cart contents before payment
- Be reassuring about security
- Handle errors gracefully - never blame the customer
- Provide clear totals including tax
- Give order confirmation with reference number

Error handling:
- Payment declined: "I'm sorry, the payment didn't go through. Would you like to try a different payment method?"
- Cart expired: "Your cart has timed out. Let me help you rebuild it quickly."
- Technical error: "We're experiencing a temporary issue. Your cart is saved - please try again in a moment."

Format for order summary:
🛒 ORDER SUMMARY
━━━━━━━━━━━━━━━━
[Items]
━━━━━━━━━━━━━━━━
Subtotal: $XX.XX
Tax: $X.XX
━━━━━━━━━━━━━━━━
TOTAL: $XX.XX"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process payment/checkout requests"""
        
        user_message = message.payload.get("user_message", "")
        entities = message.payload.get("entities", {})
        intent = message.intent
        context = message.context
        
        self.log_action(f"Processing: {intent}", {"entities": entities})
        
        # Determine action based on intent
        if intent in ["checkout", "make_payment", "pay"]:
            return await self.handle_checkout(user_message, context)
        elif intent in ["view_cart", "cart"]:
            return await self.handle_view_cart(context)
        elif intent == "add_to_cart":
            return await self.handle_add_to_cart(entities, context)
        else:
            return await self.handle_general(user_message, context)
    
    async def handle_view_cart(self, context: Dict) -> AgentResponse:
        """Show current cart contents"""
        
        session_id = context.get("session_id")
        cart = self.db.get_cart(session_id) if session_id else context.get("cart", [])
        
        if not cart:
            response_text = self.generate_response(
                "show cart",
                context,
                additional_context="Cart is empty. Encourage browsing or asking for recommendations."
            )
            return AgentResponse(
                success=True,
                message=response_text,
                data={"cart": [], "total": 0},
                suggested_actions=["browse_products", "get_recommendations"],
                next_agent=AgentType.RECOMMENDATION
            )
        
        # Calculate totals
        cart_summary = self._calculate_cart_totals(cart)
        
        additional_context = f"""
Cart Contents:
{cart_summary['items_text']}

Subtotal: {CURRENCY_SYMBOL}{cart_summary['subtotal']:.2f}
Tax ({TAX_RATE * 100}%): {CURRENCY_SYMBOL}{cart_summary['tax']:.2f}
Total: {CURRENCY_SYMBOL}{cart_summary['total']:.2f}

Items in cart: {cart_summary['item_count']}
"""
        
        response_text = self.generate_response(
            "show cart",
            context,
            additional_context=additional_context
        )
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={
                "cart": cart,
                "subtotal": cart_summary["subtotal"],
                "tax": cart_summary["tax"],
                "total": cart_summary["total"]
            },
            suggested_actions=["proceed_to_checkout", "continue_shopping", "remove_item"]
        )
    
    async def handle_add_to_cart(self, entities: Dict, context: Dict) -> AgentResponse:
        """Add item to cart"""
        
        product_id = entities.get("product_id")
        quantity = entities.get("quantity", 1)
        session_id = context.get("session_id")
        
        if not product_id:
            return AgentResponse(
                success=False,
                message="I need to know which product you'd like to add. Could you specify?",
                data={},
                suggested_actions=["specify_product", "browse_products"]
            )
        
        # Check stock first
        stock = self.db.check_stock(product_id)
        if not stock.get("in_stock"):
            return AgentResponse(
                success=False,
                message="I'm sorry, this item is currently out of stock.",
                data={"stock": stock},
                suggested_actions=["view_alternatives", "notify_when_available"],
                next_agent=AgentType.INVENTORY
            )
        
        if stock.get("quantity", 0) < quantity:
            return AgentResponse(
                success=False,
                message=f"We only have {stock.get('quantity')} units available.",
                data={"stock": stock},
                suggested_actions=["adjust_quantity", "view_alternatives"]
            )
        
        # Add to cart
        if session_id:
            success = self.db.add_to_cart(session_id, product_id, quantity)
        else:
            success = True  # In-memory cart handling
        
        product = self.db.get_product_by_id(product_id)
        
        response_text = self.generate_response(
            "added to cart",
            context,
            additional_context=f"Added {quantity}x {product.get('name', 'item')} to cart. Ask if they want to continue shopping or checkout."
        )
        
        return AgentResponse(
            success=success,
            message=response_text,
            data={
                "product": product,
                "quantity": quantity,
                "action": "added_to_cart"
            },
            suggested_actions=["continue_shopping", "view_cart", "checkout"]
        )
    
    async def handle_checkout(self, user_message: str, context: Dict) -> AgentResponse:
        """Handle checkout process"""
        
        session_id = context.get("session_id")
        cart = self.db.get_cart(session_id) if session_id else context.get("cart", [])
        
        if not cart:
            response_text = "Your cart is empty! Would you like to browse our products first?"
            return AgentResponse(
                success=False,
                message=response_text,
                data={"error": "empty_cart"},
                suggested_actions=["browse_products", "get_recommendations"],
                next_agent=AgentType.RECOMMENDATION
            )
        
        # Calculate totals
        cart_summary = self._calculate_cart_totals(cart)
        
        # Verify stock for all items
        stock_issues = await self._verify_cart_stock(cart)
        
        if stock_issues:
            issues_text = "\n".join([
                f"- {item['name']}: {item['issue']}" 
                for item in stock_issues
            ])
            response_text = self.generate_response(
                user_message,
                context,
                additional_context=f"Stock issues found:\n{issues_text}\n\nHelp customer resolve these issues."
            )
            return AgentResponse(
                success=False,
                message=response_text,
                data={"stock_issues": stock_issues},
                suggested_actions=["update_quantities", "remove_items", "view_alternatives"]
            )
        
        # Process mock payment
        payment_result = await self._process_payment(
            total=cart_summary["total"],
            payment_method="credit_card",  # Default for MVP
            context=context
        )
        
        if payment_result["success"]:
            # Create order
            order_id = await self._create_order(cart, cart_summary, context)
            
            # Clear cart
            if session_id:
                self.db.clear_cart(session_id)
            
            additional_context = f"""
ORDER CONFIRMED! 🎉

Order Number: {order_id}
Items: {cart_summary['item_count']}
Total: {CURRENCY_SYMBOL}{cart_summary['total']:.2f}

Provide a warm confirmation with these details:
1. Thank the customer enthusiastically
2. Give them their order number
3. Mention expected delivery (2-3 business days)
4. Offer to help with something else - ask if they want to:
   - Browse more products
   - Track their order
   - Get recommendations for complementary items
   
Keep the conversation going naturally - don't just end abruptly!
"""
            response_text = self.generate_response(
                "order complete",
                context,
                additional_context=additional_context
            )
            
            # Add a follow-up prompt if not present
            if "?" not in response_text[-50:]:
                response_text += "\n\n🛍️ Is there anything else I can help you with? Would you like to browse more products or get recommendations?"
            
            return AgentResponse(
                success=True,
                message=response_text,
                data={
                    "order_id": order_id,
                    "total": cart_summary["total"],
                    "items": cart,
                    "status": "confirmed",
                    "continue_conversation": True
                },
                suggested_actions=["browse_more", "track_order", "get_recommendations", "view_order"]
            )
        else:
            # Payment failed
            return await self._handle_payment_failure(
                payment_result,
                cart_summary,
                context
            )
    
    async def handle_general(self, user_message: str, context: Dict) -> AgentResponse:
        """Handle general payment questions"""
        
        additional_context = f"""
Available payment methods: {', '.join(PAYMENT_METHODS)}
Tax rate: {TAX_RATE * 100}%

Answer the customer's payment-related question.
"""
        response_text = self.generate_response(
            user_message,
            context,
            additional_context=additional_context
        )
        
        return AgentResponse(
            success=True,
            message=response_text,
            data={},
            suggested_actions=["view_cart", "checkout", "browse_products"]
        )
    
    def _calculate_cart_totals(self, cart: List[Dict]) -> Dict:
        """Calculate cart totals"""
        
        subtotal = sum(
            item.get("price", 0) * item.get("quantity", 1)
            for item in cart
        )
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        
        items_text = "\n".join([
            f"• {item.get('name', 'Item')} x{item.get('quantity', 1)} - {CURRENCY_SYMBOL}{item.get('price', 0) * item.get('quantity', 1):.2f}"
            for item in cart
        ])
        
        return {
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "item_count": sum(item.get("quantity", 1) for item in cart),
            "items_text": items_text
        }
    
    async def _verify_cart_stock(self, cart: List[Dict]) -> List[Dict]:
        """Verify stock availability for all cart items"""
        
        issues = []
        for item in cart:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            stock = self.db.check_stock(product_id)
            
            if not stock.get("in_stock"):
                issues.append({
                    "product_id": product_id,
                    "name": item.get("name", "Item"),
                    "issue": "Out of stock",
                    "available": 0
                })
            elif stock.get("quantity", 0) < quantity:
                issues.append({
                    "product_id": product_id,
                    "name": item.get("name", "Item"),
                    "issue": f"Only {stock.get('quantity')} available",
                    "available": stock.get("quantity", 0)
                })
        
        return issues
    
    async def _process_payment(
        self,
        total: float,
        payment_method: str,
        context: Dict
    ) -> Dict:
        """Process payment (mock for MVP)"""
        
        self.log_action("Processing payment", {
            "total": total,
            "method": payment_method
        })
        
        # Mock payment - always succeeds for MVP
        # In production, integrate with Stripe, PayPal, etc.
        
        # Simulate occasional failures for testing edge cases
        import random
        if random.random() < 0.05:  # 5% failure rate
            return {
                "success": False,
                "error_code": "CARD_DECLINED",
                "error_message": "Card was declined"
            }
        
        return {
            "success": True,
            "transaction_id": str(uuid.uuid4())[:8].upper(),
            "amount": total,
            "method": payment_method
        }
    
    async def _create_order(
        self,
        cart: List[Dict],
        cart_summary: Dict,
        context: Dict
    ) -> str:
        """Create order in database"""
        
        user_id = context.get("user_id", "guest")
        
        order_id = self.db.create_order(
            user_id=user_id,
            items=cart,
            total_amount=cart_summary["total"],
            payment_method="credit_card"
        )
        
        if not order_id:
            # Generate fallback order ID
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        self.log_action("Order created", {"order_id": order_id})
        
        # Update inventory
        for item in cart:
            self.db.update_inventory(
                item.get("product_id"),
                -item.get("quantity", 1)
            )
        
        return order_id
    
    async def _handle_payment_failure(
        self,
        payment_result: Dict,
        cart_summary: Dict,
        context: Dict
    ) -> AgentResponse:
        """Handle payment failures gracefully"""
        
        error_code = payment_result.get("error_code", "UNKNOWN")
        
        error_messages = {
            "CARD_DECLINED": "The card was declined. Please try a different card or payment method.",
            "INSUFFICIENT_FUNDS": "There were insufficient funds. Would you like to try a different payment method?",
            "EXPIRED_CARD": "The card appears to be expired. Please update your card details.",
            "NETWORK_ERROR": "We experienced a network issue. Please try again.",
            "UNKNOWN": "Something went wrong with the payment. Please try again."
        }
        
        error_message = error_messages.get(error_code, error_messages["UNKNOWN"])
        
        response_text = self.generate_response(
            "payment failed",
            context,
            additional_context=f"Payment failed: {error_message}\nHelp customer resolve this empathetically. Cart total: {CURRENCY_SYMBOL}{cart_summary['total']:.2f}"
        )
        
        return AgentResponse(
            success=False,
            message=response_text,
            data={
                "error_code": error_code,
                "cart_preserved": True,
                "total": cart_summary["total"]
            },
            suggested_actions=["try_different_payment", "try_again", "contact_support"]
        )


# Create and register the agent
payment_agent = PaymentAgent()
AgentRegistry.register(payment_agent)
