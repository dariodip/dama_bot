from dama_bot.agent.plugin import Plugin, Tool
from dama_bot.database.connection import SessionLocal
from dama_bot.plugins.reminders import (
    models,  # noqa: F401 - ensures ReminderDB is registered with Base
)
from dama_bot.plugins.reminders.repository import ReminderRepository
from dama_bot.plugins.reminders.scheduler import restore_pending_reminders
from dama_bot.plugins.reminders.service import ReminderService
from dama_bot.plugins.reminders.tools import get_reminder_tools


class RemindersPlugin(Plugin):
    @property
    def name(self) -> str:
        return "reminders"

    @property
    def description(self) -> str:
        return "Gestione dei promemoria"

    def get_tools(self) -> list[Tool]:
        repository = ReminderRepository(SessionLocal)
        service = ReminderService(repository)
        return get_reminder_tools(service)

    async def on_start(self, application) -> None:
        restore_pending_reminders(application)


def get_plugin() -> Plugin:
    return RemindersPlugin()
