from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReminderDB(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_id: Mapped[int] = mapped_column(Integer)
    sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class FreeDayDB(Base):
    __tablename__ = "free_days"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class MealType(Enum):
    COLAZIONE = "colazione"
    SPUNTINO = "spuntino"
    PRANZO = "pranzo"
    MERENDA = "merenda"
    CENA = "cena"

    @staticmethod
    def from_string(value: str) -> "MealType":
        return MealType(value.lower())


@dataclass
class Meal:
    type: MealType
    food: list[str]


@dataclass
class MealDay:
    colazione: Meal
    spuntino: Meal
    pranzo: Meal
    merenda: Meal
    cena: Meal
