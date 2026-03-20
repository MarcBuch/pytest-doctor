"""Custom exceptions for pytest-doctor."""


class PytestDoctorError(Exception):
    """Base exception for pytest-doctor errors."""

    pass


class DirectoryNotFoundError(PytestDoctorError):
    """Raised when a required directory is not found."""

    pass


class InvalidConfigError(PytestDoctorError):
    """Raised when configuration is invalid."""

    pass


__all__ = [
    "PytestDoctorError",
    "DirectoryNotFoundError",
    "InvalidConfigError",
]
