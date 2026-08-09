from datetime import datetime, timedelta
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools import register_reminder_tools
from dama_bot.database.models import ReminderDB


@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    register_reminder_tools(reg, service_mock)
    return reg


@pytest.mark.asyncio
async def test_create_reminder_tool(registry, service_mock):
    future_dt = datetime.now(ZoneInfo("Europe/Rome")) + timedelta(hours=2)
    future_str = future_dt.isoformat()

    db_reminder = ReminderDB(id=10, text=" dentist appointment ", remind_at=future_dt, chat_id=123)
    service_mock.create_reminder.return_value = db_reminder

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = f'{{"text": "dentist appointment", "remind_at": "{future_str}"}}'
    res = await registry.execute("reminder.create", args_json, ctx, app_mock)

    assert res.success is True
    assert "Promemoria creato con successo" in res.message
    service_mock.create_reminder.assert_called_once()


@pytest.mark.asyncio
async def test_create_reminder_tool_past_validation(registry, service_mock):
    past_dt = datetime.now(ZoneInfo("Europe/Rome")) - timedelta(hours=2)
    past_str = past_dt.isoformat()

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = f'{{"text": "past task", "remind_at": "{past_str}"}}'
    res = await registry.execute("reminder.create", args_json, ctx, app_mock)

    assert res.success is False
    assert "nel passato" in res.message
    service_mock.create_reminder.assert_not_called()


@pytest.mark.asyncio
async def test_list_reminders_tool(registry, service_mock):
    reminders = [
        ReminderDB(id=1, text="task 1", remind_at=datetime.now(), chat_id=123),
        ReminderDB(id=2, text="task 2", remind_at=datetime.now(), chat_id=123),
    ]
    service_mock.list_reminders.return_value = reminders

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    res = await registry.execute("reminder.list", "{}", ctx, None)

    assert res.success is True
    assert "task 1" in res.message
    assert "task 2" in res.message
    assert len(res.data["reminders"]) == 2


@pytest.mark.asyncio
async def test_delete_reminder_tool(registry, service_mock):
    service_mock.delete_reminder.return_value = True

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    res = await registry.execute("reminder.delete", '{"reminder_id": 1}', ctx, app_mock)

    assert res.success is True
    assert "eliminato con successo" in res.message
    service_mock.delete_reminder.assert_called_once_with(
        reminder_id=1, chat_id=123, username="dario", application=app_mock
    )


@pytest.mark.asyncio
async def test_update_reminder_tool(registry, service_mock):
    future_dt = datetime.now(ZoneInfo("Europe/Rome")) + timedelta(hours=2)
    updated_db = ReminderDB(id=1, text="updated task", remind_at=future_dt, chat_id=123)
    service_mock.update_reminder.return_value = updated_db

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = (
        f'{{"reminder_id": 1, "text": "updated task", "remind_at": "{future_dt.isoformat()}"}}'
    )
    res = await registry.execute("reminder.update", args_json, ctx, app_mock)

    assert res.success is True
    assert "aggiornato con successo" in res.message
    service_mock.update_reminder.assert_called_once()
