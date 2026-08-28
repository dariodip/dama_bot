import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.agent.core import Agent
from dama_bot.agent.models import UserContext
from dama_bot.i18n import get_translation, normalize_language

logger = logging.getLogger(__name__)


async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generic message entry point that routes text messages to the Agent."""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else 0
    username = update.effective_user.username if update.effective_user else None
    raw_lang = update.effective_user.language_code if update.effective_user else None
    language = normalize_language(raw_lang)

    user_context = UserContext(
        user_id=user_id, chat_id=chat_id, username=username, language=language
    )

    logger.info(f"Received message from @{username} (chat {chat_id}, lang {language}): '{text}'")

    # Send typing status while processing
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        registry = context.application.bot_data["registry"]
        agent = Agent(registry)
        response = await agent.handle_message(
            message=text, user_context=user_context, application=context.application
        )
        await update.message.reply_text(response.message)
    except Exception:
        logger.exception("Error in handle_agent_message")
        _ = get_translation(language).gettext
        await update.message.reply_text(
            _("Sorry, an unexpected error occurred. Please try again later.")
        )
