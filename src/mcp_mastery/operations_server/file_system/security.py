from pathlib import Path


def resolve_safe_path(workspace: Path, user_path: str) -> Path:
    """Resolve a user-provided path while enforcing workspace boundaries."""

    if not isinstance(workspace, Path):
        raise TypeError("workspace must be a pathlib.Path instance.")

    if not isinstance(user_path, str):
        raise TypeError("user_path must be a string.")

    if not user_path or not user_path.strip():
        raise ValueError("user_path cannot be empty.")

    requested_path = Path(user_path)

    if requested_path.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    if ".." in requested_path.parts:
        raise ValueError("Path traversal is not allowed.")

    try:
        resolved_workspace = workspace.resolve(strict=True)
        resolved_path = (resolved_workspace / requested_path).resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Unable to resolve the requested path.") from exc

    if not resolved_workspace.is_dir():
        raise ValueError("Workspace must be an existing directory.")

    if not resolved_path.is_relative_to(resolved_workspace):
        raise ValueError("Access outside the workspace is not allowed.")

    return resolved_path
