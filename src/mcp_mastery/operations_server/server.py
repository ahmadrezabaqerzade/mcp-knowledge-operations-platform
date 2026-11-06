from fastmcp import FastMCP

from mcp_mastery.operations_server.tools import calculation

mcp = FastMCP("Operations Server")

calculation.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
