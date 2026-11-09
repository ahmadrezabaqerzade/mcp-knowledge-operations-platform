import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from mcp_mastery.operations_server.file_system.security import resolve_safe_path

MAX_FILE_SIZE_TO_READ = 1024 * 1024


def list_files(workspace: Path, user_path: str = ".") -> list[dict[str, str]]:
    """List files and directories inside the specified workspace path."""

    safe_path = resolve_safe_path(workspace, user_path)

    if not safe_path.exists():
        raise FileNotFoundError("The specified path does not exist.")

    if not safe_path.is_dir():
        raise NotADirectoryError("The specified path is not a directory.")

    return [
        {
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file",
        }
        for entry in sorted(safe_path.iterdir(), key=lambda path: path.name)
    ]


def read_file(workspace: Path, user_path: str) -> str:
    """Read a UTF-8 text file inside the workspace."""

    safe_path = resolve_safe_path(workspace, user_path)

    if not safe_path.exists():
        raise FileNotFoundError("The specified path does not exist.")

    if safe_path.is_dir():
        raise IsADirectoryError("The specified path is a directory.")

    file_size = safe_path.stat().st_size

    if file_size > MAX_FILE_SIZE_TO_READ:
        raise ValueError(
            f"File size exceeds the maximum allowed size of "
            f"{MAX_FILE_SIZE_TO_READ} bytes."
        )

    try:
        return safe_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("File content is not valid UTF-8.") from exc


def write_file(workspace: Path, user_path: str, content: str) -> None:
    """Atomically write UTF-8 text content to a file inside the workspace."""

    if not isinstance(content, str):
        raise TypeError("content must be a string.")

    safe_path = resolve_safe_path(workspace, user_path)

    if safe_path.exists() and safe_path.is_dir():
        raise IsADirectoryError("The specified path is a directory.")

    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=safe_path.parent,
        prefix=f".{safe_path.name}.",
        suffix=".tmp",
    )

    temporary_file = None

    try:
        temporary_file = os.fdopen(
            file_descriptor,
            mode="w",
            encoding="utf-8",
            newline="",
        )

        with temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, safe_path)

    except BaseException:
        if temporary_file is None:
            try:
                os.close(file_descriptor)
            except OSError:
                pass

        try:
            os.unlink(temporary_path)
        except OSError:
            pass

        raise


def get_file_info(workspace: Path, user_path: str) -> dict[str, str | int | None]:
    """Return metadata for a file or directory inside the workspace."""

    safe_path = resolve_safe_path(workspace, user_path)

    file_stat = safe_path.stat()

    if safe_path.is_dir():
        file_type = "directory"
        file_size = None
    elif safe_path.is_file():
        file_type = "file"
        file_size = file_stat.st_size
    else:
        raise ValueError("Unsupported filesystem entry type.")

    modified_at = datetime.fromtimestamp(
        file_stat.st_mtime,
        tz=UTC,
    ).isoformat()

    return {
        "name": safe_path.name,
        "type": file_type,
        "size": file_size,
        "modified_at": modified_at,
    }
