import logging

from dama_bot.bot import create_application

from .handlers import register_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    app = create_application()
    register_handlers(app)
    logger.info("Starting bot polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
