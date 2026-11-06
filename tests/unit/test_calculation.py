import pytest

from mcp_mastery.operations_server.tools.calculation import evaluate_expression


@pytest.mark.parametrize(
    "expression, expected",
    [
        pytest.param("1 + 100", 101, id="addition"),
        pytest.param("99 - 101", -2, id="subtraction"),
        pytest.param("100 * 10", 1000, id="multiplication"),
        pytest.param("100 / 2", 50.0, id="division"),
        pytest.param("100 // 3", 33, id="floor-division"),
        pytest.param("10 % 3", 1, id="modulo"),
        pytest.param("10 ** 2", 100, id="power"),
        pytest.param("-10 + 5", -5, id="unary-negative"),
        pytest.param("+10", 10, id="unary-positive"),
        pytest.param("10 + 5 * 2", 20, id="operator-precedence"),
        pytest.param("(10 + 5) * 2", 30, id="parentheses"),
    ],
)
def test_calculation(expression: str, expected: int | float) -> None:
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression",
    [
        pytest.param("", id="empty-expression"),
        pytest.param("   ", id="whitespace-expression"),
        pytest.param("10 +", id="invalid-syntax"),
        pytest.param("10 / 0", id="division-by-zero"),
        pytest.param("1e999", id="non-finite-float"),
        pytest.param("2 ** 101", id="exponent-too-large"),
        pytest.param("2 ** 5000", id="integer-too-large"),
        pytest.param("10 & 5", id="unsupported-binary-operator"),
        pytest.param("~10", id="unsupported-unary-operator"),
        pytest.param("__import__('os')", id="function-call"),
        pytest.param("x + 10", id="undefined-name"),
        pytest.param("'hello'", id="string-constant"),
    ],
)
def test_invalid_expressions(expression: str) -> None:
    with pytest.raises(ValueError):
        evaluate_expression(expression)


@pytest.mark.parametrize(
    "expression",
    [
        pytest.param(123, id="integer-input"),
        pytest.param(10.5, id="float-input"),
        pytest.param(None, id="none-input"),
        pytest.param(True, id="boolean-input"),
    ],
)
def test_invalid_input_type(expression: object) -> None:
    with pytest.raises(TypeError):
        evaluate_expression(expression)


def test_expression_too_long() -> None:
    expression = "1" * 257

    with pytest.raises(ValueError, match="too long"):
        evaluate_expression(expression)


def test_expression_too_complex() -> None:
    expression = "1" + " + 1" * 20

    with pytest.raises(ValueError, match="too complex"):
        evaluate_expression(expression)
