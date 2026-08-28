import logging
from datetime import date

from dama_bot.plugins.free_day.models import FreeDayDB

logger = logging.getLogger(__name__)


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
