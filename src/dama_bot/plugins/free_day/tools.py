import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.free_day.i18n import get_translation
from dama_bot.plugins.free_day.service import FreeDayService

logger = logging.getLogger(__name__)


class CreateFreeDay(BaseModel):
    date: str = Field(..., description="The date of the free day in YYYY-MM-DD format")


class IsAFreeDay(BaseModel):
    date: str = Field(..., description="The date to check in YYYY-MM-DD format")


class NextFreeDay(BaseModel):
    pass


def get_free_day_tools(service: FreeDayService) -> list[Tool]:
    async def create_free_day(
        args: CreateFreeDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            day = date.fromisoformat(args.date)
            service.create_free_day(
                date=day,
                chat_id=user_context.chat_id,
                username=user_context.username or f"user_{user_context.user_id}",
            )
            return ToolResult(
                success=True,
                message=_("Free day successfully registered for {date}.").format(date=args.date),
            )
        except Exception as e:
            logger.exception("Error creating free day in tool")
            return ToolResult(
                success=False,
                message=_("Error registering free day: {error}").format(error=str(e)),
            )

    async def is_a_free_day(
        args: IsAFreeDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            day = date.fromisoformat(args.date)
            is_free = service.is_a_free_day(
                date=day,
                chat_id=user_context.chat_id,
                username=user_context.username or f"user_{user_context.user_id}",
            )
            msg = (
                _("The day {date} is a free day").format(date=args.date)
                if is_free
                else _("The day {date} is not a free day").format(date=args.date)
            )
            return ToolResult(
                success=True,
                message=msg,
                data={"is_free": is_free},
            )
        except Exception as e:
            logger.exception("Error checking if a day is a free day in tool")
            return ToolResult(
                success=False,
                message=_("Error checking if day is a free day: {error}").format(error=str(e)),
            )

    async def next_free_day(
        args: NextFreeDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        lang = user_context.language
        _ = get_translation(lang).gettext
        try:
            day = service.next_free_day(
                chat_id=user_context.chat_id,
                username=user_context.username or f"user_{user_context.user_id}",
            )
            if day is None:
                return ToolResult(
                    success=True,
                    message=_("No free day has been registered."),
                    data={"date": None},
                )
            msg = _("The next free day is {date}").format(date=day)
            return ToolResult(
                success=True,
                message=msg,
                data={"date": day.isoformat()},
            )
        except ValueError as ve:
            logger.error(f"Error getting next free day in tool: {str(ve)}")
            return ToolResult(
                success=True,
                message=_(
                    "No free day has been registered. "
                    "First register one with the 'free_day-create' tool."
                ),
            )
        except Exception as e:
            logger.exception("Error getting next free day in tool")
            return ToolResult(
                success=False,
                message=_("Error retrieving next free day: {error}").format(error=str(e)),
            )

    return [
        FunctionTool(
            name="free_day-create",
            description="Register a free day. Requires the date in YYYY-MM-DD format.",
            args_schema=CreateFreeDay,
            func=create_free_day,
        ),
        FunctionTool(
            name="free_day-is_a_free_day",
            description="Check if a date is a free day. Requires the date in YYYY-MM-DD format.",
            args_schema=IsAFreeDay,
            func=is_a_free_day,
        ),
        FunctionTool(
            name="free_day-next",
            description="Find the next upcoming free day starting from today.",
            args_schema=NextFreeDay,
            func=next_free_day,
        ),
    ]
