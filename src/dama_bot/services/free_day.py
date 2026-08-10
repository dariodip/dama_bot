import logging
from datetime import timedelta, date

from dama_bot.database.models import FreeDayDB
from dama_bot.database.repository import FreeDayRepository

logger = logging.getLogger(__name__)

STEP = 3

class FreeDayService:
    def __init__(self, repository: FreeDayRepository):
        self.repository = repository

    def create_free_day(
        self, date: date, chat_id: int, username: str
    ) -> FreeDayDB:
        logger.info(f"Creating free day via service: '{date}' for user {username} in chat {chat_id}")
        db_free_day = self.repository.create(
            date=date, username=username, chat_id=chat_id
        )
        
        return db_free_day

    def get_last_by_user(self, chat_id: int, username: str) -> FreeDayDB | None:
        return self.repository.get_last_by_user(chat_id=chat_id, username=username)

    def is_a_free_day(self, date: date, chat_id: int, username: str) -> bool:
        last_free_day = self.get_last_by_user(chat_id=chat_id, username=username)
        if last_free_day is None:
            return False
        return (date - last_free_day.date).days % STEP == 0

    def next_free_day(self, chat_id: int, username: str) -> date:
        last_free_date = self.get_last_by_user(chat_id=chat_id, username=username)
        if last_free_date is None:
            raise ValueError("Non è stato registrato alcun giorno libero")
        
        last_free_day = last_free_date.date

        today = date.today()
        if last_free_day >= today:
            return last_free_day
        offset = (today - last_free_day).days % STEP
        if offset == 0:
            return today
        return today + timedelta(days=STEP - offset)
