from datetime import UTC, datetime
from pathlib import Path

import pytest

from mcp_mastery.operations_server.file_system.service import (
    MAX_FILE_SIZE_TO_READ,
    get_file_info,
    list_files,
    read_file,
    write_file,
)


def test_list_files_empty_directory(tmp_path: Path) -> None:
    result = list_files(tmp_path)

    assert result == []


def test_list_files_with_files(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Notes", encoding="utf-8")
    (tmp_path / "report.pdf").write_text("Report", encoding="utf-8")

    result = list_files(tmp_path)

    assert result == [
        {"name": "notes.txt", "type": "file"},
        {"name": "report.pdf", "type": "file"},
    ]


def test_list_files_with_directories(tmp_path: Path) -> None:
    (tmp_path / "documents").mkdir()
    (tmp_path / "images").mkdir()

    result = list_files(tmp_path)

    assert result == [
        {"name": "documents", "type": "directory"},
        {"name": "images", "type": "directory"},
    ]


def test_list_files_with_mixed_entries(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Notes", encoding="utf-8")
    (tmp_path / "documents").mkdir()

    result = list_files(tmp_path)

    assert result == [
        {"name": "documents", "type": "directory"},
        {"name": "notes.txt", "type": "file"},
    ]


def test_list_files_only_returns_direct_children(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "notes.txt").write_text("Notes", encoding="utf-8")

    result = list_files(tmp_path)

    assert result == [
        {"name": "documents", "type": "directory"},
    ]


def test_list_files_with_nested_path(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "notes.txt").write_text("Notes", encoding="utf-8")

    result = list_files(tmp_path, "documents")

    assert result == [
        {"name": "notes.txt", "type": "file"},
    ]


def test_list_files_with_non_existing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        list_files(tmp_path, "nonexistent")


def test_list_files_when_path_is_a_file(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Notes", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        list_files(tmp_path, "notes.txt")


def test_list_files_with_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        list_files(tmp_path, "../outside")


def test_list_files_returns_sorted_entries(tmp_path: Path) -> None:
    (tmp_path / "zebra.txt").write_text("Zebra", encoding="utf-8")
    (tmp_path / "apple.txt").write_text("Apple", encoding="utf-8")
    (tmp_path / "banana.txt").write_text("Banana", encoding="utf-8")

    result = list_files(tmp_path)

    assert [entry["name"] for entry in result] == [
        "apple.txt",
        "banana.txt",
        "zebra.txt",
    ]


def test_read_file_with_valid_utf8_content(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Hello World", encoding="utf-8")

    result = read_file(tmp_path, "notes.txt")

    assert result == "Hello World"


def test_read_file_with_empty_content(tmp_path: Path) -> None:
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")

    result = read_file(tmp_path, "empty.txt")

    assert result == ""


def test_read_file_with_unicode_content(tmp_path: Path) -> None:
    content = "سلام دنیا! こんにちは世界! 🌍"
    (tmp_path / "unicode.txt").write_text(content, encoding="utf-8")

    result = read_file(tmp_path, "unicode.txt")

    assert result == content


def test_read_file_with_non_existing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_file(tmp_path, "nonexistent.txt")


def test_read_file_when_path_is_a_directory(tmp_path: Path) -> None:
    (tmp_path / "documents").mkdir()

    with pytest.raises(IsADirectoryError):
        read_file(tmp_path, "documents")


def test_read_file_exceeding_maximum_size(tmp_path: Path) -> None:
    file_path = tmp_path / "large.txt"
    file_path.write_bytes(b"a" * (MAX_FILE_SIZE_TO_READ + 1))

    with pytest.raises(ValueError, match="File size exceeds"):
        read_file(tmp_path, "large.txt")


def test_read_file_at_maximum_allowed_size(tmp_path: Path) -> None:
    file_path = tmp_path / "maximum.txt"
    content = b"a" * MAX_FILE_SIZE_TO_READ
    file_path.write_bytes(content)

    result = read_file(tmp_path, "maximum.txt")

    assert result == content.decode("utf-8")
    assert len(result.encode("utf-8")) == MAX_FILE_SIZE_TO_READ


def test_read_file_with_invalid_utf8_content(tmp_path: Path) -> None:
    file_path = tmp_path / "invalid.txt"
    file_path.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(ValueError, match="not valid UTF-8") as exc_info:
        read_file(tmp_path, "invalid.txt")

    assert isinstance(exc_info.value.__cause__, UnicodeDecodeError)


def test_read_file_with_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        read_file(tmp_path, "../outside.txt")


def test_write_file_creates_new_file(tmp_path: Path) -> None:
    result = write_file(tmp_path, "notes.txt", "Hello World")

    assert result is None
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "Hello World"


def test_write_file_overwrites_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Old content", encoding="utf-8")

    write_file(tmp_path, "notes.txt", "New content")

    assert file_path.read_text(encoding="utf-8") == "New content"


def test_write_file_with_empty_content(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.txt"

    write_file(tmp_path, "empty.txt", "")

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == ""


def test_write_file_with_unicode_content(tmp_path: Path) -> None:
    content = "سلام دنیا! こんにちは世界! 🌍"

    write_file(tmp_path, "unicode.txt", content)

    assert (tmp_path / "unicode.txt").read_text(encoding="utf-8") == content


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(None, id="none"),
        pytest.param(123, id="integer"),
        pytest.param(b"binary content", id="bytes"),
        pytest.param(["content"], id="list"),
    ],
)
def test_write_file_with_invalid_content_type(
    tmp_path: Path,
    content: object,
) -> None:
    with pytest.raises(TypeError, match="content must be a string"):
        write_file(tmp_path, "notes.txt", content)


def test_write_file_when_path_is_a_directory(tmp_path: Path) -> None:
    (tmp_path / "documents").mkdir()

    with pytest.raises(IsADirectoryError):
        write_file(tmp_path, "documents", "content")


def test_write_file_with_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        write_file(tmp_path, "../outside.txt", "content")


def test_write_file_does_not_leave_temporary_file_after_success(
    tmp_path: Path,
) -> None:
    write_file(tmp_path, "notes.txt", "Hello World")

    assert sorted(path.name for path in tmp_path.iterdir()) == ["notes.txt"]


def test_write_file_preserves_existing_content_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Original content", encoding="utf-8")

    def fail_replace(source: str, destination: Path) -> None:
        raise OSError("Simulated replacement failure.")

    monkeypatch.setattr(
        "mcp_mastery.operations_server.file_system.service.os.replace",
        fail_replace,
    )

    with pytest.raises(OSError, match="Simulated replacement failure"):
        write_file(tmp_path, "notes.txt", "New content")

    assert file_path.read_text(encoding="utf-8") == "Original content"


def test_write_file_cleans_up_temporary_file_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_replace(source: str, destination: Path) -> None:
        raise OSError("Simulated replacement failure.")

    monkeypatch.setattr(
        "mcp_mastery.operations_server.file_system.service.os.replace",
        fail_replace,
    )

    with pytest.raises(OSError):
        write_file(tmp_path, "notes.txt", "New content")

    assert list(tmp_path.iterdir()) == []


def test_get_file_info_for_file(tmp_path: Path) -> None:
    content = "Hello World"
    file_path = tmp_path / "notes.txt"
    file_path.write_text(content, encoding="utf-8")

    result = get_file_info(tmp_path, "notes.txt")

    assert result["name"] == "notes.txt"
    assert result["type"] == "file"
    assert result["size"] == len(content.encode("utf-8"))
    assert isinstance(result["modified_at"], str)


def test_get_file_info_for_empty_file(tmp_path: Path) -> None:
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")

    result = get_file_info(tmp_path, "empty.txt")

    assert result["size"] == 0


def test_get_file_info_for_unicode_file(tmp_path: Path) -> None:
    content = "Hello World🌍"
    (tmp_path / "unicode.txt").write_text(content, encoding="utf-8")

    result = get_file_info(tmp_path, "unicode.txt")

    assert result["size"] == len(content.encode("utf-8"))


def test_get_file_info_for_directory(tmp_path: Path) -> None:
    (tmp_path / "documents").mkdir()

    result = get_file_info(tmp_path, "documents")

    assert result["name"] == "documents"
    assert result["type"] == "directory"
    assert result["size"] is None


def test_get_file_info_for_nested_file(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "notes.txt").write_text("Notes", encoding="utf-8")

    result = get_file_info(tmp_path, "documents/notes.txt")

    assert result["name"] == "notes.txt"
    assert result["type"] == "file"


def test_get_file_info_for_non_existing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        get_file_info(tmp_path, "nonexistent.txt")


def test_get_file_info_with_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        get_file_info(tmp_path, "../outside.txt")


def test_get_file_info_returns_utc_timestamp(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Notes", encoding="utf-8")

    result = get_file_info(tmp_path, "notes.txt")

    modified_at = datetime.fromisoformat(result["modified_at"])

    assert modified_at.tzinfo == UTC
    assert modified_at.utcoffset().total_seconds() == 0


def test_get_file_info_returns_expected_fields(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("Notes", encoding="utf-8")

    result = get_file_info(tmp_path, "notes.txt")

    assert set(result) == {"name", "type", "size", "modified_at"}
