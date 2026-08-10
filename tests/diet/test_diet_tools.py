from datetime import date
from unittest.mock import MagicMock

import pytest

import dama_bot.services.diet as d
from dama_bot.agent.models import UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.tools.diet import register_diet_tools
from dama_bot.database.repository import DietRepository
from dama_bot.services.diet import DietService


@pytest.fixture
def service_mock():
    return DietService(DietRepository())


@pytest.fixture
def registry(service_mock):
    reg = ToolRegistry()
    register_diet_tools(reg, service_mock)
    return reg


@pytest.mark.asyncio
async def test_diet_tool_get_meals_by_day(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_meals = d.MealDay(
        colazione=d.Meal(
            type=d.MealType.COLAZIONE, food=["1 porzione di pancakes", "30 g di composta di frutta"]
        ),
        spuntino=d.Meal(type=d.MealType.SPUNTINO, food=["1 mela", "30 g di mandorle"]),
        pranzo=d.Meal(
            type=d.MealType.PRANZO,
            food=["200 g di farro", "zucchine", "100 g di tonno", "1 cucchiaio di olio d’oliva"],
        ),
        merenda=d.Meal(type=d.MealType.MERENDA, food=["1 yogurt greco", "1 kaki"]),
        cena=d.Meal(
            type=d.MealType.CENA,
            food=[
                "250 g (2 fette) di scaloppine di maiale (arista solo con farina)",
                "lattuga e carote all’insalata",
                "1 cucchiaio di olio",
                "1/2 avocado",
                "130 g di pane",
            ],
        ),
    )

    args_json = f'{{"date": "{test_str}"}}'
    ctx = UserContext(user_id=456, chat_id=123, username="DarioDip")
    app_mock = MagicMock()

    res = await registry.execute("diet-get_meals_by_day", args_json, ctx, app_mock)

    assert res.success is True
    assert f"Pasti per @{ctx.username} il {test_str}:" in res.message
    assert str(expected_meals) in res.message
    assert res.data["meals"] == expected_meals


@pytest.mark.asyncio
async def test_diet_tool_get_meals_by_day_and_meal_type(registry, service_mock):
    test_date = date(2026, 8, 10)
    test_str = test_date.isoformat()
    expected_meal = d.Meal(
        type=d.MealType.COLAZIONE, food=["1 porzione di pancakes", "30 g di composta di frutta"]
    )

    args_json = f'{{"date": "{test_str}", "meal_type": "COLAZIONE"}}'
    ctx = UserContext(user_id=456, chat_id=123, username="DarioDip")
    app_mock = MagicMock()

    res = await registry.execute("diet-get_meals_by_day_and_meal_type", args_json, ctx, app_mock)

    assert res.success is True
    assert f"Colazione per @{ctx.username} il {test_str}:" in res.message
    assert str(expected_meal) in res.message
    assert res.data["meal"] == expected_meal
