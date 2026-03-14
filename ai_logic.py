from google import genai
from config import GEMINI_API_KEY
import database as db
import logging

# AI Clientni yaratish
client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logging.error(f"⚠️ Gemini Client xatolik: {e}")
else:
    logging.warning("⚠️ GEMINI_API_KEY topilmadi yoki sozlanmagan!")

def get_ai_response(user_query, user_id):
    """
    Foydalanuvchi savoliga bilimlar bazasi asosida Gemini AI orqali javob qaytaradi.
    """
    if not client:
        return "⚠️ Hozircha AI yordamchisi faollashtirilmagan (API Key yetishmayapti)."

    try:
        # 1. Bilimlar bazasidan tegishli ma'lumotlarni qidirish
        relevant_info = db.search_knowledge(user_query)
        
        context = ""
        if relevant_info:
            context = "\nQuyidagi ma'lumotlar bilimlar bazasidan olindi:\n"
            for info in relevant_info:
                context += f"- {info['text']}\n"
        
        # 2. Prompt tayyorlash
        prompt = f"""
        Siz IT xizmatlari (Web sayt, Telegram bot, Mobil ilova, Dizayn) ko'rsatuvchi jamoaning aqlli yordamchisiz.
        Mijozlarga xushmuomala bo'ling va ularning savollariga aniq javob bering.
        
        {context}
        
        Foydalanuvchi savoli: {user_query}
        
        Agar bilimlar bazasida ma'lumot bo'lmasa, umumiy IT bilimlaringizdan foydalanib javob bering, 
        lekin jamoamiz nomidan yolg'on va'dalar bermang.
        """
        
        # 3. Gemini modelidan javob olish
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        logging.error(f"AI response xatolik: {e}")
        return "Uzr, hozircha savolingizga javob bera olmayman. Iltimos, keyinroq urinib ko'ring."
