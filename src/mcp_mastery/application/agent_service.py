from contextlib import AsyncExitStack
from pathlib import Path

from fastmcp import ClientGroup
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq

from mcp_mastery.client.loader import load_client_config
from mcp_mastery.config.factory import get_settings


class AgentService:
    def __init__(self) -> None:
        self._agent = None
        self._exit_stack: AsyncExitStack | None = None

    async def initialize(self) -> None:
        if self._agent is not None:
            raise RuntimeError("AgentService is already initialized.")

        settings = get_settings()

        llm = ChatGroq(
            model=settings.groq_model_name,
            api_key=settings.groq_api_key,
            temperature=settings.temperature,
        )

        config_path = (
            Path(__file__).resolve().parents[3] / "config" / "mcp_servers.json"
        )

        config = load_client_config(config_path).model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )

        client_group = ClientGroup.from_config(config)
        adapter = MCPAdapter(client_group)

        exit_stack = AsyncExitStack()

        try:
            await exit_stack.enter_async_context(adapter)

            tools = await adapter.list_tools()

            agent = create_agent(
                model=llm,
                tools=tools,
            )

        except BaseException:
            await exit_stack.aclose()
            raise

        self._agent = agent
        self._exit_stack = exit_stack

    async def chat(self, message: str) -> str:
        if self._agent is None:
            raise RuntimeError("AgentService is not initialized.")

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        result = await self._agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }
        )

        return result["messages"][-1].content

    async def close(self) -> None:
        if self._exit_stack is not None:
            try:
                await self._exit_stack.aclose()
            finally:
                self._exit_stack = None
                self._agent = None
