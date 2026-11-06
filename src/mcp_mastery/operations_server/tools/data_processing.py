import numpy as np
from fastmcp import FastMCP

MAX_EXACT_INTEGER = 2**53


def calculate_statistics(
    numbers: list[int | float],
) -> dict[str, int | float]:
    """Calculate descriptive statistics for a list of numbers."""

    if not numbers:
        raise ValueError("Numbers cannot be empty.")

    if any(type(number) not in (int, float) for number in numbers):
        raise TypeError("All values must be integers or floats.")

    if any(
        isinstance(number, int) and abs(number) > MAX_EXACT_INTEGER
        for number in numbers
    ):
        raise ValueError("Integer values must be within the exact float64 range.")

    if any(isinstance(number, float) and not np.isfinite(number) for number in numbers):
        raise ValueError("All numbers must be finite.")

    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            values = np.array(numbers, dtype=np.float64)

            statistics = {
                "count": int(values.size),
                "sum": float(np.sum(values)),
                "mean": float(np.mean(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "variance": float(np.var(values)),
                "standard_deviation": float(np.std(values)),
            }

    except (FloatingPointError, OverflowError, ValueError) as exc:
        raise ValueError(
            "Unable to calculate finite statistics for these numbers."
        ) from exc

    for name, value in statistics.items():
        if isinstance(value, float) and not np.isfinite(value):
            raise ValueError(f"Calculated {name} is not a finite number.")

    return statistics


def register(mcp: FastMCP) -> None:
    """Register data processing tools."""

    @mcp.tool()
    def analyze_numbers(
        numbers: list[int | float],
    ) -> dict[str, int | float]:
        """Calculate descriptive statistics for a list of numbers."""
        return calculate_statistics(numbers)
