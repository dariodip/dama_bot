from datetime import date

from dama_bot.database.repository import FreeDayRepository


def test_free_day_repository_create(db_session_factory):
    repo = FreeDayRepository(db_session_factory)
    free_day_date = date(2025, 12, 25)

    free_day = repo.create(free_day_date, "testuser", 123)

    assert free_day.id is not None
    assert free_day.date == free_day_date
    assert free_day.username == "testuser"
    assert free_day.chat_id == 123


def test_free_day_repository_get_last_free_day(db_session_factory):
    repo = FreeDayRepository(db_session_factory)
    dates = [
        [2025, 12, 25],
        [2025, 12, 31],
        [2026, 3, 1]
    ]
    expected_date = dates[-1]

    for date_list in dates:
        test_date = date(*date_list)
        repo.create(test_date, "testuser", 123)
    
    fetched = repo.get_last_by_user(123, "testuser")

    assert fetched is not None
    assert fetched.date == date(*expected_date)
