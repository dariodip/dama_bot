from datetime import date
import pytest

from dama_bot.database.models import MealType
from dama_bot.services.diet import DietService
from dama_bot.database.repository import DietRepository

@pytest.fixture
def service():
    return DietService(DietRepository())


def test_get_meals_by_day(service):
    meal_day = service.get_meals_by_day("DarioDip", date(2026, 8, 10))
    assert "pancakes" in " ".join(meal_day.colazione.food)

def test_get_meals_by_day_and_meal_type(service):
    meal = service.get_meals_by_day_and_meal_type("DarioDip", date(2026, 8, 10), MealType.COLAZIONE)
    assert "pancakes" in " ".join(meal.food)
