from fastmcp import FastMCP

from mcp_mastery.knowledge_server.tools import search

mcp = FastMCP(name="Knowledge Server")

search.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
