import pytest
from fastmcp import Client

from mcp_mastery.knowledge_server.server import mcp


@pytest.mark.asyncio
async def test_knowledge_resource() -> None:
    async with Client(mcp) as client:
        resources = await client.list_resources()

        assert "knowledge://overview" in [resource.uri for resource in resources]

        result = await client.read_resource("knowledge://overview")
        result = result[0].text

        assert "Available Knowledge Topics:" in result
        assert "machine_learning" in result
