import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.i18n import get_translation, normalize_language

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    logger.info(f"Start command requested by {update.effective_user.first_name}")
    lang = normalize_language(update.effective_user.language_code)
    first_name = update.effective_user.first_name or ""
    _ = get_translation(lang).gettext
    await update.message.reply_text(
        _("Hello {name}! I am DamaBot and I am here to help you.").format(name=first_name)
    )
