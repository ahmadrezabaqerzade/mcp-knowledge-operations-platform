from pathlib import Path

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[4]
KNOWLEDGE_DIR = (PROJECT_ROOT / "data" / "knowledge").resolve()


def get_knowledge_overview() -> str:
    """Return an overview of available knowledge topics."""
    resources = sorted(KNOWLEDGE_DIR.glob("*.md"))

    if not resources:
        return "No knowledge topics are currently available."

    topics = [resource.stem for resource in resources]

    return "Available Knowledge Topics:\n\n" + "\n".join(
        f"- {topic}" for topic in topics
    )


def get_topic(topic: str) -> str:
    """Return the content of a knowledge topic."""
    available_topics = {resource.stem for resource in KNOWLEDGE_DIR.glob("*.md")}

    if topic not in available_topics:
        return f"Knowledge topic '{topic}' was not found."

    file_path = (KNOWLEDGE_DIR / f"{topic}.md").resolve()

    if not file_path.is_relative_to(KNOWLEDGE_DIR):
        return "Access denied: invalid knowledge file path."

    if not file_path.is_file():
        return f"Knowledge topic '{topic}' is not a valid file."

    return file_path.read_text(encoding="utf-8")


def register(mcp: FastMCP) -> None:
    """Register knowledge overview resources."""

    @mcp.resource("knowledge://overview")
    def knowledge_overview() -> str:
        return get_knowledge_overview()

    @mcp.resource("knowledge://topics/{topic}")
    def knowledge_resource(topic: str) -> str:
        return get_topic(topic)
