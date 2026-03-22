"""Tests for configuration module."""

import json
from pathlib import Path

from pytest_doctor.config import Config, IgnoreConfig, load_config


class TestIgnoreConfig:
    """Tests for IgnoreConfig."""

    def test_ignore_config_defaults(self) -> None:
        """Test default IgnoreConfig includes default patterns."""
        config = IgnoreConfig()
        assert config.rules == []
        # Should include default patterns like .venv, build, etc.
        assert ".venv/**" in config.files
        assert ".pytest_cache/**" in config.files
        assert len(config.files) > 10  # Multiple defaults

    def test_ignore_config_creation_with_rules(self) -> None:
        """Test IgnoreConfig creation with rules."""
        config = IgnoreConfig(rules=["E501", "W503"])
        assert config.rules == ["E501", "W503"]

    def test_ignore_config_creation_with_files(self) -> None:
        """Test IgnoreConfig creation with custom files."""
        config = IgnoreConfig(files=["custom/**"])
        assert "custom/**" in config.files
        # Should also include defaults
        assert ".venv/**" in config.files

    def test_ignore_config_from_dict(self) -> None:
        """Test creating IgnoreConfig from dictionary includes defaults."""
        data = {
            "rules": ["E501", "W503"],
            "files": ["tests/legacy/**"],
        }
        config = IgnoreConfig.from_dict(data)
        assert config.rules == ["E501", "W503"]
        # Should include both user patterns and defaults
        assert "tests/legacy/**" in config.files
        assert ".venv/**" in config.files
        assert len(config.files) > 10

    def test_ignore_config_from_empty_dict(self) -> None:
        """Test creating IgnoreConfig from empty dict includes defaults."""
        config = IgnoreConfig.from_dict({})
        assert config.rules == []
        # Should include default patterns
        assert ".venv/**" in config.files
        assert len(config.files) > 10

    def test_ignore_config_from_none(self) -> None:
        """Test creating IgnoreConfig from None includes defaults."""
        config = IgnoreConfig.from_dict(None)
        assert config.rules == []
        # Should include default patterns
        assert ".venv/**" in config.files
        assert len(config.files) > 10


class TestConfig:
    """Tests for Config."""

    def test_config_defaults(self) -> None:
        """Test default Config."""
        config = Config()
        assert config.lint is True
        assert config.dead_code is True
        assert config.test_analysis is True
        assert config.verbose is False
        assert config.ignore.rules == []
        # Default ignore patterns should be included
        assert ".venv/**" in config.ignore.files
        assert len(config.ignore.files) > 10

    def test_config_from_dict(self) -> None:
        """Test creating Config from dictionary."""
        data = {
            "lint": False,
            "deadCode": False,
            "testAnalysis": True,
            "verbose": True,
            "ignore": {
                "rules": ["E501"],
                "files": ["tests/**"],
            },
        }
        config = Config.from_dict(data)
        assert config.lint is False
        assert config.dead_code is False
        assert config.test_analysis is True
        assert config.verbose is True
        assert config.ignore.rules == ["E501"]
        # Should include both user patterns and defaults
        assert "tests/**" in config.ignore.files
        assert ".venv/**" in config.ignore.files
        assert len(config.ignore.files) > 10

    def test_config_from_empty_dict(self) -> None:
        """Test creating Config from empty dict returns defaults."""
        config = Config.from_dict({})
        assert config.lint is True
        assert config.dead_code is True
        assert config.test_analysis is True
        assert config.verbose is False

    def test_config_from_none(self) -> None:
        """Test creating Config from None returns defaults."""
        config = Config.from_dict(None)
        assert config.lint is True
        assert config.dead_code is True
        assert config.test_analysis is True
        assert config.verbose is False

    def test_config_to_dict(self) -> None:
        """Test converting Config to dictionary."""
        config = Config(
            lint=False,
            dead_code=True,
            test_analysis=False,
            verbose=True,
        )
        result = config.to_dict()
        assert result["lint"] is False
        assert result["deadCode"] is True
        assert result["testAnalysis"] is False
        assert result["verbose"] is True

    def test_config_to_dict_with_ignore(self) -> None:
        """Test converting Config with ignore rules to dict."""
        config = Config(
            ignore=IgnoreConfig(rules=["E501"], files=["tests/**"]),
            lint=True,
            dead_code=False,
            test_analysis=True,
            verbose=False,
        )
        result = config.to_dict()
        assert result["ignore"]["rules"] == ["E501"]
        assert "tests/**" in result["ignore"]["files"]
        assert ".venv/**" in result["ignore"]["files"]


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_defaults(self, tmp_path: Path) -> None:
        """Test loading config with no config files."""
        config = load_config(tmp_path)
        assert config.lint is True
        assert config.dead_code is True
        assert config.test_analysis is True
        assert config.verbose is False

    def test_load_config_from_json(self, tmp_path: Path) -> None:
        """Test loading config from pytest-doctor.config.json."""
        config_file = tmp_path / "pytest-doctor.config.json"
        config_file.write_text(
            json.dumps(
                {
                    "lint": False,
                    "deadCode": True,
                    "verbose": True,
                }
            )
        )

        config = load_config(tmp_path)
        assert config.lint is False
        assert config.dead_code is True
        assert config.verbose is True

    def test_load_config_from_pyproject_toml(self, tmp_path: Path) -> None:
        """Test loading config from pyproject.toml."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.pytest-doctor]
lint = false
deadCode = true
testAnalysis = false
verbose = true
""")

        config = load_config(tmp_path)
        assert config.lint is False
        assert config.dead_code is True
        assert config.test_analysis is False
        assert config.verbose is True

    def test_load_config_cli_flag_override(self, tmp_path: Path) -> None:
        """Test that CLI flags override config files."""
        config_file = tmp_path / "pytest-doctor.config.json"
        config_file.write_text(json.dumps({"verbose": False}))

        config = load_config(tmp_path, verbose=True)
        assert config.verbose is True

    def test_load_config_json_overrides_defaults(self, tmp_path: Path) -> None:
        """Test that JSON config merges with default patterns."""
        config_file = tmp_path / "pytest-doctor.config.json"
        config_file.write_text(
            json.dumps(
                {
                    "ignore": {"rules": ["E501"], "files": ["legacy/**"]},
                }
            )
        )

        config = load_config(tmp_path)
        assert config.ignore.rules == ["E501"]
        # Should include both user patterns and defaults
        assert "legacy/**" in config.ignore.files
        assert ".venv/**" in config.ignore.files
        assert len(config.ignore.files) > 10

    def test_load_config_with_string_path(self, tmp_path: Path) -> None:
        """Test that load_config accepts string paths."""
        config = load_config(str(tmp_path))
        assert config is not None
        assert config.lint is True

    def test_load_config_pyproject_overrides_json(self, tmp_path: Path) -> None:
        """Test that pyproject.toml overrides JSON config."""
        # Create JSON config
        json_file = tmp_path / "pytest-doctor.config.json"
        json_file.write_text(json.dumps({"lint": True, "verbose": False}))

        # Create pyproject.toml config that should override
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.pytest-doctor]
lint = false
verbose = true
""")

        config = load_config(tmp_path)
        # pyproject.toml should win for these fields
        assert config.lint is False
        assert config.verbose is True

    def test_load_config_with_ignore_config(self, tmp_path: Path) -> None:
        """Test loading ignore configuration from pyproject.toml merges with defaults."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.pytest-doctor.ignore]
