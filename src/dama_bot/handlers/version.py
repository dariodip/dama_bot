import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.config import get_version

logger = logging.getLogger(__name__)


async def version(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Version command requested by {update.effective_user.first_name}")
    await update.message.reply_text(f"Dama Bot v{get_version()}")
