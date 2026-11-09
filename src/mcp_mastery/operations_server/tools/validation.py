from fastmcp import FastMCP

from mcp_mastery.operations_server.validation.service import (
    validate_data as validate_data_service,
)


def register(mcp: FastMCP) -> None:
    """Register data validation tools."""

    @mcp.tool()
    def validate_data(
        schema_name: str,
        data: dict[str, object],
    ) -> dict[str, object]:
        """Validate input data against a registered schema."""
        return validate_data_service(schema_name, data)
