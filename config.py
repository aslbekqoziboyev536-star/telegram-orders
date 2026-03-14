import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8662556776:AAEmY304NfZc9cYQpuUBv5xihVLEviCX0Wk")
ADMIN_ID = os.getenv("ADMIN_ID", "7342611753")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
