from datetime import datetime, timedelta

from dama_bot.database.repository import ReminderRepository


def test_reminder_repository_create(db_session_factory):
    repo = ReminderRepository(db_session_factory)
    remind_at = datetime.now() + timedelta(hours=1)

    reminder = repo.create(
        text="test reminder", remind_at=remind_at, username="testuser", chat_id=123, message_id=456
    )

    assert reminder.id is not None
    assert reminder.text == "test reminder"
    assert reminder.remind_at == remind_at
    assert reminder.username == "testuser"
    assert reminder.chat_id == 123
    assert reminder.message_id == 456
    assert reminder.sent is False


def test_reminder_repository_get_by_id(db_session_factory):
    repo = ReminderRepository(db_session_factory)
    remind_at = datetime.now() + timedelta(hours=1)

    created = repo.create("test", remind_at, "user", 111, 222)
    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.text == "test"


def test_reminder_repository_list_active(db_session_factory):
    repo = ReminderRepository(db_session_factory)
    remind_at = datetime.now() + timedelta(hours=1)

    repo.create("active1", remind_at, "user", 111)
    repo.create("active2", remind_at, "user", 111)
    # Different user/chat
    repo.create("diff_user", remind_at, "other", 222)
    # Already sent
    r4 = repo.create("sent", remind_at, "user", 111)
    repo.mark_sent(r4.id)

    active = repo.list_active(111, "user")
    assert len(active) == 2
    assert {r.text for r in active} == {"active1", "active2"}


def test_reminder_repository_delete(db_session_factory):
    repo = ReminderRepository(db_session_factory)
    remind_at = datetime.now() + timedelta(hours=1)

    r = repo.create("delete me", remind_at, "user", 111)

    # Try deleting with wrong username
    assert repo.delete(r.id, 111, "wrong_user") is False

    # Try deleting with correct username
    assert repo.delete(r.id, 111, "user") is True
    assert repo.get_by_id(r.id) is None


def test_reminder_repository_update(db_session_factory):
    repo = ReminderRepository(db_session_factory)
    remind_at = datetime.now() + timedelta(hours=1)
    new_remind_at = remind_at + timedelta(days=1)

    r = repo.create("original", remind_at, "user", 111)

    # Try updating wrong user's reminder
    assert repo.update(r.id, 111, "other", text="new text") is None

    # Update text and time
    updated = repo.update(r.id, 111, "user", text="updated text", remind_at=new_remind_at)
    assert updated is not None
    assert updated.text == "updated text"
    assert updated.remind_at == new_remind_at

    # Update only text
    updated = repo.update(r.id, 111, "user", text="only text updated")
    assert updated.text == "only text updated"
    assert updated.remind_at == new_remind_at


def test_reminder_repository_get_pending(db_session_factory):
    repo = ReminderRepository(db_session_factory)

    future = datetime.now() + timedelta(hours=2)
    past = datetime.now() - timedelta(hours=1)

    r1 = repo.create("future_pending", future, "user", 111)
    repo.create("past_pending", past, "user", 111)
    r3 = repo.create("future_sent", future, "user", 111)
    repo.mark_sent(r3.id)

    pending = repo.get_pending()
    assert len(pending) == 1
    assert pending[0].id == r1.id
