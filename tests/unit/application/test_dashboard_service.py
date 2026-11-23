from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_mastery.application import dashboard_service


@pytest.fixture
def config():
    return MagicMock()


@pytest.fixture
def manager():
    instance = MagicMock()
    instance.connect = AsyncMock()
    instance.disconnect = AsyncMock()
    return instance


@pytest.fixture
def service():
    return dashboard_service.DashboardService()


@pytest.mark.asyncio
async def test_initialize_uses_default_config_path(
    service,
    config,
    manager,
    monkeypatch,
):
    expected_path = (
        Path(dashboard_service.__file__).parents[3].resolve()
        / "config"
        / "mcp_servers.json"
    )

    load_config = MagicMock(return_value=config)
    manager_factory = MagicMock(return_value=manager)

    monkeypatch.setattr(
        dashboard_service,
        "load_client_config",
        load_config,
    )
    monkeypatch.setattr(
        dashboard_service,
        "MCPConnectionManager",
        manager_factory,
    )

    await service.initialize()

    load_config.assert_called_once_with(expected_path)
    manager_factory.assert_called_once_with(config)
    manager.connect.assert_awaited_once_with()

    assert service._config is config
    assert service._manager is manager
    assert service._config_path == expected_path


@pytest.mark.asyncio
async def test_initialize_uses_custom_config_path(
    config,
    manager,
    monkeypatch,
):
    custom_path = Path("/tmp/custom_mcp_servers.json")
    service = dashboard_service.DashboardService(config_path=custom_path)

    load_config = MagicMock(return_value=config)
    manager_factory = MagicMock(return_value=manager)

    monkeypatch.setattr(
        dashboard_service,
        "load_client_config",
        load_config,
    )
    monkeypatch.setattr(
        dashboard_service,
        "MCPConnectionManager",
        manager_factory,
    )

    await service.initialize()

    load_config.assert_called_once_with(custom_path)
    assert service._config_path == custom_path
    assert service._config is config
    assert service._manager is manager


@pytest.mark.asyncio
async def test_initialize_raises_when_already_initialized(
    service,
    config,
    monkeypatch,
):
    service._config = config

    load_config = MagicMock()
    monkeypatch.setattr(
        dashboard_service,
        "load_client_config",
        load_config,
    )

    with pytest.raises(RuntimeError, match="already initialized"):
        await service.initialize()

    load_config.assert_not_called()


@pytest.mark.asyncio
async def test_initialize_propagates_config_loading_error(
    service,
    monkeypatch,
):
    error = ValueError("Invalid configuration")
    load_config = MagicMock(side_effect=error)

    monkeypatch.setattr(
        dashboard_service,
        "load_client_config",
        load_config,
    )

    with pytest.raises(ValueError, match="Invalid configuration"):
        await service.initialize()

    assert service._config is None
    assert service._manager is None


@pytest.mark.asyncio
async def test_initialize_propagates_connection_error(
    service,
    config,
    manager,
    monkeypatch,
):
    manager.connect.side_effect = RuntimeError("Connection failed")

    monkeypatch.setattr(
        dashboard_service,
        "load_client_config",
        MagicMock(return_value=config),
    )
    monkeypatch.setattr(
        dashboard_service,
        "MCPConnectionManager",
        MagicMock(return_value=manager),
    )

    with pytest.raises(RuntimeError, match="Connection failed"):
        await service.initialize()

    assert service._config is None
    assert service._manager is None


@pytest.mark.asyncio
async def test_close_does_nothing_when_not_initialized(service):
    await service.close()

    assert service._config is None
    assert service._manager is None


@pytest.mark.asyncio
async def test_initialize_after_close_reuses_custom_config_path(
    service,
    config,
):
    custom_path = Path("/tmp/custom_mcp_servers.json")

    first_manager = MagicMock()
    first_manager.connect = AsyncMock()
    first_manager.disconnect = AsyncMock()

    second_manager = MagicMock()
    second_manager.connect = AsyncMock()
    second_manager.disconnect = AsyncMock()

    with (
        patch(
            "mcp_mastery.application.dashboard_service.load_client_config",
            return_value=config,
        ) as mock_load_config,
        patch(
            "mcp_mastery.application.dashboard_service.MCPConnectionManager",
            side_effect=[first_manager, second_manager],
        ) as mock_manager,
    ):
        service._config_path = custom_path

        await service.initialize()
        await service.close()

        await service.initialize()

    assert mock_load_config.call_count == 2
    mock_load_config.assert_any_call(custom_path)

    assert mock_manager.call_count == 2

    first_manager.connect.assert_awaited_once_with()
    first_manager.disconnect.assert_awaited_once_with()

    second_manager.connect.assert_awaited_once_with()

    assert service._config_path == custom_path
    assert service._config is config
    assert service._manager is second_manager


