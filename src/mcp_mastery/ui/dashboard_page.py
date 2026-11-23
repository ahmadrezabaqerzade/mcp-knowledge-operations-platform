import asyncio
import json
from typing import Any

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
            servers.append(details.model_dump(mode="json"))

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
            "tools": [item.model_dump(mode="json", by_alias=True) for item in tools],
            "resources": [
                item.model_dump(mode="json", by_alias=True) for item in resources
            ],
            "resource_templates": [
                item.model_dump(mode="json", by_alias=True) for item in templates
            ],
            "prompts": [
                item.model_dump(mode="json", by_alias=True) for item in prompts
            ],
        }

    finally:
        await service.close()


async def execute_server_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict:
    """Execute an MCP tool and return its result."""

    service = DashboardService()

    try:
        await service.initialize()

        result = await service.call_tool(
            server_name=server_name,
            tool_name=tool_name,
            arguments=arguments,
        )

        return {
            "content": [
                item.model_dump(mode="json")
                if hasattr(item, "model_dump")
                else str(item)
                for item in result.content
            ],
            "isError": result.is_error,
            "structuredContent": result.structured_content,
        }

    finally:
        await service.close()


def render_tool_arguments(
    input_schema: dict,
    server_name: str,
    tool_name: str,
) -> dict[str, Any] | None:
    """Render input widgets dynamically from a tool's JSON Schema."""

    properties = input_schema.get("properties", {})
    required_fields = input_schema.get("required", [])

    arguments: dict[str, Any] = {}

    for field_name, field_schema in properties.items():
        field_type = field_schema.get("type")
        field_label = field_name.replace("_", " ").title()
        default_value = field_schema.get("default")

        widget_key = f"argument_{server_name}_{tool_name}_{field_name}"

        if field_type == "string":
            value = st.text_input(
                label=field_label,
                value=default_value if default_value is not None else "",
                key=widget_key,
            )

            if value or field_name in required_fields:
                arguments[field_name] = value

        elif field_type in {"integer", "number"}:
            value = st.number_input(
                label=field_label,
                value=default_value if default_value is not None else 0,
                step=1 if field_type == "integer" else 0.1,
                key=widget_key,
            )

            arguments[field_name] = (
                int(value) if field_type == "integer" else float(value)
            )

        elif field_type == "boolean":
            arguments[field_name] = st.checkbox(
                label=field_label,
                value=bool(default_value) if default_value is not None else False,
                key=widget_key,
            )

        elif field_type in {"array", "object"}:
            raw_value = st.text_area(
                label=field_label,
                value=(json.dumps(default_value) if default_value is not None else ""),
                help="Enter a valid JSON value.",
                key=widget_key,
            )

            if raw_value.strip():
                try:
                    arguments[field_name] = json.loads(raw_value)
                except json.JSONDecodeError as exc:
                    st.error(f"Invalid JSON for {field_label}: {exc}")
                    return None

            elif field_name in required_fields:
                st.warning(f"{field_label} is required.")
                return None

        else:
            st.warning(f"Unsupported input type: {field_type}")
            return None

    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in arguments
        or arguments[field_name] is None
        or (
            isinstance(arguments[field_name], str) and not arguments[field_name].strip()
        )
    ]

    if missing_fields:
        st.warning("Please provide the required fields: " + ", ".join(missing_fields))
        return None

    return arguments


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
            tool_names = [tool["name"] for tool in inventory["tools"]]

            selected_tool_name = st.selectbox(
                "Select a tool",
                options=tool_names,
                key=f"selected_tool_{selected_server}",
            )

            selected_tool = next(
                tool
                for tool in inventory["tools"]
                if tool["name"] == selected_tool_name
            )

            st.write(
                selected_tool.get(
                    "description",
                    "No description available.",
                )
            )

            input_schema = selected_tool.get("inputSchema", {})

            with st.expander("Tool Schema"):
                st.json(input_schema)

            st.divider()

            st.subheader("Execute Tool")

            with st.form(key=f"tool_form_{selected_server}_{selected_tool_name}"):
                arguments = render_tool_arguments(
                    input_schema=input_schema,
                    server_name=selected_server,
                    tool_name=selected_tool_name,
                )

                submitted = st.form_submit_button(
                    "Execute Tool",
                    type="primary",
                )

            if submitted and arguments is not None:
                try:
                    with st.spinner(f"Executing {selected_tool_name}..."):
                        result = asyncio.run(
                            execute_server_tool(
                                server_name=selected_server,
                                tool_name=selected_tool_name,
                                arguments=arguments,
                            )
                        )

                    st.success("Tool executed successfully.")

                    st.subheader("Tool Result")
                    st.json(result)

                except Exception as exc:
                    st.error(f"Tool execution failed: {exc}")

            st.divider()

            st.subheader("All Available Tools")

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
