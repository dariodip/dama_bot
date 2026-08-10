import os

from dotenv import load_dotenv

env = os.getenv("APP_ENV", "dev")
if env != "prod":
    load_dotenv(f".env.{env}")
else:
    load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///data/dama_bot.sqlite3")
