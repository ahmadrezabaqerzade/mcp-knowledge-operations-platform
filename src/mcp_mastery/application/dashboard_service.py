from pathlib import Path

from mcp.types import Prompt, Resource, ResourceTemplate, Tool

from mcp_mastery.application.schemas import ServerDetails
from mcp_mastery.client.config import (
    HttpServerConfig,
    MCPClientConfig,
    StdioServerConfig,
)
from mcp_mastery.client.loader import load_client_config
from mcp_mastery.client.manager import MCPConnectionManager


class DashboardService:
    """Provide MCP server discovery and operations for the dashboard."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path
        self._config: MCPClientConfig | None = None
        self._manager: MCPConnectionManager | None = None

    def list_servers(self) -> list[str]:
        """List configured MCP server names."""
        if self._config is None:
            raise RuntimeError("DashboardService is not initialized.")

        return list(self._config.mcp_servers)

    def get_server_details(self, server_name: str) -> ServerDetails:
        """Return details and connection status for a configured MCP server."""
        if self._config is None or self._manager is None:
            raise RuntimeError("DashboardService is not initialized.")

        try:
            server_config = self._config.mcp_servers[server_name]
        except KeyError:
            raise KeyError(f"Unknown MCP server: {server_name}") from None

        if isinstance(server_config, StdioServerConfig):
            transport = "stdio"

        elif isinstance(server_config, HttpServerConfig):
            transport = "http"

        else:
            raise TypeError(
                f"Unsupported server config: {type(server_config).__name__}"
            )

        client = self._manager.get_client(server_name)
        return ServerDetails(
            name=server_name,
            transport=transport,
            connected=client.is_connected(),
        )

    async def initialize(self) -> None:
        """Load configuration and connect to MCP servers."""
        if self._config is not None:
            raise RuntimeError("DashboardService is already initialized.")

        if self._config_path is None:
            self._config_path = (
                Path(__file__).parents[3].resolve() / "config" / "mcp_servers.json"
            )

        config = load_client_config(self._config_path)
        manager = MCPConnectionManager(config)
        await manager.connect()

        self._config = config
        self._manager = manager

    async def list_tools(self, server_name: str) -> list[Tool]:
        """List tools exposed by a connected MCP server."""
        if self._manager is None:
            raise RuntimeError("DashboardService is not initialized.")

        client = self._manager.get_client(server_name)
        return await client.list_tools()

    async def list_resources(self, server_name: str) -> list[Resource]:
        """List resources exposed by a connected MCP server."""
        if self._manager is None:
            raise RuntimeError("DashboardService is not initialized.")

        client = self._manager.get_client(server_name)
        return await client.list_resources()

    async def list_resource_templates(self, server_name: str) -> list[ResourceTemplate]:
        """List resource templates exposed by a connected MCP server."""
        if self._manager is None:
            raise RuntimeError("DashboardService is not initialized.")

        client = self._manager.get_client(server_name)
        return await client.list_resource_templates()

    async def list_prompts(self, server_name: str) -> list[Prompt]:
        """List prompts exposed by a connected MCP server."""
        if self._manager is None:
            raise RuntimeError("DashboardService is not initialized.")

        client = self._manager.get_client(server_name)
        return await client.list_prompts()

    async def close(self) -> None:
        """Disconnect from all MCP servers."""
        if self._manager is None:
            return

        manager = self._manager

        try:
            await manager.disconnect()
        finally:
            self._manager = None
            self._config = None
