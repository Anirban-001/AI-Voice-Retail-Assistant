"""
Minimal Test API for Frontend Voice Testing
Runs without full dependencies
Includes dynamic product search simulation
"""
import uuid
import re
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

app = FastAPI(title="Test API for Voice Frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
sessions = {}

# Simulated product database with more variety
PRODUCT_DATABASE = {
    "laptop": [
        {
            "id": "laptop-1",
            "name": "MacBook Pro 16\"",
            "price": 2499.99,
            "category": "Laptops",
            "description": "Powerful laptop with M3 Pro chip, 16GB RAM, 512GB SSD",
            "stock": 5,
            "in_stock": True
        },
        {
            "id": "laptop-2",
            "name": "Dell XPS 15",
            "price": 1899.99,
            "category": "Laptops",
            "description": "Premium Windows laptop with Intel i7, 16GB RAM",
            "stock": 8,
            "in_stock": True
        },
        {
            "id": "laptop-3",
            "name": "ThinkPad X1 Carbon",
            "price": 1599.99,
            "category": "Laptops",
            "description": "Business laptop with 14\" display, great battery life",
            "stock": 12,
            "in_stock": True
        }
    ],
    "phone": [
        {
            "id": "phone-1",
            "name": "iPhone 15 Pro",
            "price": 999.99,
            "category": "Phones",
            "description": "Latest iPhone with A17 Pro chip, titanium design",
            "stock": 10,
            "in_stock": True
        },
        {
            "id": "phone-2",
            "name": "Samsung Galaxy S24",
            "price": 899.99,
            "category": "Phones",
            "description": "Flagship Android phone with AI features",
            "stock": 15,
            "in_stock": True
        },
        {
            "id": "phone-3",
            "name": "Google Pixel 8 Pro",
            "price": 799.99,
            "category": "Phones",
            "description": "Best camera phone with Google AI",
            "stock": 7,
            "in_stock": True
        }
    ],
    "headphones": [
        {
            "id": "audio-1",
            "name": "AirPods Pro",
            "price": 249.99,
            "category": "Audio",
            "description": "Premium wireless earbuds with ANC",
            "stock": 15,
            "in_stock": True
        },
        {
            "id": "audio-2",
            "name": "Sony WH-1000XM5",
            "price": 399.99,
            "category": "Audio",
            "description": "Industry-leading noise canceling headphones",
            "stock": 10,
            "in_stock": True
        },
        {
            "id": "audio-3",
            "name": "Bose QuietComfort Ultra",
            "price": 429.99,
            "category": "Audio",
            "description": "Premium headphones with spatial audio",
            "stock": 6,
            "in_stock": True
        }
    ],
    "tablet": [
        {
            "id": "tablet-1",
            "name": "iPad Pro 12.9\"",
            "price": 1099.99,
            "category": "Tablets",
            "description": "Powerful tablet with M2 chip, great for creativity",
            "stock": 8,
            "in_stock": True
        },
        {
            "id": "tablet-2",
            "name": "Samsung Galaxy Tab S9",
            "price": 799.99,
            "category": "Tablets",
            "description": "Android tablet with S Pen included",
            "stock": 12,
            "in_stock": True
        }
    ],
    "watch": [
        {
            "id": "watch-1",
            "name": "Apple Watch Series 9",
            "price": 429.99,
            "category": "Wearables",
            "description": "Advanced health and fitness tracking",
            "stock": 20,
            "in_stock": True
        },
        {
            "id": "watch-2",
            "name": "Samsung Galaxy Watch 6",
            "price": 349.99,
            "category": "Wearables",
            "description": "Stylish smartwatch with health features",
            "stock": 15,
            "in_stock": True
        }
    ]
}

def search_products(query: str) -> List[Dict]:
    """
    Simulate web search for products based on query
    This mimics what a worker agent would do
    """
    query_lower = query.lower()
    results = []
    
    # Extract product categories from query
    for category, products in PRODUCT_DATABASE.items():
        if category in query_lower or any(word in query_lower for word in category.split()):
            results.extend(products)
    
    # If no category match, search in product names and descriptions
    if not results:
        for products in PRODUCT_DATABASE.values():
            for product in products:
                if any(word in product['name'].lower() or word in product['description'].lower() 
                      for word in query_lower.split()):
                    if product not in results:
                        results.append(product)
    
    # If still nothing, return popular items
    if not results:
        results = PRODUCT_DATABASE['laptop'][:2] + PRODUCT_DATABASE['phone'][:2]
    
    return results[:6]  # Limit to 6 products

class SessionRequest(BaseModel):
    user_id: Optional[str] = None
    channel: str = "web"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    channel: str = "web"
    language: Optional[str] = None

class VoiceTextRequest(BaseModel):
    session_id: str
    transcription: str
    language: Optional[str] = None

class CartRequest(BaseModel):
    session_id: str
    product_id: str
    quantity: int = 1

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Test API for Voice Frontend",
        "version": "1.0.0-test",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/session")
def create_session(request: SessionRequest):
    session_id = str(uuid.uuid4())
    user_id = request.user_id or f"guest_{session_id[:8]}"
    
    sessions[session_id] = {
        "id": session_id,
        "user_id": user_id,
        "channel": request.channel,
        "cart": [],
        "conversation_history": [],
        "mood": "neutral",
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": user_id,
        "channel": request.channel
    }


def detect_intent(message: str) -> dict:
    """
    Analyzes user message to determine intent: conversation, search, action, or question.
    Returns intent type and confidence.
    """
    message_lower = message.lower()
    
    # Greetings and casual conversation (no product search needed)
    greeting_patterns = ["hello", "hi", "hey", "good morning", "good afternoon", "how are you", "what's up"]
    if any(pattern in message_lower for pattern in greeting_patterns):
        return {"intent": "greeting", "confidence": 0.95, "needs_search": False}
    
    # Action words (definite product search needed)
    action_patterns = ["find", "search", "show me", "looking for", "need", "want to buy", "buy", "purchase", "get me"]
    if any(pattern in message_lower for pattern in action_patterns):
        return {"intent": "search_action", "confidence": 0.9, "needs_search": True}
    
    # Cart actions
    cart_patterns = ["add to cart", "add it", "buy this", "checkout", "my cart", "remove from cart"]
    if any(pattern in message_lower for pattern in cart_patterns):
        return {"intent": "cart_action", "confidence": 0.9, "needs_search": False}
    
    # Questions about products (may need search)
    question_patterns = ["what", "which", "how much", "price", "cost", "available", "in stock", "tell me about"]
    has_question = any(pattern in message_lower for pattern in question_patterns)
    has_product_word = any(word in message_lower for word in ["laptop", "phone", "headphones", "tablet", "watch"])
    
    if has_question and has_product_word:
        return {"intent": "product_question", "confidence": 0.85, "needs_search": True}
    
    # Just mentioning products (conversation, no search)
    if has_product_word and not has_question:
        return {"intent": "conversation", "confidence": 0.7, "needs_search": False}
    
    # General help
    if "help" in message_lower or "can you" in message_lower:
        return {"intent": "help", "confidence": 0.9, "needs_search": False}
    
    # Default: conversational
    return {"intent": "conversation", "confidence": 0.6, "needs_search": False}


def search_products(query: str) -> List[Dict]:
    """
    Simulates web search for products based on query.
    Returns relevant products from PRODUCT_DATABASE.
    """
    query_lower = query.lower()
    results = []
    
    # Category matching
    for category, products_list in PRODUCT_DATABASE.items():
        if category in query_lower:
            results.extend(products_list)
    
    # Keyword matching for specific products
    keywords = {
        "macbook": "laptop",
        "iphone": "phone",
        "samsung": "phone",
        "airpods": "headphones",
        "ipad": "tablet",
        "apple watch": "watch"
    }
    
    for keyword, category in keywords.items():
        if keyword in query_lower and category in PRODUCT_DATABASE:
            if category not in [r.get("category", "") for r in results]:
                results.extend(PRODUCT_DATABASE[category])
    
    return results[:10]  # Limit results


@app.post("/api/chat")
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "user_id": request.user_id or "guest",
            "channel": request.channel,
            "cart": [],
            "conversation_history": [],
            "mood": "neutral"
        }
    
    # Detect user intent first
    message = request.message
    message_lower = message.lower()
    intent_data = detect_intent(message)
    
    # Only search for products if intent requires it
    products_found = []
    if intent_data["needs_search"]:
        products_found = search_products(message_lower)
    
    # Handle based on detected intent
    if intent_data["intent"] == "greeting":
        response = "Hello! I'm your AI shopping assistant. I can help you find products, check prices, manage your cart, and answer questions. What are you looking for today?"
        recommendations = products_found[:3] if products_found else []
    
    elif intent_data["intent"] == "help":
        response = "I can help you with:\n• Finding and searching products\n• Checking prices and availability\n• Adding items to your cart\n• Answering product questions\n\nJust ask me naturally - for example: 'Find me a laptop under $1000' or 'Show me the latest phones'."
        recommendations = []
    
    elif intent_data["intent"] == "conversation":
        # Just conversational, no product search
        if "laptop" in message_lower or "computer" in message_lower:
            response = "Laptops are great! Are you looking to buy one, or just chatting about them? Let me know if you'd like to see our selection!"
        elif "phone" in message_lower:
            response = "Phones have come a long way! If you're interested in buying one, I can show you our latest models."
        elif "thanks" in message_lower or "thank you" in message_lower:
            response = "You're welcome! Let me know if you need anything else."
        else:
            response = f"I understand you said: '{message}'. Is there something specific you'd like me to help you find or do?"
        recommendations = []
    
    elif intent_data["intent"] == "search_action" or intent_data["intent"] == "product_question":
        # User wants to search/see products
        if products_found:
            # Show search results
            if "laptop" in message_lower or "computer" in message_lower:
                product_names = ", ".join([p['name'] for p in products_found[:3]])
                response = f"I found {len(products_found)} laptops for you. Top picks: {product_names}. Check the details below!"
            elif "phone" in message_lower:
                product_names = ", ".join([p['name'] for p in products_found[:3]])
                response = f"Great! I found {len(products_found)} phones: {product_names}. All are in stock."
            elif "headphone" in message_lower or "audio" in message_lower:
                product_names = ", ".join([p['name'] for p in products_found[:2]])
                response = f"For audio, I found: {product_names}. Excellent sound quality!"
            else:
                product_names = ", ".join([p['name'] for p in products_found[:3]])
                response = f"I searched and found {len(products_found)} products: {product_names}. Check them out below!"
            recommendations = products_found
        else:
            # No results but user wants to search
            response = "I'd love to help you find that! Could you be more specific? For example, 'Show me laptops under $1000' or 'Find wireless headphones'."
            recommendations = []
    
    elif intent_data["intent"] == "cart_action":
        if "add" in message_lower or "buy" in message_lower:
            if products_found and len(products_found) == 1:
                product = products_found[0]
                response = f"Perfect! Click the Add to Cart button to add {product['name']} (${product['price']:.2f})."
                recommendations = products_found
            else:
                response = "Which product would you like to add? You can click 'Add to Cart' on any product card."
                recommendations = []
        elif "cart" in message_lower:
            cart = sessions[session_id].get("cart", [])
            if cart:
                total = sum(item['price'] * item['quantity'] for item in cart)
                response = f"Your cart has {len(cart)} items totaling ${total:.2f}. Ready to checkout?"
            else:
                response = "Your cart is currently empty. Let me help you find something!"
            recommendations = []
        else:
            response = "I can help with your cart! Say 'add to cart' to add items, or 'show my cart' to see what's in it."
            recommendations = []
    
    else:
        # Fallback for unclear intent
        response = f"I'm not sure if you want me to search for something or just chatting. If you're looking for a product, try saying 'Find me...' or 'Show me...'. Otherwise, I'm happy to chat!"
        recommendations = []
    
    return {
        "success": True,
        "message": response,
        "session_id": session_id,
        "data": {
            "recommendations": recommendations,
            "mood": {"mood": "helpful", "confidence": 0.85, "suggested_tone": "friendly"},
            "intent": intent_data["intent"],
            "search_query": message_lower if intent_data["needs_search"] else None,
            "results_count": len(recommendations)
        },
        "suggested_actions": ["view_products", "add_to_cart", "refine_search"] if recommendations else ["ask_question"],
        "context": {
            "language": "en",
            "mood": "helpful",
            "intent": intent_data["intent"],
            "handled_by": "intelligent_agent"
        }
    }

