import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.reminders.service import ReminderService

logger = logging.getLogger(__name__)


# Argument models
class CreateReminderArgs(BaseModel):
    text: str = Field(..., description="Descrizione di cosa ricordare")
    remind_at: str = Field(
        ..., description="Data e ora in cui ricordare (formato ISO: YYYY-MM-DDTHH:MM:SS)"
    )


class ListRemindersArgs(BaseModel):
    pass


class DeleteReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="L'ID numerico del promemoria da eliminare.")


class UpdateReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="L'ID numerico del promemoria da modificare.")
    text: str | None = Field(
        default=None, description="Il nuovo testo/descrizione del promemoria, o null se non cambia."
    )
    remind_at: str | None = Field(
        default=None,
        description="La nuova data e ora (formato ISO: YYYY-MM-DDTHH:MM:SS), o null se non cambia.",
    )


def _parse_future_rome_datetime(remind_at_str: str) -> tuple[datetime | None, str | None]:
    try:
        time_str = remind_at_str.replace(" ", "T")
        dt = datetime.fromisoformat(time_str)
        rome = ZoneInfo("Europe/Rome")
        dt = dt.replace(tzinfo=rome) if dt.tzinfo is None else dt.astimezone(rome)
    except Exception:
        return None, (
            f"Formato data '{remind_at_str}' non valido. Usa il formato YYYY-MM-DDTHH:MM:SS."
        )

    now = datetime.now(ZoneInfo("Europe/Rome"))
    if dt <= now:
        return (
            None,
            "Non posso programmare un promemoria nel passato. Specifica una data e ora futura.",
        )

    return dt, None


def _format_active_reminders(reminders: list[Any]) -> tuple[str, list[dict[str, Any]]]:
    reminder_list = []
    lines = ["Ecco i tuoi promemoria attivi:"]
    for r in reminders:
        reminder_list.append({"id": r.id, "text": r.text, "remind_at": r.remind_at.isoformat()})
        formatted_time = r.remind_at.strftime("%d/%m/%Y alle %H:%M")
        lines.append(f'- [{r.id}] "{r.text}" programmato per il {formatted_time}')
    return "\n".join(lines), reminder_list


