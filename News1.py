import requests
from bs4 import BeautifulSoup
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_news(limit=None, section=None):
    headers = {
        "user-agent": "Mozilla/5.0 ...",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.google.com/"
    }
    url = "https://www.securitylab.ru/analytics/" if section == "research" else "https://www.securitylab.ru/news/"
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        articles_cards = soup.find_all("a", class_="article-card", limit=limit)
        news = []
        for article in articles_cards:
            title = article.find("h2").text.strip()
            desc = article.find("p").text.strip()
            url = 'https://www.securitylab.ru' + article.get("href")
            news.append(f"{title} - {url}\n{desc}\n")
        return news
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return [f"Не удалось получить статьи из-за ошибки HTTP: {str(e)}"]
    except requests.RequestException as e:
        logger.error(f"Request error occurred: {e}")
        return [f"Не удалось получить статьи из-за сетевой ошибки: {str(e)}"]
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}")
        return [f"При обработке данных произошла непредвиденная ошибка."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received command /start")
    keyboard = [
        [InlineKeyboardButton("Все новости", callback_data='all_news')],
        [InlineKeyboardButton("Последняя новость", callback_data='latest_news')],
        [InlineKeyboardButton("Статьи", callback_data='research')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = 'Выберите категорию контента:'
    if update.callback_query:
        await update.callback_query.message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Добро пожаловать в помощь бота! Вот список доступных команд:
    /start - начать работу и выбрать категорию новостей
    /help - получить информацию о возможностях и командах бота
    Выберите категорию новостей или введите команду для дальнейших действий.
    """
    await update.message.reply_text(help_text)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'back':
        await start(update, context)
        return

    news = get_news(section=choice)
    news_text = "Новости и статьи:\n\n" + "".join(news) if news else "Нет доступных статей или новостей."
    keyboard = [
        [InlineKeyboardButton("Все новости", callback_data='all_news')],
        [InlineKeyboardButton("Последняя новость", callback_data='latest_news')],
        [InlineKeyboardButton("Статьи", callback_data='research')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=news_text, reply_markup=reply_markup)

def main():
    TOKEN = '7186235226:AAHuXrQ9yzaOCkpqI4RCxbU-WPRN2eKxZe4'
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CallbackQueryHandler(button))

    logger.info("Bot is starting")
    app.run_polling()

if __name__ == '__main__':
    main()
