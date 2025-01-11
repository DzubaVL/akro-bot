from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os  # Новый импорт

# Словарь для хранения данных
payments = {}

# Команда /start
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я бот для учета оплат за занятия по акробатике.\n\n"
        "Чтобы сообщить об оплате, напишите:\n"
        "- Сумма оплаты\n"
        "- Фамилия и имя ребенка\n"
        "- Прикрепите чек или скриншот оплаты."
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    text = update.message.text
    if user_id not in payments:
        payments[user_id] = {"amount": None, "child": None, "receipt": None}

    if not payments[user_id]["amount"]:
        payments[user_id]["amount"] = text
        await update.message.reply_text("Введите фамилию и имя ребенка.")
    elif not payments[user_id]["child"]:
        payments[user_id]["child"] = text
        await update.message.reply_text("Теперь загрузите чек или скриншот.")
    else:
        await update.message.reply_text("Ожидаю загрузки чека.")

# Обработка изображений
async def handle_photo(update: Update, context):
    user_id = update.effective_user.id
    if user_id in payments and payments[user_id]["amount"] and payments[user_id]["child"]:
        # Получаем File ID изображения
        file_id = update.message.photo[-1].file_id
        payments[user_id]["receipt"] = file_id

        # Скачиваем изображение и пересылаем администратору
        admin_id = 607926528  # Твой Telegram ID
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"Новый платеж от пользователя:\n"
                f"- Сумма: {payments[user_id]['amount']}\n"
                f"- Ребенок: {payments[user_id]['child']}\n"
                f"- Чек: см. изображение ниже"
            )
        )
        await context.bot.send_photo(chat_id=admin_id, photo=file_id)

        # Подтверждаем пользователю
        await update.message.reply_text("Спасибо! Информация об оплате отправлена тренеру. При оплате следующего занятия напишите сумму платежа, бот автоматически включится.")
        payments.pop(user_id)
    else:
        await update.message.reply_text("Сначала укажите сумму и имя ребенка.")

# Запуск бота
app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()  # Загружаем токен из переменной окружения
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Бот запущен!")
app.run_polling()