@pytest.mark.asyncio
async def test_close_disconnects_and_clears_state(
    service,
    config,
    manager,
):
    service._config = config
    service._manager = manager
    service._config_path = Path("/tmp/mcp_servers.json")

    await service.close()

    manager.disconnect.assert_awaited_once_with()

    assert service._manager is None
    assert service._config is None
    assert service._config_path == Path("/tmp/mcp_servers.json")


@pytest.mark.asyncio
async def test_close_clears_state_when_disconnect_fails(
    service,
    config,
    manager,
):
    manager.disconnect.side_effect = RuntimeError("Disconnect failed")

    service._config = config
    service._manager = manager
    service._config_path = Path("/tmp/mcp_servers.json")

    with pytest.raises(RuntimeError, match="Disconnect failed"):
        await service.close()

    assert service._manager is None
    assert service._config is None
    assert service._config_path == Path("/tmp/mcp_servers.json")


@pytest.mark.asyncio
async def test_close_can_be_called_multiple_times(
    service,
    config,
    manager,
):
    service._config = config
    service._manager = manager

    await service.close()
    await service.close()

    manager.disconnect.assert_awaited_once_with()

    assert service._manager is None
    assert service._config is None


@pytest.mark.asyncio
async def test_list_tools_returns_server_tools(service, manager):
    tools = [MagicMock(), MagicMock()]
    client = MagicMock()
    client.list_tools = AsyncMock(return_value=tools)

    service._manager = manager
    manager.get_client.return_value = client

    result = await service.list_tools("knowledge")

    manager.get_client.assert_called_once_with("knowledge")
    client.list_tools.assert_awaited_once_with()
    assert result == tools


@pytest.mark.asyncio
async def test_list_tools_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        await service.list_tools("knowledge")


@pytest.mark.asyncio
async def test_list_tools_propagates_unknown_server_error(service, manager):
    service._manager = manager
    manager.get_client.side_effect = KeyError(
        "Unknown or unavailable MCP server: unknown"
    )

    with pytest.raises(KeyError, match="Unknown or unavailable MCP server"):
        await service.list_tools("unknown")

    manager.get_client.assert_called_once_with("unknown")


@pytest.mark.asyncio
async def test_list_tools_propagates_client_error(service, manager):
    client = MagicMock()
    client.list_tools = AsyncMock(side_effect=RuntimeError("Failed to list tools"))

    service._manager = manager
    manager.get_client.return_value = client

    with pytest.raises(RuntimeError, match="Failed to list tools"):
        await service.list_tools("knowledge")

    client.list_tools.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_list_resources_returns_server_resources(service, manager):
    resources = [MagicMock(), MagicMock()]
    client = MagicMock()
    client.list_resources = AsyncMock(return_value=resources)

    service._manager = manager
    manager.get_client.return_value = client

    result = await service.list_resources("knowledge")

    manager.get_client.assert_called_once_with("knowledge")
    client.list_resources.assert_awaited_once_with()
    assert result == resources


@pytest.mark.asyncio
async def test_list_resources_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        await service.list_resources("knowledge")


@pytest.mark.asyncio
async def test_list_resources_propagates_client_error(service, manager):
    client = MagicMock()
    client.list_resources = AsyncMock(
        side_effect=RuntimeError("Failed to list resources")
    )

    service._manager = manager
    manager.get_client.return_value = client

    with pytest.raises(RuntimeError, match="Failed to list resources"):
        await service.list_resources("knowledge")

    client.list_resources.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_list_resource_templates_returns_server_templates(service, manager):
    templates = [MagicMock(), MagicMock()]
    client = MagicMock()
    client.list_resource_templates = AsyncMock(return_value=templates)

    service._manager = manager
    manager.get_client.return_value = client

    result = await service.list_resource_templates("knowledge")

    manager.get_client.assert_called_once_with("knowledge")
    client.list_resource_templates.assert_awaited_once_with()
    assert result == templates


@pytest.mark.asyncio
async def test_list_resource_templates_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        await service.list_resource_templates("knowledge")


@pytest.mark.asyncio
async def test_list_resource_templates_propagates_client_error(service, manager):
    client = MagicMock()
    client.list_resource_templates = AsyncMock(
        side_effect=RuntimeError("Failed to list resource templates")
    )

    service._manager = manager
    manager.get_client.return_value = client

    with pytest.raises(RuntimeError, match="Failed to list resource templates"):
        await service.list_resource_templates("knowledge")

    client.list_resource_templates.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_list_prompts_returns_server_prompts(service, manager):
    prompts = [MagicMock(), MagicMock()]
    client = MagicMock()
    client.list_prompts = AsyncMock(return_value=prompts)

    service._manager = manager
    manager.get_client.return_value = client

    result = await service.list_prompts("knowledge")

    manager.get_client.assert_called_once_with("knowledge")
    client.list_prompts.assert_awaited_once_with()
    assert result == prompts


