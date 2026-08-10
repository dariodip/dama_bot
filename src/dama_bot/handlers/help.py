import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

HELP_TEXT = """
Comandi disponibili:

/start: avvia il bot
/help: stampa questo messaggio di aiuto
/version: stampa la versione del bot
"""


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Help command requested by {update.effective_user.first_name}")
    await update.message.reply_text(HELP_TEXT)
