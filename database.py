from pymongo import MongoClient
from config import MONGO_URI
import logging

try:
    client = MongoClient(MONGO_URI)
    db = client["it_services_db"]
    
    products_col = db["services"]
    carts_col = db["carts"]
    orders_col = db["orders"]
    
    # Initialize basic services if collection is empty
    if products_col.count_documents({}) == 0:
        initial_services = [
            {"_id": "1", "name": "🌐 Web Sayt", "description": "Zamonaviy, tezkor va responsiv web sayt (landing page, korporativ, e-commerce) ishlab chiqish."},
            {"_id": "2", "name": "🤖 Telegram Bot", "description": "Biznes va xizmatlar uchun ko'p funksiyali Telegram botlar yaratish."},
            {"_id": "3", "name": "📱 Mobil Ilova", "description": "Android va iOS platformalari uchun qulay mobil ilovalar yaratish."},
            {"_id": "4", "name": "🎨 Dizayn (UI/UX)", "description": "Foydalanuvchilar orasida mashhur bo'ladigan zamonaviy UI/UX dizayn yaratish."}
        ]
        products_col.insert_many(initial_services)
        logging.info("✅ Initial services loaded into MongoDB.")

except Exception as e:
    logging.error(f"❌ MongoDB aloqasida xatolik: {e}")

def get_products():
    """Fetch all services/products from DB"""
    try:
        products = list(products_col.find({}))
        # Convert list of docs to a dictionary format expected by the bot
        res = {}
        for p in products:
            res[str(p["_id"])] = {
                "name": p["name"],
                "description": p["description"]
            }
        return res
    except Exception as e:
        print(f"Error getting products: {e}")
        return {}

def get_product(product_id):
    """Fetch a single service by ID"""
    try:
        p = products_col.find_one({"_id": str(product_id)})
        if p:
            return {"name": p["name"], "description": p["description"]}
    except Exception as e:
        print(f"Error getting product {product_id}: {e}")
    return None

def add_to_cart(user_id, product_id, quantity=1):
    """Add or increment a service in a user's cart"""
    try:
        product_id = str(product_id)
        user_id = str(user_id)
        
        cart = carts_col.find_one({"user_id": user_id})
        
        if not cart:
            carts_col.insert_one({"user_id": user_id, "items": {product_id: quantity}})
        else:
            items = cart.get("items", {})
            if product_id in items:
                items[product_id] += quantity
            else:
                items[product_id] = quantity
            
            carts_col.update_one({"user_id": user_id}, {"$set": {"items": items}})
    except Exception as e:
        print(f"Error adding to cart: {e}")

def get_cart(user_id):
    """Get the current cart for a user"""
    try:
        cart = carts_col.find_one({"user_id": str(user_id)})
        if cart:
            return cart.get("items", {})
    except Exception as e:
        print(f"Error getting cart: {e}")
    return {}

def clear_cart(user_id):
    """Clear a user's cart"""
    try:
        carts_col.delete_one({"user_id": str(user_id)})
    except Exception as e:
        print(f"Error clearing cart: {e}")

def save_order(user_id, username, user_name, phone, details, items):
    """Save an order directly to MongoDB"""
    try:
        order = {
            "user_id": str(user_id),
            "user_name": user_name,
            "username": username,
            "phone": phone,
            "details": details,
            "items": items,
            "status": "new"
        }
        orders_col.insert_one(order)
        return True
    except Exception as e:
        print(f"Error saving order: {e}")
        return False
