from datetime import date
from unittest.mock import MagicMock

import pytest

from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.plugins.diet.models import Meal, MealDay, MealType
from dama_bot.plugins.diet.repository import DietRepository
from dama_bot.plugins.diet.service import DietService
from dama_bot.plugins.diet.tools import get_diet_tools


@pytest.fixture
def service_mock():
    return DietService(DietRepository())


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    for tool in get_diet_tools(service_mock):
        reg.register_tool(tool)
    return reg


@pytest.mark.asyncio
async def test_diet_tool_get_meals_by_day(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_meals = MealDay(
        colazione=Meal(
            type=MealType.COLAZIONE,
            food=[
                "200 mL di latte parzialmente scremato",
                "50 g di fiocchi d'avena",
                "100 g di fragole",
            ],
        ),
        spuntino=Meal(type=MealType.SPUNTINO, food=["1 arancia", "20 g di pistacchi"]),
        pranzo=Meal(
            type=MealType.PRANZO,
            food=[
                "180 g di riso basmati",
                "150 g di petto di pollo",
                "peperoni e zucchine",
                "1 cucchiaio di olio extravergine d'oliva",
            ],
        ),
        merenda=Meal(type=MealType.MERENDA, food=["150 g di skyr", "1 kiwi"]),
        cena=Meal(
            type=MealType.CENA,
            food=[
                "220 g di salmone al forno",
                "spinaci saltati",
                "1 cucchiaio di olio extravergine d'oliva",
                "100 g di pane integrale",
            ],
        ),
    )

    args_json = f'{{"date": "{test_str}"}}'
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="Example", language="en")
    res_en = await registry.execute("diet-get_meals_by_day", args_json, ctx_en, app_mock)
    assert res_en.success is True
    assert f"Meals for @{ctx_en.username} on {test_str}:" in res_en.message
    assert str(expected_meals) in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="Example", language="it")
    res_it = await registry.execute("diet-get_meals_by_day", args_json, ctx_it, app_mock)
    assert res_it.success is True
    assert f"Pasti per @{ctx_it.username} il {test_str}:" in res_it.message
    assert str(expected_meals) in res_it.message
    assert res_it.data["meals"] == expected_meals


@pytest.mark.asyncio
async def test_diet_tool_get_meals_by_day_and_meal_type(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_meal = Meal(
        type=MealType.COLAZIONE,
        food=[
            "200 mL di latte parzialmente scremato",
            "50 g di fiocchi d'avena",
            "100 g di fragole",
        ],
    )

    args_json = f'{{"date": "{test_str}", "meal_type": "COLAZIONE"}}'
    app_mock = MagicMock()

    # English test
    ctx_en = UserContext(user_id=456, chat_id=123, username="Example", language="en")
    res_en = await registry.execute(
        "diet-get_meals_by_day_and_meal_type", args_json, ctx_en, app_mock
    )
    assert res_en.success is True
    assert f"Colazione for @{ctx_en.username} on {test_str}:" in res_en.message
    assert str(expected_meal) in res_en.message

    # Italian test
    ctx_it = UserContext(user_id=456, chat_id=123, username="Example", language="it")
    res_it = await registry.execute(
        "diet-get_meals_by_day_and_meal_type", args_json, ctx_it, app_mock
    )
    assert res_it.success is True
    assert f"Colazione per @{ctx_it.username} il {test_str}:" in res_it.message
    assert str(expected_meal) in res_it.message
    assert res_it.data["meal"] == expected_meal
