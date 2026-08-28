import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.i18n import get_translation, normalize_language

logger = logging.getLogger(__name__)


async def tool_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    logger.info(f"Tool list command requested by {update.effective_user.first_name}")
    lang = normalize_language(update.effective_user.language_code)
    _ = get_translation(lang).gettext

    registry = context.application.bot_data["registry"]
    tools = ""
    for tool in registry.get_tools():
        tools += f"- {tool}\n"

    msg = _("These are the tools I can use:\n{tools}").format(tools=tools)
    await update.message.reply_text(msg)
