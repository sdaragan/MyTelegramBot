import os
import sqlite3

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = "8635192315:AAHAfdSOviCscJeoFNg7-nTWUXT0YoC0KSI"
ADMIN_ID = 6429081620

WAITING_BROADCAST = 1
WAITING_CONFIRM = 2
WAITING_PHOTO = 3
WAITING_SETTING_TEXT = 4
WAITING_SETTING_PHOTO = 5

main_keyboard = [
    ["🍽 Меню", "🥘 Комплексные обеды"],
    ["🚚 Доставка", "📝 Оформить заказ"],
    ["🕒 Режим работы", "💳 Оплата"],
    ["📞 Контакты"]
]

admin_button_keyboard = [
    ["⚙️ Админ-панель"]
]

confirm_broadcast_keyboard = [
    ["✅ Отправить", "❌ Отмена"]
]

confirm_broadcast_markup = ReplyKeyboardMarkup(
    confirm_broadcast_keyboard,
    resize_keyboard=True
)

admin_keyboard = [
    ["👥 Пользователи", "📊 Статистика"],
    ["📢 Рассылка текста", "🖼 Рассылка фото"],
    ["📦 Заказы", "⚙️ Настройки"],
    ["🔙 Главное меню"]
]

settings_keyboard = [
    ["🍽 Обновить меню", "🥘 Обновить обеды"],
    ["🚚 Обновить доставку", "🕒 Обновить режим"],
    ["📝 Изменить текст", "🖼 Изменить фото"],
    ["🔙 Админ-панель"]
]

settings_markup = ReplyKeyboardMarkup(
    settings_keyboard,
    resize_keyboard=True
)

markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
admin_button_markup = ReplyKeyboardMarkup(admin_button_keyboard, resize_keyboard=True)
admin_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)

admin_main_keyboard = [
    ["🍽 Меню", "🍲 Комплексные обеды"],
    ["🚚 Доставка", "📝 Оформить заказ"],
    ["🕒 Режим работы", "💳 Оплата"],
    ["📞 Контакты"],
    ["⚙️ Админ-панель"]
]

admin_main_markup = ReplyKeyboardMarkup(
    admin_main_keyboard,
    resize_keyboard=True
)

import os

DB_PATH = "/data/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            orders INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = {
        "delivery_text":
        "🚚 ДОСТАВКА\n\n"
        "🕘 Пн–Пт: 09:00–18:00\n"
        "🕘 Сб–Вс: 09:00–15:00\n\n"
        "💰 Минимальный заказ: 900 ₽",

        "work_text":
        "🕒 РЕЖИМ РАБОТЫ\n\n"
        "Пн–Пт 08:00–19:00\n"
        "Сб–Вс 08:00–16:00",

        "contacts_text":
        "📞 Контакты\n\n"
        "г. Донецк\n"
        "+7 949 605-30-96",

        "menu_photo": "",
        "lunch_photo": "",
        "delivery_photo": "",
        "work_photo": "",
    }

    for key, value in defaults.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
            (key, value)
        )

    conn.commit()
    conn.close()

def save_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return ""


def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO settings(key, value)
        VALUES(?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
        (key, value)
    )

    conn.commit()
    conn.close()

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await update.message.reply_text(
        "📝 Введите текст, который хотите отправить всем пользователям.",
    )

    return WAITING_BROADCAST

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"👥 Пользователей в базе: {count}"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(orders), 0) FROM users")
    orders_count = cursor.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"📊 Статистика\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"🛒 Всего заказов: {orders_count}"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["broadcast_text"] = text

    await update.message.reply_text(
        f"Вы собираетесь отправить:\n\n{text}\n\nПодтвердите отправку.",
        reply_markup=confirm_broadcast_markup
    )

    return WAITING_CONFIRM

    if text != "✅ Отправить":
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=confirm_broadcast_markup
        )
        return WAITING_CONFIRM

    text = context.user_data.get("broadcast_text")

    if not text:
        await update.message.reply_text(
            "❌ Текст рассылки не найден.",
            reply_markup=admin_markup
        )
        return ConversationHandler.END

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    sent = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user[0],
                text=text
            )
            sent += 1
        except Exception as e:
            print(e)

    context.user_data.pop("broadcast_text", None)

    await update.message.reply_text(
        f"✅ Рассылка завершена.\n\nОтправлено: {sent}",
        reply_markup=admin_main_markup
    )

    return ConversationHandler.END

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    text = update.message.text

    sections = {
        "🍽 Обновить меню": "menu",
        "🥘 Обновить обеды": "lunch",
        "🚚 Обновить доставку": "delivery",
        "🕒 Обновить режим": "work",
    }

    if text in sections:
        context.user_data["editing"] = sections[text]

        await update.message.reply_text(
            f"Вы выбрали:\n\n{text}\n\nЧто хотите изменить?",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["📝 Изменить текст"],
                    ["🖼 Изменить фото"],
                    ["🔙 Настройки"],
                ],
                resize_keyboard=True,
            ),
        )

    return WAITING_SETTING_TEXT

