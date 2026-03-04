"""Command handler for Feishu bot slash commands."""

import json
import logging
from datetime import datetime
from typing import Optional, Tuple

from src.opencode.client import get_opencode_client
from src.storage.session_manager import get_session_manager

logger = logging.getLogger(__name__)


COMMAND_HELP = {
    "new": {
        "usage": "/new [name]",
        "description": "Create a new session",
        "example": "/new Project Discussion"
    },
    "list": {
        "usage": "/list",
        "description": "List all your sessions",
        "example": "/list"
    },
    "switch": {
        "usage": "/switch <id|name>",
        "description": "Switch to a different session",
        "example": "/switch Project Discussion"
    },
    "delete": {
        "usage": "/delete <id|name>",
        "description": "Delete a session",
        "example": "/delete old-session"
    },
    "rename": {
        "usage": "/rename <new_name>",
        "description": "Rename current session",
        "example": "/rename New Name"
    },
    "history": {
        "usage": "/history [count]",
        "description": "Show conversation history",
        "example": "/history 20"
    },
    "export": {
        "usage": "/export",
        "description": "Export current session info",
        "example": "/export"
    },
    "help": {
        "usage": "/help [command]",
        "description": "Show help message",
        "example": "/help switch"
    }
}



def parse_command(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse slash command from message text.

    Args:
        text: Message text

    Returns:
        Tuple of (command, args) or (None, None) if not a command
    """
    text = text.strip()
    if not text.startswith("/"):
        return None, None

    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    return command, args


async def handle_help_command(args: str) -> str:
    """Handle /help [command] command."""
    if args.strip():
        # Show help for specific command
        cmd = args.strip().lower().lstrip("/")
        if cmd in COMMAND_HELP:
            help_info = COMMAND_HELP[cmd]
            return f"📖 **/{cmd}**\n\n**Usage:** `{help_info['usage']}`\n**Description:** {help_info['description']}\n**Example:** `{help_info['example']}`"
        else:
            return f"❌ Unknown command: `{args}`\n\nUse `/help` to see all available commands."
    
    # Show general help
    lines = ["📖 **Available Commands:**\n"]
    for cmd, help_info in COMMAND_HELP.items():
        lines.append(f"• `/{cmd}` - {help_info['description']}")
    lines.append("\n💡 Use `/help <command>` for detailed usage.")
    lines.append("\n📝 **Tips:**")
    lines.append("• Just send a message to chat with OpenCode")
    lines.append("• Sessions are automatically created for new users")
    lines.append("• Use `/list` to see all your sessions")
    
    return "\n".join(lines)



async def handle_command(user_id: str, command: str, args: str, chat_id: str) -> str:
    """Handle slash command.

    Args:
        user_id: Feishu user ID
        command: Command name (e.g., "/new")
        args: Command arguments
        chat_id: Feishu chat ID

    Returns:
        Response message to send back
    """
    if command == "/new":
        return await handle_new_command(user_id, args)
    elif command == "/list":
        return await handle_list_command(user_id)
    elif command == "/switch":
        return await handle_switch_command(user_id, args)
    elif command == "/delete":
        return await handle_delete_command(user_id, args)
    elif command == "/export":
        return await handle_export_command(user_id, args)
    elif command == "/help":
        return await handle_help_command(args)
    elif command == "/rename":
        return await handle_rename_command(user_id, args)
    elif command == "/history":
        return await handle_history_command(user_id, args)

    else:
        return f"Unknown command: {command}\n\n{get_help_message()}"


async def handle_new_command(user_id: str, name: str) -> str:
    """Handle /new [name] command.

    Args:
        user_id: Feishu user ID
        name: Optional session name

    Returns:
        Confirmation message
    """
    session_name = name.strip() if name.strip() else "New Session"

    try:
        # Create OpenCode session
        opencode_client = await get_opencode_client()
        opencode_session_id = await opencode_client.create_session(session_name)

        # Store mapping
        session_manager = get_session_manager()
        session = session_manager.create_session(
            user_id=user_id, opencode_session_id=opencode_session_id, name=session_name
        )

        # Switch to new session
        session_manager.switch_session(user_id, opencode_session_id)

        logger.info(f"Created session '{session_name}' ({opencode_session_id}) for user {user_id}")

        return f"✅ Created new session: **{session_name}**\nSession ID: `{opencode_session_id}`\n\nYou are now using this session."

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        return f"❌ Failed to create session: {str(e)}"


async def handle_list_command(user_id: str) -> str:
    """Handle /list command."""
    # TODO: Implement in Task 12
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions(user_id, limit=20)

    if not sessions:
        return "📭 No sessions found. Use `/new` to create one."

    lines = ["📋 **Your Sessions:**\n"]
    for i, session in enumerate(sessions, 1):
        active_marker = " ✅" if session.is_active else ""
        lines.append(f"{i}. **{session.name}**{active_marker}")
        lines.append(f"   ID: `{session.opencode_session_id}`")
        lines.append(f"   Created: {session.created_at[:10]}")
        lines.append("")

    return "\n".join(lines)


async def handle_switch_command(user_id: str, args: str) -> str:
    """Handle /switch <id|name> command."""
    if not args.strip():
        return "⚠️ Please specify a session ID or name.\n\nUsage: `/switch <session_id>` or `/switch <session_name>`"

    session_manager = get_session_manager()

    # Try to find by ID first (exact match)
    sessions = session_manager.list_sessions(user_id, limit=100)

    target_session = None

    # Try exact ID match
    for session in sessions:
        if session.opencode_session_id == args.strip():
            target_session = session
            break

    # Try name match if ID not found
    if not target_session:
        target_session = session_manager.find_by_name(user_id, args.strip())

    if not target_session:
        return f"❌ Session not found: `{args}`\n\nUse `/list` to see your sessions."

    # Switch to the session
    success = session_manager.switch_session(user_id, target_session.opencode_session_id)

    if success:
        return f"✅ Switched to session: **{target_session.name}**\nID: `{target_session.opencode_session_id}`"
    else:
        return f"❌ Failed to switch session. Please try again."


async def handle_delete_command(user_id: str, args: str) -> str:
    """Handle /delete <session> command.

    Args:
        user_id: Feishu user ID
        args: Session ID or name to delete

    Returns:
        Response message
    """
    if not args.strip():
        return "⚠️ Please specify a session to delete.\n\nUsage: `/delete <session_id>` or `/delete <session_name>`"

    session_manager = get_session_manager()
    current_session = session_manager.get_current_session(user_id)

    # Find target session
    sessions = session_manager.list_sessions(user_id, limit=100)
    target_session = None

    # Try exact ID match
    for session in sessions:
        if session.opencode_session_id == args.strip():
            target_session = session
            break

    # Try name match
    if not target_session:
        target_session = session_manager.find_by_name(user_id, args.strip())

    if not target_session:
        return f"❌ Session not found: `{args}`"

    # Check if trying to delete active session
    if current_session and target_session.opencode_session_id == current_session.opencode_session_id:
        return "⚠️ Cannot delete the active session. Use `/switch` to switch to another session first."

    # Delete session
    success = session_manager.delete_session(user_id, target_session.opencode_session_id)

    if success:
        # Also delete from OpenCode (optional)
        try:
            opencode_client = await get_opencode_client()
            await opencode_client.delete_session(target_session.opencode_session_id)
        except Exception as e:
            logger.warning(f"Failed to delete OpenCode session: {e}")

        return f"✅ Deleted session: **{target_session.name}**\nID: `{target_session.opencode_session_id}`"
    else:
        return f"❌ Failed to delete session. Please try again."


def get_help_message() -> str:
    """Get quick help message."""
    return "📖 **Commands:** /new, /list, /switch, /delete, /rename, /history, /export, /help\n\nUse `/help <command>` for details."


async def handle_export_command(user_id: str, args: str) -> str:
    """Handle /export command - export current session as JSON."""
    session_manager = get_session_manager()
    current_session = session_manager.get_current_session(user_id)
    
    if not current_session:
        return "⚠️ No active session. Use `/new` to create one."
    
    # Build export data
    export_data = {
        "session": {
            "id": current_session.id,
            "opencode_session_id": current_session.opencode_session_id,
            "name": current_session.name,
            "created_at": current_session.created_at,
            "updated_at": current_session.updated_at,
            "is_active": current_session.is_active
        },
        "exported_at": datetime.utcnow().isoformat(),
        "user_id": user_id
    }
    
    # Format as JSON code block
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    return f"📦 **Session Export**\n\n```json\n{json_str}\n```\n\n💡 Copy the JSON above to save your session info."



async def handle_rename_command(user_id: str, args: str) -> str:
    """Handle /rename <new_name> command.

    Args:
        user_id: Feishu user ID
        args: New session name

    Returns:
        Confirmation message
    """
    if not args.strip():
        return "⚠️ Please specify a new name.\n\nUsage: `/rename <new_name>`"

    new_name = args.strip()
    if len(new_name) > 50:
        return "⚠️ Session name too long. Maximum 50 characters."

    session_manager = get_session_manager()
    current_session = session_manager.get_current_session(user_id)

    if not current_session:
        return "⚠️ No active session. Use `/new` to create one."

    old_name = current_session.name
    success = session_manager.rename_session(user_id, current_session.opencode_session_id, new_name)

    if success:
        return f"✅ Renamed session: **{old_name}** → **{new_name}**"
    else:
        return "❌ Failed to rename session. Please try again."


async def handle_history_command(user_id: str, args: str) -> str:
    """Handle /history [count] command."""
    session_manager = get_session_manager()
    current_session = session_manager.get_current_session(user_id)

    if not current_session:
        return "⚠️ No active session. Use `/new` to create one."

    # Parse count argument (default 10)
    try:
        limit = int(args.strip()) if args.strip() else 10
        limit = min(limit, 50)  # Max 50 messages
    except ValueError:
        limit = 10

    # TODO: Implement actual history retrieval from OpenCode API
    # For now, return placeholder
    return f"📜 **Conversation History** (Session: {current_session.name})\n\n⚠️ History feature requires OpenCode API support.\nSession ID: `{current_session.opencode_session_id}`\n\nUse `/switch` to change sessions."

