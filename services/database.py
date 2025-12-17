"""
Supabase Database Service for Agentic AI Retail System
Handles all database operations for products, inventory, orders, and sessions
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = None

def get_supabase() -> Client:
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


class DatabaseService:
    """Service for all database operations"""
    
    # =========================================================================
    # PRODUCT OPERATIONS
    # =========================================================================
    
    @staticmethod
    def get_all_products(limit: int = 50) -> List[Dict]:
        """Get all products from catalog"""
        try:
            db = get_supabase()
            response = db.table("products").select("*").limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Dict]:
        """Get single product by ID"""
        try:
            db = get_supabase()
            response = db.table("products").select("*").eq("id", product_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    @staticmethod
    def search_products(query: str, category: Optional[str] = None) -> List[Dict]:
        """Search products by name or description"""
        try:
            db = get_supabase()
            # Use ilike for case-insensitive search
            q = db.table("products").select("*").ilike("name", f"%{query}%")
            if category:
                q = q.eq("category", category)
            response = q.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    @staticmethod
    def get_products_by_category(category: str) -> List[Dict]:
        """Get products by category"""
        try:
            db = get_supabase()
            response = db.table("products").select("*").eq("category", category).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching category {category}: {e}")
            return []
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get all unique product categories"""
        try:
            db = get_supabase()
            response = db.table("products").select("category").execute()
            categories = list(set([p["category"] for p in response.data if p.get("category")]))
            return sorted(categories)
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    # =========================================================================
    # INVENTORY OPERATIONS
    # =========================================================================
    
    @staticmethod
    def get_inventory(product_id: str) -> Optional[Dict]:
        """Get inventory for a product"""
        try:
            db = get_supabase()
            response = db.table("inventory").select("*").eq("product_id", product_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching inventory for {product_id}: {e}")
            return None
    
    @staticmethod
    def check_stock(product_id: str) -> Dict:
        """Check if product is in stock and quantity available"""
        try:
            inventory = DatabaseService.get_inventory(product_id)
            if not inventory:
                return {"in_stock": False, "quantity": 0, "status": "not_found"}
            
            quantity = inventory.get("quantity", 0)
            return {
                "in_stock": quantity > 0,
                "quantity": quantity,
                "status": "available" if quantity > 0 else "out_of_stock",
                "low_stock": quantity > 0 and quantity <= 5
            }
        except Exception as e:
            logger.error(f"Error checking stock: {e}")
            return {"in_stock": False, "quantity": 0, "status": "error"}
    
    @staticmethod
    def update_inventory(product_id: str, quantity_change: int) -> bool:
        """Update inventory quantity (negative for reduction)"""
        try:
            db = get_supabase()
            # Get current inventory
            current = DatabaseService.get_inventory(product_id)
            if not current:
                return False
            
            new_quantity = max(0, current.get("quantity", 0) + quantity_change)
            
            db.table("inventory").update({
                "quantity": new_quantity,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("product_id", product_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating inventory: {e}")
            return False
    
    @staticmethod
    def get_low_stock_products(threshold: int = 5) -> List[Dict]:
        """Get products with low stock"""
        try:
            db = get_supabase()
            response = db.table("inventory").select("*, products(*)").lte("quantity", threshold).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching low stock: {e}")
            return []
    
    # =========================================================================
    # ORDER OPERATIONS
    # =========================================================================
    
    @staticmethod
    def create_order(
        user_id: str,
        items: List[Dict],
        total_amount: float,
        payment_method: str,
        shipping_address: Optional[Dict] = None
    ) -> Optional[str]:
        """Create a new order"""
        try:
            db = get_supabase()
            order_data = {
                "user_id": user_id,
                "items": items,
                "total_amount": total_amount,
                "payment_method": payment_method,
                "shipping_address": shipping_address,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = db.table("orders").insert(order_data).execute()
            
            if response.data:
                order_id = response.data[0]["id"]
                logger.info(f"Created order {order_id}")
                return order_id
            return None
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    @staticmethod
    def get_order(order_id: str) -> Optional[Dict]:
        """Get order by ID"""
        try:
            db = get_supabase()
            response = db.table("orders").select("*").eq("id", order_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return None
    
    @staticmethod
    def update_order_status(order_id: str, status: str) -> bool:
        """Update order status"""
        try:
            db = get_supabase()
            db.table("orders").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", order_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    @staticmethod
    def get_user_orders(user_id: str) -> List[Dict]:
        """Get all orders for a user"""
        try:
            db = get_supabase()
            response = db.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching user orders: {e}")
            return []
    
    # =========================================================================
    # SESSION/CONTEXT OPERATIONS
    # =========================================================================
    
    @staticmethod
    def create_session(user_id: str, channel: str = "web") -> Optional[str]:
        """Create a new user session"""
        try:
            db = get_supabase()
            session_data = {
                "user_id": user_id,
                "channel": channel,
                "language": "en",
                "mood": "neutral",
                "context": {},
                "conversation_history": [],
                "cart": [],
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            response = db.table("sessions").insert(session_data).execute()
            
            if response.data:
                return response.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        try:
            db = get_supabase()
            response = db.table("sessions").select("*").eq("id", session_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {e}")
            return None
    
    @staticmethod
    def update_session(session_id: str, updates: Dict) -> bool:
        """Update session data"""
        try:
            db = get_supabase()
            updates["last_activity"] = datetime.utcnow().isoformat()
            db.table("sessions").update(updates).eq("id", session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    @staticmethod
    def add_to_conversation_history(session_id: str, role: str, content: str) -> bool:
        """Add message to conversation history"""
        try:
            session = DatabaseService.get_session(session_id)
            if not session:
                return False
            
            history = session.get("conversation_history", [])
            history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last N messages
            from config import MAX_CONVERSATION_HISTORY
            history = history[-MAX_CONVERSATION_HISTORY:]
            
            return DatabaseService.update_session(session_id, {"conversation_history": history})
        except Exception as e:
            logger.error(f"Error adding to conversation: {e}")
            return False
    
    # =========================================================================
    # CART OPERATIONS
    # =========================================================================
    
    @staticmethod
    def add_to_cart(session_id: str, product_id: str, quantity: int = 1) -> bool:
        """Add item to cart"""
        try:
            session = DatabaseService.get_session(session_id)
            if not session:
                return False
            
            cart = session.get("cart", [])
            
            # Check if product already in cart
            for item in cart:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    return DatabaseService.update_session(session_id, {"cart": cart})
            
            # Add new item
            product = DatabaseService.get_product_by_id(product_id)
            if not product:
                return False
            
            cart.append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })
            
            return DatabaseService.update_session(session_id, {"cart": cart})
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False
    
    @staticmethod
    def get_cart(session_id: str) -> List[Dict]:
        """Get cart items"""
        try:
            session = DatabaseService.get_session(session_id)
            return session.get("cart", []) if session else []
        except Exception as e:
            logger.error(f"Error getting cart: {e}")
            return []
    
    @staticmethod
    def clear_cart(session_id: str) -> bool:
        """Clear cart"""
        return DatabaseService.update_session(session_id, {"cart": []})
    
    # =========================================================================
    # ANALYTICS/STATS
    # =========================================================================
    
    @staticmethod
    def get_stats() -> Dict:
        """Get system statistics"""
        try:
            db = get_supabase()
            
            products_count = len(db.table("products").select("id").execute().data)
            orders_count = len(db.table("orders").select("id").execute().data)
            sessions_count = len(db.table("sessions").select("id").execute().data)
            
            return {
                "total_products": products_count,
                "total_orders": orders_count,
                "active_sessions": sessions_count
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_products": 0, "total_orders": 0, "active_sessions": 0}
