from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

import mcp_mastery.application.agent_service as agent_service_module
from mcp_mastery.application.agent_service import AgentService


@pytest.mark.asyncio
async def test_chat_before_initialization_raises_error() -> None:
    service = AgentService()

    with pytest.raises(
        RuntimeError,
        match="AgentService is not initialized.",
    ):
        await service.chat("Hello")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
async def test_chat_with_empty_message_raises_error(message: str) -> None:
    service = AgentService()
    service._agent = object()

    with pytest.raises(
        ValueError,
        match="Message cannot be empty.",
    ):
        await service.chat(message)


@pytest.mark.asyncio
async def test_chat_returns_agent_response() -> None:
    service = AgentService()

    expected_response = "Hello! How can I help you?"

    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={
            "messages": [
                AIMessage(content=expected_response),
            ]
        }
    )

    service._agent = mock_agent

    response = await service.chat("Hello")

    assert response == expected_response

    mock_agent.ainvoke.assert_awaited_once_with(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ]
        }
    )


@pytest.mark.asyncio
async def test_close_releases_resources_and_resets_state() -> None:
    service = AgentService()

    mock_exit_stack = AsyncMock()
    service._exit_stack = mock_exit_stack
    service._agent = MagicMock()

    await service.close()

    mock_exit_stack.aclose.assert_awaited_once()

    assert service._exit_stack is None
    assert service._agent is None


@pytest.mark.asyncio
async def test_close_before_initialization_does_not_raise() -> None:
    service = AgentService()

    await service.close()

    assert service._exit_stack is None
    assert service._agent is None


@pytest.mark.asyncio
async def test_initialize_creates_agent_and_keeps_adapter_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AgentService()

    settings = SimpleNamespace(
        groq_model_name="openai/gpt-oss-120b",
        groq_api_key="test-api-key",
        temperature=0.0,
    )

    monkeypatch.setattr(
        agent_service_module,
        "get_settings",
        lambda: settings,
    )

    mock_llm = MagicMock()
    monkeypatch.setattr(
        agent_service_module,
        "ChatGroq",
        MagicMock(return_value=mock_llm),
    )

    mock_config = MagicMock()
    mock_config.model_dump.return_value = {"mcpServers": {}}

    monkeypatch.setattr(
        agent_service_module,
        "load_client_config",
        MagicMock(return_value=mock_config),
    )

    mock_client_group = MagicMock()

    monkeypatch.setattr(
        agent_service_module.ClientGroup,
        "from_config",
        MagicMock(return_value=mock_client_group),
    )

    mock_adapter = MagicMock()
    mock_adapter.__aenter__ = AsyncMock(return_value=mock_adapter)
    mock_adapter.__aexit__ = AsyncMock(return_value=None)
    mock_adapter.list_tools = AsyncMock(return_value=["tool"])

    monkeypatch.setattr(
        agent_service_module,
        "MCPAdapter",
        MagicMock(return_value=mock_adapter),
    )

    expected_agent = MagicMock()

    mock_create_agent = MagicMock(return_value=expected_agent)

    monkeypatch.setattr(
        agent_service_module,
        "create_agent",
        mock_create_agent,
    )

    await service.initialize()

    assert service._agent is expected_agent
    assert service._exit_stack is not None

    mock_adapter.__aenter__.assert_awaited_once()
    mock_adapter.list_tools.assert_awaited_once()

    mock_create_agent.assert_called_once_with(
        model=mock_llm,
        tools=["tool"],
    )

    mock_adapter.__aexit__.assert_not_awaited()

    await service.close()

    mock_adapter.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_initialize_closes_adapter_when_listing_tools_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AgentService()

    settings = SimpleNamespace(
        groq_model_name="openai/gpt-oss-120b",
        groq_api_key="test-api-key",
        temperature=0.0,
    )

    monkeypatch.setattr(
        agent_service_module,
        "get_settings",
        lambda: settings,
    )

    monkeypatch.setattr(
        agent_service_module,
        "ChatGroq",
        MagicMock(),
    )

    mock_config = MagicMock()
    mock_config.model_dump.return_value = {"mcpServers": {}}

    monkeypatch.setattr(
        agent_service_module,
        "load_client_config",
        MagicMock(return_value=mock_config),
    )

    monkeypatch.setattr(
        agent_service_module.ClientGroup,
        "from_config",
        MagicMock(),
    )

    mock_adapter = MagicMock()
    mock_adapter.__aenter__ = AsyncMock(return_value=mock_adapter)
    mock_adapter.__aexit__ = AsyncMock(return_value=None)
    mock_adapter.list_tools = AsyncMock(
        side_effect=RuntimeError("Tool discovery failed.")
    )

    monkeypatch.setattr(
        agent_service_module,
        "MCPAdapter",
        MagicMock(return_value=mock_adapter),
    )

    with pytest.raises(RuntimeError, match="Tool discovery failed."):
        await service.initialize()

    mock_adapter.__aenter__.assert_awaited_once()
    mock_adapter.__aexit__.assert_awaited_once()

    assert service._agent is None
    assert service._exit_stack is None


@pytest.mark.asyncio
async def test_initialize_twice_raises_error() -> None:
    service = AgentService()
    service._agent = MagicMock()

    with pytest.raises(
        RuntimeError,
        match="AgentService is already initialized.",
    ):
        await service.initialize()
