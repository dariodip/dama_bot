import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import FunctionTool, Tool
from dama_bot.plugins.reminders.i18n import get_translation
from dama_bot.plugins.reminders.service import ReminderService

logger = logging.getLogger(__name__)


# Argument models
class CreateReminderArgs(BaseModel):
    text: str = Field(..., description="Description of what to remind")
    remind_at: str = Field(
        ..., description="Date and time for the reminder (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )


class ListRemindersArgs(BaseModel):
    pass


class DeleteReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="The numeric ID of the reminder to delete.")


class UpdateReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="The numeric ID of the reminder to update.")
    text: str | None = Field(
        default=None, description="The new text/description of the reminder, or null if unchanged."
    )
    remind_at: str | None = Field(
        default=None,
        description=(
            "The new date and time (ISO format: YYYY-MM-DDTHH:MM:SS), or null if unchanged."
        ),
    )


def _parse_future_rome_datetime(
    remind_at_str: str, lang: str = "en"
) -> tuple[datetime | None, str | None]:
    _ = get_translation(lang).gettext
    try:
        time_str = remind_at_str.replace(" ", "T")
        dt = datetime.fromisoformat(time_str)
        rome = ZoneInfo("Europe/Rome")
        dt = dt.replace(tzinfo=rome) if dt.tzinfo is None else dt.astimezone(rome)
    except Exception:
        err = _("Invalid date format '{date_str}'. Use ISO format YYYY-MM-DDTHH:MM:SS.").format(
            date_str=remind_at_str
        )
        return None, err

    now = datetime.now(ZoneInfo("Europe/Rome"))
    if dt <= now:
        return (
            None,
            _("Cannot schedule a reminder in the past. Please specify a future date and time."),
        )

    return dt, None


def _format_active_reminders(
    reminders: list[Any], lang: str = "en"
) -> tuple[str, list[dict[str, Any]]]:
    _ = get_translation(lang).gettext
    reminder_list = []
    lines = [_("Here are your active reminders:")]
    dt_fmt = _("%d/%m/%Y at %H:%M")
    for r in reminders:
        reminder_list.append({"id": r.id, "text": r.text, "remind_at": r.remind_at.isoformat()})
        formatted_time = r.remind_at.strftime(dt_fmt)
        lines.append(
            _('- [{id}] "{text}" scheduled for {time}').format(
                id=r.id, text=r.text, time=formatted_time
            )
        )
    return "\n".join(lines), reminder_list


async def _create_reminder(
    service: ReminderService,
    args: CreateReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    lang = user_context.language
    _ = get_translation(lang).gettext
    dt, error_msg = _parse_future_rome_datetime(args.remind_at, lang=lang)
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

        dt_fmt = _("%d/%m/%Y at %H:%M")
        formatted_time = db_reminder.remind_at.strftime(dt_fmt)
        return ToolResult(
            success=True,
            message=_("Reminder successfully created for {time}.").format(time=formatted_time),
            data={
                "id": db_reminder.id,
                "text": db_reminder.text,
                "remind_at": db_reminder.remind_at.isoformat(),
            },
        )
    except Exception as e:
        logger.exception("Error creating reminder in tool")
        return ToolResult(
            success=False,
            message=_("Error creating reminder: {error}").format(error=str(e)),
        )


async def _list_reminders(
    service: ReminderService,
    args: ListRemindersArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    lang = user_context.language
    _ = get_translation(lang).gettext
    try:
        reminders = service.list_reminders(
            chat_id=user_context.chat_id,
            username=user_context.username or f"user_{user_context.user_id}",
        )

        if not reminders:
            return ToolResult(
                success=True,
                message=_("You currently have no active reminders."),
                data={"reminders": []},
            )

        msg, reminder_list = _format_active_reminders(reminders, lang=lang)
        return ToolResult(success=True, message=msg, data={"reminders": reminder_list})
    except Exception as e:
        logger.exception("Error listing reminders in tool")
        return ToolResult(
            success=False,
            message=_("Error retrieving reminders: {error}").format(error=str(e)),
        )


async def _delete_reminder(
    service: ReminderService,
    args: DeleteReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    lang = user_context.language
    _ = get_translation(lang).gettext
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
                message=_("Reminder {id} successfully deleted.").format(id=args.reminder_id),
                data={"id": args.reminder_id},
            )
        else:
            return ToolResult(
                success=False,
                message=_(
                    "Reminder with ID {id} not found or you are not authorized to delete it."
                ).format(id=args.reminder_id),
            )
    except Exception as e:
        logger.exception("Error deleting reminder in tool")
        return ToolResult(
            success=False,
            message=_("Error deleting reminder: {error}").format(error=str(e)),
        )


async def _update_reminder(
    service: ReminderService,
    args: UpdateReminderArgs,
    user_context: UserContext,
    application: Any,
) -> ToolResult:
    lang = user_context.language
    _ = get_translation(lang).gettext
    dt = None
    if args.remind_at is not None:
        dt, error_msg = _parse_future_rome_datetime(args.remind_at, lang=lang)
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
            dt_fmt = _("%d/%m/%Y at %H:%M")
            formatted_time = db_reminder.remind_at.strftime(dt_fmt)
            return ToolResult(
                success=True,
                message=_(
                    'Reminder {id} successfully updated. New status: "{text}" for {time}.'
                ).format(
                    id=db_reminder.id,
                    text=db_reminder.text,
                    time=formatted_time,
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
                message=_(
                    "Reminder with ID {id} not found or you are not authorized to edit it."
                ).format(id=args.reminder_id),
            )
    except Exception as e:
        logger.exception("Error updating reminder in tool")
        return ToolResult(
            success=False,
            message=_("Error updating reminder: {error}").format(error=str(e)),
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
