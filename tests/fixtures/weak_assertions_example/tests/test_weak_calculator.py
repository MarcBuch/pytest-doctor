"""Tests for calculator with weak assertions."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import add, subtract, multiply, divide, is_positive


def test_add_basic():
    """Test add function - weak assertion."""
    result = add(2, 3)
    # Weak: only checks it's not None
    assert result is not None


def test_subtract_basic():
    """Test subtract function - weak assertion."""
    result = subtract(5, 3)
    # Weak: only checks positive
    assert result > 0


def test_multiply_basic():
    """Test multiply function - weak assertion."""
    result = multiply(4, 5)
    # Weak: only checks truthy
    assert result


def test_divide_positive():
    """Test divide with positive numbers - weak assertion."""
    result = divide(10.0, 2.0)
    # Weak: only checks >= 0
    assert result >= 0


def test_is_positive_true():
    """Test is_positive with positive number - weak assertion."""
    result = is_positive(5)
    # Weak: only checks it's truthy
    assert result


def test_is_positive_false():
    """Test is_positive with zero - weak assertion."""
    result = is_positive(0)
    # Weak: only checks it's falsy (doesn't verify it's exactly False)
    assert not result
