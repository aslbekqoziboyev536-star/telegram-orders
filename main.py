import telebot
import logging
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import BOT_TOKEN
from handlers import register_handlers

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Render uchun health-check HTTP server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # HTTP loglarini o'chir

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logging.info(f"✅ Health-check server {port}-portda ishga tushdi")
    server.serve_forever()

def main():
    # 1. Botni tekshirish
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    # 2. Render uchun HTTP serverini fon threadida ishga tushirish
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 3. Botni yaratish va handlerlarni ro'yxatdan o'tkazish
    bot = telebot.TeleBot(BOT_TOKEN)
    register_handlers(bot)

    logging.info("🚀 Bot Polling rejimida ishga tushmoqda...")

    # 4. Webhookni tozalash va Pollingni boshlash (409 xatosi uchun retry)
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                logging.warning("⚠️ 409 Conflict: boshqa bot instance ishlayapti. 15 soniyadan keyin qayta uriniladi...")
                time.sleep(15)
            else:
                logging.error(f"❌ Telegram API xatoligi: {e}")
                time.sleep(5)
        except Exception as e:
            logging.error(f"❌ Bot ishlashida xatolik: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

