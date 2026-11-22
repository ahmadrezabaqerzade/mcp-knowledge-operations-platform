import asyncio

import streamlit as st

from mcp_mastery.application.agent_service import AgentService


async def get_agent_response(message: str) -> str:
    """Initialize the agent, process a message, and release its resources."""
    service = AgentService()

    try:
        await service.initialize()
        return await service.chat(message)
    finally:
        await service.close()


def render_chat_page() -> None:
    """Render the MCP Chat Assistant page."""

    st.title("🤖 MCP Chat Assistant")

    st.caption(
        "Ask questions and interact with your Knowledge and Operations MCP servers."
    )

    # Initialize chat history for the current user session.
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display previous messages.
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Receive a new user message.
    if prompt := st.chat_input("Ask something..."):
        # Save and display the user message.
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate the assistant response.
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):
                try:
                    response = asyncio.run(get_agent_response(prompt))

                    st.markdown(response)

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                        }
                    )

                except Exception as exc:
                    st.error(f"An error occurred: {exc}")

    # Clear conversation history.
    if st.button("Clear conversation"):
        st.session_state.chat_messages = []
        st.rerun()
