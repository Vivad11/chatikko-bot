import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from together import Together
from threading import Thread

# Запуск простого Flask-сервера
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive"

@app_flask.route(f'/{os.getenv("TELEGRAM_BOT_TOKEN")}', methods=['POST'])
def webhook():
    data = request.get_json()
    logging.info(f"Received webhook data: {data}")  # Логирование полученных данных
    update = Update.de_json(data, app.bot)
    app.update_queue.put(update)
    return 'OK', 200

def run():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение токенов
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

# Обработчик
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Получено сообщение от пользователя: {user_message}")
    try:
        # Используем asyncio.to_thread для синхронного API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response.choices[0].message.content
        await update.message.reply_text(reply_text)
    except Exception as e:
        logging.error(f"Ошибка при запросе к Together AI: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# Запуск
if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN or not TOGETHER_API_KEY:
        raise ValueError("Нужны переменные TELEGRAM_BOT_TOKEN и TOGETHER_API_KEY")

    keep_alive()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Бот запущен и готов принимать сообщения.")
    
    # Webhook
    app.bot.set_webhook(f"https://{os.getenv('RENDER_URL')}/{TELEGRAM_BOT_TOKEN}")
    app.run_polling(drop_pending_updates=True)  # Убедись, что бот не пропустит сообщения
