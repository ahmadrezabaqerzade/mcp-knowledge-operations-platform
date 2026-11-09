from fastmcp import FastMCP

from mcp_mastery.config.factory import get_settings
from mcp_mastery.operations_server.file_system import service


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def list_files(user_path: str = ".") -> list[dict[str, str]]:
        """List files and directories inside the configured workspace."""

        workspace = get_settings().mcp_workspace
        return service.list_files(workspace, user_path)

    @mcp.tool()
    def read_file(user_path: str) -> str:
        """Read a UTF-8 text file inside the configured workspace."""

        workspace = get_settings().mcp_workspace
        return service.read_file(workspace, user_path)

    @mcp.tool()
    def write_file(user_path: str, content: str) -> str:
        """Write UTF-8 text content to a file inside the configured workspace."""

        workspace = get_settings().mcp_workspace
        service.write_file(workspace, user_path, content)
        return "File written successfully."

    @mcp.tool()
    def get_file_info(user_path: str) -> dict[str, str | int | None]:
        """Get metadata for a file or directory inside the configured workspace."""

        workspace = get_settings().mcp_workspace
        return service.get_file_info(workspace, user_path)
