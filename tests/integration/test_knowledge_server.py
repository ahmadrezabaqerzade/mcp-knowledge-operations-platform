import pytest
from fastmcp import Client

from mcp_mastery.knowledge_server.server import mcp


@pytest.mark.asyncio
async def test_search_knowledge_tool() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert any(tool.name == "search_knowledge" for tool in tools)

        result = await client.call_tool(
            "search_knowledge", {"query": "machine_learning"}
        )

        assert result.structured_content is not None
        assert len(result.structured_content) > 0
