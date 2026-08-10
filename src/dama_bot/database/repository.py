import logging
from datetime import datetime, date

from dama_bot.database.models import ReminderDB, FreeDayDB

logger = logging.getLogger(__name__)


class ReminderRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(
        self,
        text: str,
        remind_at: datetime,
        username: str,
        chat_id: int,
        message_id: int | None = None,
    ) -> ReminderDB:
        with self.session_factory() as session:
            db_reminder = ReminderDB(
                text=text,
                remind_at=remind_at,
                username=username,
                chat_id=chat_id,
                message_id=message_id if message_id is not None else 0,
                sent=False,
            )
            session.add(db_reminder)
            session.commit()
            # Refresh to load auto-generated fields (like id and created_at)
            session.refresh(db_reminder)
            return db_reminder

    def get_by_id(self, reminder_id: int) -> ReminderDB | None:
        with self.session_factory() as session:
            return session.get(ReminderDB, reminder_id)

    def list_active(self, chat_id: int, username: str) -> list[ReminderDB]:
        with self.session_factory() as session:
            return (
                session.query(ReminderDB)
                .filter(
                    ReminderDB.chat_id == chat_id,
                    ReminderDB.username == username,
                    ReminderDB.sent.is_(False),
                )
                .all()
            )

    def delete(self, reminder_id: int, chat_id: int, username: str) -> bool:
        with self.session_factory() as session:
            reminder = (
                session.query(ReminderDB)
                .filter(
                    ReminderDB.id == reminder_id,
                    ReminderDB.chat_id == chat_id,
                    ReminderDB.username == username,
                )
                .first()
            )
            if reminder:
                session.delete(reminder)
                session.commit()
                return True
            return False

    def update(
        self,
        reminder_id: int,
        chat_id: int,
        username: str,
        text: str | None = None,
        remind_at: datetime | None = None,
    ) -> ReminderDB | None:
        with self.session_factory() as session:
            reminder = (
                session.query(ReminderDB)
                .filter(
                    ReminderDB.id == reminder_id,
                    ReminderDB.chat_id == chat_id,
                    ReminderDB.username == username,
                )
                .first()
            )
            if reminder:
                if text is not None:
                    reminder.text = text
                if remind_at is not None:
                    reminder.remind_at = remind_at
                session.commit()
                session.refresh(reminder)
                return reminder
            return None

    def get_pending(self) -> list[ReminderDB]:
        with self.session_factory() as session:
            return (
                session.query(ReminderDB)
                .filter(
                    ReminderDB.sent.is_(False),
                    ReminderDB.remind_at > datetime.now(),
                )
                .all()
            )

    def mark_sent(self, reminder_id: int) -> bool:
        with self.session_factory() as session:
            reminder = session.get(ReminderDB, reminder_id)
            if reminder:
                reminder.sent = True
                session.commit()
                return True
            return False


class FreeDayRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(
        self,
        date: date,
        username: str,
        chat_id: int,
    ) -> FreeDayDB:
        with self.session_factory() as session:
            db_free_day = FreeDayDB(
                date=date,
                username=username,
                chat_id=chat_id,
            )
            session.add(db_free_day)
            session.commit()
            # Refresh to load auto-generated fields (like id and created_at)
            session.refresh(db_free_day)
            return db_free_day

    def get_last_by_user(self, chat_id: int, username: str) -> FreeDayDB | None:
        with self.session_factory() as session:
            return (
                session.query(FreeDayDB)
                .filter(
                    FreeDayDB.chat_id == chat_id,
                    FreeDayDB.username == username,
                )
                .order_by(FreeDayDB.date.desc())
                .first()
            )
