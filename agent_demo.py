import asyncio
from pathlib import Path

from fastmcp import ClientGroup
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import AIMessage, ToolMessage
from langchain_groq import ChatGroq
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

from mcp_mastery.client.loader import load_client_config


class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_model_name: str = "openai/gpt-oss-120b"
    groq_api_key: SecretStr
    temperature: float = 0.0


async def main() -> None:
    console = Console()

    server_style = Style(color="green", bold=True)
    tool_style = Style(color="cyan", bold=True)

    llm_config = ModelConfig()

    llm = ChatGroq(
        model=llm_config.groq_model_name,
        api_key=llm_config.groq_api_key,
        temperature=llm_config.temperature,
    )

    config_path = Path(__file__).resolve().parent / "config" / "mcp_servers.json"

    config = load_client_config(config_path).model_dump(
        mode="json",
        by_alias=True,
        exclude_none=True,
    )

    client_group = ClientGroup.from_config(config)
    adapter = MCPAdapter(client_group)

    async with adapter:
        tools = await adapter.list_tools()

        console.print("\n[bold]Discovered MCP Tools[/bold]")

        for tool in sorted(tools, key=lambda item: item.name):
            server_name, _, tool_name = tool.name.partition("_")
            console.print(
                f"{server_name}: {tool_name}",
                style=server_style,
            )

        agent = create_agent(
            model=llm,
            tools=tools,
        )

        console.print(
            Panel(
                "Agent initialized successfully.",
                title="LangChain Agent",
                border_style="green",
            )
        )

        user_message = (
            "Briefly explain what Python is. "
            "Use the Knowledge Server's search_knowledge tool "
            "to search for Python. "
            "Then use the Operations Server's calculate tool "
            "to calculate 8 * 125. "
            "You must call both tools. "
            "Keep the final answer very short."
        )

        console.print(Panel(user_message, title="User Request", border_style="blue"))

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]
            }
        )

        console.print("\n[bold]Execution Trace[/bold]")

        for message in result["messages"]:
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    console.print(
                        f"Tool call: {tool_call['name']}",
                        style=tool_style,
                    )

            elif isinstance(message, ToolMessage):
                console.print(
                    Panel(
                        str(message.content),
                        title=f"Tool Result: {message.name}",
                        border_style="cyan",
                    )
                )

        final_message = result["messages"][-1]

        console.print(
            Panel(
                str(final_message.content),
                title="Agent Final Answer",
                border_style="green",
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
