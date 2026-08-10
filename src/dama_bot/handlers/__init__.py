from telegram.ext import Application, CommandHandler, MessageHandler, filters

from dama_bot.handlers.help import help
from dama_bot.handlers.start import start
from dama_bot.handlers.version import version


def register_handlers(app: Application) -> None:
    from dama_bot.handlers.message_handler import handle_agent_message

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("version", version))
    # Route all non-command text messages to the Agent
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_agent_message))
