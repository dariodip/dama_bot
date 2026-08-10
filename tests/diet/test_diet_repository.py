from datetime import date
import pytest

from dama_bot.database.repository import DietRepository
from dama_bot.database.models import MealType


def test_get_meals_by_day():
    repo = DietRepository()

    meals = repo.get_meals_by_day("DarioDip", date(2026, 8, 10))
    assert "pancakes" in " ".join(meals.colazione.food)
    assert meals.colazione.type == MealType.COLAZIONE

def test_get_meals_by_day_for_user():
    repo = DietRepository()

    meals = repo.get_meals_by_day("Manu123stella", date(2026, 8, 10))
    assert "150ml Latte magro senza lattosio" in " ".join(meals.colazione.food)
    assert meals.colazione.type == MealType.COLAZIONE
