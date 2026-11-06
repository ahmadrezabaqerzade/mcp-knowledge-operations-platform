from pathlib import Path

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[4]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def get_knowledge_overview() -> str:
    """Return an overview of available knowledge topics."""
    resources = sorted(KNOWLEDGE_DIR.glob("*.md"))

    if not resources:
        return "No knowledge topics are currently available."

    topics = [resource.stem for resource in resources]

    return "Available Knowledge Topics:\n\n" + "\n".join(
        f"- {topic}" for topic in topics
    )


def register(mcp: FastMCP) -> None:
    """Register knowledge overview resources."""

    @mcp.resource("knowledge://overview")
    def knowledge_overview() -> str:
        return get_knowledge_overview()