async def setting_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    section = context.user_data.get("editing")
    if not section:
        return ConversationHandler.END

    text = update.message.text

    if text == "🖼 Изменить фото":
        context.user_data["editing"] = section
        await update.message.reply_text("📷 Отправьте новую фотографию.")
        return WAITING_SETTING_PHOTO

    elif text == "📝 Изменить текст":
        await update.message.reply_text("✏️ Отправьте новый текст.")
        return WAITING_SETTING_TEXT

    if section == "delivery":
        set_setting("delivery_text", text)

    elif section == "work":
        set_setting("work_text", text)

    elif section == "contacts":
        set_setting("contacts_text", text)

    context.user_data.pop("editing", None)

    await update.message.reply_text(
        "✅ Текст успешно обновлён.",
        reply_markup=settings_markup
    )

    return ConversationHandler.END

async def setting_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    if not update.message.photo:
        await update.message.reply_text("❌ Отправьте фотографию.")
        return WAITING_SETTING_PHOTO

    photo = update.message.photo[-1].file_id

    section = context.user_data.get("editing")

    print("SETTING PHOTO")
    print("SECTION =", section)

    if section == "menu":
        set_setting("menu_photo", photo)

    elif section == "lunch":
        set_setting("lunch_photo", photo)

    elif section == "delivery":
        set_setting("delivery_photo", photo)

    elif section == "work":
        set_setting("work_photo", photo)

    context.user_data.pop("editing", None)

    await update.message.reply_text(
        "✅ Фото успешно обновлено.",
        reply_markup=settings_markup
    )

    return ConversationHandler.END

async def sendphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await update.message.reply_text(
        "📷 Отправьте фотографию с подписью, которую нужно разослать всем пользователям."
    )

    return WAITING_PHOTO

