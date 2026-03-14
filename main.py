import os
import telebot
from flask import Flask, request, jsonify, send_file
import logging

from config import BOT_TOKEN, WEBHOOK_URL
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)

# 1. Initialize Bot
if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN is missing in the environment.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
register_handlers(bot)

# 2. Initialize Flask App
app = Flask(__name__)

# --- FLASK ROUTES ---

@app.route('/')
def serve_webapp():
    """Serves the Mini App HTML file"""
    try:
        return send_file('webapp.html')
    except Exception as e:
        return f"Error loading webapp: {e}", 500


@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Receives updates from Telegram and forwards to the Bot"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid data type', 403


@app.route('/setWebhook', methods=['GET', 'POST'])
def set_webhook():
    """Endpoint to setup the webhook with Telegram"""
    if not WEBHOOK_URL:
        return "WEBHOOK_URL is missing in environment variables.", 400
        
    s = bot.remove_webhook()
    # The webhook URL is the base render domain + the secure bot token path
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    
    s = bot.set_webhook(url=webhook_url)
    if s:
        return jsonify({"status": "success", "webhook_url": webhook_url})
    else:
        return jsonify({"status": "failed"}), 400


# --- STARTUP CONDITIONS ---
if __name__ == "__main__":
    if WEBHOOK_URL:
        # If running on server with Webhooks
        port = int(os.environ.get('PORT', 5000))
        logging.info(f"🚀 Starting Bot with Webhooks on port {port}...")
        app.run(host='0.0.0.0', port=port)
    else:
        # If running locally without Webhook URL
        logging.info("🐢 WEBHOOK_URL topilmadi. Polling rejimida ishga tushirilmoqda...")
        bot.remove_webhook()
        bot.infinity_polling()
