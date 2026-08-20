from typing import Any

from dama_bot.agent.plugin import Plugin, Tool
from dama_bot.plugins.garbage.service import GarbageService
from dama_bot.plugins.garbage.tools import get_garbage_tools


class GarbagePlugin(Plugin):
    @property
    def name(self) -> str:
        return "garbage"

    @property
    def description(self) -> str:
        return "Gestione della raccolta differenziata"

    def get_tools(self) -> list[Tool]:
        service = GarbageService()
        return get_garbage_tools(service)

    async def on_start(self, application: Any) -> None:
        pass


def get_plugin() -> Plugin:
    return GarbagePlugin()
