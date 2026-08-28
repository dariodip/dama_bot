import re
import sys
from pathlib import Path


def validate_plugin_name(name: str) -> bool:
    if not name:
        return False
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/new_plugin.py <plugin_name>")
        sys.exit(1)

    plugin_name = sys.argv[1]
    if not validate_plugin_name(plugin_name):
        print(f"Error: Invalid plugin name '{plugin_name}'. It must be a valid Python identifier.")
        sys.exit(1)

    base_dir = Path(__file__).resolve().parent.parent / "src" / "dama_bot" / "plugins" / plugin_name

    if base_dir.exists():
        print(f"Error: Plugin '{plugin_name}' already exists at {base_dir}")
        sys.exit(1)

    try:
        base_dir.mkdir(parents=True)
    except Exception as e:
        print(f"Error creating plugin directory: {e}")
        sys.exit(1)

    # Create __init__.py
    (base_dir / "__init__.py").write_text(f'"""{plugin_name.capitalize()} plugin."""\n')

    # Create i18n.py
    i18n_code = f"""import gettext
from pathlib import Path

from dama_bot.i18n import normalize_language

LOCALES_DIR = Path(__file__).parent / "locales"


def get_translation(lang: str | None = None) -> gettext.NullTranslations:
    normalized = normalize_language(lang)
    return gettext.translation(
        domain="{plugin_name}",
        localedir=str(LOCALES_DIR),
        languages=[normalized],
        fallback=True,
    )
"""
    (base_dir / "i18n.py").write_text(i18n_code)

    # Create locales directories and initial po files
    for lang in ["en", "it"]:
        po_dir = base_dir / "locales" / lang / "LC_MESSAGES"
        po_dir.mkdir(parents=True, exist_ok=True)
        if lang == "it":
            example_msgstr = "Esempio strumento eseguito con argomento: {arg}"
        else:
            example_msgstr = "Example tool executed with arg: {arg}"
        po_content = f"""msgid ""
msgstr ""
"Project-Id-Version: dama_bot-{plugin_name} 0.1.0\\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

msgid "Example tool executed with arg: {{arg}}"
msgstr "{example_msgstr}"
"""
        (po_dir / f"{plugin_name}.po").write_text(po_content)

    # Create tools.py
    tools_code = f"""import logging
from typing import Any

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.{plugin_name}.i18n import get_translation

logger = logging.getLogger(__name__)

class ExampleToolArgs(BaseModel):
    example_arg: str = Field(..., description="An example argument")

def get_{plugin_name}_tools() -> list[Tool]:
    async def example_tool(
        args: ExampleToolArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            return ToolResult(
                success=True,
                message=_("Example tool executed with arg: {{arg}}").format(arg=args.example_arg),
            )
        except Exception as e:
            logger.exception("Error in example_tool")
            return ToolResult(
                success=False,
                message=f"Error executing example tool: {{str(e)}}",
            )

    return [
        FunctionTool(
            name="{plugin_name}-example_tool",
            description="An example tool for the {plugin_name} plugin.",
            args_schema=ExampleToolArgs,
            func=example_tool,
        ),
    ]
"""
    (base_dir / "tools.py").write_text(tools_code)

    # Create plugin.py
    plugin_code = f"""from dama_bot.agent.plugin import Plugin, Tool
from dama_bot.plugins.{plugin_name}.tools import get_{plugin_name}_tools

class {plugin_name.capitalize()}Plugin:
    @property
    def name(self) -> str:
        return "{plugin_name}"

    @property
    def description(self) -> str:
        return "{plugin_name.capitalize()} plugin description"

    def get_tools(self) -> list[Tool]:
        return get_{plugin_name}_tools()

def get_plugin() -> Plugin:
    return {plugin_name.capitalize()}Plugin()
"""
    (base_dir / "plugin.py").write_text(plugin_code)

    print(f"Success! Plugin '{plugin_name}' created at {base_dir}")
    print("Run `make compile-locales` to compile newly created translation catalogs.")
    print("Don't forget to enable it in settings.toml!")


if __name__ == "__main__":
    main()
