import pytest

from mcp_mastery.operations_server.validation.service import validate_data


def test_validate_valid_data() -> None:
    result = validate_data(
        "user_profile",
        {
            "username": "ahmadreza",
            "age": 25,
            "is_active": True,
        },
    )

    assert result["valid"] is True
    assert result["data"] == {
        "username": "ahmadreza",
        "age": 25,
        "is_active": True,
    }
    assert result["errors"] == []


def test_validate_invalid_data() -> None:
    result = validate_data(
        "user_profile",
        {
            "username": "ab",
            "age": 15,
            "is_active": True,
        },
    )

    assert result["valid"] is False
    assert result["data"] is None
    assert len(result["errors"]) == 2

    errors = result["errors"]
    assert isinstance(errors, list)

    assert errors[0]["field"] == "username"
    assert errors[0]["type"] == "string_too_short"

    assert errors[1]["field"] == "age"
    assert errors[1]["type"] == "greater_than_equal"


def test_validate_unknown_schema() -> None:
    result = validate_data("nonexistent_schema", {})

    assert result["valid"] is False
    assert result["data"] is None
    assert result["errors"] == [
        {
            "field": "schema_name",
            "message": "Unknown schema: nonexistent_schema",
            "type": "unknown_schema",
        }
    ]


def test_validate_multiple_errors() -> None:
    result = validate_data(
        "user_profile",
        {
            "username": "ab",
            "age": 15,
            "is_active": "yes",
        },
    )

    assert result["valid"] is False
    assert result["data"] is None
    assert len(result["errors"]) == 3

    errors = result["errors"]
    assert isinstance(errors, list)

    error_fields = {error["field"] for error in errors}
    error_types = {error["type"] for error in errors}

    assert error_fields == {"username", "age", "is_active"}
    assert error_types == {
        "string_too_short",
        "greater_than_equal",
        "bool_type",
    }


def test_validate_strict_types() -> None:
    result = validate_data(
        "user_profile",
        {
            "username": "ahmadreza",
            "age": "25",
            "is_active": True,
        },
    )

    assert result["valid"] is False
    assert result["data"] is None

    errors = result["errors"]
    assert isinstance(errors, list)
    assert len(errors) == 1
    assert errors[0]["field"] == "age"
    assert errors[0]["type"] == "int_type"


@pytest.mark.parametrize(
    "missing_field",
    ["username", "age", "is_active"],
)
def test_validate_missing_fields(missing_field: str) -> None:
    data: dict[str, object] = {
        "username": "ahmadreza",
        "age": 25,
        "is_active": True,
    }
    del data[missing_field]

    result = validate_data("user_profile", data)

    assert result["valid"] is False
    assert result["data"] is None

    errors = result["errors"]
    assert isinstance(errors, list)

    assert any(
        error["field"] == missing_field and error["type"] == "missing"
        for error in errors
    )


def test_error_response_does_not_expose_input() -> None:
    result = validate_data(
        "user_profile",
        {
            "username": "ab",
            "age": 15,
            "is_active": True,
        },
    )

    assert result["valid"] is False

    errors = result["errors"]
    assert isinstance(errors, list)

    for error in errors:
        assert "input" not in error
