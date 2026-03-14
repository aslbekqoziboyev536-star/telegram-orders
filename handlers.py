import telebot
from telebot import types
import json

import keyboards as kb
import database as db
import ai_logic as ai
from config import ADMIN_ID

# Status dictionary o'rniga oddiy xotirada saqlash usuli
# user_id: status
user_states = {}

def register_handlers(bot: telebot.TeleBot):
    
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        text = "Assalomu alaykum! 🚀 IT xizmatlari buyurtma botiga xush kelibsiz!\n\nBiz sizga Web sayt, Telegram bot va Mobil ilovalar yaratishda yordam beramiz. Quyidagi menyudan kerakli bo'limni tanlang 👇"
        bot.send_message(message.chat.id, text, reply_markup=kb.main_menu_kb())

    @bot.message_handler(func=lambda msg: msg.text == "ℹ️ Ma'lumot")
    def info_handler(message):
        text = (
            "💻 Bizning jamoa quyidagi yo'nalishlarda xizmat ko'rsatadi:\n\n"
            "🌐 Web Sayt - Biznesingiz uchun korporativ saytlar, internet do'konlar va landing pagelar.\n"
            "🤖 Telegram Bot - Biznesni avtomatlashtirish, mijozlar bilan ishlash botlari.\n"
            "📱 Mobil Ilova - Android va iOS platformalari uchun zamonaviy ilovalar.\n\n"
            "Loyihangizni muhokama qilish va buyurtma berish uchun bosh menyudagi '💻 Oddiy xizmat buyurtirish' tugmasini bosing."
        )
        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda msg: msg.text == "💻 Oddiy xizmat buyurtirish")
    def show_products(message):
        bot.send_message(message.chat.id, "Qaysi xizmat turlariga qiziqyapiz? Narxlar loyiha qamroviga qarab belgilanadi:", reply_markup=kb.products_menu_kb())

    # Admin uchun bilimlar bazasiga ma'lumot qo'shish
    @bot.message_handler(commands=['add_info'])
    def add_info_handler(message):
        if str(message.from_user.id) != str(ADMIN_ID):
            bot.reply_to(message, "Siz admin emassiz! ❌")
            return
        
        text_to_add = message.text.replace('/add_info', '').strip()
        if not text_to_add:
            bot.reply_to(message, "Iltimos, qo'shmoqchi bo'lgan ma'lumotingizni yozing.\nMisol: `/add_info Bizning ofisimiz Toshkent shahrida.`", parse_mode="Markdown")
            return
        
        if db.add_knowledge(text_to_add):
            bot.reply_to(message, "✅ Ma'lumot bilimlar bazasiga qo'shildi!")
        else:
            bot.reply_to(message, "❌ Xatolik yuz berdi.")

    # Mini App dan kelgan ma'lumotlarni qabul qilish
    @bot.message_handler(content_types=['web_app_data'])
    def web_app_handler(message):
        # JSON formatida kelgan data-ni o'qiymiz
        data = message.web_app_data.data
        try:
            order_data = json.loads(data)
            
            services = "\n".join([f"✔️ {s}" for s in order_data.get('services', [])])
            phone = order_data.get('phone', 'Noma\'lum')
            details = order_data.get('details', 'Yo\'q')
            
            user_name = message.from_user.first_name
            username = f"@{message.from_user.username}" if message.from_user.username else "-"

            order_text = (
                f"🌟 *YANGI MINI-APP BUYURTMA*\n\n"
                f"👤 *Mijoz:* {user_name}\n"
                f"🔗 *Username:* {username}\n"
                f"📱 *Telefon:* {phone}\n\n"
                f"📁 *Tanlangan xizmatlar:*\n{services}\n\n"
                f"📝 *Loyiha tafsilotlari:*\n{details}"
            )
            
            if ADMIN_ID and ADMIN_ID != "YOUR_ADMIN_ID_HERE":
                bot.send_message(ADMIN_ID, order_text, parse_mode="Markdown")
            
            # Save to Database
            db.save_order(
                user_id=message.from_user.id,
                username=message.from_user.username,
                user_name=user_name,
                phone=phone,
                details=details,
                items=order_data.get('services', [])
            )

            bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi! Tez orada mutaxassislarimiz bog'lanishadi.", reply_markup=kb.main_menu_kb())
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring yoki odatiy buyurtmadan foydalaning.", reply_markup=kb.main_menu_kb())

    # Xizmatni tanlash (inline callback)
    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
    def add_product(call):
        product_id = call.data.split("_")[1]
        product = db.get_product(product_id)
        
        if product:
            db.add_to_cart(call.from_user.id, product_id, 1)
            bot.answer_callback_query(call.id, f"✅ {product['name']} qiziqishlar ro'yxatiga qo'shildi!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ Xizmat topilmadi.", show_alert=True)

    @bot.message_handler(func=lambda msg: msg.text == "📁 Tanlangan xizmatlar")
    def show_cart(message):
        cart = db.get_cart(message.from_user.id)
        if not cart:
            bot.send_message(message.chat.id, "Siz hali xizmat tanlamadingiz. '💻 Oddiy xizmat buyurtirish' orqali o'zingizga kerakli xizmatni belgilang.")
            return

        text = "📁 *Siz tanlagan xizmatlar:*\n\n"
        
        for pid, qty in cart.items():
            product = db.get_product(pid)
            text += f"🔹 {product['name']}\n— {product['description']}\n\n"
        
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=kb.cart_menu_kb())

    # Ro'yxatni tozalash
    @bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
    def clear_cart(call):
        db.clear_cart(call.from_user.id)
        bot.edit_message_text("Ro'yxat tozalandi 🗑", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Tozalandi")

    # So'rov yuborish
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
    def start_order_confirmation(call):
        cart = db.get_cart(call.from_user.id)
        if not cart:
            bot.answer_callback_query(call.id, "Siz xizmat tanlamadingiz!", show_alert=True)
            return
        
        user_states[call.from_user.id] = {'state': 'waiting_for_phone'}
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "Mutaxassislarimiz aloqaga chiqishi uchun pastdagi tugmani bosish orqali telefon raqamingizni yuboring 📱 yoki qo'lda kiriting (masalan: +998901234567):",
            reply_markup=kb.contact_request_kb()
        )
        bot.answer_callback_query(call.id)

    # Bekor qilish tugmasi
    @bot.message_handler(func=lambda msg: msg.text == "❌ Bekor qilish")
    def cancel_order(message):
        user_id = message.from_user.id
        db.clear_cart(user_id)
        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, "Amal bekor qilindi. Bosh menyudasiz.", reply_markup=kb.main_menu_kb())

    # Telefonni va tafsilotlarni qabul qilish
    @bot.message_handler(content_types=['text', 'contact'])
    def handle_states(message):
        user_id = message.from_user.id
        
        if user_id not in user_states:
            return # E'tiborsiz qoldiramiz agar state yo'q bo'lsa
            
        current_state = user_states[user_id].get('state')
        
        if current_state == 'waiting_for_phone':
            phone_number = ""
            if message.content_type == 'contact':
                phone_number = message.contact.phone_number
            elif message.text:
                phone_number = message.text

            if not phone_number:
                bot.send_message(message.chat.id, "Iltimos, telefon raqamingizni jo'nating!")
                return
                
            user_states[user_id]['phone'] = phone_number
            user_states[user_id]['state'] = 'waiting_for_details'
            
            bot.send_message(
                message.chat.id,
                "Rahmat! Endi loyihangiz haqida qisqacha ma'lumot yoki talablaringizni yozib yuboring (masalan: Menga online do'kon uchun Telegram bot kerak).\n\nAgar hozir yozishni xohlamasangiz shunchaki 'Yo\\'q' deb yozishingiz mumkin.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            
        elif current_state == 'waiting_for_details':
            phone = user_states[user_id].get('phone')
            details = message.text

            cart = db.get_cart(user_id)
            user_name = message.from_user.first_name
            username = f"@{message.from_user.username}" if message.from_user.username else "Yo'q"
            
            order_text = (
                f"🚨 *YANGI IT XIZMAT SO'ROVI*\n\n"
                f"👤 *Mijoz:* {user_name}\n"
                f"🔗 *Username:* {username}\n"
                f"📱 *Telefon:* {phone}\n\n"
                f"📁 *Qiziqayotgan yo'nalishlari:*\n"
            )
            
            for pid, qty in cart.items():
                product = db.get_product(pid)
                order_text += f"✔️ {product['name']}\n"
                
            order_text += f"\n📝 *Loyiha tafsilotlari:*\n{details}"
            
            try:
                if ADMIN_ID and ADMIN_ID != "YOUR_ADMIN_ID_HERE":
                    bot.send_message(ADMIN_ID, order_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send to admin: {e}")
                
            # Prepare bought items for DB
            bought_items = []
            for pid, qty in cart.items():
                product = db.get_product(pid)
                bought_items.append(product['name'])

            # Save to Database
            db.save_order(
                user_id=user_id,
                username=message.from_user.username,
                user_name=user_name,
                phone=phone,
                details=details,
                items=bought_items
            )

            db.clear_cart(user_id)
            user_states.pop(user_id, None)
            
            bot.send_message(
                message.chat.id,
                "✅ So'rovingiz muvaffaqiyatli qabul qilindi! Tez orada mutaxassislarimiz siz bilan bog'lanib barcha detallarni kelishib olishadi.",
                reply_markup=kb.main_menu_kb()
            )

        # AI Fallback Handler
        @bot.message_handler(func=lambda msg: True, content_types=['text'])
        def ai_responder(message):
            # Agar foydalanuvchi biror state ichida bo'lsa (telefon raqami kutilyapti va h.k.), AI aralashmaydi
            if message.from_user.id in user_states:
                return
            
            # AI orqali javob olish
            bot.send_chat_action(message.chat.id, 'typing')
            response = ai.get_ai_response(message.text, message.from_user.id)
            bot.reply_to(message, response)
