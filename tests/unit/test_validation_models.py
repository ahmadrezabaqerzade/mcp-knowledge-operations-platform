import pytest
from pydantic import ValidationError

from mcp_mastery.operations_server.validation.models import UserProfile


def test_valid_user_profile() -> None:
    profile = UserProfile(
        username="ahmadreza",
        age=25,
        is_active=True,
    )

    assert profile.username == "ahmadreza"
    assert profile.age == 25
    assert profile.is_active is True


@pytest.mark.parametrize("username", ["ab", "a" * 31])
def test_invalid_username_length(username: str) -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            username=username,
            age=25,
            is_active=True,
        )


@pytest.mark.parametrize("age", [17, 121])
def test_invalid_age_range(age: int) -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            username="ahmadreza",
            age=age,
            is_active=True,
        )


def test_strict_integer_validation() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            username="ahmadreza",
            age="25",
            is_active=True,
        )


def test_strict_boolean_validation() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            username="ahmadreza",
            age=25,
            is_active="true",
        )


def test_extra_fields_are_forbidden() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            username="ahmadreza",
            age=25,
            is_active=True,
            email="ahmad@example.com",
        )


@pytest.mark.parametrize(
    "missing_field",
    ["username", "age", "is_active"],
)
def test_required_fields(missing_field: str) -> None:
    data: dict[str, object] = {
        "username": "ahmadreza",
        "age": 25,
        "is_active": True,
    }
    del data[missing_field]

    with pytest.raises(ValidationError):
        UserProfile.model_validate(data)
