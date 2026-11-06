import ast
import math
import operator

from fastmcp import FastMCP

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

MAX_EXPRESSION_LENGTH = 256
MAX_AST_DEPTH = 20
MAX_INTEGER_BITS = 4096
MAX_EXPONENT = 100


def evaluate_expression(expression: str) -> int | float:
    """Safely evaluate a mathematical expression using an AST whitelist."""

    if not isinstance(expression, str):
        raise TypeError("Expression must be a string.")

    if not expression.strip():
        raise ValueError("Expression cannot be empty.")

    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid mathematical expression.") from exc

    def validate_result(value: int | float) -> int | float:
        if type(value) not in (int, float):
            raise ValueError("Only numeric results are allowed.")

        if isinstance(value, int) and value.bit_length() > MAX_INTEGER_BITS:
            raise ValueError("Result is too large.")

        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Result is not finite.")

        return value

    def evaluate(node: ast.AST, depth: int = 0) -> int | float:
        if depth > MAX_AST_DEPTH:
            raise ValueError("Expression is too complex.")

        if isinstance(node, ast.Expression):
            return evaluate(node.body, depth + 1)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numeric values are allowed.")

            return validate_result(node.value)

        if isinstance(node, ast.BinOp):
            operator_function = BINARY_OPERATORS.get(type(node.op))

            if operator_function is None:
                raise ValueError("Unsupported binary operator.")

            left = evaluate(node.left, depth + 1)
            right = evaluate(node.right, depth + 1)

            if isinstance(node.op, ast.Pow):
                if abs(right) > MAX_EXPONENT:
                    raise ValueError("Exponent is too large.")

            if (
                isinstance(node.op, ast.Mult)
                and isinstance(left, int)
                and isinstance(right, int)
                and left.bit_length() + right.bit_length() > MAX_INTEGER_BITS + 1
            ):
                raise ValueError("Result is too large.")

            try:
                result = operator_function(left, right)
            except (ZeroDivisionError, OverflowError, ValueError) as exc:
                raise ValueError("Invalid mathematical operation.") from exc

            return validate_result(result)

        if isinstance(node, ast.UnaryOp):
            operator_function = UNARY_OPERATORS.get(type(node.op))

            if operator_function is None:
                raise ValueError("Unsupported unary operator.")

            result = operator_function(evaluate(node.operand, depth + 1))

            return validate_result(result)

        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    return evaluate(tree)


def register(mcp: FastMCP) -> None:
    """Register calculation tools."""

    @mcp.tool()
    def calculate(expression: str) -> int | float:
        """Evaluate a mathematical expression safely."""
        return evaluate_expression(expression)