@pytest.mark.asyncio
async def test_list_prompts_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        await service.list_prompts("knowledge")


@pytest.mark.asyncio
async def test_list_prompts_propagates_client_error(service, manager):
    client = MagicMock()
    client.list_prompts = AsyncMock(side_effect=RuntimeError("Failed to list prompts"))

    service._manager = manager
    manager.get_client.return_value = client

    with pytest.raises(RuntimeError, match="Failed to list prompts"):
        await service.list_prompts("knowledge")

    client.list_prompts.assert_awaited_once_with()


def test_list_servers_returns_configured_server_names(service):
    config = MagicMock()
    config.mcp_servers = {
        "knowledge": MagicMock(),
        "operations": MagicMock(),
    }

    service._config = config

    result = service.list_servers()

    assert result == ["knowledge", "operations"]


def test_list_servers_returns_empty_list_when_no_servers(service):
    config = MagicMock()
    config.mcp_servers = {}

    service._config = config

    result = service.list_servers()

    assert result == []


def test_list_servers_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        service.list_servers()


def test_get_server_details_returns_stdio_server_details(service, manager):
    config = MagicMock()
    config.mcp_servers = {
        "knowledge": MagicMock(spec=dashboard_service.StdioServerConfig),
    }

    client = MagicMock()
    client.is_connected.return_value = True

    service._config = config
    service._manager = manager
    manager.get_client.return_value = client

    result = service.get_server_details("knowledge")

    assert result.name == "knowledge"
    assert result.transport == "stdio"
    assert result.connected is True

    manager.get_client.assert_called_once_with("knowledge")
    client.is_connected.assert_called_once_with()


def test_get_server_details_returns_http_server_details(service, manager):
    config = MagicMock()
    config.mcp_servers = {
        "knowledge": MagicMock(spec=dashboard_service.HttpServerConfig),
    }

    client = MagicMock()
    client.is_connected.return_value = True

    service._config = config
    service._manager = manager
    manager.get_client.return_value = client

    result = service.get_server_details("knowledge")

    assert result.name == "knowledge"
    assert result.transport == "http"
    assert result.connected is True

    manager.get_client.assert_called_once_with("knowledge")
    client.is_connected.assert_called_once_with()


def test_get_server_details_returns_disconnected_status(service, manager):
    config = MagicMock()
    config.mcp_servers = {
        "knowledge": MagicMock(spec=dashboard_service.StdioServerConfig),
    }

    client = MagicMock()
    client.is_connected.return_value = False

    service._config = config
    service._manager = manager
    manager.get_client.return_value = client

    result = service.get_server_details("knowledge")

    assert result.name == "knowledge"
    assert result.transport == "stdio"
    assert result.connected is False

    client.is_connected.assert_called_once_with()


def test_get_server_details_raises_for_unknown_server(service, manager):
    config = MagicMock()
    config.mcp_servers = {
        "knowledge": MagicMock(spec=dashboard_service.StdioServerConfig),
    }

    service._config = config
    service._manager = manager

    with pytest.raises(KeyError, match="Unknown MCP server: missing"):
        service.get_server_details("missing")

    manager.get_client.assert_not_called()


def test_get_server_details_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        service.get_server_details("knowledge")


@pytest.mark.asyncio
async def test_call_tool_returns_tool_result(service, manager):
    result = MagicMock()
    arguments = {"expression": "10 + 20"}

    client = MagicMock()
    client.call_tool = AsyncMock(return_value=result)

    service._manager = manager
    manager.get_client.return_value = client

    response = await service.call_tool(
        server_name="operations",
        tool_name="calculate",
        arguments=arguments,
    )

    manager.get_client.assert_called_once_with("operations")
    client.call_tool.assert_awaited_once_with(
        name="calculate",
        arguments=arguments,
    )
    assert response is result


@pytest.mark.asyncio
async def test_call_tool_raises_when_not_initialized(service):
    with pytest.raises(RuntimeError, match="not initialized"):
        await service.call_tool(
            server_name="operations",
            tool_name="calculate",
        )


@pytest.mark.asyncio
async def test_call_tool_propagates_client_error(service, manager):
    client = MagicMock()
    client.call_tool = AsyncMock(side_effect=RuntimeError("Tool execution failed"))

    service._manager = manager
    manager.get_client.return_value = client

    with pytest.raises(RuntimeError, match="Tool execution failed"):
        await service.call_tool(
            server_name="operations",
            tool_name="calculate",
            arguments={"expression": "10 + 20"},
        )

    client.call_tool.assert_awaited_once_with(
        name="calculate",
        arguments={"expression": "10 + 20"},
    )
