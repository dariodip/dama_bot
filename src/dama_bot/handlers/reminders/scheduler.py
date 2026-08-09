import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def ensure_rome_tz(dt: datetime) -> datetime:
    """Ensure the datetime has Europe/Rome timezone info attached or converted."""
    rome = ZoneInfo("Europe/Rome")
    if dt.tzinfo is None:
        return dt.replace(tzinfo=rome)
    return dt.astimezone(rome)


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    reminder = job.data

    logger.info(f"Sending reminder {reminder['id']}")

    await context.bot.send_message(chat_id=job.chat_id, text=f"Ricordati:\n\n{reminder['text']}")

    mark_as_sent(reminder["id"])


def schedule_reminder(application, reminder):
    remind_at = ensure_rome_tz(reminder.remind_at)
    logger.info("Scheduling reminder %s at %s (%s)", reminder.text, remind_at, remind_at.tzinfo)

    job = application.job_queue.run_once(
        send_reminder,
        when=remind_at,
        chat_id=reminder.chat_id,
        name=f"reminder_{reminder.id}",
        data={"id": reminder.id, "text": reminder.text},
    )
    logger.info("Creato job %s per %s", job.name, remind_at)


def restore_pending_reminders(application):
    from dama_bot.database.connection import SessionLocal
    from dama_bot.database.repository import ReminderRepository

    repo = ReminderRepository(SessionLocal)
    reminders = repo.get_pending()

    logger.info(f"Restoring {len(reminders)} pending reminders")

    for reminder in reminders:
        remind_at = ensure_rome_tz(reminder.remind_at)
        application.job_queue.run_once(
            send_reminder,
            when=remind_at,
            chat_id=reminder.chat_id,
            name=f"reminder_{reminder.id}",
            data={"id": reminder.id, "text": reminder.text},
        )


def cancel_reminder_job(job_queue, reminder_id: int):
    """Cancel a scheduled reminder job in the Telegram JobQueue by its ID."""
    job_name = f"reminder_{reminder_id}"
    jobs = job_queue.get_jobs_by_name(job_name)
    if jobs:
        logger.info(f"Canceling scheduled job(s) for reminder {reminder_id}")
        for job in jobs:
            job.schedule_removal()


def mark_as_sent(reminder_id: int):
    from dama_bot.database.connection import SessionLocal
    from dama_bot.database.repository import ReminderRepository

    repo = ReminderRepository(SessionLocal)
    repo.mark_sent(reminder_id)
