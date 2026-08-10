import logging
from datetime import datetime

from dama_bot.database.models import ReminderDB
from dama_bot.database.repository import ReminderRepository
from dama_bot.handlers.reminders.scheduler import cancel_reminder_job, schedule_reminder

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self, repository: ReminderRepository):
        self.repository = repository

    def create_reminder(
        self, text: str, remind_at: datetime, chat_id: int, user_id: int, username: str, application
    ) -> ReminderDB:
        logger.info(f"Creating reminder via service: '{text}' at {remind_at}")
        db_reminder = self.repository.create(
            text=text, remind_at=remind_at, username=username, chat_id=chat_id, message_id=user_id
        )
        # Schedule it in telegram job queue
        schedule_reminder(application, db_reminder)
        return db_reminder

    def list_reminders(self, chat_id: int, username: str) -> list[ReminderDB]:
        logger.info(f"Listing active reminders for chat {chat_id}, user {username}")
        return self.repository.list_active(chat_id=chat_id, username=username)

    def delete_reminder(self, reminder_id: int, chat_id: int, username: str, application) -> bool:
        logger.info(f"Deleting reminder {reminder_id} for chat {chat_id}")
        # Cancel the Telegram job queue job first
        cancel_reminder_job(application.job_queue, reminder_id)
        # Delete from repository
        return self.repository.delete(reminder_id=reminder_id, chat_id=chat_id, username=username)

    def update_reminder(
        self,
        reminder_id: int,
        chat_id: int,
        username: str,
        text: str | None,
        remind_at: datetime | None,
        application,
    ) -> ReminderDB | None:
        logger.info(f"Updating reminder {reminder_id} for chat {chat_id}")

        # Check if reminder exists and belongs to the user
        existing = self.repository.get_by_id(reminder_id)
        if not existing or existing.chat_id != chat_id or existing.username != username:
            logger.warning(f"Reminder {reminder_id} not found or permission denied")
            return None

        # Call repository update
        db_reminder = self.repository.update(
            reminder_id=reminder_id,
            chat_id=chat_id,
            username=username,
            text=text,
            remind_at=remind_at,
        )

        if db_reminder and remind_at is not None:
            # If the scheduling time changed, cancel old job and schedule new one
            cancel_reminder_job(application.job_queue, reminder_id)
            schedule_reminder(application, db_reminder)

        return db_reminder
