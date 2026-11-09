from collections.abc import Iterator
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_mastery.config.factory import get_settings
from mcp_mastery.operations_server.server import mcp


@pytest.fixture
def workspace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Path]:
    """Provide an isolated workspace for each integration test."""

    monkeypatch.setenv("MCP_WORKSPACE", str(tmp_path))
    get_settings.cache_clear()

    try:
        yield tmp_path
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_list_files_tool(workspace: Path) -> None:
    (workspace / "notes.txt").write_text("Hello", encoding="utf-8")
    (workspace / "report.txt").write_text("Report", encoding="utf-8")
    (workspace / "documents").mkdir()

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="list_files",
            arguments={"user_path": "."},
        )

    assert not result.is_error

    files = result.structured_content["result"]

    assert len(files) == 3
    assert {entry["name"] for entry in files} == {
        "notes.txt",
        "report.txt",
        "documents",
    }

    file_types = {entry["name"]: entry["type"] for entry in files}

    assert file_types == {
        "notes.txt": "file",
        "report.txt": "file",
        "documents": "directory",
    }


@pytest.mark.asyncio
async def test_read_file_tool(workspace: Path) -> None:
    expected_content = "Hello, MCP File System!"
    (workspace / "notes.txt").write_text(
        expected_content,
        encoding="utf-8",
    )

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="read_file",
            arguments={"user_path": "notes.txt"},
        )

    assert not result.is_error
    assert result.structured_content["result"] == expected_content


@pytest.mark.asyncio
async def test_write_file_tool_creates_new_file(workspace: Path) -> None:
    content = "New file created through MCP."

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="write_file",
            arguments={
                "user_path": "new_file.txt",
                "content": content,
            },
        )

    assert not result.is_error
    assert result.structured_content["result"] == "File written successfully."
    assert (workspace / "new_file.txt").read_text(encoding="utf-8") == content


@pytest.mark.asyncio
async def test_write_file_tool_overwrites_existing_file(workspace: Path) -> None:
    file_path = workspace / "notes.txt"
    file_path.write_text("Old content", encoding="utf-8")

    new_content = "Updated content"

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="write_file",
            arguments={
                "user_path": "notes.txt",
                "content": new_content,
            },
        )

    assert not result.is_error
    assert file_path.read_text(encoding="utf-8") == new_content


@pytest.mark.asyncio
async def test_get_file_info_tool(workspace: Path) -> None:
    file_path = workspace / "notes.txt"
    content = "File metadata test."
    file_path.write_text(content, encoding="utf-8")

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="get_file_info",
            arguments={"user_path": "notes.txt"},
        )

    assert not result.is_error

    info = result.structured_content

    assert info["name"] == "notes.txt"
    assert info["type"] == "file"
    assert info["size"] == len(content.encode("utf-8"))
    assert info["modified_at"]


@pytest.mark.asyncio
async def test_file_system_tool_rejects_path_traversal(
    workspace: Path,
) -> None:
    outside_file = workspace.parent / "outside.txt"
    outside_file.write_text("Sensitive content", encoding="utf-8")

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="Path traversal is not allowed"):
            await client.call_tool(
                name="read_file",
                arguments={"user_path": "../outside.txt"},
            )


@pytest.mark.asyncio
async def test_list_files_tool_with_nested_path(workspace: Path) -> None:
    nested_directory = workspace / "documents"
    nested_directory.mkdir()

    (nested_directory / "notes.txt").write_text(
        "Nested file content.",
        encoding="utf-8",
    )
    (nested_directory / "report.txt").write_text(
        "Nested report content.",
        encoding="utf-8",
    )

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="list_files",
            arguments={"user_path": "documents"},
        )

    assert not result.is_error

    files = result.structured_content["result"]

    assert len(files) == 2
    assert {entry["name"] for entry in files} == {
        "notes.txt",
        "report.txt",
    }
    assert all(entry["type"] == "file" for entry in files)


@pytest.mark.asyncio
async def test_get_file_info_tool_for_directory(workspace: Path) -> None:
    directory = workspace / "documents"
    directory.mkdir()

    async with Client(mcp) as client:
        result = await client.call_tool(
            name="get_file_info",
            arguments={"user_path": "documents"},
        )

    assert not result.is_error

    info = result.structured_content

    assert info["name"] == "documents"
    assert info["type"] == "directory"
    assert info["size"] is None
    assert info["modified_at"]
