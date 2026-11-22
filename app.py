import streamlit as st

from mcp_mastery.ui.chat_page import render_chat_page
from mcp_mastery.ui.dashboard_page import render_dashboard_page

st.set_page_config(
    page_title="MCP Knowledge Platform",
    page_icon="🤖",
    layout="wide",
)

st.sidebar.title("MCP Knowledge Platform")

selected_page = st.sidebar.radio(
    "Navigation",
    options=[
        "Chat Assistant",
        "MCP Dashboard",
    ],
)

if selected_page == "Chat Assistant":
    render_chat_page()

elif selected_page == "MCP Dashboard":
    render_dashboard_page()
