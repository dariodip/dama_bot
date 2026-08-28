from datetime import date
from unittest.mock import MagicMock

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.plugins.garbage.service import MULTIMATERIALE, GarbageService
from dama_bot.plugins.garbage.tools import get_garbage_tools


@pytest.fixture
def service_mock():
    return GarbageService()


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    for tool in get_garbage_tools(service_mock):
        reg.register_tool(tool)
    return reg


@pytest.mark.asyncio
async def test_garbage_tool_type_for_day(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_garbage = MULTIMATERIALE

    args_json = f'{{"date": "{test_str}"}}'
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("garbage-get_garbage_type_for_day", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert f"The garbage type for {test_str} is {expected_garbage}" in res_en.message
    assert res_en.data["garbage_type"] == expected_garbage

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("garbage-get_garbage_type_for_day", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert f"Il tipo di rifiuto per il {test_str} è {expected_garbage}" in res_it.message
    assert res_it.data["garbage_type"] == expected_garbage


@pytest.mark.asyncio
async def test_garbage_tool_is_not_indifferenziato_week(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_indifferenziato_week = False

    args_json = f'{{"date": "{test_str}"}}'
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert f"The week of {test_str} is not an indifferenziata week" in res_en.message
    assert res_en.data["is_indifferenziato_week"] == expected_indifferenziato_week

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert f"La settimana del {test_str} non è una settimana dell'indifferenziata" in res_it.message
    assert res_it.data["is_indifferenziato_week"] == expected_indifferenziato_week


@pytest.mark.asyncio
async def test_garbage_tool_is_indifferenziato_week(registry, service_mock):
    test_date = date(2026, 8, 17)
    test_str = test_date.isoformat()
    expected_indifferenziato_week = True

    args_json = f'{{"date": "{test_str}"}}'
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="dario", language="en")
    res_en = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert f"The week of {test_str} is an indifferenziata week" in res_en.message
    assert res_en.data["is_indifferenziato_week"] == expected_indifferenziato_week

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="dario", language="it")
    res_it = await registry.execute("garbage-is_indifferenziato_week", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert f"La settimana del {test_str} è una settimana dell'indifferenziata" in res_it.message
    assert res_it.data["is_indifferenziato_week"] == expected_indifferenziato_week
