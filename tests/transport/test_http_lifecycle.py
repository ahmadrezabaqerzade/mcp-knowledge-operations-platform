import asyncio
import socket
from collections.abc import AsyncIterator
from contextlib import suppress

import httpx2
import pytest
import uvicorn
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from servers.http_server import mcp


@pytest.fixture
async def http_server_url() -> AsyncIterator[str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen()
    sock.setblocking(False)

    port = sock.getsockname()[1]

    server = uvicorn.Server(
        uvicorn.Config(
            mcp.http_app(path="/mcp"),
            log_level="error",
        )
    )

    server_task = asyncio.create_task(server.serve(sockets=[sock]))

    try:
        async with asyncio.timeout(10):
            while not server.started:
                if server_task.done():
                    await server_task
                await asyncio.sleep(0.01)

        yield f"http://127.0.0.1:{port}/mcp"

    finally:
        server.should_exit = True

        try:
            await asyncio.wait_for(server_task, timeout=5)
        except TimeoutError:
            server_task.cancel()
            with suppress(asyncio.CancelledError):
                await server_task
        finally:
            sock.close()


@pytest.mark.asyncio
async def test_http_healthy(http_server_url: str) -> None:
    transport = StreamableHttpTransport(url=http_server_url)

    async with Client(transport) as client:
        tools = await client.list_tools()

        assert "ping" in [tool.name for tool in tools]

        result = await client.call_tool("ping")

        assert not result.is_error
        assert result.structured_content["result"] == "HTTP server is alive"

    assert not client.is_connected()


@pytest.mark.asyncio
async def test_http_server_unavailable() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    http_clients: list[httpx2.AsyncClient] = []

    def http_client_factory(**kwargs: object) -> httpx2.AsyncClient:
        http_client = httpx2.AsyncClient(**kwargs)
        http_clients.append(http_client)
        return http_client

    transport = StreamableHttpTransport(
        url=f"http://127.0.0.1:{port}/mcp",
        httpx_client_factory=http_client_factory,
    )
    client = Client(transport)

    with pytest.raises(RuntimeError, match="Client failed to connect:"):
        async with client:
            pytest.fail("Client context should not be entered")

    assert not client.is_connected()
    assert len(http_clients) == 1
    assert http_clients[0].is_closed
