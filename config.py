import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8662556776:AAEmY304NfZc9cYQpuUBv5xihVLEviCX0Wk")
ADMIN_ID = os.getenv("ADMIN_ID", "7342611753")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") # Render url e.g. https://my-bot.onrender.com
