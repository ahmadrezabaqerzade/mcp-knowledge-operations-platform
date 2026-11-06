import pytest
from fastmcp import Client

from mcp_mastery.operations_server.server import mcp


@pytest.mark.asyncio
async def test_data_processing_tool() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert "analyze_numbers" in [tool.name for tool in tools]

        result = await client.call_tool(
            name="analyze_numbers", arguments={"numbers": [1, 2, 3, 4, 5]}
        )

        assert not result.is_error

        content = result.structured_content
        assert content["count"] == 5
        assert content["sum"] == 15.0
        assert content["mean"] == 3.0
        assert content["min"] == 1.0
        assert content["max"] == 5.0
        assert content["median"] == 3.0
        assert content["variance"] == 2.0
        assert content["standard_deviation"] == pytest.approx(1.41421356237)
