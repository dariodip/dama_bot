import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Start command requested by {update.effective_user.first_name}")
    await update.message.reply_text(f"Ciao {update.effective_user.first_name}! Sono DamaBot")
