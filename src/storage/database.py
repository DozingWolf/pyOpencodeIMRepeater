"""SQLite database operations for session management."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Session:
    """Session data model."""

    id: int
    user_id: str
    opencode_session_id: str
    name: str
    created_at: str
    updated_at: str
    is_active: bool


def get_db_path() -> Path:
    """Get database file path."""
    from src.config import get_settings
    settings = get_settings()
    return Path(settings.database_path)
    """Get database file path."""
    return Path("data/sessions.db")


def get_connection() -> sqlite3.Connection:
    """Get database connection."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            opencode_session_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON sessions(user_id)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_opencode_session_id ON sessions(opencode_session_id)"
    )
    conn.commit()
    conn.close()


def create_session(user_id: str, opencode_session_id: str, name: str) -> int:
    """Create a new session.

    Args:
        user_id: Feishu user ID
        opencode_session_id: OpenCode session ID
        name: Session name

    Returns:
        Created session ID
    """
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, opencode_session_id, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, opencode_session_id, name, now, now),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_session(user_id: str, opencode_session_id: str) -> Optional[Session]:
    """Get session by user_id and opencode_session_id.

    Args:
        user_id: Feishu user ID
        opencode_session_id: OpenCode session ID

    Returns:
        Session object or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sessions WHERE user_id = ? AND opencode_session_id = ?",
        (user_id, opencode_session_id),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return Session(**dict(row))
    return None


def get_session_by_id(session_id: int) -> Optional[Session]:
    """Get session by ID.

    Args:
        session_id: Session ID

    Returns:
        Session object or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Session(**dict(row))
    return None


def list_sessions(user_id: str, limit: int = 20, offset: int = 0) -> List[Session]:
    """List sessions for a user.

    Args:
        user_id: Feishu user ID
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip

    Returns:
        List of Session objects
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        (user_id, limit, offset),
    )
    rows = cursor.fetchall()
    conn.close()
    return [Session(**dict(row)) for row in rows]


def delete_session(user_id: str, opencode_session_id: str) -> bool:
    """Delete a session.

    Args:
        user_id: Feishu user ID
        opencode_session_id: OpenCode session ID

    Returns:
        True if session was deleted, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM sessions WHERE user_id = ? AND opencode_session_id = ?",
        (user_id, opencode_session_id),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def set_active_session(user_id: str, opencode_session_id: str) -> bool:
    """Set a session as active for a user.

    Args:
        user_id: Feishu user ID
        opencode_session_id: OpenCode session ID

    Returns:
        True if session was activated, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Deactivate all sessions for this user
    cursor.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
    # Activate the specified session
    cursor.execute(
        "UPDATE sessions SET is_active = 1, updated_at = ? WHERE user_id = ? AND opencode_session_id = ?",
        (datetime.utcnow().isoformat(), user_id, opencode_session_id),
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_active_session(user_id: str) -> Optional[Session]:
    """Get the active session for a user.

    Args:
        user_id: Feishu user ID

    Returns:
        Active Session object or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE user_id = ? AND is_active = 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Session(**dict(row))
    return None



def rename_session(user_id: str, opencode_session_id: str, new_name: str) -> bool:
    """Rename a session.

    Args:
        user_id: Feishu user ID
        opencode_session_id: OpenCode session ID
        new_name: New session name

    Returns:
        True if session was renamed, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET name = ?, updated_at = ? WHERE user_id = ? AND opencode_session_id = ?",
        (new_name, datetime.utcnow().isoformat(), user_id, opencode_session_id),
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def cleanup_old_sessions(days: int = 30) -> int:
    """Remove sessions not updated in N days.
    
    Preserves active sessions (is_active = 1).
    
    Args:
        days: Number of days to keep sessions (default 30)
        
    Returns:
        Number of deleted sessions
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    # Don't delete active sessions
    cursor.execute(
        'DELETE FROM sessions WHERE updated_at < ? AND is_active = 0',
        (cutoff,)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted
