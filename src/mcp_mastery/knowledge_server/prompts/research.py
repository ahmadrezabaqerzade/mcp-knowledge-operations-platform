from fastmcp import FastMCP


def get_prompt(topic: str, level: str, focus: str) -> str:
    """Return a research prompt based on topic, level, and focus."""
    return f"""You are an expert research assistant.

Research Topic: {topic}
Research Level: {level}
Focus Area: {focus}

Please provide:
1. A clear introduction.
2. Core concepts and theoretical foundations.
3. Important methods and techniques.
4. Practical applications.
5. Current challenges and open research questions.
6. Reliable references for further study."""


def register(mcp: FastMCP) -> None:
    """Register the research prompt template."""

    @mcp.prompt
    def research_topic(topic: str, level: str, focus: str) -> str:
        """Generate a structured research prompt."""
        return get_prompt(topic, level, focus)
