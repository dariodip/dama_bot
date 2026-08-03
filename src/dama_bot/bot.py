from telegram.ext import Application
from dama_bot.config import TELEGRAM_BOT_TOKEN

def create_application() -> Application:
    return Application.builder().token(TELEGRAM_BOT_TOKEN).build()
