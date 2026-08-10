from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools.free_day import register_free_day_tools
from dama_bot.database.models import FreeDayDB


@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    register_free_day_tools(reg, service_mock)
    return reg


@pytest.mark.asyncio
async def test_create_free_day_tool(registry, service_mock):
    future_dt = date.today() + timedelta(days=2)
    future_str = future_dt.isoformat()

    db_free_day = FreeDayDB(date=future_dt, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = f'{{"date": "{future_str}"}}'
    res = await registry.execute("free_day-create", args_json, ctx, app_mock)

    assert res.success is True
    assert "Giorno libero registrato con successo" in res.message
    service_mock.create_free_day.assert_called_once()

@pytest.mark.asyncio
async def test_is_a_free_day(registry, service_mock):
    test_date = date.today() + timedelta(days=2)
    test_str = test_date.isoformat()

    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = f'{{"date": "{test_str}"}}'
    res = await registry.execute("free_day-is_a_free_day", args_json, ctx, app_mock)

    assert res.success is True
    assert "non" not in res.message
    service_mock.is_a_free_day.assert_called_once()


@pytest.mark.asyncio
async def test_is_not_a_free_day(registry, service_mock):
    test_date = date(2025, 12, 25)
    next_day = test_date + timedelta(days=1)
    test_str = next_day.isoformat()

    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = f'{{"date": "{test_str}"}}'
    res = await registry.execute("free_day-is_a_free_day", args_json, ctx, app_mock)

    assert res.success is True
    service_mock.is_a_free_day.assert_called_once()

@pytest.mark.asyncio
async def test_tool_next_free_day(registry, service_mock):
    test_date = date.today() - timedelta(days=-1)
    expected_date = test_date + timedelta(days=2)

    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day

    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    args_json = '{}'
    res = await registry.execute("free_day-next", args_json, ctx, app_mock)
    assert res.success is True
    assert "Il prossimo giorno libero è il" in res.message
