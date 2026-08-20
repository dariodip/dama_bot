import importlib
import logging
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from dama_bot.agent.plugin import Plugin
from dama_bot.agent.registry import ToolRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    def __init__(self, registry: ToolRegistry, config_path: Path):
        self.registry = registry
        self.config_path = config_path
        self.plugins: list[Plugin] = []

    def load_plugins(self) -> None:
        if not self.config_path.exists():
            logger.warning(f"Plugin configuration not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            logger.error(f"Failed to parse plugin config: {e}")
            return

        enabled_plugins = config.get("plugins", {}).get("enabled", [])

        for plugin_name in enabled_plugins:
            try:
                # Expecting the plugin to be accessible via dama_bot.plugins.<name>.plugin
                module_name = f"dama_bot.plugins.{plugin_name}.plugin"
                module = importlib.import_module(module_name)

                # The module must expose a 'get_plugin' function that returns a Plugin instance
                if hasattr(module, "get_plugin"):
                    plugin: Plugin = module.get_plugin()
                    logger.info(f"Loading plugin '{plugin.name}'")
                    self.plugins.append(plugin)
                    for tool in plugin.get_tools():
                        self.registry.register_tool(tool)
                        logger.debug(f"Registered tool '{tool.name}' from plugin '{plugin.name}'")
                else:
                    logger.error(
                        f"Plugin module '{module_name}' does not expose a 'get_plugin' function"
                    )
            except Exception as e:
                logger.exception(f"Failed to load plugin '{plugin_name}': {e}")
