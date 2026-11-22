import pytest
from pydantic import ValidationError

from mcp_mastery.config.factory import get_settings
from mcp_mastery.config.settings import Settings


@pytest.fixture(autouse=True)
def configure_settings(monkeypatch):
    """Configure environment and clear settings cache."""

    monkeypatch.setenv("GROQ_API_KEY", "test-api-key")

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_settings(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.setenv("MCP_WORKSPACE", str(workspace))

    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.mcp_workspace == workspace.resolve()


def test_get_settings_returns_cached_instance(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.setenv("MCP_WORKSPACE", str(workspace))

    settings_a = get_settings()
    settings_b = get_settings()

    assert settings_a is settings_b


def test_get_settings_creates_new_instance_after_cache_clear(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.setenv("MCP_WORKSPACE", str(workspace))

    settings_a = get_settings()

    get_settings.cache_clear()

    settings_b = get_settings()

    assert settings_a is not settings_b
    assert settings_a.mcp_workspace == settings_b.mcp_workspace


def test_settings_rejects_non_existing_workspace(tmp_path):
    workspace = tmp_path / "nonexistent"

    with pytest.raises(ValidationError):
        Settings(mcp_workspace=workspace)


def test_settings_rejects_file_as_workspace(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Hello", encoding="utf-8")

    with pytest.raises(ValidationError):
        Settings(mcp_workspace=file_path)


def test_settings_expands_home_directory(tmp_path, monkeypatch):
    home = tmp_path / "home"
    workspace = home / "workspace"
    workspace.mkdir(parents=True)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("MCP_WORKSPACE", "~/workspace")

    settings = get_settings()

    assert settings.mcp_workspace == workspace.resolve()


def test_settings_default_groq_model_name(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    settings = Settings(
        mcp_workspace=workspace,
        groq_api_key="test-api-key",
    )

    assert settings.groq_model_name == "openai/gpt-oss-120b"


def test_settings_default_temperature(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    settings = Settings(
        mcp_workspace=workspace,
        groq_api_key="test-api-key",
    )

    assert settings.temperature == 0.0


def test_settings_groq_api_key_is_secret(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    settings = Settings(
        mcp_workspace=workspace,
        groq_api_key="test-api-key",
    )

    assert settings.groq_api_key.get_secret_value() == "test-api-key"
    assert str(settings.groq_api_key) == "**********"
