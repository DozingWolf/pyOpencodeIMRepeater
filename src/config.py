"""Configuration management for OpenCode IM Repeater."""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from typing import Tuple, Type


class YamlConfigSource(PydanticBaseSettingsSource):
    """Custom source for YAML configuration."""

    def __init__(self, settings_cls: Type[BaseSettings], yaml_config: dict):
        super().__init__(settings_cls)
        self.yaml_config = yaml_config

    def get_field_value(self, field, field_name):
        if field_name in self.yaml_config:
            return self.yaml_config[field_name], field_name, False
        return None, None, False

    def __call__(self) -> dict:
        return self.yaml_config


class Settings(BaseSettings):
    """Application settings with YAML and environment variable support."""

    # OpenCode settings
    opencode_api_url: str = Field(
        default="http://localhost:4096", description="OpenCode API endpoint"
    )
    opencode_password: str = Field(default="", description="OpenCode authentication password")

    # Feishu settings
    feishu_app_id: str = Field(default="", description="Feishu application ID")
    feishu_app_secret: str = Field(default="", description="Feishu application secret")
    feishu_encrypt_key: str = Field(default="", description="Feishu message encryption key")
    feishu_verification_token: str = Field(default="", description="Feishu verification token")

    # Server settings
    server_host: str = Field(default="0.0.0.0", description="Server bind host")
    server_port: int = Field(default=8080, description="Server bind port")

    # Database settings
    database_path: str = Field(default="data/sessions.db", description="SQLite database path")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customize configuration sources priority.

        Priority order (highest to lowest):
        1. Environment variables
        2. .env file
        3. YAML config file
        4. Default values
        """
        yaml_config = load_yaml_config()
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSource(settings_cls, yaml_config),
            init_settings,
        )


def load_yaml_config() -> dict:
    """Load configuration from YAML file.

    Returns:
        Dictionary with configuration values, empty dict if file not found.
    """
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton).

    Loads configuration with environment variables overriding YAML config.

    Returns:
        Settings instance with merged configuration.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset settings singleton (useful for testing)."""
    global _settings
    _settings = None
