import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.garbage.i18n import get_translation
from dama_bot.plugins.garbage.service import GarbageService

logger = logging.getLogger(__name__)


class GarbageTypeForDay(BaseModel):
    date: str = Field(
        ...,
        description="The date to check garbage type for, in YYYY-MM-DD format",
    )


class IndifferenziatoWeek(BaseModel):
    date: str = Field(
        ...,
        description="The date to check if it's an indifferenziata week, in YYYY-MM-DD format",
    )


def get_garbage_tools(service: GarbageService) -> list[Tool]:
    async def get_garbage_type_for_day(
        args: GarbageTypeForDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            day = date.fromisoformat(args.date)
            garbage_type = service.get_garbage_type_for_day(day)
            return ToolResult(
                success=True,
                message=_("The garbage type for {date} is {garbage_type}").format(
                    date=args.date, garbage_type=garbage_type
                ),
                data={"garbage_type": garbage_type},
            )
        except Exception as e:
            logger.exception("Error getting garbage type for day in tool")
            return ToolResult(
                success=False,
                message=_("Error retrieving garbage type: {error}").format(error=str(e)),
            )

    async def is_indifferenziato_week(
        args: IndifferenziatoWeek, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            day = date.fromisoformat(args.date)
            is_indiff = service.is_indifferenziato_week(day)
            msg = (
                _("The week of {date} is an indifferenziata week").format(date=args.date)
                if is_indiff
                else _("The week of {date} is not an indifferenziata week").format(date=args.date)
            )
            return ToolResult(
                success=True,
                message=msg,
                data={"is_indifferenziato_week": is_indiff},
            )
        except Exception as e:
            logger.exception("Error checking if a day is in an indifferenziato week in tool")
            return ToolResult(
                success=False,
                message=_("Error checking week type: {error}").format(error=str(e)),
            )

    return [
        FunctionTool(
            name="garbage-get_garbage_type_for_day",
            description="Returns the garbage type for a specific date in YYYY-MM-DD format.",
            args_schema=GarbageTypeForDay,
            func=get_garbage_type_for_day,
        ),
        FunctionTool(
            name="garbage-is_indifferenziato_week",
            description=(
                "Checks whether a given date falls in an indifferenziata week in YYYY-MM-DD format."
            ),
            args_schema=IndifferenziatoWeek,
            func=is_indifferenziato_week,
        ),
    ]
