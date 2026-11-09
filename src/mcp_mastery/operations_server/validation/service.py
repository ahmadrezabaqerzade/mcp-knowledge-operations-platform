from pydantic import ValidationError

from mcp_mastery.operations_server.validation.registry import SCHEMA_REGISTRY


def validate_data(
    schema_name: str,
    data: dict[str, object],
) -> dict[str, object]:
    """Validate data against a registered Pydantic schema."""

    model = SCHEMA_REGISTRY.get(schema_name)

    if model is None:
        return {
            "valid": False,
            "data": None,
            "errors": [
                {
                    "field": "schema_name",
                    "message": f"Unknown schema: {schema_name}",
                    "type": "unknown_schema",
                }
            ],
        }

    try:
        validated_model = model.model_validate(data)

        return {
            "valid": True,
            "data": validated_model.model_dump(),
            "errors": [],
        }

    except ValidationError as exc:
        validation_errors = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]

        return {
            "valid": False,
            "data": None,
            "errors": validation_errors,
        }
