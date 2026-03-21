"""Configuration management for pytest-doctor."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class IgnoreConfig:
    """Configuration for ignored rules and files."""

    # Default patterns to ignore (virtual environments, build artifacts, etc.)
    DEFAULT_IGNORE_FILES: list[str] = field(
        default_factory=lambda: [
            ".venv/**",
            "venv/**",
            ".env/**",
            "env/**",
            ".tox/**",
            "tox/**",
            ".eggs/**",
            "eggs/**",
            "*.egg-info/**",
            "build/**",
            "dist/**",
            ".pytest_cache/**",
            ".mypy_cache/**",
            ".ruff_cache/**",
            "node_modules/**",
            ".git/**",
            ".hg/**",
            ".svn/**",
            "__pycache__/**",
        ],
        init=False,
    )

    rules: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Merge user-provided patterns with defaults."""
        # Start with default patterns
        default_patterns = [
            ".venv/**",
            "venv/**",
            ".env/**",
            "env/**",
            ".tox/**",
            "tox/**",
            ".eggs/**",
            "eggs/**",
            "*.egg-info/**",
            "build/**",
            "dist/**",
            ".pytest_cache/**",
            ".mypy_cache/**",
            ".ruff_cache/**",
            "node_modules/**",
            ".git/**",
            ".hg/**",
            ".svn/**",
            "__pycache__/**",
        ]

        # Add user-provided patterns (avoiding duplicates)
        user_patterns = set(self.files)
        self.files = default_patterns + [p for p in user_patterns if p not in default_patterns]

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> IgnoreConfig:
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(
            rules=data.get("rules", []),
            files=data.get("files", []),
        )


@dataclass
class Config:
    """Main configuration for pytest-doctor."""

    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    lint: bool = True
    dead_code: bool = True
    test_analysis: bool = True
    verbose: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Config:
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(
            ignore=IgnoreConfig.from_dict(data.get("ignore")),
            lint=data.get("lint", True),
            dead_code=data.get("deadCode", True),
            test_analysis=data.get("testAnalysis", True),
            verbose=data.get("verbose", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ignore": {
                "rules": self.ignore.rules,
                "files": self.ignore.files,
            },
            "lint": self.lint,
            "deadCode": self.dead_code,
            "testAnalysis": self.test_analysis,
            "verbose": self.verbose,
        }


def load_config(
    path: str | Path,
    verbose: bool | None = None,
    fix: bool | None = None,
    diff: str | None = None,
) -> Config:
    """
    Load configuration from files and CLI flags.

    Configuration precedence:
    1. CLI flags (highest priority)
    2. pytest-doctor.config.json file
    3. pyproject.toml [tool.pytest-doctor] section
    4. Default configuration (lowest priority)

    Args:
        path: Directory to search for config files
        verbose: CLI --verbose flag override
        fix: CLI --fix flag override (not used in config, for CLI only)
        diff: CLI --diff flag override (not used in config, for CLI only)

    Returns:
        Merged configuration with CLI flags taking precedence
    """
    config_dir = Path(path)

    # Start with defaults
    config = Config()

    # Try to load from pytest-doctor.config.json
    json_config_path = config_dir / "pytest-doctor.config.json"
    if json_config_path.exists():
        config_data = json.loads(json_config_path.read_text())
        config = Config.from_dict(config_data)

    # Try to load from pyproject.toml
    pyproject_path = config_dir / "pyproject.toml"
    if pyproject_path.exists():
        toml_data = tomllib.loads(pyproject_path.read_text())
        pytest_doctor_config = toml_data.get("tool", {}).get("pytest-doctor")
        if pytest_doctor_config:
            # Merge with existing config (pyproject.toml overrides json config)
            pyproject_config = Config.from_dict(pytest_doctor_config)
            # Only override if explicitly set in pyproject
            config = Config(
                ignore=pyproject_config.ignore or config.ignore,
                lint=pyproject_config.lint,
                dead_code=pyproject_config.dead_code,
                test_analysis=pyproject_config.test_analysis,
                verbose=pyproject_config.verbose or config.verbose,
            )

    # Apply CLI flag overrides (highest priority)
    if verbose is not None:
        config.verbose = verbose

    return config
