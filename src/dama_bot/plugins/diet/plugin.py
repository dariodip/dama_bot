from typing import Any

from dama_bot.agent.plugin import Plugin, Tool
from dama_bot.plugins.diet.repository import DietRepository
from dama_bot.plugins.diet.service import DietService
from dama_bot.plugins.diet.tools import get_diet_tools


class DietPlugin(Plugin):
    @property
    def name(self) -> str:
        return "diet"

    @property
    def description(self) -> str:
        return "Gestione della dieta e dei pasti"

    def get_tools(self) -> list[Tool]:
        repository = DietRepository()
        service = DietService(repository)
        return get_diet_tools(service)

    async def on_start(self, application: Any) -> None:
        pass


def get_plugin() -> Plugin:
    return DietPlugin()
