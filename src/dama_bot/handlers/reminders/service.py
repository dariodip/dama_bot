from datetime import datetime

from dama_bot.database.connection import SessionLocal
from dama_bot.database.models import ReminderDB

from .models import Reminder

def create_reminder(
    reminder: Reminder,
    chat_id: int,
    user_id: int,
    username: str
    ):
    with SessionLocal() as session:
        db_reminder = ReminderDB(
            chat_id=chat_id,
            text=reminder.text,
            remind_at=reminder.remind_at,
            message_id=user_id,
            username=username
        )
        session.add(db_reminder)
        session.commit()
        return db_reminder

def get_pending_reminders():
    with SessionLocal() as session:
        return (
            session.query(ReminderDB)
            .filter(
                ReminderDB.sent == False,
                ReminderDB.remind_at > datetime.now(),
            )
            .all()
        )