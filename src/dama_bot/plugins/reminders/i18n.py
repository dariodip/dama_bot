import gettext
from pathlib import Path

from dama_bot.i18n import normalize_language

LOCALES_DIR = Path(__file__).parent / "locales"


def get_translation(lang: str | None = None) -> gettext.NullTranslations:
    normalized = normalize_language(lang)
    return gettext.translation(
        domain="reminders",
        localedir=str(LOCALES_DIR),
        languages=[normalized],
        fallback=True,
    )
