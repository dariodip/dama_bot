import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dama_bot.database.models import Base


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session_factory(db_engine):
    Session = sessionmaker(bind=db_engine, expire_on_commit=False)
    return Session
