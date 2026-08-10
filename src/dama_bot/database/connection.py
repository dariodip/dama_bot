from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dama_bot.config import SQLITE_URL

engine = create_engine(SQLITE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
