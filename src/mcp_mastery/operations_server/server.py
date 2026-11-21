import argparse

from fastmcp import FastMCP

from mcp_mastery.operations_server.tools import (
    calculation,
    data_processing,
    file_system,
    validation,
)

mcp = FastMCP("Operations Server")

calculation.register(mcp)
data_processing.register(mcp)
validation.register(mcp)
file_system.register(mcp)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Operations MCP Server.")

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="HTTP server host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8002,
        help="HTTP server port (default: 8002)",
    )

    return parser.parse_args()


def main() -> None:
    args = get_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )


if __name__ == "__main__":
    main()
