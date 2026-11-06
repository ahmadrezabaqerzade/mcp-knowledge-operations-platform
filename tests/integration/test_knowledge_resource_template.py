import pytest
from fastmcp import Client

from mcp_mastery.knowledge_server.server import mcp


@pytest.mark.asyncio
async def test_knowledge_resource_template() -> None:
    async with Client(mcp) as client:
        resource_templates = await client.list_resource_templates()

        assert "knowledge://topics/{topic}" in [
            r.uri_template for r in resource_templates
        ]

        result = await client.read_resource("knowledge://topics/python")
        content = result[0].text

        assert content.strip()
        assert "Python" in content
