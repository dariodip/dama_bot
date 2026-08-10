from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from dama_bot.database.models import FreeDayDB
from dama_bot.services.free_day import FreeDayService


@pytest.fixture
def repo_mock():
    return MagicMock()


@pytest.fixture
def service(repo_mock):
    return FreeDayService(repo_mock)


def test_create_free_day(service, repo_mock, mocker):
    test_date = date(2025, 12, 25)
    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    repo_mock.create.return_value = db_free_day

    res = service.create_free_day(test_date, 123, "user")

    assert res == db_free_day
    repo_mock.create.assert_called_once_with(date=test_date, username="user", chat_id=123)


def test_get_last_by_user(service, repo_mock):
    test_date = date(2025, 12, 25)
    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    repo_mock.get_last_by_user.return_value = db_free_day

    res = service.get_last_by_user(123, "user")

    assert res == db_free_day
    repo_mock.get_last_by_user.assert_called_once_with(chat_id=123, username="user")


def test_is_a_free_day(service, repo_mock):
    test_date = date(2025, 12, 25)
    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    repo_mock.get_last_by_user.return_value = db_free_day

    assert service.is_a_free_day(test_date, 123, "user") is True
    repo_mock.get_last_by_user.assert_called_once_with(chat_id=123, username="user")


def test_next_free_day(service, repo_mock):
    test_date = date(2025, 12, 25)
    _next_free_day = date(2025, 12, 28)
    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    repo_mock.get_last_by_user.return_value = db_free_day

    res = service.next_free_day(123, "user")

    assert res is not None

    repo_mock.get_last_by_user.assert_called_once_with(chat_id=123, username="user")


def test_is_not_a_free_day(service, repo_mock):
    test_date = date(2025, 12, 25)
    db_free_day = FreeDayDB(date=test_date, username="user", chat_id=123)
    repo_mock.get_last_by_user.return_value = db_free_day

    res = service.is_a_free_day(test_date + timedelta(days=1), 123, "user")

    assert res is False
    repo_mock.get_last_by_user.assert_called_once_with(chat_id=123, username="user")
