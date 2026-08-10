import logging

from telegram import Update
from telegram.ext import ContextTypes

from dama_bot.agent.core import Agent
from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools.diet import register_diet_tools
from dama_bot.agent.tools.free_day import register_free_day_tools
from dama_bot.agent.tools.garbage import register_garbage_tools
from dama_bot.agent.tools.reminder import register_reminder_tools
from dama_bot.database.connection import SessionLocal
from dama_bot.database.repository import DietRepository, FreeDayRepository, ReminderRepository
from dama_bot.services.diet import DietService
from dama_bot.services.free_day import FreeDayService
from dama_bot.services.garbage import GarbageService
from dama_bot.services.reminder import ReminderService

logger = logging.getLogger(__name__)

registry = ToolRegistry()
# Initialize dependencies and agent
reminder_repository = ReminderRepository(SessionLocal)
reminder_service = ReminderService(reminder_repository)
register_reminder_tools(registry, reminder_service)

free_day_repository = FreeDayRepository(SessionLocal)
free_day_service = FreeDayService(free_day_repository)
register_free_day_tools(registry, free_day_service)

garbage_service = GarbageService()
register_garbage_tools(registry, garbage_service)

diet_repository = DietRepository()
diet_service = DietService(diet_repository)
register_diet_tools(registry, diet_service)

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
