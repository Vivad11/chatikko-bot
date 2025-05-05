import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from together import Together

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение токенов
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Проверка переменных окружения
if not TELEGRAM_BOT_TOKEN or not TOGETHER_API_KEY:
    raise ValueError("Переменные окружения TELEGRAM_BOT_TOKEN и TOGETHER_API_KEY обязательны!")

# Инициализация Together AI
client = Together(api_key=TOGETHER_API_KEY)

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Получено сообщение от пользователя: {user_message}")

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=200,
        )
        reply_text = response.choices[0].message.content.strip()
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Ошибка при ответе от Together AI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке. Попробуйте позже.")

# Запуск бота
def main():
    logging.info("Запуск Telegram-бота...")

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен и готов принимать сообщения.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
