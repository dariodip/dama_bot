import logging
from pathlib import Path

from telegram.ext import Application

from dama_bot.agent.loader import PluginLoader
from dama_bot.agent.registry import ToolRegistry
from dama_bot.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


async def post_init(application: Application):
    # Initialize the plugin loader globally here or attach it to the application bot_data
    registry = ToolRegistry()
    config_path = Path("settings.toml")
    loader = PluginLoader(registry, config_path)
    loader.load_plugins()

    application.bot_data["registry"] = registry

    # Call on_start on all plugins
    for plugin in loader.plugins:
        if hasattr(plugin, "on_start"):
            await plugin.on_start(application)

    # Initialize database schema *after* plugins have imported their models
    from dama_bot.database.connection import engine
    from dama_bot.database.models import Base

    Base.metadata.create_all(engine)


async def error_handler(update, context):
    logger.exception("Exception while handling update", exc_info=context.error)


def create_application() -> Application:
    return Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
