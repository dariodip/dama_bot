import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.config import get_version
from dama_bot.i18n import get_translation, normalize_language

logger = logging.getLogger(__name__)


async def version(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    logger.info(f"Version command requested by {update.effective_user.first_name}")
    lang = normalize_language(update.effective_user.language_code)
    _ = get_translation(lang).gettext
    await update.message.reply_text(_("Dama Bot {version}").format(version=get_version()))
