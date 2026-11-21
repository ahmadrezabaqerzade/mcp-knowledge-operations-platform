from fastmcp import FastMCP

mcp = FastMCP("HTTP Test Server")


@mcp.tool()
def ping() -> str:
    """Return a health-check response."""
    return "HTTP server is alive"


def main() -> None:
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8765,
        show_banner=False,
    )


if __name__ == "__main__":
    main()
