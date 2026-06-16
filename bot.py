from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8635192315:AAHMavDFFCZmvpoyjh_tjuZggeCYGpwG8TI"

main_keyboard = [
    ["🍽 Меню", "🥘 Комплексные обеды"],
    ["🚕 Доставка", "📝 Сделать заказ"],
    ["📞 Контакты"]
]

markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Вас приветствует столовая «Щи-Борщи».\n\nВыберите нужный раздел:",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🍽 Меню":
        await update.message.reply_photo(
            photo=open("menu.jpg", "rb"),
            caption="🍽 Меню"
        )

    elif text == "🥘 Комплексные обеды":
        await update.message.reply_photo(
            photo=open("iunch.jpg", "rb"),
            caption="🥘 Комплексные обеды"
        )

    elif text == "🚚 Доставка":
        await update.message.reply_text(
            "🚚 Доставка работает с 8:00 до 18:00.\nМинимальный заказ: 1000 ₽."
        )

    elif text == "📝 Сделать заказ":
        await update.message.reply_text(
            "📝 Напишите заказ одним сообщением:\n\n"
            "Что хотите заказать\n"
            "Количество\n"
            "Адрес доставки\n"
            "Телефон"
        )

    elif text == "📞 Контакты":
        await update.message.reply_text(
            "📞 Телефон: +7 949 371-48-07\nАдрес: ул. Калинина 104"
        )

    else:
        await update.message.reply_text("Спасибо! Мы получили ваше сообщение.")
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()