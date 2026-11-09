import pytest
from pydantic import ValidationError

from mcp_mastery.client.config import MCPClientConfig, MCPServerConfig


class TestMCPServerConfig:
    """Tests for MCP server configuration."""

    def test_valid_server_config(self) -> None:
        config = MCPServerConfig(
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
        config = MCPServerConfig(command="uv")

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
            MCPServerConfig(command=command)

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
            MCPServerConfig.model_validate(
                {
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
            MCPServerConfig.model_validate(
                {
                    "command": "uv",
                    "env": env,
                }
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            MCPServerConfig.model_validate(
                {
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
                        "command": "uv",
                        "args": ["run", "python"],
                    }
                }
            }
        )

        assert len(config.mcp_servers) == 1
        assert config.mcp_servers["knowledge"].command == "uv"

    def test_valid_multiple_servers(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcpServers": {
                    "knowledge": {"command": "uv"},
                    "operations": {"command": "python"},
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
                        server_name: {"command": "uv"},
                    }
                }
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            MCPClientConfig.model_validate(
                {
                    "mcpServers": {
                        "knowledge": {"command": "uv"},
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
                    "knowledge": {"command": "uv"},
                }
            }
        )

        assert "knowledge" in config.mcp_servers

    def test_accepts_python_field_name(self) -> None:
        config = MCPClientConfig.model_validate(
            {
                "mcp_servers": {
                    "knowledge": {"command": "uv"},
                }
            }
        )

        assert "knowledge" in config.mcp_servers

    def test_dumps_using_json_alias(self) -> None:
        config = MCPClientConfig(
            mcp_servers={
                "knowledge": MCPServerConfig(command="uv"),
            }
        )

        result = config.model_dump(by_alias=True)

        assert "mcpServers" in result
        assert "mcp_servers" not in result


class TestMCPServerConfigDefaults:
    """Tests for default value isolation."""

    def test_default_args_are_independent_between_instances(self) -> None:
        first = MCPServerConfig(command="uv")
        second = MCPServerConfig(command="python")

        first.args.append("run")

        assert first.args == ["run"]
        assert second.args == []
