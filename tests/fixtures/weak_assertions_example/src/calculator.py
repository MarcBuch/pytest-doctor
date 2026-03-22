"""Simple calculator with weak assertions in tests."""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide two numbers (with weak boundary check)."""
    if b <= 0:
        return 0.0
    return a / b


def is_positive(n: int) -> bool:
    """Check if number is positive."""
    return n > 0
