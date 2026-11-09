import json
from pathlib import Path

from mcp_mastery.client.config import MCPClientConfig


def load_client_config(config_path: Path) -> MCPClientConfig:
    """Load and validate MCP client configuration from a JSON file."""

    if not isinstance(config_path, Path):
        raise TypeError("config_path must be a pathlib.Path instance.")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")

    if not config_path.is_file():
        raise ValueError(f"Configuration path is not a file: {config_path}")

    try:
        config_data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Configuration file contains invalid JSON: {config_path}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Configuration file is not valid UTF-8: {config_path}"
        ) from exc

    return MCPClientConfig.model_validate(config_data)
