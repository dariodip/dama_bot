from datetime import date

from dama_bot.plugins.diet.models import MealType
from dama_bot.plugins.diet.repository import DietRepository


def test_get_meals_by_day():
    repo = DietRepository()

    meals = repo.get_meals_by_day("Example", date(2026, 8, 10))
    assert "latte" in " ".join(meals.colazione.food)
    assert meals.colazione.type == MealType.COLAZIONE
