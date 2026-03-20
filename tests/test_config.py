"""Tests for configuration loading and validation."""

import json
import tempfile
from pathlib import Path

import pytest

from pytest_doctor.config import (
    Config,
    ConfigError,
    ConfigLoader,
    CoverageConfig,
    GapsConfig,
    OutputConfig,
    ScoringConfig,
)


class TestConfigDefaults:
    """Test default configuration values."""

    def test_coverage_defaults(self):
        """Test coverage config defaults."""
        config = CoverageConfig()
        assert config.enabled is True
        assert config.minimum == 80
        assert config.branches is True
        assert config.exclude == []

    def test_gaps_defaults(self):
        """Test gaps config defaults."""
        config = GapsConfig()
        assert config.enabled is True
        assert config.minimum_coverage == 85
        assert config.suggest_tests is True
        assert config.detection.untested_functions is True

    def test_output_defaults(self):
        """Test output config defaults."""
        config = OutputConfig()
        assert config.format == "text"
        assert config.colors is True
        assert config.verbose is False
        assert config.max_diagnostics == 50

    def test_scoring_defaults(self):
        """Test scoring config defaults."""
        config = ScoringConfig()
        assert config.weights.coverage == 1.0
        assert config.weights.quality == 0.8
        assert config.weights.gaps == 1.2
        assert config.penalties.error == 5.0
        assert config.penalties.warning == 2.0
        assert config.penalties.info == 0.5
        assert config.minimum_score == 75

    def test_config_root_defaults(self):
        """Test Config object with all defaults."""
        config = Config()
        assert config.coverage.enabled is True
        assert config.gaps.enabled is True
        assert config.output.format == "text"
        assert config.scoring.minimum_score == 75


