import telebot
import logging
from config import BOT_TOKEN
from handlers import register_handlers

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # 1. Botni tekshirish
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    # 2. Botni yaratish va handlerlarni ro'yxatdan o'tkazish
    bot = telebot.TeleBot(BOT_TOKEN)
    register_handlers(bot)

    logging.info("🚀 Bot Polling rejimida ishga tushmoqda...")
    
    # 3. Webhookni tozalash va Pollingni boshlash
    try:
        bot.remove_webhook()
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logging.error(f"❌ Bot ishlashida xatolik: {e}")

if __name__ == "__main__":
    main()
