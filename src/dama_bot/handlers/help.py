import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.i18n import get_translation, normalize_language

logger = logging.getLogger(__name__)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    logger.info(f"Help command requested by {update.effective_user.first_name}")
    lang = normalize_language(update.effective_user.language_code)
    _ = get_translation(lang).gettext
    await update.message.reply_text(
        _(
            "Available commands:\n\n"
            "/start: start the bot\n"
            "/help: print this help message\n"
            "/version: print the bot version\n"
            "/tools: list available tools\n"
        )
    )
