import logging
from datetime import date

import yaml

from dama_bot.config import BASEDIR
from dama_bot.plugins.diet.models import Meal, MealDay, MealType

logger = logging.getLogger(__name__)


class DietRepository:
    def get_meals_by_day(self, username: str, day: date) -> MealDay:
        path = BASEDIR / "data" / "diet" / f"{username}.yml"
        with open(path) as f:
            day_meal = yaml.safe_load(f)["dieta"]["giorni"][day.weekday()]
        return MealDay(
            colazione=Meal(food=day_meal["colazione"], type=MealType.COLAZIONE),
            spuntino=Meal(food=day_meal["spuntino"], type=MealType.SPUNTINO),
            pranzo=Meal(food=day_meal["pranzo"], type=MealType.PRANZO),
            merenda=Meal(food=day_meal["merenda"], type=MealType.MERENDA),
            cena=Meal(food=day_meal["cena"], type=MealType.CENA),
        )
