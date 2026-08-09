from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from dama_bot.database.models import ReminderDB
from dama_bot.database.repository import ReminderRepository
from dama_bot.handlers.reminders.scheduler import (
    cancel_reminder_job,
    ensure_rome_tz,
    restore_pending_reminders,
    schedule_reminder,
)


def test_ensure_rome_tz():
    # Naive datetime
    naive = datetime(2026, 8, 9, 12, 0, 0)
    aware_rome = ensure_rome_tz(naive)
    assert aware_rome.tzinfo == ZoneInfo("Europe/Rome")
    assert aware_rome.hour == 12

    # Aware UTC datetime
    utc_dt = datetime(2026, 8, 9, 10, 0, 0, tzinfo=UTC)
    aware_rome_from_utc = ensure_rome_tz(utc_dt)
    assert aware_rome_from_utc.tzinfo == ZoneInfo("Europe/Rome")
    # 10:00 UTC should be 12:00 in Europe/Rome during daylight saving (August)
    assert aware_rome_from_utc.hour == 12


def test_schedule_reminder():
    app_mock = MagicMock()
    reminder = ReminderDB(
        id=42, text="dentist", remind_at=datetime(2026, 8, 9, 15, 0, 0), chat_id=999
    )

    schedule_reminder(app_mock, reminder)

    app_mock.job_queue.run_once.assert_called_once()
    call_args = app_mock.job_queue.run_once.call_args[1]

    assert call_args["chat_id"] == 999
    assert call_args["name"] == "reminder_42"
    assert call_args["data"] == {"id": 42, "text": "dentist"}
    assert call_args["when"].tzinfo == ZoneInfo("Europe/Rome")


def test_cancel_reminder_job():
    jq_mock = MagicMock()
    job_mock = MagicMock()
    jq_mock.get_jobs_by_name.return_value = [job_mock]

    cancel_reminder_job(jq_mock, 42)

    jq_mock.get_jobs_by_name.assert_called_once_with("reminder_42")
    job_mock.schedule_removal.assert_called_once()


def test_restore_pending_reminders(db_session_factory, mocker):
    repo = ReminderRepository(db_session_factory)
    mocker.patch("dama_bot.database.repository.ReminderRepository.get_pending")

    future_time = datetime.now() + timedelta(hours=2)
    # Simple setup
    r1 = ReminderDB(id=1, text="r1", remind_at=future_time, chat_id=101)
    r2 = ReminderDB(id=2, text="r2", remind_at=future_time, chat_id=102)

    repo.get_pending.return_value = [r1, r2]

    app_mock = MagicMock()
    restore_pending_reminders(app_mock)

    assert app_mock.job_queue.run_once.call_count == 2