rules = ["E501", "W503"]
files = ["tests/legacy/**", "src/old/**"]
""")

        config = load_config(tmp_path)
        assert config.ignore.rules == ["E501", "W503"]
        # Should include both user patterns and defaults
        assert "tests/legacy/**" in config.ignore.files
        assert "src/old/**" in config.ignore.files
        assert ".venv/**" in config.ignore.files
        assert len(config.ignore.files) > 10

    def test_load_config_with_assertion_quality(self, tmp_path: Path) -> None:
        """Test loading config with assertion quality settings."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.pytest-doctor]
assertionQuality = true
mutationDepth = "deep"
mutationTimeoutMs = 10000
""")

        config = load_config(tmp_path)
        assert config.assertion_quality is True
        assert config.mutation_depth == "deep"
        assert config.mutation_timeout_ms == 10000

    def test_load_config_assertion_quality_disabled_by_default(self, tmp_path: Path) -> None:
        """Test that assertion quality is disabled by default."""
        config = load_config(tmp_path)
        assert config.assertion_quality is False
        assert config.mutation_depth == "standard"
        assert config.mutation_timeout_ms == 5000

    def test_config_mutation_depth_validation(self) -> None:
        """Test mutation depth validation."""
        # Valid values should work
        config = Config.from_dict({"mutationDepth": "light"})
        assert config.mutation_depth == "light"

        config = Config.from_dict({"mutationDepth": "standard"})
        assert config.mutation_depth == "standard"

        config = Config.from_dict({"mutationDepth": "deep"})
        assert config.mutation_depth == "deep"

        # Invalid value should default to "standard"
        config = Config.from_dict({"mutationDepth": "invalid"})
        assert config.mutation_depth == "standard"

    def test_config_from_dict_assertion_quality(self) -> None:
        """Test creating Config with assertion quality settings."""
        data = {
            "assertionQuality": True,
            "mutationDepth": "light",
            "mutationTimeoutMs": 8000,
        }
        config = Config.from_dict(data)
        assert config.assertion_quality is True
        assert config.mutation_depth == "light"
        assert config.mutation_timeout_ms == 8000

    def test_config_to_dict_assertion_quality(self) -> None:
        """Test converting Config to dict includes assertion quality."""
        config = Config(
            assertion_quality=True,
            mutation_depth="deep",
            mutation_timeout_ms=15000,
        )
        data = config.to_dict()
        assert data["assertionQuality"] is True
        assert data["mutationDepth"] == "deep"
        assert data["mutationTimeoutMs"] == 15000