async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фотографию"
        )
        return WAITING_PHOTO

    photo = update.message.photo[-1].file_id
    caption = update.message.caption or ""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    conn.close()

    sent = 0

    for user in users:
        try:
            await context.bot.send_photo(
                chat_id=user[0],
                photo=photo,
                caption=caption
            )
            sent += 1
        except Exception as e:
            print(e)

    await update.message.reply_text(
        f"✅ Рассылка завершена.\n\nОтправлено: {sent}"
    )

    return ConversationHandler.END

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    text = update.message.text

    if text == "❌ Отмена":
        context.user_data.pop("broadcast_text", None)
        await update.message.reply_text(
            "❌ Рассылка отменена.",
            reply_markup=admin_markup
        )
        return ConversationHandler.END

    if text != "✅ Отправить":
        await update.message.reply_text(
            "Выберите:\n\n✅ Отправить\nили\n❌ Отмена",
            reply_markup=confirm_broadcast_markup
        )
        return WAITING_CONFIRM

    text = context.user_data.get("broadcast_text")

    if not text:
        await update.message.reply_text(
            "Текст рассылки не найден.",
            reply_markup=admin_markup
        )
        return ConversationHandler.END

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    sent = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user[0],
                text=text
            )
            sent += 1
        except Exception:
            pass

    context.user_data.pop("broadcast_text", None)

    await update.message.reply_text(
        f"✅ Рассылка завершена.\n\nОтправлено: {sent}",
        reply_markup=admin_markup
    )

    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    channel_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/shchiborshchidonetsk")]
    ])

    await update.message.reply_text(
        "Здравствуйте! Вас приветствует столовая «Щи-Борщи». 🍲\n\n"
        "📢 Подписывайтесь на наш Telegram-канал, чтобы следить за последними новостями, свежим меню и приятными предложениями.\n\n"
        "Нажмите кнопку ниже, чтобы перейти в канал 👇",
        reply_markup=channel_keyboard
    )

    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            "Добро пожаловать, администратор 👋",
            reply_markup=admin_main_markup
        )

    else:
        await update.message.reply_text(
            "Выберите нужный раздел:",
            reply_markup=markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    text = update.message.text
   
    if update.effective_user.id == ADMIN_ID:

        if text == "⚙️ Админ-панель":
            await update.message.reply_text(
                "⚙️ Панель администратора",
                reply_markup=admin_markup
            )
            return

        elif text == "🔙 Главное меню":
            await update.message.reply_text(
                "Главное меню",
                reply_markup=admin_main_markup
            )
            return

        elif text == "👥 Пользователи":
            await users(update, context)
            return

        elif text == "📊 Статистика":
            await stats(update, context)
            return

        elif text == "📦 Заказы":

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT COALESCE(SUM(orders), 0) FROM users")
            orders_count = cursor.fetchone()[0]

            conn.close()

            await update.message.reply_text(
                f"📦 Заказы\n\n"
                f"📊 Всего заказов: {orders_count}\n\n"
                f"💬 Все новые заказы автоматически отправляются в чат администратора.\n"
                f"Используйте этот чат для просмотра и обработки заказов."
            )

            return

        elif text == "⚙️ Настройки":
            await update.message.reply_text(
                "⚙️ Настройки\n\nВыберите раздел для изменения:",
                reply_markup=settings_markup
            )
            return

        elif text in [
            "🍽 Обновить меню",
            "🥘 Обновить обеды",
            "🚚 Обновить доставку",
            "🕒 Обновить режим"
        ]:
            return await settings(update, context)

    buttons = ["🍽 Меню", "🥘 Комплексные обеды", "🚚 Доставка", "📝 Оформить заказ", "🕒 Режим работы", "💳 Оплата", "📞 Контакты"]

    if context.user_data.get("waiting_for_order") and text not in buttons:
        context.user_data["waiting_for_order"] = False

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔔 НОВЫЙ ЗАКАЗ\n\n"
                f"{text}\n\n"
                "👤 От пользователя:\n"
                f"@{update.message.from_user.username}"
            )
        )

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET orders = orders + 1 WHERE user_id = ?",
            (update.effective_user.id,)
        )

        conn.commit()
        conn.close()

        await update.message.reply_text(
            "✅ Спасибо! Ваш заказ получен.\n\n"
            "Мы свяжемся с вами для подтверждения заказа."
        )

        return

    elif text == "🍽 Меню":
        with open("menu.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="🍽 Меню"
            )
        return

    elif text == "🥘 Комплексные обеды":
       with open("iunch.jpg", "rb") as photo:
           await update.message.reply_photo(
               photo=photo,
               caption="🍲 Комплексные обеды"
           )
       return 

    elif text == "🚚 Доставка":
        await update.message.reply_text(
            get_setting("delivery_text")
        )

        photo = get_setting("delivery_photo")
 
        if photo:
            await update.message.reply_photo(photo=photo)

    elif text == "📝 Оформить заказ":
        context.user_data["waiting_for_order"] = True
        await update.message.reply_text(
        "📝 ОФОРМИТЬ ЗАКАЗ\n\n"
        "Отправьте заказ одним сообщением по шаблону:\n\n"
        "👤 Имя\n"
        "📞 Телефон\n"
        "📍 Адрес доставки\n"
        "🍽 Блюда и количество\n\n"
        "Или свяжитесь с нами:\n"
        "📞 +7 949 605-30-96"
    )

    elif text == "🕒 Режим работы":
        await update.message.reply_text(
            get_setting("work_text")
        )

        photo = get_setting("work_photo")

        if photo:
            await update.message.reply_photo(photo=photo)
   
    elif text == "💳 Оплата":
        await update.message.reply_text(
            "💳 СПОСОБЫ ОПЛАТЫ\n\n"
            "💵 Наличные\n\n"
            "💳 Банковская карта\n\n"
            "📱 Оплата по QR-коду\n\n"
            "✅ Выберите наиболее удобный для вас способ оплаты."
        )

    elif text == "📞 Контакты":
        await update.message.reply_text(
            get_setting("contacts_text")
        )

    if text == "📝 Изменить текст":
        context.user_data["editing_mode"] = "text"
        return await setting_text(update, context)

    if text == "🖼 Изменить фото":
        context.user_data["editing_mode"] = "photo"
        return await setting_photo(update, context)

    else:
        await update.message.reply_text("Спасибо! Мы получили ваше сообщение.")
init_db()
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[
    CommandHandler("send", send),
    CommandHandler("sendphoto", sendphoto),

    MessageHandler(
        filters.TEXT & filters.Regex("^📢 Рассылка текста$"),
        send
    ),

    MessageHandler(
        filters.TEXT & filters.Regex("^🖼 Рассылка фото$"),
        sendphoto
    ),
],

    states={
        WAITING_BROADCAST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast)
        ],

        WAITING_CONFIRM: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_broadcast)
        ],

        WAITING_PHOTO: [
            MessageHandler(filters.PHOTO, broadcast_photo)
        ],

        WAITING_SETTING_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, setting_text)
        ],

        WAITING_SETTING_PHOTO: [
            MessageHandler(filters.PHOTO, setting_photo)
        ],
},

    fallbacks=[],
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()