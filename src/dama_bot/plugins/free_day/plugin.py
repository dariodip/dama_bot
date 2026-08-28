from typing import Any

from dama_bot.agent.plugin import Plugin, Tool
from dama_bot.database.connection import SessionLocal
from dama_bot.plugins.free_day import (
    models,  # noqa: F401 - ensures FreeDayDB is registered with Base
)
from dama_bot.plugins.free_day.repository import FreeDayRepository
from dama_bot.plugins.free_day.service import FreeDayService
from dama_bot.plugins.free_day.tools import get_free_day_tools


class FreeDayPlugin(Plugin):
    @property
    def name(self) -> str:
        return "free_day"

    @property
    def description(self) -> str:
        return "Gestione dei giorni liberi"

    def get_tools(self) -> list[Tool]:
        repository = FreeDayRepository(SessionLocal)
        service = FreeDayService(repository)
        return get_free_day_tools(service)

    async def on_start(self, application: Any) -> None:
        pass


def get_plugin() -> Plugin:
    return FreeDayPlugin()
