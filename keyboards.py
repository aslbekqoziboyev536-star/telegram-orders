from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_products
import os

# Web App manzili (Buni o'zingiz host qilgan manzilingizga almashtiring)
WEB_APP_URL = "https://your-webapp-link.vercel.app"

def main_menu_kb() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Web App orqali buyurtma berish uchun alohida tugma
    btn_webapp = KeyboardButton(text="✨ Mini App orqali buyurtirish", web_app=WebAppInfo(url=WEB_APP_URL))
    
    # Oddiy Telegram menyusi
    btn_buy = KeyboardButton(text="💻 Oddiy xizmat buyurtirish")
    btn_cart = KeyboardButton(text="📁 Tanlangan xizmatlar")
    btn_info = KeyboardButton(text="ℹ️ Ma'lumot")
    
    kb.add(btn_webapp)
    kb.add(btn_buy)
    kb.add(btn_cart, btn_info)
    
    return kb

def products_menu_kb() -> InlineKeyboardMarkup:
    """Xizmatlar ro'yxati (inline tugmalar)"""
    products = get_products()
    kb = InlineKeyboardMarkup(row_width=1)
    
    for pid, pdata in products.items():
        kb.add(InlineKeyboardButton(text=f"{pdata['name']}", callback_data=f"buy_{pid}"))
        
    return kb

def cart_menu_kb() -> InlineKeyboardMarkup:
    """Tanlangan xizmatlar opsiyalari"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="✅ So'rovni yuborish", callback_data="confirm_order"))
    kb.add(InlineKeyboardButton(text="🗑 Ro'yxatni tozalash", callback_data="clear_cart"))
    return kb

def contact_request_kb() -> ReplyKeyboardMarkup:
    """Telefon raqam so'rash klaviaturasi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_contact = KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
    btn_cancel = KeyboardButton(text="❌ Bekor qilish")
    kb.add(btn_contact)
    kb.add(btn_cancel)
    return kb

def cancel_only_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text="❌ Bekor qilish"))
    return kb
