import pytest
from fastmcp import Client

from mcp_mastery.operations_server.server import mcp


@pytest.mark.asyncio
async def test_validate_data_tool_with_valid_input() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert "validate_data" in [tool.name for tool in tools]

        schema_name = "user_profile"
        data = {"username": "ahmadreza", "age": 26, "is_active": True}
        result = await client.call_tool(
            name="validate_data", arguments={"schema_name": schema_name, "data": data}
        )
        content = result.structured_content

        assert not result.is_error
        assert content["valid"] is True
        assert content["data"] == data
        assert not content["errors"]


@pytest.mark.asyncio
async def test_validate_data_tool_with_invalid_input() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert "validate_data" in [tool.name for tool in tools]

        schema_name = "user_profile"
        data = {"username": "ab", "age": 15, "is_active": True}
        result = await client.call_tool(
            name="validate_data", arguments={"schema_name": schema_name, "data": data}
        )
        content = result.structured_content

        assert not result.is_error
        assert content["valid"] is False
        assert content["data"] is None
        assert len(content["errors"]) == 2
        assert {error["field"] for error in content["errors"]} == {
            "username",
            "age",
        }


@pytest.mark.asyncio
async def test_validate_data_tool_with_unknown_schema() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert "validate_data" in [tool.name for tool in tools]

        schema_name = "unknown_schema"
        data = {"username": "ahmadreza", "age": 26, "is_active": True}
        result = await client.call_tool(
            name="validate_data", arguments={"schema_name": schema_name, "data": data}
        )
        content = result.structured_content

        assert not result.is_error
        assert content["valid"] is False
        assert content["data"] is None
        assert len(content["errors"]) == 1
        assert {error["field"] for error in content["errors"]} == {
            "schema_name",
        }
        assert content["errors"][0]["type"] == "unknown_schema"
        assert content["errors"][0]["message"] == "Unknown schema: unknown_schema"
