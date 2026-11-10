from pathlib import Path

from mcp_mastery.client.loader import load_client_config
from mcp_mastery.client.manager import MCPConnectionManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "mcp_servers.json"


async def test_client_manager_connects_to_both_servers() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        knowledge_client = manager.get_client("knowledge")
        operations_client = manager.get_client("operations")

        assert knowledge_client.is_connected()
        assert operations_client.is_connected()


async def test_client_manager_discovers_tools() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        knowledge_tools = await manager.get_client("knowledge").list_tools()
        operations_tools = await manager.get_client("operations").list_tools()

        knowledge_tool_names = {tool.name for tool in knowledge_tools}
        operations_tool_names = {tool.name for tool in operations_tools}

        assert "search_knowledge" in knowledge_tool_names

        assert {
            "calculate",
            "analyze_numbers",
            "validate_data",
            "list_files",
            "read_file",
            "write_file",
            "get_file_info",
        }.issubset(operations_tool_names)


async def test_client_manager_calls_knowledge_tool() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        client = manager.get_client("knowledge")

        result = await client.call_tool(
            "search_knowledge",
            {"query": "python"},
        )

        assert not result.is_error
        assert len(result.content) > 0

        text_content = result.content[0].text

        assert "python.md" in text_content


async def test_client_manager_calls_operations_tool() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        client = manager.get_client("operations")

        result = await client.call_tool(
            "calculate",
            {"expression": "10 + 20"},
        )

        assert not result.is_error
        assert result.structured_content is not None
        assert result.structured_content["result"] == 30


async def test_client_manager_reads_knowledge_overview() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        client = manager.get_client("knowledge")

        result = await client.read_resource("knowledge://overview")

        assert len(result) == 1
        assert "python" in result[0].text
        assert "machine_learning" in result[0].text
        assert "mcp" in result[0].text


async def test_client_manager_reads_knowledge_resource_template() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        client = manager.get_client("knowledge")

        result = await client.read_resource("knowledge://topics/python")

        assert len(result) == 1
        assert "python" in result[0].text.casefold()


async def test_client_manager_gets_research_prompt() -> None:
    config = load_client_config(CONFIG_PATH)

    async with MCPConnectionManager(config) as manager:
        client = manager.get_client("knowledge")

        result = await client.get_prompt(
            "research_topic",
            {
                "topic": "Transformer Architecture",
                "level": "Advanced",
                "focus": "Self-Attention",
            },
        )

        assert len(result.messages) == 1

        prompt_text = result.messages[0].content.text

        assert "Transformer Architecture" in prompt_text
        assert "Advanced" in prompt_text
        assert "Self-Attention" in prompt_text
