import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from dama_bot.agent.models import CreateReminderArgs, ToolResult, UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.services.reminder import ReminderService

logger = logging.getLogger(__name__)


# Argument models
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


def register_reminder_tools(registry: ToolRegistry, service: ReminderService):
    @registry.register(
        name="reminder_create",
        description=(
            "Crea un nuovo promemoria. Richiede il testo e la data/ora a cui "
            "inviarlo (in formato ISO YYYY-MM-DDTHH:MM:SS, timezone Europe/Rome)."
        ),
        args_schema=CreateReminderArgs,
    )
    async def create_reminder(
        args: CreateReminderArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        try:
            # Parse datetime string
            time_str = args.remind_at.replace(" ", "T")
            dt = datetime.fromisoformat(time_str)

            # Ensure Europe/Rome timezone
            rome = ZoneInfo("Europe/Rome")
            dt = dt.replace(tzinfo=rome) if dt.tzinfo is None else dt.astimezone(rome)
        except Exception:
            return ToolResult(
                success=False,
                message=(
                    f"Formato data '{args.remind_at}' non valido. "
                    "Usa il formato YYYY-MM-DDTHH:MM:SS."
                ),
            )

        # Validate that the datetime is in the future
        now = datetime.now(ZoneInfo("Europe/Rome"))
        if dt <= now:
            return ToolResult(
                success=False,
                message=(
                    "Non posso creare un promemoria nel passato. Specifica una data e ora futura."
                ),
            )

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

    @registry.register(
        name="reminder_list",
        description=(
            "Elenca tutti i promemoria attivi (non ancora inviati e programmati "
            "per il futuro) per l'utente corrente."
        ),
        args_schema=ListRemindersArgs,
    )
    async def list_reminders(
        args: ListRemindersArgs, user_context: UserContext, application: Any
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

            reminder_list = []
            msg = "Ecco i tuoi promemoria attivi:\n"
            for r in reminders:
                reminder_list.append(
                    {"id": r.id, "text": r.text, "remind_at": r.remind_at.isoformat()}
                )
                formatted_time = r.remind_at.strftime("%d/%m/%Y alle %H:%M")
                msg += f'- [{r.id}] "{r.text}" programmato per il {formatted_time}\n'

            return ToolResult(success=True, message=msg.strip(), data={"reminders": reminder_list})
        except Exception as e:
            logger.exception("Error listing reminders in tool")
            return ToolResult(
                success=False, message=f"Errore durante il recupero dei promemoria: {str(e)}"
            )

    @registry.register(
        name="reminder_delete",
        description="Elimina un promemoria esistente identificato dal suo ID numerico.",
        args_schema=DeleteReminderArgs,
    )
    async def delete_reminder(
        args: DeleteReminderArgs, user_context: UserContext, application: Any
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

    @registry.register(
        name="reminder_update",
        description=(
            "Modifica il testo o la data/ora di un promemoria esistente usando il suo ID numerico."
        ),
        args_schema=UpdateReminderArgs,
    )
    async def update_reminder(
        args: UpdateReminderArgs, user_context: UserContext, application: Any
    ) -> ToolResult:
        dt = None
        if args.remind_at is not None:
            try:
                time_str = args.remind_at.replace(" ", "T")
                dt = datetime.fromisoformat(time_str)
                rome = ZoneInfo("Europe/Rome")
                dt = dt.replace(tzinfo=rome) if dt.tzinfo is None else dt.astimezone(rome)

                # Validate date is in the future
                now = datetime.now(ZoneInfo("Europe/Rome"))
                if dt <= now:
                    return ToolResult(
                        success=False,
                        message=(
                            "Non posso programmare un promemoria nel passato. "
                            "Specifica una data e ora futura."
                        ),
                    )
            except Exception:
                return ToolResult(
                    success=False,
                    message=(
                        f"Formato data '{args.remind_at}' non valido. "
                        "Usa il formato YYYY-MM-DDTHH:MM:SS."
                    ),
                )

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
