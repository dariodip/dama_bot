import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.diet.i18n import get_translation
from dama_bot.plugins.diet.models import MealType
from dama_bot.plugins.diet.service import DietService

logger = logging.getLogger(__name__)


class GetMealsByDay(BaseModel):
    date: str = Field(..., description="The date in YYYY-MM-DD format")


class GetMealsByDayAndMealType(BaseModel):
    date: str = Field(..., description="The date in YYYY-MM-DD format")
    meal_type: str = Field(
        ...,
        description=(
            "The meal type to retrieve. Accepts"
            " 'colazione', 'merenda', 'pranzo', 'cena', 'spuntino'"
        ),
    )


def get_diet_tools(service: DietService) -> list[Tool]:
    async def get_meals_by_day(
        args: GetMealsByDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            username = user_context.username or f"user_{user_context.user_id}"
            day = date.fromisoformat(args.date)
            meals = service.get_meals_by_day(username=username, day=day)
            msg = _("Meals for @{username} on {date}:\n\n{meals}").format(
                username=username, date=args.date, meals=meals
            )
            return ToolResult(
                success=True,
                message=msg,
                data={"meals": meals},
            )
        except Exception as e:
            logger.exception("Error getting meals by day in tool")
            return ToolResult(
                success=False,
                message=_("Error retrieving meals for {date}: {error}").format(
                    date=args.date, error=str(e)
                ),
            )

    async def get_meals_by_day_and_meal_type(
        args: GetMealsByDayAndMealType, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            username = user_context.username or f"user_{user_context.user_id}"
            day = date.fromisoformat(args.date)
            meal_type = MealType.from_string(args.meal_type)
            meal = service.get_meals_by_day_and_meal_type(
                username=username, day=day, meal_type=meal_type
            )
            meal_name = args.meal_type.lower().capitalize()
            msg = _("{meal_type} for @{username} on {date}:\n\n{meal}").format(
                meal_type=meal_name, username=username, date=args.date, meal=meal
            )
            return ToolResult(
                success=True,
                message=msg,
                data={"meal": meal},
            )
        except Exception as e:
            logger.exception("Error getting meals by day and meal type in tool")
            return ToolResult(
                success=False,
                message=_("Error retrieving meal {meal_type} for {date}: {error}").format(
                    meal_type=args.meal_type, date=args.date, error=str(e)
                ),
            )

    return [
        FunctionTool(
            name="diet-get_meals_by_day",
            description="Retrieve all meals for a user for a given day in YYYY-MM-DD format.",
            args_schema=GetMealsByDay,
            func=get_meals_by_day,
        ),
        FunctionTool(
            name="diet-get_meals_by_day_and_meal_type",
            description=(
                "Retrieve a specific meal type for a user for a given day in YYYY-MM-DD format."
            ),
            args_schema=GetMealsByDayAndMealType,
            func=get_meals_by_day_and_meal_type,
        ),
    ]