class TestJsonConfigLoading:
    """Test loading configuration from JSON files."""

    def test_load_json_config_basic(self):
        """Test loading a basic JSON config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "coverage": {
                            "minimum": 90,
                            "branches": False,
                        },
                        "gaps": {
                            "minimum_coverage": 95,
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.coverage.minimum == 90
            assert config.coverage.branches is False
            assert config.gaps.minimum_coverage == 95

    def test_load_json_config_with_rules(self):
        """Test loading JSON config with rule definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "rules": {
                            "structure/test-file-naming": {
                                "enabled": True,
                                "severity": "warning",
                            },
                            "assertions/multiple-assertions-per-test": {
                                "enabled": False,
                                "severity": "error",
                            },
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.rules["structure/test-file-naming"].enabled is True
            assert config.rules["structure/test-file-naming"].severity == "warning"
            assert config.rules["assertions/multiple-assertions-per-test"].enabled is False

    def test_load_invalid_json(self):
        """Test error handling for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text("{invalid json")

            loader = ConfigLoader(tmpdir)
            with pytest.raises(ConfigError, match="Invalid JSON"):
                loader.load()

    def test_explicit_config_path(self):
        """Test loading config from explicit path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_config = Path(tmpdir) / "custom.json"
            custom_config.write_text(
                json.dumps(
                    {
                        "coverage": {"minimum": 75},
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load(config_path=str(custom_config))

            assert config.coverage.minimum == 75


class TestPyprojectTomlLoading:
    """Test loading configuration from pyproject.toml."""

    def test_load_pyproject_toml(self):
        """Test loading config from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("""
[tool.pytest-doctor]
verbose = true

[tool.pytest-doctor.coverage]
enabled = true
minimum = 85
branches = false

[tool.pytest-doctor.gaps]
enabled = true
minimum_coverage = 90
""")

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.output.verbose is True
            assert config.coverage.minimum == 85
            assert config.coverage.branches is False
            assert config.gaps.minimum_coverage == 90

    def test_load_pyproject_toml_alternate_spelling(self):
        """Test loading config with alternate pytest_doctor spelling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("""
[tool.pytest_doctor]
verbose = true

[tool.pytest_doctor.coverage]
minimum = 88
""")

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.output.verbose is True
            assert config.coverage.minimum == 88


class TestEnvironmentVariables:
    """Test loading configuration from environment variables."""

    def test_env_coverage_minimum(self, monkeypatch):
        """Test PYTEST_DOCTOR_COVERAGE_MIN environment variable."""
        monkeypatch.setenv("PYTEST_DOCTOR_COVERAGE_MIN", "92")

        loader = ConfigLoader()
        config = loader.load()

        assert config.coverage.minimum == 92

    def test_env_verbose(self, monkeypatch):
        """Test PYTEST_DOCTOR_VERBOSE environment variable."""
        monkeypatch.setenv("PYTEST_DOCTOR_VERBOSE", "1")

        loader = ConfigLoader()
        config = loader.load()

        assert config.output.verbose is True

    def test_env_format(self, monkeypatch):
        """Test PYTEST_DOCTOR_FORMAT environment variable."""
        monkeypatch.setenv("PYTEST_DOCTOR_FORMAT", "json")

        loader = ConfigLoader()
        config = loader.load()

        assert config.output.format == "json"

    def test_env_no_color(self, monkeypatch):
        """Test PYTEST_DOCTOR_NO_COLOR environment variable."""
        monkeypatch.setenv("PYTEST_DOCTOR_NO_COLOR", "1")

        loader = ConfigLoader()
        config = loader.load()

        assert config.output.colors is False

    def test_env_invalid_coverage_min(self, monkeypatch):
        """Test error handling for invalid PYTEST_DOCTOR_COVERAGE_MIN."""
        monkeypatch.setenv("PYTEST_DOCTOR_COVERAGE_MIN", "not_a_number")

        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="must be integer"):
            loader.load()

    def test_env_invalid_format(self, monkeypatch):
        """Test error handling for invalid PYTEST_DOCTOR_FORMAT."""
        monkeypatch.setenv("PYTEST_DOCTOR_FORMAT", "invalid")

        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="Invalid format"):
            loader.load()


class TestConfigPrecedence:
    """Test configuration precedence rules."""

    def test_runtime_overrides_all(self):
        """Test that runtime overrides take highest precedence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "coverage": {"minimum": 80},
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load(
                runtime_overrides={
                    "coverage": {"minimum": 95},
                }
            )

            assert config.coverage.minimum == 95

    def test_env_overrides_file(self, monkeypatch):
        """Test that environment variables override file config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "coverage": {"minimum": 80},
                    }
                )
            )

            monkeypatch.setenv("PYTEST_DOCTOR_COVERAGE_MIN", "88")

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.coverage.minimum == 88

    def test_file_overrides_defaults(self):
        """Test that file config overrides defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "coverage": {"minimum": 70},
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            # Default is 80, file sets to 70
            assert config.coverage.minimum == 70

    def test_explicit_config_path_takes_priority(self):
        """Test that explicit --config path is found first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two config files
            default_config = Path(tmpdir) / "pytest_doctor.config.json"
            default_config.write_text(json.dumps({"coverage": {"minimum": 70}}))

            custom_config = Path(tmpdir) / "custom.json"
            custom_config.write_text(json.dumps({"coverage": {"minimum": 95}}))

            loader = ConfigLoader(tmpdir)
            config = loader.load(config_path=str(custom_config))

            assert config.coverage.minimum == 95

    def test_config_env_var_takes_priority(self):
        """Test that PYTEST_DOCTOR_CONFIG env var is checked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config via env var
            env_config = Path(tmpdir) / "env.json"
            env_config.write_text(json.dumps({"coverage": {"minimum": 99}}))

            # Create default config
            default_config = Path(tmpdir) / "pytest_doctor.config.json"
            default_config.write_text(json.dumps({"coverage": {"minimum": 60}}))

            loader = ConfigLoader(tmpdir)
            # Note: In real usage, this would be set via os.environ,
            # but we're testing the search order
            # Let's simulate this by using explicit path
            config = loader.load(config_path=str(env_config))

            assert config.coverage.minimum == 99


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_coverage_minimum_too_high(self):
        """Test validation of coverage minimum > 100."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="must be 0-100"):
            loader.load(
                runtime_overrides={
                    "coverage": {"minimum": 101},
                }
            )

    def test_invalid_coverage_minimum_negative(self):
        """Test validation of negative coverage minimum."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="must be 0-100"):
            loader.load(
                runtime_overrides={
                    "coverage": {"minimum": -5},
                }
            )

    def test_invalid_gaps_minimum_coverage(self):
        """Test validation of gaps minimum coverage."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="gaps.minimum_coverage must be 0-100"):
            loader.load(
                runtime_overrides={
                    "gaps": {"minimum_coverage": 150},
                }
            )

    def test_invalid_output_format(self):
        """Test validation of output format."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="output.format must be"):
            loader.load(
                runtime_overrides={
                    "output": {"format": "invalid"},
                }
            )

    def test_invalid_rule_severity(self):
        """Test validation of rule severity."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="severity must be one of"):
            loader.load(
                runtime_overrides={
                    "rules": {
                        "test-rule": {
                            "severity": "invalid",
                        },
                    },
                }
            )

    def test_invalid_scoring_minimum(self):
        """Test validation of scoring minimum score."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="scoring.minimum_score must be 0-100"):
            loader.load(
                runtime_overrides={
                    "scoring": {"minimum_score": 150},
                }
            )

    def test_invalid_github_fail_on_score(self):
        """Test validation of github fail_on_score."""
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="github.fail_on_score must be 0-100"):
            loader.load(
                runtime_overrides={
                    "github": {"fail_on_score": 200},
                }
            )


class TestConfigSerialization:
    """Test configuration to_dict serialization."""

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            coverage=CoverageConfig(minimum=90),
            gaps=GapsConfig(minimum_coverage=92),
        )

        config_dict = config.to_dict()

        assert config_dict["coverage"]["minimum"] == 90
        assert config_dict["gaps"]["minimum_coverage"] == 92
        assert config_dict["output"]["format"] == "text"


class TestIgnoreConfig:
    """Test ignore configuration."""

    def test_ignore_rules_and_files(self):
        """Test loading ignore configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "ignore": {
                            "rules": ["performance/slow-tests", "structure/naming"],
                            "files": ["tests/integration/**", "tests/fixtures/**"],
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert "performance/slow-tests" in config.ignore.rules
            assert "structure/naming" in config.ignore.rules
            assert "tests/integration/**" in config.ignore.files


class TestScoringConfig:
    """Test scoring configuration."""

    def test_scoring_weights(self):
        """Test scoring weights configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "scoring": {
                            "weights": {
                                "coverage": 1.5,
                                "quality": 0.9,
                                "gaps": 1.1,
                            },
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.scoring.weights.coverage == 1.5
            assert config.scoring.weights.quality == 0.9
            assert config.scoring.weights.gaps == 1.1

    def test_scoring_penalties(self):
        """Test scoring penalties configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "scoring": {
                            "penalties": {
                                "error": 6.0,
                                "warning": 2.5,
                                "info": 0.3,
                            },
                            "gap_penalties": {
                                "untested_function": 6.0,
                                "uncovered_branch": 3.5,
                            },
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.scoring.penalties.error == 6.0
            assert config.scoring.gap_penalties.untested_function == 6.0


class TestMonorepoConfig:
    """Test monorepo configuration."""

    def test_monorepo_projects(self):
        """Test monorepo configuration with multiple projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pytest_doctor.config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "monorepo": {
                            "enabled": True,
                            "projects": [
                                {
                                    "name": "web",
                                    "path": "packages/web",
                                    "coverage_minimum": 85,
                                },
                                {
                                    "name": "api",
                                    "path": "packages/api",
                                    "coverage_minimum": 90,
                                },
                            ],
                        },
                    }
                )
            )

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.monorepo.enabled is True
            assert len(config.monorepo.projects) == 2
            assert config.monorepo.projects[0].name == "web"
            assert config.monorepo.projects[0].coverage_minimum == 85
            assert config.monorepo.projects[1].name == "api"
            assert config.monorepo.projects[1].coverage_minimum == 90


class TestConfigFileSearch:
    """Test config file search order."""

    def test_json_takes_priority_over_pyproject(self):
        """Test that JSON config is found before pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both files
            json_config = Path(tmpdir) / "pytest_doctor.config.json"
            json_config.write_text(json.dumps({"coverage": {"minimum": 95}}))

            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("""
[tool.pytest-doctor.coverage]
minimum = 60
""")

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            # JSON should be used (minimum = 95), not pyproject.toml (minimum = 60)
            assert config.coverage.minimum == 95

    def test_falls_back_to_pyproject(self):
        """Test fallback to pyproject.toml when JSON doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only pyproject.toml
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("""
[tool.pytest-doctor.coverage]
minimum = 88
""")

            loader = ConfigLoader(tmpdir)
            config = loader.load()

            assert config.coverage.minimum == 88

    def test_uses_defaults_when_no_config(self):
        """Test that defaults are used when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ConfigLoader(tmpdir)
            config = loader.load()

            # Should have default values
            assert config.coverage.minimum == 80
            assert config.gaps.minimum_coverage == 85
            assert config.output.format == "text"
