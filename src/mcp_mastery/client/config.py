from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MCPServerConfig(BaseModel):
    """Configuration for an individual MCP server."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    cwd: Path | None = None
    keep_alive: bool | None = None

    @field_validator("command")
    @classmethod
    def validate_command(cls, value: str) -> str:
        """Ensure the server command is not empty."""

        if not value.strip():
            raise ValueError("command must not be empty or whitespace.")

        return value

    @field_validator("args")
    @classmethod
    def validate_args(cls, value: list[str]) -> list[str]:
        """Ensure server arguments are not empty strings."""

        if any(not arg.strip() for arg in value):
            raise ValueError("args must not contain empty strings.")

        return value


class MCPClientConfig(BaseModel):
    """Configuration for the MCP client and its servers."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        populate_by_name=True,
    )

    mcp_servers: dict[str, MCPServerConfig] = Field(
        alias="mcpServers",
        min_length=1,
    )

    @field_validator("mcp_servers")
    @classmethod
    def validate_mcp_server_names(
        cls,
        value: dict[str, MCPServerConfig],
    ) -> dict[str, MCPServerConfig]:
        """Ensure MCP server names are not empty."""

        if any(not name.strip() for name in value):
            raise ValueError("MCP server names must not be empty or whitespace.")

        return value
