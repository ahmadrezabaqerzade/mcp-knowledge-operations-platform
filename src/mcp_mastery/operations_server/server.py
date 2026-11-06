from fastmcp import FastMCP

from mcp_mastery.operations_server.tools import calculation, data_processing

mcp = FastMCP("Operations Server")

calculation.register(mcp)
data_processing.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
