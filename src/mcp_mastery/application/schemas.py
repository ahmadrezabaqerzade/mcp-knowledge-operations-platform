from typing import Literal

from pydantic import BaseModel, ConfigDict


class ServerDetails(BaseModel):
    """Represent MCP server details for the dashboard."""

    model_config = ConfigDict(frozen=True)

    name: str
    transport: Literal["stdio", "http"]
    connected: bool
