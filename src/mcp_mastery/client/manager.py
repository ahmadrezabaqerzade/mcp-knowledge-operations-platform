from contextlib import AsyncExitStack

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from mcp_mastery.client.config import MCPClientConfig


class MCPConnectionManager:
    """Manage connections to multiple MCP servers."""

    def __init__(self, config: MCPClientConfig) -> None:
        self._config = config
        self._clients: dict[str, Client] = {}
        self._exit_stack: AsyncExitStack | None = None

    async def connect(self) -> None:
        """Connect to all configured MCP servers."""

        if self._exit_stack is not None:
            raise RuntimeError("MCP connections are already initialized.")

        exit_stack = AsyncExitStack()

        try:
            for name, server_config in self._config.mcp_servers.items():
                transport = StdioTransport(
                    command=server_config.command,
                    args=server_config.args,
                    env=server_config.env,
                    cwd=(
                        str(server_config.cwd)
                        if server_config.cwd is not None
                        else None
                    ),
                    keep_alive=(
                        server_config.keep_alive
                        if server_config.keep_alive is not None
                        else False
                    ),
                )

                client = Client(transport)

                await exit_stack.enter_async_context(client)

                self._clients[name] = client

            self._exit_stack = exit_stack

        except BaseException:
            self._clients.clear()
            await exit_stack.aclose()
            raise

    async def disconnect(self) -> None:
        """Disconnect from all MCP servers."""

        if self._exit_stack is None:
            return

        exit_stack = self._exit_stack
        self._exit_stack = None
        self._clients.clear()

        await exit_stack.aclose()

    def get_client(self, server_name: str) -> Client:
        """Return the connected client for a named MCP server."""

        if self._exit_stack is None:
            raise RuntimeError("MCP connections are not initialized.")

        try:
            return self._clients[server_name]
        except KeyError:
            raise KeyError(
                f"Unknown or unavailable MCP server: {server_name}"
            ) from None

    async def __aenter__(self) -> MCPConnectionManager:
        """Connect to configured MCP servers when entering the context."""

        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Disconnect from all MCP servers when leaving the context."""

        await self.disconnect()
