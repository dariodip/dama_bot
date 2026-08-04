from telegram.ext import Application, CommandHandler

from dama_bot.handlers.start import start
from dama_bot.handlers.help import help
from dama_bot.handlers.reminders import remind

def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("remind", remind))