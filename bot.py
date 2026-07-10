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

main_keyboard = [
    ["🍽 Меню", "🥘 Комплексные обеды"],
    ["🚚 Доставка", "📝 Оформить заказ"],
    ["🕒 Режим работы", "💳 Оплата"],
    ["📞 Контакты"]
]

markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()

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

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await update.message.reply_text(
        "Введите текст, который хотите разослать всем пользователям."
    )
    return WAITING_BROADCAST

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

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

    conn.close()

    await update.message.reply_text(
        f"Рассылка завершена.\n\nОтправлено: {sent}"
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

    await update.message.reply_text(
        "Выберите нужный раздел:",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
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

        await update.message.reply_text(
            "✅ Спасибо! Ваш заказ получен.\n\n"
            "Мы свяжемся с вами для подтверждения заказа."
        )
        return

    if text == "🍽 Меню":
        await update.message.reply_photo(
            photo=open("menu.jpg", "rb"),
            caption="🍽 Меню"
        )

    elif text == "🥘 Комплексные обеды":
        await update.message.reply_photo(
            photo=open("lunch2.jpg", "rb"),
            caption="🥘 Комплексные обеды"
        )

    elif text == "🚚 Доставка":
        await update.message.reply_text(
        "🚚 ДОСТАВКА\n\n"
        "🕘 Понедельник–Пятница: 09:00–18:00\n"
        "🕘 Суббота–Воскресенье: 09:00–15:00\n\n"
        "💰 Минимальный заказ: от 900 ₽\n\n"
        "📍 Доставка во все районы г. Донецка\n\n"
        "📞 Для уточнения времени доставки:\n"
        "+7 949 605-30-96"
    )

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
            "🕒 РЕЖИМ РАБОТЫ\n\n"
            "• Понедельник – Пятница: 08:00 – 19:00\n\n"
            "• Суббота – Воскресенье: 08:00 – 16:00\n\n"
            "❤️ Будем рады видеть вас в нашей столовой!"
        )

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
        "📞 КОНТАКТЫ\n\n"
        "🏠 Столовая «Щи-Борщи»\n\n"
        "📍 Адрес:\n"
        "г. Донецк, ул. Калинина, 104\n\n"
        "📞 Телефон:\n"
        "+7 949 605-30-96\n\n"
        "🚚 Доставка по всем районам г. Донецка\n\n"
        "❤️ Спасибо, что выбираете нас!"
    )

    else:
        await update.message.reply_text("Спасибо! Мы получили ваше сообщение.")
init_db()
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("send", send)],
    states={
        WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast)]
    },
    fallbacks=[],
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()