"""Tests for calculator with strong assertions."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import add, subtract, multiply, divide, is_positive


def test_add_positive_numbers():
    """Test add with two positive numbers - strong assertion."""
    result = add(2, 3)
    # Strong: exact value check
    assert result == 5


def test_add_negative_numbers():
    """Test add with negative numbers - strong assertion."""
    result = add(-2, -3)
    # Strong: exact value check
    assert result == -5


def test_subtract_positive():
    """Test subtract with positive result - strong assertion."""
    result = subtract(5, 3)
    # Strong: exact value check
    assert result == 2


def test_subtract_negative():
    """Test subtract with negative result - strong assertion."""
    result = subtract(3, 5)
    # Strong: exact value check
    assert result == -2


def test_multiply_positive():
    """Test multiply with positive numbers - strong assertion."""
    result = multiply(4, 5)
    # Strong: exact value check
    assert result == 20


def test_multiply_by_zero():
    """Test multiply by zero - strong assertion."""
    result = multiply(4, 0)
    # Strong: exact value check
    assert result == 0


def test_divide_positive():
    """Test divide with positive numbers - strong assertion."""
    result = divide(10.0, 2.0)
    # Strong: exact value check (with float tolerance)
    assert result == 5.0


def test_divide_by_zero_raises():
    """Test divide by zero raises exception - strong assertion."""
    # Strong: checks exception is raised
    with pytest.raises(ValueError):
        divide(10.0, 0.0)


def test_divide_by_negative_raises():
    """Test divide by negative raises exception - strong assertion."""
    # Strong: checks exception is raised for negative divisor
    with pytest.raises(ValueError):
        divide(10.0, -2.0)


def test_is_positive_true():
    """Test is_positive returns True for positive - strong assertion."""
    result = is_positive(5)
    # Strong: checks exact boolean value
    assert result is True


def test_is_positive_false():
    """Test is_positive returns False for zero - strong assertion."""
    result = is_positive(0)
    # Strong: checks exact boolean value
    assert result is False


def test_is_positive_negative():
    """Test is_positive returns False for negative - strong assertion."""
    result = is_positive(-5)
    # Strong: checks exact boolean value
    assert result is False
