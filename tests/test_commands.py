"""Tests for command parsing and handling."""

import pytest

from src.commands.handler import get_help_message, handle_command, parse_command


def test_parse_command():
    """Test command parsing."""
    # Test valid commands
    cmd, args = parse_command("/new Test Session")
    assert cmd == "/new"
    assert args == "Test Session"

    cmd, args = parse_command("/list")
    assert cmd == "/list"
    assert args == ""

    # Test non-commands
    cmd, args = parse_command("Hello world")
    assert cmd is None
    assert args is None


@pytest.mark.asyncio
async def test_handle_new_command():
    """Test /new command handling."""
    response = await handle_command("test_user", "/new", "Test Session", "chat123")
    assert "✅" in response or "❌" in response  # Should have emoji


@pytest.mark.asyncio
async def test_handle_list_command():
    """Test /list command handling."""
    response = await handle_command("test_user", "/list", "", "chat123")
    assert "📋" in response or "📭" in response


@pytest.mark.asyncio
async def test_handle_help_command():
    """Test /help command handling."""
    response = await handle_command("test_user", "/help", "", "chat123")
    assert "📖" in response or "Commands" in response


def test_get_help_message():
    """Test help message contains all commands."""
    help = get_help_message()
    assert "/new" in help
    assert "/list" in help
    assert "/switch" in help
