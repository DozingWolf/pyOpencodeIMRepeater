"""Tests for configuration management."""

import os
import pytest
from src.config import get_settings, Settings, reset_settings


@pytest.fixture(autouse=True)
def reset_settings_before_each_test():
    """Reset settings singleton before each test."""
    reset_settings()
    yield
    reset_settings()


def test_settings_default():
    """Test default settings values."""
    settings = get_settings()
    assert settings.opencode_api_url == "http://localhost:4096"
    assert settings.server_port == 8080
    assert settings.server_host == "0.0.0.0"
    assert settings.database_path == "data/sessions.db"


def test_settings_singleton():
    """Test that get_settings returns a singleton."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_from_environment():
    """Test that settings can be loaded from environment variables."""
    os.environ["OPENCODE_API_URL"] = "http://custom:9999"
    os.environ["SERVER_PORT"] = "3000"

    reset_settings()
    settings = get_settings()

    assert settings.opencode_api_url == "http://custom:9999"
    assert settings.server_port == 3000

    # Cleanup
    del os.environ["OPENCODE_API_URL"]
    del os.environ["SERVER_PORT"]


def test_settings_reset():
    """Test that reset_settings clears the singleton."""
    s1 = get_settings()
    reset_settings()
    s2 = get_settings()
    assert s1 is not s2


def test_settings_from_yaml(tmp_path):
    """Test that settings can be loaded from YAML file."""
    # Create a temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    
    # Write YAML config
    config_file.write_text("""opencode_api_url: http://yaml:8888
server_port: 5000
""")
    
    # Change to temp directory to test YAML loading
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        reset_settings()
        settings = get_settings()
        assert settings.opencode_api_url == "http://yaml:8888"
        assert settings.server_port == 5000
    finally:
        os.chdir(old_cwd)
