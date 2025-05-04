import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import together_ai_sdk  # Импортируем SDK для Together AI
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение токенов из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Используем ключ от Together AI

# Инициализация клиента Together AI
client = together_ai_sdk.Client(api_key=TOGETHER_API_KEY)

# Обработчик входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Получено сообщение от пользователя: {user_message}")

    try:
        # Используем метод для отправки запроса к Together AI
        response = client.chat.create(
            model="together-ai-gpt-3.5",  # Используй модель, предоставленную Together AI
            messages=[{"role": "user", "content": user_message}]
        )

        # Отправляем ответ пользователю
        reply_text = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply_text)
    except Exception as e:
        logging.error(f"Ошибка при запросе к Together AI: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# Основная функция запуска бота
if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN or not TOGETHER_API_KEY:
        raise ValueError("Переменные окружения TELEGRAM_BOT_TOKEN и TOGETHER_API_KEY обязательны!")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен и готов принимать сообщения.")
    app.run_polling()
