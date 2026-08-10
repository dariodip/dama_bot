import logging

from telegram.ext import Application

from dama_bot.config import TELEGRAM_BOT_TOKEN
from dama_bot.handlers.reminders.scheduler import restore_pending_reminders

logger = logging.getLogger(__name__)


async def post_init(application: Application):
    restore_pending_reminders(application)


async def error_handler(update, context):
    logger.exception("Exception while handling update", exc_info=context.error)


def create_application() -> Application:
    return Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
