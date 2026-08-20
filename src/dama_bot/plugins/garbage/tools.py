import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.garbage.service import GarbageService

logger = logging.getLogger(__name__)


class GarbageTypeForDay(BaseModel):
    date: str = Field(
        ...,
        description="La data per cui si vuole conoscere il tipo di rifiuto "
        + "in formato YYYY-MM-DD",
    )


class IndifferenziatoWeek(BaseModel):
    date: str = Field(
        ...,
        description=(
            "La data per cui si vuole conoscere se è una settimana "
            + "dell'indifferenziata o del vetro in formato YYYY-MM-DD"
        ),
    )


def get_garbage_tools(service: GarbageService) -> list[Tool]:
    async def get_garbage_type_for_day(
        args: GarbageTypeForDay, user_context: UserContext, application: Any
    ) -> ToolResult:
        try:
            day = date.fromisoformat(args.date)
            garbage_type = service.get_garbage_type_for_day(day)
            return ToolResult(
                success=True,
                message=f"Il tipo di rifiuto per il {args.date} è {garbage_type}",
                data={"garbage_type": garbage_type},
            )
        except Exception as e:
            logger.exception("Error getting garbage type for day in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il recupero del tipo di rifiuto: {str(e)}",
            )

    async def is_indifferenziato_week(
        args: IndifferenziatoWeek, user_context: UserContext, application: Any
    ) -> ToolResult:
        try:
            day = date.fromisoformat(args.date)
            is_indifferenziato_week = service.is_indifferenziato_week(day)
            msg = (
                f"La settimana del {args.date}"
                + f"{' ' if is_indifferenziato_week else ' non '}"
                + "è una settimana dell'indifferenziata"
            )
            return ToolResult(
                success=True,
                message=msg,
                data={"is_indifferenziato_week": is_indifferenziato_week},
            )
        except Exception as e:
            logger.exception("Error checking if a day is in an indifferenziato week in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il controllo della settimana: {str(e)}",
            )

    return [
        FunctionTool(
            name="garbage-get_garbage_type_for_day",
            description=(
                "Restituisce il tipo di rifiuto da gettare in una data"
                " specificain formato YYYY-MM-DD"
            ),
            args_schema=GarbageTypeForDay,
            func=get_garbage_type_for_day,
        ),
        FunctionTool(
            name="garbage-is_indifferenziato_week",
            description=(
                "Controlla se una data ricade in una settimana dell'indifferenziata"
                "in formato YYYY-MM-DD"
            ),
            args_schema=IndifferenziatoWeek,
            func=is_indifferenziato_week,
        ),
    ]
