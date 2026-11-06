import pytest
from fastmcp import Client

from mcp_mastery.operations_server.server import mcp


@pytest.mark.asyncio
async def test_calculation_tool() -> None:
    async with Client(mcp) as client:
        results = await client.list_tools()

        assert "calculate" in [r.name for r in results]

        result = await client.call_tool(
            name="calculate", arguments={"expression": "10 + 20"}
        )

        assert not result.is_error

        assert result.structured_content["result"] == 30
