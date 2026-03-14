import google.generativeai as genai
from config import GEMINI_API_KEY
import database as db
import logging

# API kalitini sozlash
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logging.warning("⚠️ GEMINI_API_KEY topilmadi yoki sozlanmagan!")

def get_ai_response(user_query, user_id):
    """
    Foydalanuvchi savoliga bilimlar bazasi asosida Gemini AI orqali javob qaytaradi.
    """
    try:
        # 1. Bilimlar bazasidan tegishli ma'lumotlarni qidirish
        relevant_info = db.search_knowledge(user_query)
        
        context = ""
        if relevant_info:
            context = "\nQuyidagi ma'lumotlar bilimlar bazasidan olindi:\n"
            for info in relevant_info:
                context += f"- {info['text']}\n"
        
        # 2. Gemini modelini sozlash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. Prompt tayyorlash
        prompt = f"""
        Siz IT xizmatlari (Web sayt, Telegram bot, Mobil ilova, Dizayn) ko'rsatuvchi jamoaning aqlli yordamchisiz.
        Mijozlarga xushmuomala bo'ling va ularning savollariga aniq javob bering.
        
        {context}
        
        Foydalanuvchi savoli: {user_query}
        
        Agar bilimlar bazasida ma'lumot bo'lmasa, umumiy IT bilimlaringizdan foydalanib javob bering, 
        lekin jamoamiz nomidan yolg'on va'dalar bermang.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logging.error(f"AI response xatolik: {e}")
        return "Uzr, hozircha savolingizga javob bera olmayman. Iltimos, keyinroq urinib ko'ring."