@app.post("/api/voice/text")
def voice_text(request: VoiceTextRequest):
    session_id = request.session_id
    
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "user_id": "voice_user",
            "channel": "voice",
            "cart": [],
            "conversation_history": [],
            "mood": "neutral"
        }
    
    # Detect intent from voice transcription
    message = request.transcription
    message_lower = message.lower()
    intent_data = detect_intent(message)
    
    # Only search if intent requires it
    products_found = []
    if intent_data["needs_search"]:
        products_found = search_products(message_lower)
    
    # Handle based on intent
    if intent_data["intent"] == "greeting":
        response = "Hello! I'm your voice shopping assistant. Just tell me what you're looking for and I'll find it for you!"
    
    elif intent_data["intent"] == "help":
        response = "I can search for products, check prices, add items to your cart, or answer questions. Just speak naturally!"
    
    elif intent_data["intent"] == "conversation":
        # Just chatting, no search needed
        if "laptop" in message_lower or "phone" in message_lower or "headphone" in message_lower:
            response = "Interesting! Are you looking to buy one, or just chatting? Let me know if you want to see our selection!"
        elif "thanks" in message_lower or "thank you" in message_lower:
            response = "You're very welcome! Anything else I can help with?"
        else:
            response = "I heard you! Is there a product you'd like me to search for?"
    
    elif intent_data["intent"] == "search_action" or intent_data["intent"] == "product_question":
        # User wants product search
        if products_found:
            if "laptop" in message_lower:
                product_names = " or ".join([p['name'] for p in products_found[:2]])
                response = f"I found {len(products_found)} laptops. Top options are {product_names}. Want more details?"
            elif "phone" in message_lower:
                product_names = " and ".join([p['name'] for p in products_found[:2]])
                response = f"Great! I found {product_names}. All in stock. Which one interests you?"
            elif "headphone" in message_lower or "audio" in message_lower:
                product_names = " and ".join([p['name'] for p in products_found[:2]])
                response = f"For audio, I have {product_names}. Excellent sound quality!"
            else:
                product_names = ", ".join([p['name'] for p in products_found[:3]])
                response = f"Found {len(products_found)} products: {product_names}. Check the screen!"
        else:
            response = "I'd love to help! Can you be more specific about what you're looking for?"
    
    elif intent_data["intent"] == "cart_action":
        if "add" in message_lower or "buy" in message_lower:
            if products_found and len(products_found) == 1:
                product = products_found[0]
                response = f"Perfect! Adding {product['name']} at ${product['price']:.2f} to your cart."
            else:
                response = "Which product would you like? Click Add to Cart on the one you want!"
        elif "cart" in message_lower:
            cart = sessions[session_id].get("cart", [])
            if cart:
                total = sum(item['price'] * item['quantity'] for item in cart)
                response = f"Your cart has {len(cart)} items totaling ${total:.2f}. Ready to checkout?"
            else:
                response = "Your cart is empty. Let me help you find something!"
        else:
            response = "I can help with your cart! Just say what you'd like to do."
    
    else:
        # Unclear intent
        response = f"I heard '{request.transcription}'. Are you looking to search for a product? Just say 'find' or 'show me' followed by what you want!"
    
    return {
        "success": True,
        "message": response,
        "session_id": session_id,
        "data": {
            "recommendations": products_found,
            "mood": {"mood": "friendly", "confidence": 0.9},
            "search_query": message,
            "results_count": len(products_found)
        },
        "suggested_actions": ["view_results", "add_to_cart"],
        "context": {
            "mood": "friendly",
            "language": "en",
            "handled_by": "voice_search_agent"
        }
    }
    session_id = request.session_id
    
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "user_id": "voice_user",
            "channel": "voice",
            "cart": [],
            "conversation_history": [],
            "mood": "neutral"
        }
    
    # Enhanced voice processing with natural conversation
    message = request.transcription.lower()
    
    # Greetings
    if any(word in message for word in ["hello", "hi", "hey"]):
        response = "Hello! I'm your voice shopping assistant. You can ask me about laptops, phones, audio equipment, or I can help you add items to your cart. What would you like to explore?"
    
    # Product searches
    elif "laptop" in message or "computer" in message:
        response = "Great! For laptops, I highly recommend the MacBook Pro sixteen inch. It's priced at twenty-four ninety-nine and offers exceptional performance. It's perfect for creative work and has five units in stock. Would you like to add it to your cart?"
    
    elif "phone" in message or "iphone" in message or "mobile" in message:
        response = "Perfect! The iPhone fifteen Pro is our top smartphone at nine ninety-nine. It features the latest processor, pro camera system, and comes in titanium. We have ten units available. Interested?"
    
    elif "airpod" in message or "earbuds" in message or "audio" in message:
        response = "For audio, the AirPods Pro are excellent at two forty-nine ninety-nine. They have active noise cancellation, spatial audio, and incredible sound quality. We have fifteen in stock. Should I add them to your cart?"
    
    # Shopping actions
    elif any(phrase in message for phrase in ["add", "buy", "purchase", "get", "want"]):
        if "laptop" in message or "macbook" in message:
            response = "Perfect! I'm adding the MacBook Pro to your cart right now. It's twenty-four ninety-nine. Would you like to continue shopping or check out?"
        elif "phone" in message or "iphone" in message:
            response = "Great choice! Adding the iPhone fifteen Pro to your cart at nine ninety-nine. Anything else you need?"
        elif "airpod" in message or "audio" in message:
            response = "Excellent! The AirPods Pro are being added to your cart at two forty-nine. Can I help you with anything else?"
        else:
            response = "I'd be happy to add that to your cart! Which product would you like - laptop, phone, or audio equipment?"
    
    # Cart questions
    elif "cart" in message:
        cart = sessions[session_id].get("cart", [])
        if cart:
            total = sum(item['price'] * item['quantity'] for item in cart)
            response = f"Your cart has {len(cart)} items totaling ${total:.2f}. Ready to checkout?"
        else:
            response = "Your cart is empty. Let me help you find something great!"
    
    # Stock/availability
    elif any(word in message for word in ["stock", "available", "have"]):
        response = "Everything is in stock! We have MacBook Pros, iPhone fifteen Pros, and AirPods Pro all ready for immediate delivery. What catches your interest?"
    
    # Price questions
    elif any(word in message for word in ["price", "cost", "much"]):
        response = "Our prices are: MacBook Pro at twenty-four ninety-nine, iPhone fifteen Pro at nine ninety-nine, and AirPods Pro at two forty-nine. All competitively priced! What fits your budget?"
    
    # Help
    elif "help" in message:
        response = "I can help you browse products, check prices and stock, add items to your cart, or answer questions. Just speak naturally and tell me what you need!"
    
    # Browsing
    elif any(word in message for word in ["show", "see", "browse", "what"]):
        response = "I'll show you our top products! We have premium laptops, latest smartphones, and high-quality audio gear. What type of product interests you most?"
    
    # Default conversational response
    else:
        response = f"I heard you say {request.transcription}. I'm here to help with product recommendations, checking stock, or adding items to your cart. What would you like to know?"
    
    return {
        "success": True,
        "message": response,
        "session_id": session_id,
        "data": {
            "mood": {"mood": "friendly", "confidence": 0.9}
        },
        "suggested_actions": ["continue_browsing", "add_to_cart"],
        "context": {
            "mood": "friendly",
            "language": "en"
        }
    }

