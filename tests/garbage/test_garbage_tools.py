from datetime import date
from unittest.mock import MagicMock

import pytest

import dama_bot.services.garbage as g
from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools.garbage import register_garbage_tools
from dama_bot.services.garbage import GarbageService


@pytest.fixture
def service_mock():
    return GarbageService()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    register_garbage_tools(reg, service_mock)
    return reg


@pytest.mark.asyncio
async def test_garbage_tool_type_for_day(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_garbage = g.MULTIMATERIALE

    args_json = f'{{"date": "{test_str}"}}'
    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    res = await registry.execute("garbage-get_garbage_type_for_day", args_json, ctx, app_mock)

    assert res.success is True
    assert f"Il tipo di rifiuto per il {test_str} è {expected_garbage}" in res.message
    assert res.data["garbage_type"] == expected_garbage


@pytest.mark.asyncio
async def test_garbage_tool_is_not_indifferenziato_week(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_indifferenziato_week = False

    args_json = f'{{"date": "{test_str}"}}'
    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    res = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx, app_mock)

    assert res.success is True
    assert f"La settimana del {test_str} non è una settimana dell'indifferenziata" in res.message
    assert res.data["is_indifferenziato_week"] == expected_indifferenziato_week


@pytest.mark.asyncio
async def test_garbage_tool_is_indifferenziato_week(registry, service_mock):
    test_date = date(2026, 8, 17)
    test_str = test_date.isoformat()
    expected_indifferenziato_week = True

    args_json = f'{{"date": "{test_str}"}}'
    ctx = UserContext(user_id=456, chat_id=123, username="dario")
    app_mock = MagicMock()

    res = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx, app_mock)

    assert res.success is True
    assert f"La settimana del {test_str} è una settimana dell'indifferenziata" in res.message
    assert res.data["is_indifferenziato_week"] == expected_indifferenziato_week
