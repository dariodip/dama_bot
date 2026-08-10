from dama_bot.services.free_day import FreeDayService
from dama_bot.agent.registry import ToolRegistry
from dama_bot.agent.models import UserContext, ToolResult
from pydantic import BaseModel, Field
from datetime import date
import logging
from typing import Any

logger = logging.getLogger(__name__)

class CreateFreeDay(BaseModel):
    date: str = Field(..., description="La data del giorno libero in formato YYYY-MM-DD")

class IsAFreeDay(BaseModel):
    date: str = Field(..., description="La data da controllare in formato YYYY-MM-DD")

class NextFreeDay(BaseModel):
    pass

def register_free_day_tools(registry: ToolRegistry, service: FreeDayService):
    @registry.register(
        name="free_day-create",
        description=(
            "Registra un giorno libero."
            "Richiede la data in formato YYYY-MM-DD."
        ),
        args_schema=CreateFreeDay,
    )
    async def create_free_day(args: CreateFreeDay, user_context: UserContext, application: Any) -> ToolResult:
        try:
            day = date.fromisoformat(args.date)
            service.create_free_day(date=day, chat_id=user_context.chat_id, username=user_context.username or f"user_{user_context.user_id}")
            return ToolResult(
                success=True,
                message=f"Giorno libero registrato con successo per il {args.date}.",
            )
        except Exception as e:
            logger.exception("Error creating free day in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante la registrazione del giorno libero: {str(e)}",
            )

    @registry.register(
        name="free_day-is_a_free_day",
        description=(
            "Controlla se un giorno è un giorno libero."
            "Richiede la data in formato YYYY-MM-DD."
        ),
        args_schema=IsAFreeDay,
    )
    async def is_a_free_day(args: IsAFreeDay, user_context: UserContext, application: Any) -> ToolResult:
        try:
            day = date.fromisoformat(args.date)
            is_free = service.is_a_free_day(date=day, chat_id=user_context.chat_id, username=user_context.username or f"user_{user_context.user_id}")
            msg = f"Il giorno {args.date}{'' if is_free else 'non'} è libero"
            return ToolResult(
                success=True,
                message=msg,
                data={"is_free": is_free},
            )
        except Exception as e:
            logger.exception("Error checking if a day is a free day in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il controllo se un giorno è un giorno libero: {str(e)}",
            )

    @registry.register(
        name="free_day-next",
        description=(
            "Trova il prossimo giorno libero a partire da oggi."
        ),
        args_schema=NextFreeDay,
    )
    async def next_free_day(args: NextFreeDay, user_context:UserContext, application:Any) -> ToolResult:
        try:
            day = service.next_free_day(chat_id=user_context.chat_id, username=user_context.username or f"user_{user_context.user_id}")
            if day is None:
                return ToolResult(
                    success=True,
                    message="Non è stato registrato alcun giorno libero.",
                    data={"date": None},
                )
            msg = f"Il prossimo giorno libero è il {day}"
            return ToolResult(
                success=True,
                message=msg,
                data={"date": day.isoformat()},
            )
        except ValueError as ve:
            logger.error(f"Error getting next free day in tool: {str(ve)}")
            return ToolResult(
                success=True,
                message="Non è stato registrato alcun giorno libero. Per prima cosa registrane uno con il tool 'create_free_day'.",
            )
        except Exception as e:
            logger.exception("Error getting next free day in tool")
            return ToolResult(
                success=False,
                message=f"Errore durante il recupero del prossimo giorno libero: {str(e)}",
            )