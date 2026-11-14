import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import MCPError

SERVER_PATH = Path(__file__).parent / "servers" / "crash_server.py"
STARTUP_FAILURE_SERVER_PATH = (
    Path(__file__).parent / "servers" / "startup_failure_server.py"
)


@pytest.mark.asyncio
async def test_healthy() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )
    async with Client(transport) as client:
        tools = await client.list_tools()

        assert "ping" in [tool.name for tool in tools]

        result = await client.call_tool("ping")

        assert not result.is_error

        assert result.structured_content["result"] == "Server is alive"


@pytest.mark.asyncio
async def test_crash() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )
    async with Client(transport) as client:
        tools = await client.list_tools()

        assert "crash_server" in [tool.name for tool in tools]

        with pytest.raises(MCPError, match="Connection closed"):
            await client.call_tool("crash_server")

    assert not client.is_connected()


@pytest.mark.asyncio
async def test_startup_failure() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=[str(STARTUP_FAILURE_SERVER_PATH)],
    )
    client = Client(transport)

    with pytest.raises(MCPError, match="Connection closed"):
        async with client:
            pytest.fail("Client context should not be entered")

    assert not client.is_connected()
