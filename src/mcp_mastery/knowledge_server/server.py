from fastmcp import FastMCP

from mcp_mastery.knowledge_server.resources import knowledge
from mcp_mastery.knowledge_server.tools import search

mcp = FastMCP(name="Knowledge Server")

search.register(mcp)
knowledge.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
