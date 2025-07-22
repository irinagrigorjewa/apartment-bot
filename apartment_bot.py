import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler
import schedule
import time
import threading

# 🔑 Токен и твой Telegram ID
TELEGRAM_TOKEN = '7600421133:AAHGaWINYagwEyS2WzEfaowsbreFvoZ9rWQ'
YOUR_CHAT_ID = '603000026'
MAX_PRICE = 360

bot = Bot(token=TELEGRAM_TOKEN)

# 🔍 1. Kufar
def get_kufar_listings():
    url = 'https://www.kufar.by/l/rent/minsk?cmp=1&cur=USD&prc=r%3A0%3B360'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for item in soup.select('a[data-testid="listing-card-link"]'):
        title = item.select_one('h3')
        price = item.select_one('p span')
        link = 'https://www.kufar.by' + item['href']
        if title and price:
            results.append(f"🏡 Kufar\n{title.text.strip()}\n💵 {price.text.strip()}\n🔗 {link}")
    return results

# 🔍 2. Realt.by
def get_realt_listings():
    url = 'https://realt.by/rent/flat-for-long/?currency=usd&rent_type%5B%5D=2&city=494&page=1&price%5Bmax%5D=360'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for card in soup.select('div[class*=teaser-title] a[href*="/object/"]'):
        title = card.text.strip()
        link = "https://realt.by" + card['href']
        price = card.find_parent("div").find_next_sibling("div")
        price_text = price.text.strip() if price else "Цена не указана"
        results.append(f"🏡 Realt.by\n{title}\n💵 {price_text}\n🔗 {link}")
    return results

# 🔍 3. Onliner.by
def get_onliner_listings():
    url = 'https://r.onliner.by/ak/?rent_type%5B%5D=1&currency=usd&price%5Bmax%5D=360&city[minsk]=true'
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for card in soup.select('div[class*="classified"]'):
        title = card.select_one('a[class*="classified__title"]')
        price = card.select_one('div[class*="classified__price"]')
        if title and price:
            link = title['href']
            results.append(f"🏡 Onliner\n{title.text.strip()}\n💵 {price.text.strip()}\n🔗 {link}")
    return results

# 🔍 4. Domovita.by
def get_domovita_listings():
    url = 'https://domovita.by/minsk/flats/rent?currency=usd&priceMax=360'
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for card in soup.select('a.card'):
        title = card.select_one('h2')
        price = card.select_one('.price')
        if title and price:
            link = 'https://domovita.by' + card['href']
            results.append(f"🏡 Domovita\n{title.text.strip()}\n💵 {price.text.strip()}\n🔗 {link}")
    return results

# 🔔 Объединённая отправка
def send_new_listings():
    all_listings = (
        get_kufar_listings() +
        get_realt_listings() +
        get_onliner_listings() +
        get_domovita_listings()
    )

    # Удалим дубли и отправим только первые 10 новых
    seen = set()
    unique_listings = []
    for item in all_listings:
        if item not in seen:
            seen.add(item)
            unique_listings.append(item)

    if unique_listings:
        for listing in unique_listings[:10]:
            bot.send_message(chat_id=YOUR_CHAT_ID, text=listing)
    else:
        bot.send_message(chat_id=YOUR_CHAT_ID, text="Новых квартир не найдено.")

# Команда /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🔍 Бот отслеживает аренду квартир до $360 в Минске.")

# Планировщик
def schedule_checker():
    schedule.every(60).minutes.do(send_new_listings)
    while True:
        schedule.run_pending()
        time.sleep(5)

# Основной запуск
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    thread = threading.Thread(target=schedule_checker)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

