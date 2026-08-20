from dataclasses import dataclass
from enum import Enum


class MealType(Enum):
    COLAZIONE = "colazione"
    SPUNTINO = "spuntino"
    PRANZO = "pranzo"
    MERENDA = "merenda"
    CENA = "cena"

    @staticmethod
    def from_string(value: str) -> "MealType":
        return MealType(value.lower())


@dataclass
class Meal:
    type: MealType
    food: list[str]


@dataclass
class MealDay:
    colazione: Meal
    spuntino: Meal
    pranzo: Meal
    merenda: Meal
    cena: Meal
