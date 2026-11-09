from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_mastery.client.config import MCPClientConfig, MCPServerConfig
from mcp_mastery.client.manager import MCPConnectionManager


class FakeClient:
    """A fake asynchronous MCP client for unit testing."""

    def __init__(self, *, fail_on_connect: bool = False) -> None:
        self.enter = AsyncMock()
        self.exit = AsyncMock(return_value=False)

        if fail_on_connect:
            self.enter.side_effect = RuntimeError("Connection failed.")
        else:
            self.enter.return_value = self

    async def __aenter__(self) -> FakeClient:
        return await self.enter()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        return await self.exit(exc_type, exc_val, exc_tb)


def create_config() -> MCPClientConfig:
    """Create a configuration with two MCP servers."""

    return MCPClientConfig(
        mcp_servers={
            "knowledge": MCPServerConfig(
                command="uv",
                args=["run", "python", "-m", "knowledge.server"],
            ),
            "operations": MCPServerConfig(
                command="uv",
                args=["run", "python", "-m", "operations.server"],
            ),
        }
    )


class TestMCPConnectionManager:
    """Tests for MCP connection lifecycle management."""

    @pytest.mark.asyncio
    async def test_connects_to_all_configured_servers(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        clients = [FakeClient(), FakeClient()]
        client_factory = MagicMock(side_effect=clients)
        transport_factory = MagicMock(side_effect=lambda **kwargs: kwargs)

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            client_factory,
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            transport_factory,
        )

        manager = MCPConnectionManager(create_config())

        await manager.connect()

        assert manager.get_client("knowledge") is clients[0]
        assert manager.get_client("operations") is clients[1]

        assert client_factory.call_count == 2
        assert transport_factory.call_count == 2

        for client in clients:
            client.enter.assert_awaited_once()

        await manager.disconnect()

    @pytest.mark.asyncio
    async def test_connect_rejects_repeated_connection(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        clients = [FakeClient(), FakeClient()]

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(side_effect=clients),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            MagicMock(),
        )

        manager = MCPConnectionManager(create_config())

        await manager.connect()

        with pytest.raises(RuntimeError, match="already initialized"):
            await manager.connect()

        await manager.disconnect()

    @pytest.mark.asyncio
    async def test_failed_connection_closes_previous_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        first_client = FakeClient()
        second_client = FakeClient(fail_on_connect=True)

        clients = [first_client, second_client]

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(side_effect=clients),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            MagicMock(),
        )

        manager = MCPConnectionManager(create_config())

        with pytest.raises(RuntimeError, match="Connection failed"):
            await manager.connect()

        first_client.exit.assert_awaited_once()
        second_client.exit.assert_not_awaited()

        with pytest.raises(RuntimeError, match="not initialized"):
            manager.get_client("knowledge")

    @pytest.mark.asyncio
    async def test_disconnect_without_connection(
        self,
    ) -> None:
        manager = MCPConnectionManager(create_config())

        await manager.disconnect()

        assert manager._exit_stack is None
        assert manager._clients == {}

    @pytest.mark.asyncio
    async def test_disconnect_can_be_called_multiple_times(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        client = FakeClient()

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(return_value=client),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            MagicMock(),
        )

        config = MCPClientConfig(
            mcp_servers={
                "knowledge": MCPServerConfig(command="uv"),
            }
        )

        manager = MCPConnectionManager(config)

        await manager.connect()
        await manager.disconnect()
        await manager.disconnect()

        client.exit.assert_awaited_once()
        assert manager._exit_stack is None
        assert manager._clients == {}

    @pytest.mark.asyncio
    async def test_get_client_rejects_unknown_server(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        client = FakeClient()

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(return_value=client),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            MagicMock(),
        )

        config = MCPClientConfig(
            mcp_servers={
                "knowledge": MCPServerConfig(command="uv"),
            }
        )

        manager = MCPConnectionManager(config)

        await manager.connect()

        with pytest.raises(KeyError, match="Unknown or unavailable"):
            manager.get_client("unknown")

        await manager.disconnect()

    def test_get_client_rejects_access_before_connection(
        self,
    ) -> None:
        manager = MCPConnectionManager(create_config())

        with pytest.raises(RuntimeError, match="not initialized"):
            manager.get_client("knowledge")

    @pytest.mark.asyncio
    async def test_async_context_manager(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        clients = [FakeClient(), FakeClient()]

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(side_effect=clients),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            MagicMock(),
        )

        manager = MCPConnectionManager(create_config())

        async with manager as connected_manager:
            assert connected_manager is manager
            assert connected_manager.get_client("knowledge") is clients[0]
            assert connected_manager.get_client("operations") is clients[1]

        for client in clients:
            client.exit.assert_awaited_once()

        assert manager._exit_stack is None
        assert manager._clients == {}

    @pytest.mark.asyncio
    async def test_transport_receives_configured_arguments(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        client = FakeClient()
        transport_factory = MagicMock(return_value=object())

        monkeypatch.setattr(
            "mcp_mastery.client.manager.Client",
            MagicMock(return_value=client),
        )
        monkeypatch.setattr(
            "mcp_mastery.client.manager.StdioTransport",
            transport_factory,
        )

        config = MCPClientConfig(
            mcp_servers={
                "knowledge": MCPServerConfig(
                    command="uv",
                    args=["run", "python"],
                    env={"APP_ENV": "test"},
                    cwd=tmp_path,
                    keep_alive=True,
                ),
            }
        )

        manager = MCPConnectionManager(config)

        await manager.connect()

        transport_factory.assert_called_once_with(
            command="uv",
            args=["run", "python"],
            env={"APP_ENV": "test"},
            cwd=str(tmp_path),
            keep_alive=True,
        )

        await manager.disconnect()
