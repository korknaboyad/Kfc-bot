import telebot
from telebot import types
from datetime import datetime

BOT_TOKEN = "8164135376:AAGDuNAB_NTk1OPq-oZeP326F_Zd_fTjoJQ"
bot = telebot.TeleBot(BOT_TOKEN)

# ========== КРАСИВОЕ МЕНЮ ==========
menu = {
    "🍗 БАСКЕТЫ": {
        "Баскет 5 стрипсов": {"price": 299, "desc": "5 сочных куриных стрипсов", "emoji": "🍗"},
        "Баскет 8 крыльев": {"price": 349, "desc": "8 острых крылышек", "emoji": "🍗"},
        "Баскет Mix": {"price": 499, "desc": "Микс из стрипсов и крыльев", "emoji": "🍗"},
    },
    "🍔 БУРГЕРЫ": {
        "Шефбургер": {"price": 189, "desc": "Классический бургер KFC", "emoji": "🍔"},
        "Твистер": {"price": 169, "desc": "Сочная лепешка с курицей", "emoji": "🌯"},
        "Боксмастер": {"price": 219, "desc": "Большой сочный бургер", "emoji": "🍔"},
    },
    "🍟 СНЭКИ": {
        "Картофель фри": {"price": 89, "desc": "Хрустящий картофель", "emoji": "🍟"},
        "Наггетсы 6 шт": {"price": 129, "desc": "Куриные наггетсы", "emoji": "🐔"},
        "Сырные палочки": {"price": 99, "desc": "Горячие сырные палочки", "emoji": "🧀"},
    },
    "🥤 НАПИТКИ": {
        "Pepsi 0.5л": {"price": 79, "desc": "Освежающий напиток", "emoji": "🥤"},
        "Чай": {"price": 49, "desc": "Горячий чай", "emoji": "🍵"},
        "Кофе": {"price": 89, "desc": "Ароматный кофе", "emoji": "☕"},
    },
    "🍦 ДЕСЕРТЫ": {
        "Пломбир": {"price": 79, "desc": "Нежный пломбир", "emoji": "🍦"},
        "Чизкейк": {"price": 119, "desc": "Классический чизкейк", "emoji": "🍰"},
        "Яблочный пирог": {"price": 89, "desc": "С яблоком и корицей", "emoji": "🥧"},
    }
}

user_carts = {}

# ========== КЛАВИАТУРА ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🍽️ МЕНЮ", "🛒 КОРЗИНА")
    markup.add("⭐ АКЦИИ", "📞 КОНТАКТЫ")
    markup.add("ℹ️ О НАС", "🚚 ДОСТАВКА")
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=["start"])
def start(message):
    text = f"""
╔══════════════════════════════╗
║     🍗 ДОБРО ПОЖАЛОВАТЬ 🍗    ║
╠══════════════════════════════╣
║   Привет, {message.from_user.first_name}!   ║
║   KFC - вкус, который дарит  ║
║        улыбку! 😋           ║
╚══════════════════════════════╝
    """
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_keyboard())

# ========== МЕНЮ ==========
@bot.message_handler(func=lambda m: m.text == "🍽️ МЕНЮ")
def show_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat in menu.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "🍽️ *НАШЕ МЕНЮ* 🍽️\n\nВыбери категорию:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_category(call):
    cat = call.data.replace("cat_", "")
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for item, data in menu[cat].items():
        btn_text = f"{data['emoji']} {item} - {data['price']}₽"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"item_{cat}_{item}"))
    
    markup.add(types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back_menu"))
    bot.edit_message_text(f"📋 *{cat}*\n\nВыбери блюдо:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def show_item(call):
    _, cat, item = call.data.split("_", 2)
    data = menu[cat][item]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ В КОРЗИНУ", callback_data=f"add_{cat}_{item}"))
    markup.add(types.InlineKeyboardButton("◀️ НАЗАД", callback_data=f"cat_{cat}"))
    
    text = f"""
{data['emoji']} *{item}*

📝 {data['desc']}

💰 Цена: *{data['price']}₽*
    """
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
# ========== КОРЗИНА ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart(call):
    _, cat, item = call.data.split("_", 2)
    user_id = call.from_user.id
    price = menu[cat][item]["price"]
    emoji = menu[cat][item]["emoji"]
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append({"name": item, "price": price, "emoji": emoji})
    
    bot.answer_callback_query(call.id, f"✅ {item} добавлен в корзину!", show_alert=False)
    
    # Возвращаемся в категорию
    markup = types.InlineKeyboardMarkup(row_width=1)
    for it, dt in menu[cat].items():
        btn_text = f"{dt['emoji']} {it} - {dt['price']}₽"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"item_{cat}_{it}"))
    markup.add(types.InlineKeyboardButton("◀️ НАЗАД", callback_data="back_menu"))
    bot.edit_message_text(f"📋 *{cat}*\n\n✅ Добавлено!\n\nВыбери еще:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛒 КОРЗИНА")
