from datetime import datetime, timedelta
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.plugins.reminders.models import ReminderDB
from dama_bot.plugins.reminders.tools import get_reminder_tools


@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    for tool in get_reminder_tools(service_mock):
        reg.register_tool(tool)
    return reg


@pytest.mark.asyncio
async def test_create_reminder_tool(registry, service_mock):
    future_dt = datetime.now(ZoneInfo("Europe/Rome")) + timedelta(hours=2)
    future_str = future_dt.isoformat()

    db_reminder = ReminderDB(id=10, text=" dentist appointment ", remind_at=future_dt, chat_id=123)
    service_mock.create_reminder.return_value = db_reminder

    app_mock = MagicMock()
    args_json = f'{{"text": "dentist appointment", "remind_at": "{future_str}"}}'

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("reminder-create", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "Reminder successfully created" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("reminder-create", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "Promemoria creato con successo" in res_it.message
    assert service_mock.create_reminder.call_count == 2


@pytest.mark.asyncio
async def test_create_reminder_tool_past_validation(registry, service_mock):
    past_dt = datetime.now(ZoneInfo("Europe/Rome")) - timedelta(hours=2)
    past_str = past_dt.isoformat()

    app_mock = MagicMock()
    args_json = f'{{"text": "past task", "remind_at": "{past_str}"}}'

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("reminder-create", args_json, ctx_en, app_mock)
    assert res_en.success is False
    assert "in the past" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("reminder-create", args_json, ctx_it, app_mock)
    assert res_it.success is False
    assert "nel passato" in res_it.message
    service_mock.create_reminder.assert_not_called()


@pytest.mark.asyncio
async def test_list_reminders_tool(registry, service_mock):
    reminders = [
        ReminderDB(id=1, text="task 1", remind_at=datetime.now(), chat_id=123),
        ReminderDB(id=2, text="task 2", remind_at=datetime.now(), chat_id=123),
    ]
    service_mock.list_reminders.return_value = reminders

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("reminder-list", "{}", ctx_en, None)
    assert res_en.success is True
    assert "Here are your active reminders" in res_en.message
    assert "task 1" in res_en.message
    assert "task 2" in res_en.message
    assert len(res_en.data["reminders"]) == 2

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("reminder-list", "{}", ctx_it, None)
    assert res_it.success is True
    assert "Ecco i tuoi promemoria attivi" in res_it.message


@pytest.mark.asyncio
async def test_delete_reminder_tool(registry, service_mock):
    service_mock.delete_reminder.return_value = True
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("reminder-delete", '{"reminder_id": 1}', ctx_en, app_mock)
    assert res_en.success is True
    assert "Reminder 1 successfully deleted." in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("reminder-delete", '{"reminder_id": 1}', ctx_it, app_mock)
    assert res_it.success is True
    assert "Promemoria 1 eliminato con successo." in res_it.message


@pytest.mark.asyncio
async def test_update_reminder_tool(registry, service_mock):
    future_dt = datetime.now(ZoneInfo("Europe/Rome")) + timedelta(hours=2)
    updated_db = ReminderDB(id=1, text="updated task", remind_at=future_dt, chat_id=123)
    service_mock.update_reminder.return_value = updated_db

    app_mock = MagicMock()
    args_json = (
        f'{{"reminder_id": 1, "text": "updated task", "remind_at": "{future_dt.isoformat()}"}}'
    )

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("reminder-update", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "Reminder 1 successfully updated" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("reminder-update", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "Promemoria 1 aggiornato con successo" in res_it.message
