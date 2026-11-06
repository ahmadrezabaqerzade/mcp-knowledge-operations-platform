from fastmcp import Client

from mcp_mastery.knowledge_server.server import mcp


async def test_knowledge_prompt() -> None:
    async with Client(mcp) as client:
        prompts = await client.list_prompts()

        assert "research_topic" in [p.name for p in prompts]

        result = await client.get_prompt(
            name="research_topic",
            arguments={
                "topic": "Machine Learning",
                "level": "Advanced",
                "focus": "Model Evaluation",
            },
        )

        assert result.messages

        message = result.messages[0].content.text

        assert "Machine Learning" in message
        assert "Advanced" in message
        assert "Model Evaluation" in message
