"""High-level session management layer."""

import logging
from typing import Optional, List

from src.storage.database import (
    Session,
    init_db,
    create_session as db_create_session,
    get_session as db_get_session,
    get_session_by_id,
    list_sessions as db_list_sessions,
    delete_session as db_delete_session,
    set_active_session,
    get_active_session,
    cleanup_old_sessions as db_cleanup_old_sessions,
)

logger = logging.getLogger(__name__)


class SessionManager:
    """High-level session management.

    Provides a clean API for session CRUD operations and switching.
    Wraps the database layer with initialization handling and logging.
    """

    def __init__(self):
        """Initialize session manager."""
        self._initialized = False

    def init_db(self) -> None:
        """Initialize database if not already initialized."""
        if not self._initialized:
            init_db()
            self._initialized = True

    def create_session(self, user_id: str, opencode_session_id: str, name: str) -> Session:
        """Create a new session mapping.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID
            name: Session display name

        Returns:
            Created Session object

        Raises:
            ValueError: If session already exists (opencode_session_id is unique)
        """
        self.init_db()
        session_id = db_create_session(user_id, opencode_session_id, name)
        logger.info(f"Created session: {session_id} for user {user_id}")
        return self.get_session_by_id(session_id)

    def get_session(self, user_id: str, opencode_session_id: str) -> Optional[Session]:
        """Get session by user and OpenCode session ID.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID

        Returns:
            Session object or None if not found
        """
        self.init_db()
        return db_get_session(user_id, opencode_session_id)

    def get_session_by_id(self, session_id: int) -> Optional[Session]:
        """Get session by database ID.

        Args:
            session_id: Session database ID

        Returns:
            Session object or None if not found
        """
        self.init_db()
        return get_session_by_id(session_id)

    def list_sessions(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Session]:
        """List sessions for a user.

        Args:
            user_id: Feishu user ID
            limit: Maximum sessions to return (default 20)
            offset: Number of sessions to skip (default 0)

        Returns:
            List of Session objects, ordered by updated_at DESC
        """
        self.init_db()
        return db_list_sessions(user_id, limit, offset)

    def delete_session(self, user_id: str, opencode_session_id: str) -> bool:
        """Delete a session.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID

        Returns:
            True if session was deleted, False if not found
        """
        self.init_db()
        result = db_delete_session(user_id, opencode_session_id)
        if result:
            logger.info(f"Deleted session {opencode_session_id} for user {user_id}")
        return result

    def switch_session(self, user_id: str, opencode_session_id: str) -> bool:
        """Switch to a specific session.

        Deactivates all other sessions for the user and activates the specified one.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID to switch to

        Returns:
            True if switch was successful, False if session not found
        """
        self.init_db()
        result = set_active_session(user_id, opencode_session_id)
        if result:
            logger.info(f"Switched to session {opencode_session_id} for user {user_id}")
        return result

    def get_current_session(self, user_id: str) -> Optional[Session]:
        """Get the currently active session for a user.

        Args:
            user_id: Feishu user ID

        Returns:
            Active Session object or None if no active session
        """
        self.init_db()
        return get_active_session(user_id)

    def get_or_create_session(
        self, user_id: str, opencode_session_id: str, name: str = "Default Session"
    ) -> Session:
        """Get existing session or create new one.

        Useful for idempotent session creation.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID
            name: Session name (only used if creating new)

        Returns:
            Existing or newly created Session object
        """
        session = self.get_session(user_id, opencode_session_id)
        if session:
            return session
        return self.create_session(user_id, opencode_session_id, name)

    def find_by_name(self, user_id: str, name: str) -> Optional[Session]:
        """Find session by name for a user.

        Case-insensitive name matching.

        Args:
            user_id: Feishu user ID
            name: Session name to search for

        Returns:
            Session object or None if not found
        """
        sessions = self.list_sessions(user_id, limit=100)
        for session in sessions:
            if session.name.lower() == name.lower():
                return session
        return None

    def count_sessions(self, user_id: str) -> int:
        """Count total sessions for a user.

        Args:
            user_id: Feishu user ID

        Returns:
            Total number of sessions for the user
        """
        # Get all sessions (with high limit)
        sessions = self.list_sessions(user_id, limit=10000)
        return len(sessions)


    def rename_session(self, user_id: str, opencode_session_id: str, new_name: str) -> bool:
        """Rename a session.

        Args:
            user_id: Feishu user ID
            opencode_session_id: OpenCode session ID
            new_name: New session name

        Returns:
            True if session was renamed, False otherwise
        """
        from src.storage.database import rename_session as db_rename_session
        
        self.init_db()
        result = db_rename_session(user_id, opencode_session_id, new_name)
        if result:
            logger.info(f"Renamed session {opencode_session_id} to '{new_name}' for user {user_id}")
        return result

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions not updated in N days.
        
        Preserves active sessions.
        
        Args:
            days: Number of days to keep sessions (default 30)
            
        Returns:
            Number of deleted sessions
        """
        self.init_db()
        deleted = db_cleanup_old_sessions(days)
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old sessions (older than {days} days)")
        return deleted

# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get session manager singleton.

    Returns:
        SessionManager singleton instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
