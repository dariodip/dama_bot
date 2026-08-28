from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.plugins.free_day.models import FreeDayDB
from dama_bot.plugins.free_day.tools import get_free_day_tools


@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    for tool in get_free_day_tools(service_mock):
        reg.register_tool(tool)
    return reg


@pytest.mark.asyncio
async def test_create_free_day_tool(registry, service_mock):
    future_dt = date.today() + timedelta(days=2)
    future_str = future_dt.isoformat()

    db_free_day = FreeDayDB(date=future_dt, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day

    app_mock = MagicMock()
    args_json = f'{{"date": "{future_str}"}}'

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("free_day-create", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "Free day successfully registered" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("free_day-create", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "Giorno libero registrato con successo" in res_it.message


@pytest.mark.asyncio
async def test_is_a_free_day(registry, service_mock):
    test_date = date.today() + timedelta(days=2)
    test_str = test_date.isoformat()

    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    service_mock.create_free_day.return_value = db_free_day
    service_mock.is_a_free_day.return_value = True

    app_mock = MagicMock()
    args_json = f'{{"date": "{test_str}"}}'

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("free_day-is_a_free_day", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "is a free day" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("free_day-is_a_free_day", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "è libero" in res_it.message
    assert "non" not in res_it.message


@pytest.mark.asyncio
async def test_is_not_a_free_day(registry, service_mock):
    test_date = date(2025, 12, 25)
    next_day = test_date + timedelta(days=1)
    test_str = next_day.isoformat()

    service_mock.is_a_free_day.return_value = False

    app_mock = MagicMock()
    args_json = f'{{"date": "{test_str}"}}'

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("free_day-is_a_free_day", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "is not a free day" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("free_day-is_a_free_day", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "non è libero" in res_it.message


@pytest.mark.asyncio
async def test_tool_next_free_day(registry, service_mock):
    test_date = date.today() + timedelta(days=1)
    service_mock.next_free_day.return_value = test_date

    app_mock = MagicMock()
    args_json = "{}"

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("free_day-next", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert "The next free day is" in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("free_day-next", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert "Il prossimo giorno libero è il" in res_it.message
