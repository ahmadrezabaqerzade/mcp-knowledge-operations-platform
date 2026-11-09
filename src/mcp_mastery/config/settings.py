from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mcp_workspace: Path

    @field_validator("mcp_workspace")
    @classmethod
    def validate_workspace(cls, value: Path) -> Path:
        """Ensure the workspace exists and is a directory."""

        path = value.expanduser().resolve()

        if not path.exists():
            raise ValueError("The configured workspace does not exist.")

        if not path.is_dir():
            raise ValueError("The configured workspace is not a directory.")

        return path
