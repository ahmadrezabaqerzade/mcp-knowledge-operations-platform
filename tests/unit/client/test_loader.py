import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mcp_mastery.client.config import MCPClientConfig
from mcp_mastery.client.loader import load_client_config


class TestLoadClientConfig:
    """Tests for loading MCP client configuration."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "mcp_servers.json"

        config_data = {
            "mcpServers": {
                "knowledge": {
                    "command": "uv",
                    "args": [
                        "run",
                        "python",
                        "-m",
                        "mcp_mastery.knowledge_server.server",
                    ],
                },
                "operations": {
                    "command": "uv",
                    "args": [
                        "run",
                        "python",
                        "-m",
                        "mcp_mastery.operations_server.server",
                    ],
                },
            }
        }

        config_path.write_text(
            json.dumps(config_data),
            encoding="utf-8",
        )

        config = load_client_config(config_path)

        assert isinstance(config, MCPClientConfig)
        assert set(config.mcp_servers) == {"knowledge", "operations"}
        assert config.mcp_servers["knowledge"].command == "uv"
        assert config.mcp_servers["operations"].command == "uv"

    def test_file_not_found(self, tmp_path: Path) -> None:
        config_path = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError):
            load_client_config(config_path)

    def test_path_is_directory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            load_client_config(tmp_path)

    def test_invalid_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / "invalid.json"
        config_path.write_text(
            '{"mcpServers": invalid}',
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="invalid JSON"):
            load_client_config(config_path)

    def test_invalid_utf8(self, tmp_path: Path) -> None:
        config_path = tmp_path / "invalid_encoding.json"
        config_path.write_bytes(b"\xff\xfe\xfa")

        with pytest.raises(ValueError, match="valid UTF-8"):
            load_client_config(config_path)

    def test_invalid_config_structure(self, tmp_path: Path) -> None:
        config_path = tmp_path / "invalid_config.json"
        config_path.write_text(
            json.dumps({"mcpServers": {}}),
            encoding="utf-8",
        )

        with pytest.raises(ValidationError):
            load_client_config(config_path)

    @pytest.mark.parametrize(
        "config_path",
        [
            pytest.param("config.json", id="string_path"),
            pytest.param(None, id="none_path"),
            pytest.param(123, id="integer_path"),
        ],
    )
    def test_invalid_path_type(self, config_path: object) -> None:
        with pytest.raises(TypeError, match="pathlib.Path"):
            load_client_config(config_path)  # type: ignore[arg-type]