async def _create_reminder(
    service: ReminderService,
    args: CreateReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    dt, error_msg = _parse_future_rome_datetime(args.remind_at)
    if error_msg:
        return ToolResult(success=False, message=error_msg)

    try:
        db_reminder = service.create_reminder(
            text=args.text,
            remind_at=dt,
            chat_id=user_context.chat_id,
            user_id=user_context.user_id,
            username=user_context.username or f"user_{user_context.user_id}",
            application=application,
        )

        formatted_time = db_reminder.remind_at.strftime("%d/%m/%Y alle %H:%M")
        return ToolResult(
            success=True,
            message=f"Promemoria creato con successo per il {formatted_time}.",
            data={
                "id": db_reminder.id,
                "text": db_reminder.text,
                "remind_at": db_reminder.remind_at.isoformat(),
            },
        )
    except Exception as e:
        logger.exception("Error creating reminder in tool")
        return ToolResult(
            success=False, message=f"Errore durante la creazione del promemoria: {str(e)}"
        )


async def _list_reminders(
    service: ReminderService,
    args: ListRemindersArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    try:
        reminders = service.list_reminders(
            chat_id=user_context.chat_id,
            username=user_context.username or f"user_{user_context.user_id}",
        )

        if not reminders:
            return ToolResult(
                success=True,
                message="Non hai promemoria attivi al momento.",
                data={"reminders": []},
            )

        msg, reminder_list = _format_active_reminders(reminders)
        return ToolResult(success=True, message=msg, data={"reminders": reminder_list})
    except Exception as e:
        logger.exception("Error listing reminders in tool")
        return ToolResult(
            success=False, message=f"Errore durante il recupero dei promemoria: {str(e)}"
        )


async def _delete_reminder(
    service: ReminderService,
    args: DeleteReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    try:
        success = service.delete_reminder(
            reminder_id=args.reminder_id,
            chat_id=user_context.chat_id,
            username=user_context.username or f"user_{user_context.user_id}",
            application=application,
        )

        if success:
            return ToolResult(
                success=True,
                message=f"Promemoria {args.reminder_id} eliminato con successo.",
                data={"id": args.reminder_id},
            )
        else:
            return ToolResult(
                success=False,
                message=(
                    f"Promemoria con ID {args.reminder_id} non trovato "
                    "o non sei autorizzato a eliminarlo."
                ),
            )
    except Exception as e:
        logger.exception("Error deleting reminder in tool")
        return ToolResult(
            success=False, message=f"Errore durante l'eliminazione del promemoria: {str(e)}"
        )


async def _update_reminder(
    service: ReminderService,
    args: UpdateReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    dt = None
    if args.remind_at is not None:
        dt, error_msg = _parse_future_rome_datetime(args.remind_at)
        if error_msg:
            return ToolResult(success=False, message=error_msg)

    try:
        db_reminder = service.update_reminder(
            reminder_id=args.reminder_id,
            chat_id=user_context.chat_id,
            username=user_context.username or f"user_{user_context.user_id}",
            text=args.text,
            remind_at=dt,
            application=application,
        )

        if db_reminder:
            formatted_time = db_reminder.remind_at.strftime("%d/%m/%Y alle %H:%M")
            return ToolResult(
                success=True,
                message=(
                    f"Promemoria {db_reminder.id} aggiornato con successo. "
                    f'Nuovo stato: "{db_reminder.text}" per il {formatted_time}.'
                ),
                data={
                    "id": db_reminder.id,
                    "text": db_reminder.text,
                    "remind_at": db_reminder.remind_at.isoformat(),
                },
            )
        else:
            return ToolResult(
                success=False,
                message=(
                    f"Promemoria con ID {args.reminder_id} non trovato "
                    "o non sei autorizzato a modificarlo."
                ),
            )
    except Exception as e:
        logger.exception("Error updating reminder in tool")
        return ToolResult(
            success=False, message=f"Errore durante l'aggiornamento del promemoria: {str(e)}"
        )


def get_reminder_tools(service: ReminderService) -> list[Tool]:
    async def create_reminder(
        args: CreateReminderArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        return await _create_reminder(service, args, user_context, application)

    async def list_reminders(
        args: ListRemindersArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        return await _list_reminders(service, args, user_context, application)

    async def delete_reminder(
        args: DeleteReminderArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        return await _delete_reminder(service, args, user_context, application)

    async def update_reminder(
        args: UpdateReminderArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        return await _update_reminder(service, args, user_context, application)

    return [
        FunctionTool(
            name="reminder-create",
            description=(
                "Crea un nuovo promemoria. Richiede il testo e la data/ora a cui "
                "inviarlo (in formato ISO YYYY-MM-DDTHH:MM:SS, timezone Europe/Rome)."
            ),
            args_schema=CreateReminderArgs,
            func=create_reminder,
        ),
        FunctionTool(
            name="reminder-list",
            description=(
                "Elenca tutti i promemoria attivi (non ancora inviati e programmati "
                "per il futuro) per l'utente corrente."
            ),
            args_schema=ListRemindersArgs,
            func=list_reminders,
        ),
        FunctionTool(
            name="reminder-delete",
            description="Elimina un promemoria esistente identificato dal suo ID numerico.",
            args_schema=DeleteReminderArgs,
            func=delete_reminder,
        ),
        FunctionTool(
            name="reminder-update",
            description=(
                "Modifica il testo o la data/ora di un promemoria esistente"
                " usando il suo ID numerico."
            ),
            args_schema=UpdateReminderArgs,
            func=update_reminder,
        ),
    ]
