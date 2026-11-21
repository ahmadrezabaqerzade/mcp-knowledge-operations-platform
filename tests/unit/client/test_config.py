import pytest
from pydantic import ValidationError

from mcp_mastery.client.config import (
    HttpServerConfig,
    MCPClientConfig,
    StdioServerConfig,
)


class TestMCPServerConfig:
    """Tests for MCP server configuration."""

    def test_valid_server_config(self) -> None:
        config = StdioServerConfig(
            transport="stdio",
            command="uv",
            args=["run", "python", "-m", "mcp_mastery.server"],
            env={"APP_ENV": "test"},
            cwd=None,
            keep_alive=True,
        )

        assert config.command == "uv"
        assert config.args == [
            "run",
            "python",
            "-m",
            "mcp_mastery.server",
        ]
        assert config.env == {"APP_ENV": "test"}
        assert config.cwd is None
        assert config.keep_alive is True

    def test_default_values(self) -> None:
        config = StdioServerConfig(transport="stdio", command="uv")

        assert config.args == []
        assert config.env is None
        assert config.cwd is None
        assert config.keep_alive is None

    @pytest.mark.parametrize(
        "command",
        [
            pytest.param("", id="empty_command"),
            pytest.param("   ", id="whitespace_command"),
        ],
    )
    def test_invalid_command(self, command: str) -> None:
        with pytest.raises(ValidationError):
            StdioServerConfig(transport="stdio", command=command)

    @pytest.mark.parametrize(
        "args",
        [
            pytest.param(["run", ""], id="empty_argument"),
            pytest.param(["run", "   "], id="whitespace_argument"),
            pytest.param(["run", 123], id="non_string_argument"),
            pytest.param("run python", id="string_instead_of_list"),
        ],
    )
    def test_invalid_args(self, args: list[str] | str) -> None:
        with pytest.raises(ValidationError):
            StdioServerConfig.model_validate(
                {
                    "transport": "stdio",
                    "command": "uv",
                    "args": args,
                }
            )

    @pytest.mark.parametrize(
        "env",
        [
            pytest.param({"APP_ENV": 123}, id="non_string_value"),
            pytest.param({"APP_ENV": True}, id="boolean_value"),
            pytest.param("APP_ENV=test", id="string_instead_of_dict"),
        ],
    )
    def test_invalid_env(self, env: dict[str, str] | str) -> None:
        with pytest.raises(ValidationError):
            StdioServerConfig.model_validate(
                {
                    "transport": "stdio",
                    "command": "uv",
                    "env": env,
                }
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            StdioServerConfig.model_validate(
                {
                    "transport": "stdio",
                    "command": "uv",
                    "unknown": "value",
                }
            )


class TestMCPClientConfig:
    """Tests for MCP client configuration."""

    def test_valid_single_server(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {
                        "transport": "stdio",
                        "command": "uv",
                        "args": ["run", "python"],
                    }
                }
            }
        )

        assert len(config.mcp_servers) == 1
        assert config.mcp_servers["knowledge"].command == "uv"

    def test_valid_http_server(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {
                        "transport": "http",
                        "url": "http://127.0.0.1:8001/mcp",
                    }
                }
            }
        )

        server = config.mcp_servers["knowledge"]

        assert isinstance(server, HttpServerConfig)
        assert str(server.url) == "http://127.0.0.1:8001/mcp"

    def test_valid_mixed_transports(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {
                        "transport": "http",
                        "url": "http://127.0.0.1:8001/mcp",
                    },
                    "operations": {
                        "transport": "stdio",
                        "command": "uv",
                        "args": ["run", "python"],
                    },
                }
            }
        )

        assert isinstance(config.mcp_servers["knowledge"], HttpServerConfig)
        assert isinstance(config.mcp_servers["operations"], StdioServerConfig)

    def test_valid_multiple_servers(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {"transport": "stdio", "command": "uv"},
                    "operations": {"transport": "stdio", "command": "python"},
                }
            }
        )

        assert set(config.mcp_servers) == {"knowledge", "operations"}

    def test_rejects_empty_server_mapping(self) -> None:
        with pytest.raises(ValidationError):
            MCPClientConfig.model_validate({"mcpServers": {}})

    @pytest.mark.parametrize(
        "server_name",
        [
            pytest.param("", id="empty_name"),
            pytest.param("   ", id="whitespace_name"),
        ],
    )
    def test_rejects_invalid_server_name(self, server_name: str) -> None:
        with pytest.raises(ValidationError):
            MCPClientConfig.model_validate(
                {
                    "mcpServers": {
                        server_name: {"transport": "stdio", "command": "uv"},
                    }
                }
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            MCPClientConfig.model_validate(
                {
                    "mcpServers": {
                        "knowledge": {"transport": "stdio", "command": "uv"},
                    },
                    "unknown": "value",
                }
            )


class TestMCPClientConfigAliases:
    """Tests for configuration aliases."""

    def test_accepts_json_alias(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {"transport": "stdio", "command": "uv"},
                }
            }
        )

        assert "knowledge" in config.mcp_servers

    def test_accepts_python_field_name(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcp_servers": {
                    "knowledge": {"transport": "stdio", "command": "uv"},
                }
            }
        )

        assert "knowledge" in config.mcp_servers

    def test_dumps_using_json_alias(self) -> None:
        config = MCPClientConfig(
            mcp_servers={
                "knowledge": StdioServerConfig(transport="stdio", command="uv"),
            }
        )

        result = config.model_dump(by_alias=True)

        assert "mcpServers" in result
        assert "mcp_servers" not in result


class TestMCPServerConfigDefaults:
    """Tests for default value isolation."""

    def test_default_args_are_independent_between_instances(self) -> None:
        first = StdioServerConfig(transport="stdio", command="uv")
        second = StdioServerConfig(transport="stdio", command="python")

        first.args.append("run")

        assert first.args == ["run"]
        assert second.args == []
