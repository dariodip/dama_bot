import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.agent.core import Agent
from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools import register_reminder_tools
from dama_bot.database.connection import SessionLocal
from dama_bot.database.repository import ReminderRepository
from dama_bot.services.reminder import ReminderService

logger = logging.getLogger(__name__)

# Initialize dependencies and agent
repository = ReminderRepository(SessionLocal)
service = ReminderService(repository)
registry = ToolRegistry()
register_reminder_tools(registry, service)
agent = Agent(registry)


async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generic message entry point that routes text messages to the Agent."""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    user_context = UserContext(user_id=user_id, chat_id=chat_id, username=username)

    logger.info(f"Received message from @{username} (chat {chat_id}): '{text}'")

    # Send typing status while processing
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        response = await agent.handle_message(
            message=text, user_context=user_context, application=context.application
        )
        await update.message.reply_text(response.message)
    except Exception:
        logger.exception("Error in handle_agent_message")
        await update.message.reply_text(
            "Scusa, si è verificato un errore imprevisto. Riprova più tardi."
        )
