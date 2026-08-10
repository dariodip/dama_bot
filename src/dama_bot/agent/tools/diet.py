from dama_bot.services.diet import DietService
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.models import UserContext, ToolResult
from dama_bot.database.models import MealType
from pydantic import BaseModel, Field
from datetime import date
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GetMealsByDay(BaseModel):
    date: str = Field(..., description="La data del giorno in formato YYYY-MM-DD")

class GetMealsByDayAndMealType(BaseModel):
    date: str = Field(..., description="La data del giorno in formato YYYY-MM-DD")
    meal_type: str = Field(..., description="Il tipo di pasto da recuperare. Accetta i valori 'colazione', 'merenda', 'pranzo', 'cena', 'spuntino'")


def register_diet_tools(registry: ToolRegistry, service: DietService):

    @registry.register(
        name="diet-get_meals_by_day",
        description=(
            "Recupera tutti i pasti per un utente per un dato giorno."
            "Da non usare se l'utente chiede un pasto specifico."
            "Richiede la data in formato YYYY-MM-DD."
            "Specifica sempre l'utente che ha richiesto l'informazione nel messaggio."
        ),
        args_schema=GetMealsByDay,
    )
    async def get_meals_by_day(args: GetMealsByDay, user_context: UserContext, application: Any) -> ToolResult:
        try:
            username = user_context.username or f"user_{user_context.user_id}"
            day = date.fromisoformat(args.date)
            meals = service.get_meals_by_day(username=username, day=day)
            msg = f"Pasti per @{username} il {args.date}:\n\n{meals}"
            return ToolResult(
                success=True,
                message=msg,
                data={"meals": meals},
            )
        except Exception as e:
            logger.exception("Error getting meals by day in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il recupero dei pasti per il giorno {args.date}: {str(e)}",
            )
    
    @registry.register(
        name="diet-get_meals_by_day_and_meal_type",
        description=(
            "Recupera un tipo di pasto per un utente per un dato giorno."
            "Il tipo di pasto può essere colazione, spuntino, merenda, pranzo e cena."
            "Richiede la data in formato YYYY-MM-DD e il tipo di pasto."
            "Specifica sempre l'utente che ha richiesto l'informazione nel messaggio."
        ),
        args_schema=GetMealsByDayAndMealType,
    )
    async def get_meals_by_day_and_meal_type(args: GetMealsByDayAndMealType, user_context: UserContext, application: Any) -> ToolResult:
        try:
            username = user_context.username or f"user_{user_context.user_id}"
            day = date.fromisoformat(args.date)
            meal_type = MealType.from_string(args.meal_type)
            meal = service.get_meals_by_day_and_meal_type(username=username, day=day, meal_type=meal_type)
            msg = f"{args.meal_type.lower().capitalize()} per @{username} il {args.date}:\n\n{meal}"
            return ToolResult(
                success=True,
                message=msg,
                data={"meal": meal},
            )
        except Exception as e:
            logger.exception("Error getting meals by day and meal type in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il recupero del pasto {args.meal_type} per il giorno {args.date}: {str(e)}",
            )
