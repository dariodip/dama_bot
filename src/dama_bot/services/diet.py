import logging
from datetime import date

from dama_bot.database.models import MealType, Meal, MealDay
from dama_bot.database.repository import DietRepository

logger = logging.getLogger(__name__)


class DietService:
    def __init__(self, repository: DietRepository) -> None:
        self.repository = repository

    def get_meals_by_day(self, username: str, day: date) -> MealDay:
        return self.repository.get_meals_by_day(username, day)

    def get_meals_by_day_and_meal_type(
        self, username: str, day: date, meal_type: MealType
    ) -> Meal:
        meal_day = self.repository.get_meals_by_day(username, day)
        match meal_type:
            case MealType.COLAZIONE:
                return meal_day.colazione
            case MealType.SPUNTINO:
                return meal_day.spuntino
            case MealType.PRANZO:
                return meal_day.pranzo
            case MealType.MERENDA:
                return meal_day.merenda
            case MealType.CENA:
                return meal_day.cena
            case _:
                raise ValueError(f"Tipo di pasto non valido: {meal_type}")
