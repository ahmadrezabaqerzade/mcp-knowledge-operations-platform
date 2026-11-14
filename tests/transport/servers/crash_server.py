import os

from fastmcp import FastMCP

mcp = FastMCP("Crash Server")


@mcp.tool()
def ping() -> str:
    return "Server is alive"


@mcp.tool()
def crash_server() -> None:
    os._exit(1)


def main() -> None:
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