def show_cart(message):
    user_id = message.from_user.id
    
    if user_id not in user_carts or not user_carts[user_id]:
        bot.send_message(message.chat.id, "🛒 *КОРЗИНА ПУСТА*\n\nДобавь блюда из меню! 🍗", parse_mode="Markdown")
        return
    
    text = "🛒 *ТВОЯ КОРЗИНА*\n\n"
    total = 0
    for i, item in enumerate(user_carts[user_id], 1):
        text += f"{i}. {item['emoji']} {item['name']} - *{item['price']}₽*\n"
        total += item['price']
    text += f"\n{'─' * 25}\n💰 *ИТОГО: {total}₽*\n{'─' * 25}"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ ОФОРМИТЬ", callback_data="checkout"),
        types.InlineKeyboardButton("🗑 ОЧИСТИТЬ", callback_data="clear_cart")
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def checkout(call):
    user_id = call.from_user.id
    total = sum(item["price"] for item in user_carts[user_id])
    order_num = datetime.now().strftime("%H%M")
    
    text = f"""
╔══════════════════════════════╗
║      ✅ ЗАКАЗ ОФОРМЛЕН ✅     ║
╠══════════════════════════════╣
║  📋 Номер: #{order_num}
║  💰 Сумма: {total}₽
║  ⏱️ Время: {datetime.now().strftime('%H:%M')}
╠══════════════════════════════╣
║  🚚 Доставка: 30-40 минут
║  📞 Оператор свяжется с вами
║  Спасибо за заказ! 🍗
╚══════════════════════════════╝
    """
    user_carts[user_id] = []
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "Заказ оформлен! 🎉")

@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def clear_cart(call):
    user_carts[call.from_user.id] = []
    bot.answer_callback_query(call.id, "🗑 Корзина очищена!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat in menu.keys():
        markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.edit_message_text("🍽️ *НАШЕ МЕНЮ* 🍽️\n\nВыбери категорию:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

# ========== ОСТАЛЬНОЕ ==========
@bot.message_handler(func=lambda m: m.text == "⭐ АКЦИИ")
def promotions(m):
    bot.send_message(m.chat.id, "⭐ *АКЦИИ*\n\n🎁 Комбо обед - 299₽\n🔥 Счастливые часы (14-16) - скидка 20%\n🎂 День рождения - подарок!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📞 КОНТАКТЫ")
def contacts(m):
    bot.send_message(m.chat.id, "📞 *КОНТАКТЫ*\n\n☎️ 8-800-555-35-35\n📧 info@kfc.ru\n🌐 kfc.ru\n📍 ул. Тверская, 15", parse_mode="Markdown")
@bot.message_handler(func=lambda m: m.text == "ℹ️ О НАС")
def about(m):
    bot.send_message(m.chat.id, "ℹ️ *О KFC*\n\n🍗 С 1952 года\n🌍 24 000+ ресторанов\n✨ Свежие продукты, быстрая доставка", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚚 ДОСТАВКА")
def delivery(m):
    bot.send_message(m.chat.id, "🚚 *ДОСТАВКА*\n\n✅ Мин. заказ: 500₽\n⏱️ 30-40 минут\n💵 От 1000₽ - бесплатно\n🎁 В день рождения - бесплатно!", parse_mode="Markdown")

print("🔥 KFC БОТ ЗАПУЩЕН! 🔥")
bot.infinity_polling()
