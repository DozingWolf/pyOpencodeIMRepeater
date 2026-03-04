"""Database operations tests."""

import os
import tempfile

import pytest

from src.storage.database import (
    create_session,
    delete_session,
    get_active_session,
    get_session,
    init_db,
    list_sessions,
    set_active_session,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up a temporary database for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        # Patch database path
        import src.storage.database as db_module
        from pathlib import Path

        original_get_db_path = db_module.get_db_path
        db_module.get_db_path = lambda: Path(db_path)
        init_db()
        yield
        db_module.get_db_path = original_get_db_path


def test_create_and_get_session():
    """Test creating and retrieving a session."""
    session_id = create_session("user1", "session1", "Test")
    assert session_id == 1

    session = get_session("user1", "session1")
    assert session is not None
    assert session.name == "Test"
    assert session.user_id == "user1"
    assert session.opencode_session_id == "session1"


def test_list_sessions():
    """Test listing sessions for a user."""
    create_session("user1", "s1", "Session 1")
    create_session("user1", "s2", "Session 2")
    create_session("user2", "s3", "Session 3")  # Different user

    sessions = list_sessions("user1")
    assert len(sessions) == 2

    # Verify only user1's sessions are returned
    for session in sessions:
        assert session.user_id == "user1"


def test_delete_session():
    """Test deleting a session."""
    create_session("user1", "to_delete", "Delete Me")
    result = delete_session("user1", "to_delete")
    assert result is True

    session = get_session("user1", "to_delete")
    assert session is None


def test_delete_nonexistent_session():
    """Test deleting a session that doesn't exist."""
    result = delete_session("user1", "nonexistent")
    assert result is False


def test_active_session():
    """Test setting and getting active session."""
    create_session("user1", "s1", "Session 1")
    create_session("user1", "s2", "Session 2")

    # Set s2 as active
    set_active_session("user1", "s2")
    active = get_active_session("user1")
    assert active is not None
    assert active.opencode_session_id == "s2"
    assert active.is_active == 1


def test_active_session_switch():
    """Test switching active session."""
    create_session("user1", "s1", "Session 1")
    create_session("user1", "s2", "Session 2")

    # Set s1 as active
    set_active_session("user1", "s1")
    active = get_active_session("user1")
    assert active.opencode_session_id == "s1"

    # Switch to s2
    set_active_session("user1", "s2")
    active = get_active_session("user1")
    assert active.opencode_session_id == "s2"

    # Verify s1 is no longer active
    s1 = get_session("user1", "s1")
    assert s1.is_active == 0


def test_get_nonexistent_session():
    """Test getting a session that doesn't exist."""
    session = get_session("nonexistent_user", "nonexistent_session")
    assert session is None


def test_get_active_session_when_none():
    """Test getting active session when none is set."""
    create_session("user1", "s1", "Session 1")
    # Don't set any session as active
    active = get_active_session("user1")
    assert active is None
