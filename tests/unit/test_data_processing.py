import pytest

from mcp_mastery.operations_server.tools.data_processing import (
    calculate_statistics,
)


def test_calculate_statistics() -> None:
    result = calculate_statistics([1, 2, 3, 4, 5])

    assert result["count"] == 5
    assert result["sum"] == 15.0
    assert result["mean"] == 3.0
    assert result["min"] == 1.0
    assert result["max"] == 5.0
    assert result["median"] == 3.0
    assert result["variance"] == 2.0
    assert result["standard_deviation"] == pytest.approx(1.41421356237)


def test_single_value() -> None:
    result = calculate_statistics([5])

    assert result == {
        "count": 1,
        "sum": 5.0,
        "mean": 5.0,
        "min": 5.0,
        "max": 5.0,
        "median": 5.0,
        "variance": 0.0,
        "standard_deviation": 0.0,
    }


def test_negative_numbers() -> None:
    result = calculate_statistics([-5, -3, -1])

    assert result["count"] == 3
    assert result["sum"] == -9.0
    assert result["mean"] == -3.0
    assert result["min"] == -5.0
    assert result["max"] == -1.0
    assert result["median"] == -3.0
    assert result["variance"] == pytest.approx(8 / 3)
    assert result["standard_deviation"] == pytest.approx((8 / 3) ** 0.5)


def test_float_numbers() -> None:
    result = calculate_statistics([1.5, 2.5, 3.5])

    assert result["count"] == 3
    assert result["sum"] == pytest.approx(7.5)
    assert result["mean"] == pytest.approx(2.5)
    assert result["median"] == pytest.approx(2.5)
    assert result["variance"] == pytest.approx(2 / 3)
    assert result["standard_deviation"] == pytest.approx((2 / 3) ** 0.5)


def test_population_variance() -> None:
    result = calculate_statistics([2, 4, 6, 8])

    # Population variance divides by N, not N - 1.
    assert result["variance"] == pytest.approx(5.0)


def test_exact_float64_integer_boundary() -> None:
    result = calculate_statistics([2**53])

    assert result["min"] == float(2**53)
    assert result["max"] == float(2**53)


@pytest.mark.parametrize(
    "numbers",
    [
        pytest.param([], id="empty-list"),
    ],
)
def test_empty_input(numbers: list[int | float]) -> None:
    with pytest.raises(ValueError, match="empty"):
        calculate_statistics(numbers)


@pytest.mark.parametrize(
    "numbers",
    [
        pytest.param(["hello"], id="string"),
        pytest.param([1, "2"], id="mixed-types"),
        pytest.param([True], id="boolean"),
        pytest.param([False, 1], id="mixed-boolean"),
        pytest.param([None], id="none"),
        pytest.param([complex(1, 2)], id="complex-number"),
    ],
)
def test_invalid_types(numbers: list) -> None:
    with pytest.raises(TypeError):
        calculate_statistics(numbers)


@pytest.mark.parametrize(
    "numbers",
    [
        pytest.param([float("nan")], id="nan"),
        pytest.param([float("inf")], id="positive-infinity"),
        pytest.param([float("-inf")], id="negative-infinity"),
        pytest.param([1, float("inf")], id="mixed-infinity"),
    ],
)
def test_non_finite_values(numbers: list[int | float]) -> None:
    with pytest.raises(ValueError, match="finite"):
        calculate_statistics(numbers)


def test_integer_outside_float64_exact_range() -> None:
    with pytest.raises(ValueError, match="exact float64 range"):
        calculate_statistics([10**20, 10**20 + 1])


@pytest.mark.parametrize(
    "numbers",
    [
        pytest.param([1e308, 1e308], id="sum-overflow"),
        pytest.param([1e308, -1e308], id="variance-overflow"),
    ],
)
def test_overflow(numbers: list[float]) -> None:
    with pytest.raises(ValueError, match="Unable to calculate"):
        calculate_statistics(numbers)
