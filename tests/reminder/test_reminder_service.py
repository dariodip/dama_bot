from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from dama_bot.database.models import ReminderDB
from dama_bot.services.reminder import ReminderService


@pytest.fixture
def repo_mock():
    return MagicMock()


@pytest.fixture
def service(repo_mock):
    return ReminderService(repo_mock)


def test_create_reminder(service, repo_mock, mocker):
    schedule_mock = mocker.patch("dama_bot.services.reminder.schedule_reminder")

    remind_at = datetime.now() + timedelta(hours=1)
    db_reminder = ReminderDB(id=1, text="test", remind_at=remind_at, chat_id=123, username="user")
    repo_mock.create.return_value = db_reminder

    app_mock = MagicMock()
    res = service.create_reminder(
        text="test",
        remind_at=remind_at,
        chat_id=123,
        user_id=456,
        username="user",
        application=app_mock,
    )

    assert res == db_reminder
    repo_mock.create.assert_called_once_with(
        text="test", remind_at=remind_at, username="user", chat_id=123, message_id=456
    )
    schedule_mock.assert_called_once_with(app_mock, db_reminder)


def test_list_reminders(service, repo_mock):
    r_list = [ReminderDB(id=1, text="r1"), ReminderDB(id=2, text="r2")]
    repo_mock.list_active.return_value = r_list

    res = service.list_reminders(123, "user")
    assert res == r_list
    repo_mock.list_active.assert_called_once_with(chat_id=123, username="user")


def test_delete_reminder(service, repo_mock, mocker):
    cancel_mock = mocker.patch("dama_bot.services.reminder.cancel_reminder_job")
    repo_mock.delete.return_value = True

    app_mock = MagicMock()
    res = service.delete_reminder(reminder_id=1, chat_id=123, username="user", application=app_mock)

    assert res is True
    cancel_mock.assert_called_once_with(app_mock.job_queue, 1)
    repo_mock.delete.assert_called_once_with(reminder_id=1, chat_id=123, username="user")


def test_update_reminder(service, repo_mock, mocker):
    cancel_mock = mocker.patch("dama_bot.services.reminder.cancel_reminder_job")
    schedule_mock = mocker.patch("dama_bot.services.reminder.schedule_reminder")

    remind_at = datetime.now() + timedelta(hours=1)
    db_reminder = ReminderDB(id=1, text="orig", remind_at=remind_at, chat_id=123, username="user")

    repo_mock.get_by_id.return_value = db_reminder

    # Try updating someone else's reminder or non-existent
    app_mock = MagicMock()
    assert service.update_reminder(99, 123, "other", "new", None, app_mock) is None

    # Update text only (no rescheduling)
    repo_mock.update.return_value = ReminderDB(
        id=1, text="new", remind_at=remind_at, chat_id=123, username="user"
    )
    res = service.update_reminder(1, 123, "user", "new", None, app_mock)

    assert res is not None
    assert res.text == "new"
    cancel_mock.assert_not_called()
    schedule_mock.assert_not_called()

    # Update time (trigger rescheduling)
    new_time = remind_at + timedelta(days=1)
    repo_mock.update.return_value = ReminderDB(
        id=1, text="new", remind_at=new_time, chat_id=123, username="user"
    )

    res = service.update_reminder(1, 123, "user", "new", new_time, app_mock)
    assert res.remind_at == new_time
    cancel_mock.assert_called_once_with(app_mock.job_queue, 1)
    schedule_mock.assert_called_once_with(app_mock, repo_mock.update.return_value)
