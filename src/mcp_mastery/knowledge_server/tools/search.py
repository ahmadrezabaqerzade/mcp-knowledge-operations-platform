from pathlib import Path

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[4]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def search_knowledge(query: str) -> list[dict[str, str]]:
    """Search for a query across all Markdown knowledge files."""
    normalized_query = query.strip().casefold()

    if not normalized_query:
        return []

    results = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        if normalized_query in content.casefold():
            results.append(
                {
                    "file": file_path.name,
                    "content": content,
                }
            )
    return results


def register(mcp: FastMCP) -> None:
    """Register knowledge search tools."""
    mcp.tool(search_knowledge)
