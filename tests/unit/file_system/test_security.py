from pathlib import Path

import pytest

from mcp_mastery.operations_server.file_system.security import (
    resolve_safe_path,
)


@pytest.mark.parametrize(
    "user_path",
    [
        pytest.param(
            "notes.txt",
            id="existing_file_inside_workspace",
        ),
        pytest.param(
            "documents/notes.txt",
            id="nested_file_path",
        ),
        pytest.param(
            "new_file.txt",
            id="non_existing_file_inside_workspace",
        ),
    ],
)
def test_valid_path(user_path: str, tmp_path: Path) -> None:
    if user_path != "new_file.txt":
        file_path = tmp_path / user_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("Test content", encoding="utf-8")

    expected_path = (tmp_path.resolve(strict=True) / user_path).resolve()

    assert resolve_safe_path(tmp_path, user_path) == expected_path


@pytest.mark.parametrize(
    "invalid_input, expected_exception",
    [
        pytest.param("", ValueError, id="empty_string"),
        pytest.param("   ", ValueError, id="whitespace_only"),
        pytest.param(None, TypeError, id="none_input"),
        pytest.param(123, TypeError, id="integer_input"),
        pytest.param("/etc/passwd", ValueError, id="absolute_path"),
        pytest.param("../secret.txt", ValueError, id="parent_directory_traversal"),
        pytest.param(
            "documents/../../secret.txt",
            ValueError,
            id="nested_directory_traversal",
        ),
    ],
)
def test_invalid_path(
    invalid_input: object,
    expected_exception: type[Exception],
    tmp_path: Path,
) -> None:
    with pytest.raises(expected_exception):
        resolve_safe_path(tmp_path, invalid_input)


def test_path_with_symlink_outside_workspace(tmp_path: Path) -> None:
    outside_directory = tmp_path.parent / "outside"
    outside_directory.mkdir(exist_ok=True)

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    symlink = workspace / "external_link"

    try:
        symlink.symlink_to(outside_directory, target_is_directory=True)
    except OSError:
        pytest.skip("Unable to create symlinks on this system.")

    with pytest.raises(ValueError, match="outside the workspace"):
        resolve_safe_path(workspace, "external_link/secret.txt")


def test_non_existing_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "nonexistent"

    with pytest.raises(ValueError):
        resolve_safe_path(workspace, "notes.txt")


def test_workspace_is_file(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace.txt"
    workspace.write_text("Not a directory", encoding="utf-8")

    with pytest.raises(ValueError, match="Workspace must be an existing directory"):
        resolve_safe_path(workspace, "notes.txt")
