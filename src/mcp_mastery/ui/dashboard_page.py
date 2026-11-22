import asyncio

import streamlit as st

from mcp_mastery.application.dashboard_service import DashboardService


async def get_server_details() -> list[dict]:
    """Connect to MCP servers and retrieve their details."""

    service = DashboardService()

    try:
        await service.initialize()

        servers = []

        for server_name in service.list_servers():
            details = service.get_server_details(server_name)
            servers.append(details.model_dump())

        return servers

    finally:
        await service.close()


async def get_server_inventory(server_name: str) -> dict[str, list[dict]]:
    """Retrieve all MCP capabilities exposed by a server."""

    service = DashboardService()

    try:
        await service.initialize()

        tools = await service.list_tools(server_name)
        resources = await service.list_resources(server_name)
        templates = await service.list_resource_templates(server_name)
        prompts = await service.list_prompts(server_name)

        return {
            "tools": [item.model_dump(mode="json") for item in tools],
            "resources": [item.model_dump(mode="json") for item in resources],
            "resource_templates": [item.model_dump(mode="json") for item in templates],
            "prompts": [item.model_dump(mode="json") for item in prompts],
        }

    finally:
        await service.close()


def render_dashboard_page() -> None:
    """Render the MCP Dashboard page."""

    st.title("🖥️ MCP Dashboard")

    st.caption("Monitor your configured MCP servers and inspect their capabilities.")

    refresh_clicked = st.button("🔄 Refresh server status")

    if "dashboard_servers" not in st.session_state or refresh_clicked:
        try:
            with st.status("Connecting to MCP servers...", expanded=True) as status:
                servers = asyncio.run(get_server_details())

                st.session_state.dashboard_servers = servers

                status.update(
                    label="MCP server information loaded successfully.",
                    state="complete",
                    expanded=False,
                )

        except Exception as exc:
            st.error(f"Failed to load MCP servers: {exc}")
            return

    servers = st.session_state.dashboard_servers

    if not servers:
        st.info("No MCP servers are configured.")
        return

    st.subheader("Configured Servers")

    columns = st.columns(len(servers))

    for column, server in zip(columns, servers, strict=False):
        with column:
            with st.container(border=True):
                connection_status = (
                    "Connected" if server["connected"] else "Disconnected"
                )

                st.metric(
                    label=server["name"],
                    value=connection_status,
                )

                st.caption(f"Transport: {server['transport'].upper()}")

                with st.expander("Server Details"):
                    st.write(f"**Server name:** {server['name']}")
                    st.write(f"**Transport:** {server['transport']}")
                    st.write(f"**Connected:** {server['connected']}")

    st.divider()

    st.subheader("MCP Server Inspector")

    server_names = [server["name"] for server in servers]

    selected_server = st.selectbox(
        "Select an MCP server",
        options=server_names,
    )

    if st.button("🔍 Inspect server"):
        try:
            with st.spinner(f"Inspecting {selected_server}..."):
                inventory = asyncio.run(get_server_inventory(selected_server))

                st.session_state[f"inventory_{selected_server}"] = inventory

        except Exception as exc:
            st.error(f"Failed to inspect server: {exc}")
            return

    inventory_key = f"inventory_{selected_server}"

    if inventory_key not in st.session_state:
        st.info("Select a server and click Inspect server to view its capabilities.")
        return

    inventory = st.session_state[inventory_key]

    tools_tab, resources_tab, templates_tab, prompts_tab = st.tabs(
        ["Tools", "Resources", "Resource Templates", "Prompts"]
    )

    with tools_tab:
        st.subheader(f"Tools ({len(inventory['tools'])})")

        if inventory["tools"]:
            for index, tool in enumerate(inventory["tools"], start=1):
                with st.expander(f"{index}. {tool.get('name', 'Unnamed tool')}"):
                    st.json(tool)
        else:
            st.info("This server does not expose any tools.")

    with resources_tab:
        st.subheader(f"Resources ({len(inventory['resources'])})")

        if inventory["resources"]:
            for index, resource in enumerate(inventory["resources"], start=1):
                with st.expander(
                    f"{index}. {resource.get('name', 'Unnamed resource')}"
                ):
                    st.json(resource)
        else:
            st.info("This server does not expose any resources.")

    with templates_tab:
        st.subheader(f"Resource Templates ({len(inventory['resource_templates'])})")

        if inventory["resource_templates"]:
            for index, template in enumerate(inventory["resource_templates"], start=1):
                with st.expander(
                    f"{index}. {template.get('name', 'Unnamed template')}"
                ):
                    st.json(template)
        else:
            st.info("This server does not expose any resource templates.")

    with prompts_tab:
        st.subheader(f"Prompts ({len(inventory['prompts'])})")

        if inventory["prompts"]:
            for index, prompt in enumerate(inventory["prompts"], start=1):
                with st.expander(f"{index}. {prompt.get('name', 'Unnamed prompt')}"):
                    st.json(prompt)
        else:
            st.info("This server does not expose any prompts.")
