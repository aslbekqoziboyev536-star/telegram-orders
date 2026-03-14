from pymongo import MongoClient
from config import MONGO_URI
import logging

try:
    client = MongoClient(MONGO_URI)
    db = client["it_services_db"]
    
    products_col = db["services"]
    carts_col = db["carts"]
    orders_col = db["orders"]
    knowledge_col = db["knowledge_base"]
    users_col = db["users"]
    
    # Text index yaratish (qidiruv uchun)
    knowledge_col.create_index([("text", "text")])
    users_col.create_index("user_id", unique=True)
    
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

def add_knowledge(text):
    """Admin tomonidan bilimlar bazasiga ma'lumot qo'shish"""
    try:
        knowledge_col.insert_one({"text": text})
        return True
    except Exception as e:
        print(f"Error adding knowledge: {e}")
        return False

def save_user(user_id, username, full_name):
    """Foydalanuvchini bazaga saqlash (statistik uchun)"""
    try:
        users_col.update_one(
            {"user_id": str(user_id)},
            {"$set": {"username": username, "full_name": full_name}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving user: {e}")

def get_admin_stats():
    """Admin panel uchun statistikani olish"""
    try:
        user_count = users_col.count_documents({})
        total_orders = orders_col.count_documents({})
        new_orders = orders_col.count_documents({"status": "new"})
        confirmed_orders = orders_col.count_documents({"status": "confirmed"})
        canceled_orders = orders_col.count_documents({"status": "canceled"})
        
        return {
            "users": user_count,
            "total": total_orders,
            "new": new_orders,
            "confirmed": confirmed_orders,
            "canceled": canceled_orders
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}

def get_orders_by_status(status):
    """Status bo'yicha buyurtmalarni olish"""
    try:
        return list(orders_col.find({"status": status}))
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

def get_order_by_id(order_id):
    """ID bo'yicha buyurtmani olish"""
    from bson.objectid import ObjectId
    try:
        return orders_col.find_one({"_id": ObjectId(order_id)})
    except Exception as e:
        print(f"Error getting order by id: {e}")
        return None

def update_order_status(order_id, status):
    """Buyurtma statusini o'zgartirish"""
    from bson.objectid import ObjectId
    try:
        orders_col.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}})
        return True
    except Exception as e:
        print(f"Error updating order: {e}")
        return False
