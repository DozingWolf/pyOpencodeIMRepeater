"""Tests for session manager."""

import pytest
from src.storage.session_manager import get_session_manager, SessionManager
from src.storage.database import Session


@pytest.fixture
def session_manager(temp_db):
    """Create a session manager with temporary database."""
    # Reset the singleton to use the new temp_db
    import src.storage.session_manager as sm_module

    sm_module._session_manager = None

    manager = get_session_manager()
    manager.init_db()
    yield manager

    # Cleanup
    sm_module._session_manager = None


def test_create_session(session_manager):
    """Test creating a new session."""
    session_id = session_manager.create_session("user1", "session1", "Test Session")
    assert session_id is not None
    assert isinstance(session_id, Session)
    assert session_id.user_id == "user1"
    assert session_id.opencode_session_id == "session1"
    assert session_id.name == "Test Session"


def test_get_session(session_manager):
    """Test retrieving a session."""
    # Create a session
    created = session_manager.create_session("user1", "session1", "Test Session")

    # Get the session
    retrieved = session_manager.get_session("user1", "session1")
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.user_id == "user1"


def test_get_session_not_found(session_manager):
    """Test retrieving a non-existent session."""
    retrieved = session_manager.get_session("user1", "nonexistent")
    assert retrieved is None


def test_list_sessions(session_manager):
    """Test listing sessions for a user."""
    # Create multiple sessions
    session_manager.create_session("user1", "session1", "Session 1")
    session_manager.create_session("user1", "session2", "Session 2")
    session_manager.create_session("user2", "session3", "Session 3")

    # List sessions for user1
    sessions = session_manager.list_sessions("user1")
    assert len(sessions) == 2

    # List sessions for user2
    sessions = session_manager.list_sessions("user2")
    assert len(sessions) == 1


def test_delete_session(session_manager):
    """Test deleting a session."""
    # Create a session
    session_manager.create_session("user1", "session1", "Test Session")

    # Delete the session
    result = session_manager.delete_session("user1", "session1")
    assert result is True

    # Verify it's deleted
    retrieved = session_manager.get_session("user1", "session1")
    assert retrieved is None


def test_delete_session_not_found(session_manager):
    """Test deleting a non-existent session."""
    result = session_manager.delete_session("user1", "nonexistent")
    assert result is False


def test_switch_session(session_manager):
    """Test switching active session."""
    # Create two sessions
    session_manager.create_session("user1", "session1", "Session 1")
    session_manager.create_session("user1", "session2", "Session 2")

    # Switch to session1
    result = session_manager.switch_session("user1", "session1")
    assert result is True

    # Verify session1 is active
    active = session_manager.get_current_session("user1")
    assert active is not None
    assert active.opencode_session_id == "session1"

    # Switch to session2
    session_manager.switch_session("user1", "session2")
    active = session_manager.get_current_session("user1")
    assert active.opencode_session_id == "session2"


def test_get_or_create_session(session_manager):
    """Test get or create session functionality."""
    # First call should create
    session1 = session_manager.get_or_create_session("user1", "session1", "Test")
    assert session1 is not None
    assert session1.name == "Test"

    # Second call should get existing
    session2 = session_manager.get_or_create_session("user1", "session1", "Different")
    assert session2.id == session1.id
    assert session2.name == "Test"  # Name shouldn't change


def test_find_by_name(session_manager):
    """Test finding session by name."""
    session_manager.create_session("user1", "session1", "My Session")

    # Find by name (case-insensitive)
    found = session_manager.find_by_name("user1", "my session")
    assert found is not None
    assert found.opencode_session_id == "session1"

    # Not found
    not_found = session_manager.find_by_name("user1", "nonexistent")
    assert not_found is None


def test_count_sessions(session_manager):
    """Test counting sessions for a user."""
    session_manager.create_session("user1", "session1", "Session 1")
    session_manager.create_session("user1", "session2", "Session 2")
    session_manager.create_session("user2", "session3", "Session 3")

    count = session_manager.count_sessions("user1")
    assert count == 2

    count = session_manager.count_sessions("user2")
    assert count == 1


def test_rename_session(session_manager):
    """Test renaming a session."""
    session_manager.create_session("user1", "session1", "Old Name")

    # Rename
    result = session_manager.rename_session("user1", "session1", "New Name")
    assert result is True

    # Verify rename
    session = session_manager.get_session("user1", "session1")
    assert session.name == "New Name"


def test_singleton():
    """Test that get_session_manager returns a singleton."""
    sm1 = get_session_manager()
    sm2 = get_session_manager()
    assert sm1 is sm2


def test_cleanup_old_sessions(session_manager):
    """Test cleaning up old sessions."""
    import time
    from datetime import datetime, timedelta
    
    # Create a session
    session_manager.create_session("user1", "session1", "Old Session")
    session_manager.create_session("user1", "session2", "New Session")
    
    # Make session1 active (should be preserved)
    session_manager.switch_session("user1", "session1")
    
    # Cleanup (should not delete active session even if old)
    deleted = session_manager.cleanup_old_sessions(days=30)
    assert deleted == 0  # No sessions deleted since session1 is active
