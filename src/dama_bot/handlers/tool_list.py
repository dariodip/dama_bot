import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def tool_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Tool list command requested by {update.effective_user.first_name}")

    registry = context.application.bot_data["registry"]
    tools = ""
    for tool in registry.get_tools():
        tools += f"- {tool}\n"

    await update.message.reply_text(f"These are the tools I can use:\n{tools}")
