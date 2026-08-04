import logging

from dama_bot.handlers.reminders.service import get_pending_reminders
from telegram.ext import ContextTypes
from dama_bot.database.connection import SessionLocal
from dama_bot.database.models import ReminderDB

logger = logging.getLogger(__name__)

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    reminder = job.data
    
    logger.info(f"Sending reminder {reminder['id']}")

    await context.bot.send_message(
        chat_id=job.chat_id, 
        text=f"Ricordati:\n\n{reminder['text']}"
    )

    mark_as_sent(reminder["id"])
    

def schedule_reminder(
    application,
    reminder: ReminderDB
):
    logger.info("Scheduling reminder %s at %s (%s)",
    reminder.text, reminder.remind_at, reminder.remind_at.tzinfo)

    job = application.job_queue.run_once(
        send_reminder,
        when=reminder.remind_at,
        chat_id=reminder.chat_id,
        data={
            "id": reminder.id,
            "text": reminder.text
        })
    logger.info("Creato job %s per %s", job.name, reminder.remind_at)

def restore_pending_reminders(application):
    reminders = get_pending_reminders()
    
    logger.info(f"Restoring {len(reminders)} pending reminders")

    for reminder in reminders:
        application.job_queue.run_once(
            send_reminder,
            when=reminder.remind_at,
            chat_id=reminder.chat_id,
            data={
                'id': reminder.id,
                'text': reminder.text
            }
        )

def mark_as_sent(reminder_id: int):
    with SessionLocal() as session:
        reminder = session.get(
            ReminderDB,
            reminder_id
        )

        if reminder:
            reminder.sent = True
            session.commit()
