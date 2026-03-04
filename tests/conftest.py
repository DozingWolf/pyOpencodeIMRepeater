"""Pytest configuration and fixtures."""

import os
import tempfile
import pytest
from pathlib import Path
from src.config import reset_settings
from src.storage.database import get_db_path


@pytest.fixture(autouse=True)
def reset_settings_before_each_test():
    """Reset settings singleton before each test."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing.

    This fixture sets the DATABASE_PATH environment variable
    to a temporary directory and yields the path.
    """
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_PATH"] = str(db_path)
    yield db_path
    # Cleanup
    if "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]