@app.get("/api/products")
def get_products(category: Optional[str] = None, search: Optional[str] = None, limit: int = 20):
    # Build search query from parameters
    query = search or ""
    if category:
        query = f"{category} {query}".strip()
    
    # Use dynamic search
    if query:
        filtered = search_products(query)
    else:
        # Return all products from all categories
        filtered = []
        for cat_products in PRODUCT_DATABASE.values():
            filtered.extend(cat_products)
    
    return {
        "success": True,
        "products": filtered[:limit],
        "count": len(filtered)
    }

@app.post("/api/cart/add")
def add_to_cart(request: CartRequest):
    session_id = request.session_id
    
    if session_id not in sessions:
        return {"success": False, "error": "Session not found"}
    
    # Search across all categories to find the product
    product = None
    for cat_products in PRODUCT_DATABASE.values():
        product = next((p for p in cat_products if p["id"] == request.product_id), None)
        if product:
            break
    
    if not product:
        return {"success": False, "error": "Product not found"}
    
    cart = sessions[session_id]["cart"]
    
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
    
    return {
        "success": True,
        "cart": cart,
        "item_count": sum(i["quantity"] for i in cart),
        "total": sum(i["price"] * i["quantity"] for i in cart)
    }

@app.get("/api/cart/{session_id}")
def get_cart(session_id: str):
    if session_id not in sessions:
        return {"success": False, "error": "Session not found"}
    
    cart = sessions[session_id]["cart"]
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

@app.get("/api/stats")
def get_stats():
    # Count all products across all categories
    total_products = sum(len(prods) for prods in PRODUCT_DATABASE.values())
    
    return {
        "success": True,
        "stats": {
            "total_products": total_products,
            "active_sessions": len(sessions),
            "total_sales": 0,
            "products_sold": 0,
            "avg_order_value": 0
        }
    }

@app.get("/api/categories")
def get_categories():
    # Get categories from PRODUCT_DATABASE keys
    categories = list(PRODUCT_DATABASE.keys())
    return {
        "success": True,
        "categories": categories
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  🧪 TEST API SERVER - Voice Frontend Testing")
    print("=" * 60)
    print("\n📡 API: http://localhost:8000")
    print("📡 Docs: http://localhost:8000/docs")
    print("\n🎤 Voice endpoint ready: POST /api/voice/text")
    print("💬 Chat endpoint ready: POST /api/chat")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
