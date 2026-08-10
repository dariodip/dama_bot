from dama_bot.services.garbage import GarbageService
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.models import UserContext, ToolResult
from pydantic import BaseModel, Field
from datetime import date
import logging
from typing import Any

logger = logging.getLogger(__name__)

class GarbageTypeForDay(BaseModel):
    date: str = Field(..., description="La data per cui si vuole conoscere il tipo di rifiuto in formato YYYY-MM-DD")

class IndifferenziatoWeek(BaseModel):
    date: str = Field(..., description="La data per cui si vuole conoscere se è una settimana dell'indifferenziata o del vetro in formato YYYY-MM-DD")

def register_garbage_tools(registry: ToolRegistry, service: GarbageService):
    @registry.register(
        name="garbage-get_garbage_type_for_day",
        description=(
            "Restituisce il tipo di rifiuto da gettare in una data specifica"
            "in formato YYYY-MM-DD"
        ),
        args_schema=GarbageTypeForDay,
    )
    async def get_garbage_type_for_day(args: GarbageTypeForDay, user_context: UserContext, application: Any) -> ToolResult:
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

    @registry.register(
        name="garbage-is_indifferenziato_week",
        description=(
            "Controlla se una data ricade in una settimana dell'indifferenziata"
            "in formato YYYY-MM-DD"
        ),
        args_schema=IndifferenziatoWeek,
    )
    async def is_indifferenziato_week(args: IndifferenziatoWeek, user_context: UserContext, application: Any) -> ToolResult:
        try:
            day = date.fromisoformat(args.date)
            is_indifferenziato_week = service.is_indifferenziato_week(day)
            msg = f"La settimana del {args.date}{' ' if is_indifferenziato_week else ' non '}è una settimana dell'indifferenziata"
            return ToolResult(
                success=True,
                message=msg,
                data={"is_indifferenziato_week": is_indifferenziato_week},
            )
        except Exception as e:
            logger.exception("Error checking if a day is in an indifferenziato week in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il controllo della settimana dell'indifferenziata: {str(e)}",
            )
