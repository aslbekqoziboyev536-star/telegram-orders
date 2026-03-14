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
        user_id = str(message.from_user.id)
        db.save_user(user_id, message.from_user.username, message.from_user.first_name)
        
        if user_id == str(ADMIN_ID):
            bot.send_message(message.chat.id, "Salom Admin! 🚀 Siz maxsus boshqaruv panelidasiz.", reply_markup=kb.admin_menu_kb())
        else:
            text = "Assalomu alaykum! 🚀 IT xizmatlari buyurtma botiga xush kelibsiz!\n\nBiz sizga Web sayt, Telegram bot va Mobil ilovalar yaratishda yordam beramiz. Quyidagi menyudan kerakli bo'limni tanlang 👇"
            bot.send_message(message.chat.id, text, reply_markup=kb.main_menu_kb())

    # Professional Admin Panel Handlers
    @bot.message_handler(func=lambda msg: str(msg.from_user.id) == str(ADMIN_ID))
    def admin_handlers(message):
        if message.text == "📊 Statistika":
            stats = db.get_admin_stats()
            text = (
                f"📊 *Professional Admin Statistika:*\n\n"
                f"👥 Foydalanuvchilar soni: {stats.get('users', 0)}\n"
                f"🟡 Yangi buyurtmalar soni: {stats.get('new', 0)}\n"
                f"✅ Tasdiqlangan buyurtmalar soni: {stats.get('confirmed', 0)}\n"
                f"❌ Bekor qilingan buyurtmalar soni: {stats.get('canceled', 0)}\n"
                f"📦 Jami buyurtmalar soni: {stats.get('total', 0)}"
            )
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
            
        elif message.text == "🆕 Yangi buyurtmalar" or message.text == "/submit":
            orders = db.get_orders_by_status("new")
            if not orders:
                bot.send_message(message.chat.id, "Hozircha yangi buyurtmalar yo'q. 🤷‍♂️")
                return
            
            text = "🆕 *Yangi buyurtmalar ro'yxati:*\n\n"
            for i, order in enumerate(orders, 1):
                # Birinchi tanlangan xizmat nomi loyiha nomi sifatida ishlatiladi
                proj_name = order.get('items', ['Noma’lum'])[0]
                text += f"{i}. {proj_name} — /submit_{order['_id']}\n"
            
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

        elif message.text.startswith("/submit_"):
            order_id = message.text.replace("/submit_", "")
            order = db.get_order_by_id(order_id)
            if not order:
                bot.send_message(message.chat.id, "❌ Buyurtma topilmadi.")
                return
            
            u_name = order.get('user_name', 'Noma’lum')
            u_login = order.get('username', '-')
            u_phone = order.get('phone', '-')
            u_details = order.get('details', '-')
            
            services_list = "\n".join([f"✔️ {s}" for s in order.get('items', [])])
            details = (
                f"📝 *BUYURTMA TAFSILOTLARI*\n\n"
                f"👤 Mijoz: {u_name}\n"
                f"🔗 Username: @{u_login}\n"
                f"📱 Tel: {u_phone}\n\n"
                f"📁 Xizmatlar:\n{services_list}\n\n"
                f"💬 Tavsif: {u_details}"
            )
            bot.send_message(message.chat.id, details, parse_mode="Markdown", reply_markup=kb.admin_order_kb(order['_id']))

        elif message.text == "✅ Tasdiqlanganlar":
            orders = db.get_orders_by_status("confirmed")
            text = "✅ *Tasdiqlangan loyihalar:*\n\n"
            if not orders:
                text += "Ro'yxat bo'sh."
            else:
                for o in orders:
                    name = o.get('user_name', 'Noma’lum')
                    service = o.get('items', ['-'])[0]
                    text += f"🔹 {name} - {service} (/submit_{o['_id']})\n"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

        elif message.text == "❌ Bekor qilinganlar":
            orders = db.get_orders_by_status("canceled")
            text = "❌ *Bekor qilingan loyihalar:*\n\n"
            if not orders:
                text += "Ro'yxat bo'sh."
            else:
                for o in orders:
                    name = o.get('user_name', 'Noma’lum')
                    service = o.get('items', ['-'])[0]
                    text += f"🔸 {name} - {service} (/submit_{o['_id']})\n"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
            
        elif message.text == "➕ Bilim qo'shish":
            bot.send_message(message.chat.id, "Bilimlar bazasiga ma'lumot qo'shish uchun: `/add_info [matn]`")

    # Callback handlers for admin approval
    @bot.callback_query_handler(func=lambda call: call.data.startswith(("conf_", "canc_")))
    def admin_approval_action(call):
        action, order_id = call.data.split("_")
        order = db.get_order_by_id(order_id)
        
        if not order:
            bot.answer_callback_query(call.id, "Xatolik: Buyurtma topilmadi!")
            return

        if action == "conf":
            db.update_order_status(order_id, "confirmed")
            bot.edit_message_text(f"✅ Buyurtma tasdiqlandi!\nMijoz: {order.get('user_name')}", call.message.chat.id, call.message.message_id)
            
            # Userga xabar yuborish (EXACT REQUESTED TEMPLATE)
            tg_username = f"@{order.get('username')}" if order.get('username') else order.get('user_name', 'Foydalanuvchi')
            project_name = order.get('items', ['Loyiha'])[0]
            
            user_msg = (
                f"Assalomu aleykum, {tg_username}! Sizning {project_name} nomli buyurtmangiz admin tomonidan tasdiqlandi! "
                f"Endi admin siz bilan aloqaga chiqishi mumki. "
                f"Diqqat! Agar admin siz bilan aloqaga chiqishga urinib, siz 7 kun ichida javob bermasangiz, buyurtmangiz bekor qilinadi!"
            )
            try:
                bot.send_message(order['user_id'], user_msg)
            except Exception as e:
                print(f"Bildirishnoma yuborishda xato: {e}")
                
        elif action == "canc":
            db.update_order_status(order_id, "canceled")
            bot.edit_message_text(f"❌ Buyurtma bekor qilindi.\nMijoz: {order.get('user_name')}", call.message.chat.id, call.message.message_id)

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
        data = message.web_app_data.data
        try:
            order_data = json.loads(data)
            services = "\n".join([f"✔️ {s}" for s in order_data.get('services', [])])
            phone = order_data.get('phone', 'Noma\'lum')
            details = order_data.get('details', 'Yo\'q')
            user_name = message.from_user.first_name
            # username ni @ belgisisiz saqlaymiz (admin panelda @ qo'shiladi)
            username = message.from_user.username or "-"

            # Save to Database with UNIQUE status
            db.save_order(
                user_id=message.from_user.id,
                username=username,
                user_name=user_name,
                phone=phone,
                details=details,
                items=order_data.get('services', [])
            )

            bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi! Tez orada mutaxassislarimiz bog'lanishadi.", reply_markup=kb.main_menu_kb())
            
            # Admin notification
            order_text = f"🆕 *YANGI MINI-APP BUYURTMA*\nMijoz: {user_name}\nLoyiha: {order_data.get('services', ['-'])[0]}"
            bot.send_message(ADMIN_ID, order_text, parse_mode="Markdown")

        except Exception as e:
            bot.send_message(message.chat.id, "❌ Xatolik yuz berdi.", reply_markup=kb.main_menu_kb())

    @bot.message_handler(func=lambda msg: msg.text == "📁 Tanlangan xizmatlar")
    def show_cart(message):
        cart = db.get_cart(message.from_user.id)
        if not cart:
            bot.send_message(message.chat.id, "Siz hali xizmat tanlamadingiz.")
            return

        text = "📁 *Siz tanlagan xizmatlar:*\n\n"
        for pid, qty in cart.items():
            product = db.get_product(pid)
            text += f"🔹 {product['name']}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=kb.cart_menu_kb())

    # So'rov yuborish
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
    def start_order_confirmation(call):
        user_states[call.from_user.id] = {'state': 'waiting_for_phone'}
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Telefon raqamingizni yuboring:", reply_markup=kb.contact_request_kb())

    @bot.message_handler(func=lambda msg: msg.text == "❌ Bekor qilish")
    def cancel_order(message):
        db.clear_cart(message.from_user.id)
        user_states.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "Bekor qilindi.", reply_markup=kb.main_menu_kb())

    @bot.message_handler(content_types=['text', 'contact'])
    def handle_states(message):
        user_id = message.from_user.id
        if user_id not in user_states:
            if str(user_id) != str(ADMIN_ID):
                bot.reply_to(message, "Iltimos, botga to'g'ridan to'g'ri xabar yuboora olmaysiz. Tugmalar va buyruqlar orqali ishlang!")
            return
            
        state_data = user_states[user_id]
        if state_data.get('state') == 'waiting_for_phone':
            phone = message.contact.phone_number if message.content_type == 'contact' else message.text
            user_states[user_id]['phone'] = phone
            user_states[user_id]['state'] = 'waiting_for_details'
            bot.send_message(message.chat.id, "Loyiha haqida yozing:", reply_markup=types.ReplyKeyboardRemove())
        elif state_data.get('state') == 'waiting_for_details':
            # Save final order
            db.save_order(user_id, message.from_user.username, message.from_user.first_name, state_data['phone'], message.text, ["Manual Order"])
            user_states.pop(user_id, None)
            bot.send_message(message.chat.id, "✅ Rahmat! Buyurtma qabul qilindi.", reply_markup=kb.main_menu_kb())
