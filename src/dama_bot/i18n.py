import gettext
from pathlib import Path

from dama_bot.config import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

LOCALES_DIR = Path(__file__).parent / "locales"


def normalize_language(lang_code: str | None) -> str:
    if not lang_code:
        return DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES else "en"
    code = lang_code.split("-")[0].split("_")[0].lower()
    if code in SUPPORTED_LANGUAGES:
        return code
    return DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES else "en"


def get_translation(
    lang: str | None = None, domain: str = "dama_bot", locales_dir: Path = LOCALES_DIR
) -> gettext.NullTranslations:
    normalized = normalize_language(lang)
    return gettext.translation(
        domain=domain,
        localedir=str(locales_dir),
        languages=[normalized],
        fallback=True,
    )
