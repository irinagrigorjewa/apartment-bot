import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # задайте через переменную окружения
CHAT_ID = os.getenv("CHAT_ID")                # ID вашего Telegram

logging.basicConfig(level=logging.INFO)

# Пример команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

# Функция поиска квартир (простой пример)
def fetch_apartments():
    url = "https://realt.by/rent/flat-for-long/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".bd-item")[:3]  # пример: берем первые 3 квартиры
    return [item.get_text(strip=True) for item in items]

# Команда для отправки новых квартир
async def check_apartments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = fetch_apartments()
    if results:
        for apt in results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=apt)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ничего не найдено")

# Главная функция запуска
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_apartments))

    await app.run_polling()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())

