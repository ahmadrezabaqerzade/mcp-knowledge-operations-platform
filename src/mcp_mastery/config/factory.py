from functools import lru_cache

from mcp_mastery.config.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()
