"""Configuration loading and validation for pytest-doctor.

This module handles loading configuration from multiple sources with proper precedence:
1. Runtime arguments (highest priority)
2. Environment variables
3. Config files (pytest_doctor.config.json, pyproject.toml, setup.cfg)
4. Built-in defaults (lowest priority)
"""
# ruff: noqa: E712
# mypy: ignore-errors

import json
import os
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Optional


class ConfigError(Exception):
    """Configuration loading or validation error."""

    pass


@dataclass
class CoverageConfig:
    """Coverage analysis settings."""

    enabled: bool = True
    minimum: int = 80
    branches: bool = True
    exclude: list[str] = field(default_factory=list)


@dataclass
class GapDetectionConfig:
    """Gap detection sub-settings."""

    untested_functions: bool = True
    uncovered_branches: bool = True
    missing_exceptions: bool = True
    state_transitions: bool = True
    edge_cases: bool = True


@dataclass
class GapsConfig:
    """Gap detection settings."""

    enabled: bool = True
    detection: GapDetectionConfig = field(default_factory=GapDetectionConfig)
    minimum_coverage: int = 85
    suggest_tests: bool = True


@dataclass
class RuleConfig:
    """Individual rule configuration."""

    enabled: bool = True
    severity: str = "warning"  # error, warning, info
    # Additional rule-specific options are stored dynamically


@dataclass
class RulesConfig:
    """Rules configuration as a dict of rule_name -> RuleConfig."""

    _rules: dict[str, RuleConfig] = field(default_factory=dict)

    def __getitem__(self, key: str) -> RuleConfig:
        """Get rule config by name."""
        return self._rules.get(key, RuleConfig())

    def __setitem__(self, key: str, value: RuleConfig) -> None:
        """Set rule config by name."""
        self._rules[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if rule is configured."""
        return key in self._rules

    def items(self):
        """Return rule items."""
        return self._rules.items()

    def get(self, key: str, default: Optional[RuleConfig] = None) -> Optional[RuleConfig]:
        """Get rule config with default."""
        return self._rules.get(key, default)


@dataclass
class IgnoreConfig:
    """Ignore patterns configuration."""

    rules: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)


@dataclass
class ScoringWeights:
    """Scoring weights configuration."""

    coverage: float = 1.0
    quality: float = 0.8
    gaps: float = 1.2


@dataclass
class ScoringPenalties:
    """Scoring penalties configuration."""

    error: float = 5.0
    warning: float = 2.0
    info: float = 0.5


@dataclass
class GapPenalties:
    """Gap-specific penalties configuration."""

    untested_function: float = 5.0
    uncovered_branch: float = 3.0
    missing_exception: float = 4.0
    missing_edge_case: float = 1.0


@dataclass
class ScoringConfig:
    """Scoring algorithm customization."""

    weights: ScoringWeights = field(default_factory=ScoringWeights)
    penalties: ScoringPenalties = field(default_factory=ScoringPenalties)
    gap_penalties: GapPenalties = field(default_factory=GapPenalties)
    minimum_score: int = 75


@dataclass
class OutputConfig:
    """Output formatting options."""

    format: str = "text"  # text, json, html
    colors: bool = True
    verbose: bool = False
    show_metadata: bool = True
    max_diagnostics: int = 50


@dataclass
class GitHubConfig:
    """GitHub Actions integration settings."""

    post_comment: bool = True
    fail_on_score: int = 75
    fail_on_gaps: bool = True
    fail_on_errors: bool = True


@dataclass
class MonorepoProject:
    """Individual monorepo project configuration."""

    name: str
    path: str
    coverage_minimum: int = 80


@dataclass
class MonorepoConfig:
    """Monorepo project settings."""

    enabled: bool = False
    projects: list[MonorepoProject] = field(default_factory=list)


@dataclass
class Config:
    """Complete configuration object."""

    coverage: CoverageConfig = field(default_factory=CoverageConfig)
    gaps: GapsConfig = field(default_factory=GapsConfig)
    rules: RulesConfig = field(default_factory=RulesConfig)
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    monorepo: MonorepoConfig = field(default_factory=MonorepoConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary, excluding internal fields."""
        result = {}
        for key, value in asdict(self).items():
            if key == "rules":
                # Handle RulesConfig specially - it's a dict of rule configs
                result[key] = {k: asdict(v) for k, v in self.rules._rules.items()}
            else:
                result[key] = value
        return result


class ConfigLoader:
    """Load and merge configuration from multiple sources."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize config loader.

        Args:
            project_root: Root directory to search for config files.
                         Defaults to current working directory.
        """
        self.project_root = Path(project_root or os.getcwd())

    def load(
        self,
        config_path: Optional[str] = None,
        runtime_overrides: Optional[dict[str, Any]] = None,
    ) -> Config:
        """Load and merge configuration from all sources.

        Configuration precedence (highest to lowest):
        1. Runtime overrides (arguments)
        2. Environment variables
        3. Config file specified via --config flag
        4. Local config files (pytest_doctor.config.json, pyproject.toml, setup.cfg)
        5. Built-in defaults

        Args:
            config_path: Explicit path to config file to use.
            runtime_overrides: Dictionary of runtime configuration overrides.

        Returns:
            Merged Config object.

        Raises:
            ConfigError: If config file is invalid or required options are missing.
        """
        # Start with defaults
        config = Config()

        # Load from file sources in order of precedence
        file_config = self._load_from_files(config_path)
        if file_config:
            config = self._merge_configs(config, file_config)

        # Load from environment variables
        env_config = self._load_from_env()
        if env_config:
            config = self._merge_configs(config, env_config)

        # Apply runtime overrides (highest priority)
        if runtime_overrides:
            runtime_config = self._dict_to_config(runtime_overrides)
            config = self._merge_configs(config, runtime_config)

        # Validate final config
        self._validate_config(config)

        return config

    def _load_from_files(self, explicit_path: Optional[str] = None) -> Optional[Config]:
        """Load configuration from files.

        Search order:
        1. Path from PYTEST_DOCTOR_CONFIG environment variable
        2. Explicit path argument
        3. pytest_doctor.config.json in project root
        4. [tool.pytest-doctor] in pyproject.toml
        5. [tool.pytest_doctor] in pyproject.toml (alternate spelling)
        6. [pytest-doctor] in setup.cfg

        Args:
            explicit_path: Explicit path to config file.

        Returns:
            Parsed Config object or None if no config file found.

        Raises:
            ConfigError: If a config file is invalid.
        """
        config_paths = self._get_config_search_paths(explicit_path)

        for config_path in config_paths:
            if not config_path.exists():
                continue

            if config_path.suffix == ".json":
                return self._load_json_config(config_path)
            elif config_path.name == "pyproject.toml":
                return self._load_pyproject_toml(config_path)
            elif config_path.name == "setup.cfg":
                return self._load_setup_cfg(config_path)

        return None

    def _get_config_search_paths(self, explicit_path: Optional[str]) -> list[Path]:
        """Get list of config file paths to search in order.

        Args:
            explicit_path: Explicit path to prioritize.

        Returns:
            List of Path objects to search.
        """
        paths = []

        # 1. Explicit path argument
        if explicit_path:
            paths.append(Path(explicit_path))

        # 2. Environment variable
        env_config = os.environ.get("PYTEST_DOCTOR_CONFIG")
        if env_config:
            paths.append(Path(env_config))

        # 3. Local config files in project root
        paths.extend(
            [
                self.project_root / "pytest_doctor.config.json",
                self.project_root / "pyproject.toml",
                self.project_root / "setup.cfg",
            ]
        )

        return paths

    def _load_json_config(self, path: Path) -> Config:
        """Load JSON config file.

        Args:
            path: Path to JSON config file.

        Returns:
            Parsed Config object.

        Raises:
            ConfigError: If JSON is invalid.
        """
        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {path}: {e}") from e
        except OSError as e:
            raise ConfigError(f"Cannot read config file {path}: {e}") from e

        return self._dict_to_config(data)

    def _load_pyproject_toml(self, path: Path) -> Optional[Config]:
        """Load config from pyproject.toml.

        Args:
            path: Path to pyproject.toml file.

        Returns:
            Parsed Config object or None if no pytest-doctor config found.

        Raises:
            ConfigError: If TOML parsing fails.
        """
        try:
            import tomllib as tomllib_module  # Python 3.11+  # type: ignore[import,import-untyped]

            tomllib = tomllib_module
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                # If tomli is not available, skip pyproject.toml
                return None

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)  # type: ignore
        except Exception as e:
            raise ConfigError(f"Cannot read pyproject.toml {path}: {e}") from e

        # Look for [tool.pytest-doctor] or [tool.pytest_doctor]
        tool_config = data.get("tool", {})
        config_data = tool_config.get("pytest-doctor") or tool_config.get("pytest_doctor")

        if not config_data:
            return None

        return self._dict_to_config(config_data)

    def _load_setup_cfg(self, path: Path) -> Optional[Config]:
        """Load config from setup.cfg.

        Args:
            path: Path to setup.cfg file.

        Returns:
            Parsed Config object or None if no pytest-doctor config found.

        Raises:
            ConfigError: If setup.cfg parsing fails.
        """
        try:
            import configparser
        except ImportError:
            return None

        try:
            parser = configparser.ConfigParser()
            parser.read(path)
        except Exception as e:
            raise ConfigError(f"Cannot read setup.cfg {path}: {e}") from e

        if not parser.has_section("pytest-doctor"):
            return None

        # Convert setup.cfg section to dictionary
        data: dict[str, Any] = {}
        for key, value in parser.items("pytest-doctor"):
            # Handle list values (comma or newline separated)
            if key in ("exclude", "rules", "files"):
                data[key] = [v.strip() for v in value.split("\n") if v.strip()]
            elif value.lower() in ("true", "false"):
                data[key] = value.lower() == "true"
            elif value.isdigit():
                data[key] = int(value)
            else:
                data[key] = value

        return self._dict_to_config(data)

    def _load_from_env(self) -> Optional[Config]:
        """Load configuration from environment variables.

        Supported variables:
        - PYTEST_DOCTOR_COVERAGE_MIN: Minimum coverage percentage
        - PYTEST_DOCTOR_VERBOSE: Enable verbose output
        - PYTEST_DOCTOR_FORMAT: Output format
        - PYTEST_DOCTOR_NO_COLOR: Disable colors

        Returns:
            Config object with environment-based values or None if none set.
        """
        env_data: dict[str, Any] = {}

        # Coverage minimum
        if "PYTEST_DOCTOR_COVERAGE_MIN" in os.environ:
            try:
                coverage_min = int(os.environ["PYTEST_DOCTOR_COVERAGE_MIN"])
                env_data.setdefault("coverage", {})
                env_data["coverage"]["minimum"] = coverage_min
            except ValueError as e:
                raise ConfigError(
                    f"PYTEST_DOCTOR_COVERAGE_MIN must be integer, "
                    f"got: {os.environ['PYTEST_DOCTOR_COVERAGE_MIN']}"
                ) from e

        # Verbose output
        if "PYTEST_DOCTOR_VERBOSE" in os.environ:
            env_data.setdefault("output", {})
            env_data["output"]["verbose"] = os.environ["PYTEST_DOCTOR_VERBOSE"].lower() in (
                "1",
                "true",
                "yes",
            )

        # Output format
        if "PYTEST_DOCTOR_FORMAT" in os.environ:
            fmt = os.environ["PYTEST_DOCTOR_FORMAT"]
            if fmt not in ("text", "json", "html"):
                raise ConfigError(f"Invalid format: {fmt}. Must be text, json, or html")
            env_data.setdefault("output", {})
            env_data["output"]["format"] = fmt

        # Colors
        if "PYTEST_DOCTOR_NO_COLOR" in os.environ:
            env_data.setdefault("output", {})
            env_data["output"]["colors"] = False

        return self._dict_to_config(env_data) if env_data else None

    def _dict_to_config(self, data: dict[str, Any]) -> Config:  # noqa: C901
        """Convert dictionary to Config object.

        Args:
            data: Dictionary representation of config.

        Returns:
            Config object.

        Raises:
            ConfigError: If config is invalid.
        """
        config = Config()

        # Handle top-level verbose flag
        if "verbose" in data:
            config.output.verbose = data["verbose"]

        # Handle coverage config
        if "coverage" in data:
            coverage_data = data["coverage"]
            if isinstance(coverage_data, dict):
                config.coverage = CoverageConfig(
                    **self._filter_fields(coverage_data, CoverageConfig)
                )

        # Handle gaps config
        if "gaps" in data:
            gaps_data = data["gaps"]
            if isinstance(gaps_data, dict):
                gap_detection = gaps_data.get("detection", {})
                if isinstance(gap_detection, dict):
                    config.gaps.detection = GapDetectionConfig(
                        **self._filter_fields(gap_detection, GapDetectionConfig)
                    )
                config.gaps = GapsConfig(
                    **self._filter_fields(
                        {k: v for k, v in gaps_data.items() if k != "detection"}, GapsConfig
                    ),
                    detection=config.gaps.detection,
                )

        # Handle rules config
        if "rules" in data:
            rules_data = data["rules"]
            if isinstance(rules_data, dict):
                for rule_name, rule_config in rules_data.items():
                    if isinstance(rule_config, dict):
                        config.rules[rule_name] = RuleConfig(
                            **self._filter_fields(rule_config, RuleConfig)
                        )

        # Handle ignore config
        if "ignore" in data:
            ignore_data = data["ignore"]
            if isinstance(ignore_data, dict):
                config.ignore = IgnoreConfig(**self._filter_fields(ignore_data, IgnoreConfig))

        # Handle scoring config
        if "scoring" in data:
            scoring_data = data["scoring"]
            if isinstance(scoring_data, dict):
                weights = scoring_data.get("weights", {})
                if isinstance(weights, dict):
                    config.scoring.weights = ScoringWeights(
                        **self._filter_fields(weights, ScoringWeights)
                    )

                penalties = scoring_data.get("penalties", {})
                if isinstance(penalties, dict):
                    config.scoring.penalties = ScoringPenalties(
                        **self._filter_fields(penalties, ScoringPenalties)
                    )

                gap_penalties = scoring_data.get("gap_penalties", {})
                if isinstance(gap_penalties, dict):
                    config.scoring.gap_penalties = GapPenalties(
                        **self._filter_fields(gap_penalties, GapPenalties)
                    )

                # Handle top-level scoring fields
                scoring_filtered = {
                    k: v
                    for k, v in scoring_data.items()
                    if k not in ("weights", "penalties", "gap_penalties")
                }
                for key, value in scoring_filtered.items():
                    if hasattr(config.scoring, key):
                        setattr(config.scoring, key, value)

        # Handle output config
        if "output" in data:
            output_data = data["output"]
            if isinstance(output_data, dict):
                config.output = OutputConfig(**self._filter_fields(output_data, OutputConfig))

        # Handle github config
        if "github" in data:
            github_data = data["github"]
            if isinstance(github_data, dict):
                config.github = GitHubConfig(**self._filter_fields(github_data, GitHubConfig))

        # Handle monorepo config
        if "monorepo" in data:
            monorepo_data = data["monorepo"]
            if isinstance(monorepo_data, dict):
                projects = monorepo_data.get("projects", [])
                parsed_projects = []
                if isinstance(projects, list):
                    for proj in projects:
                        if isinstance(proj, dict):
                            parsed_projects.append(
                                MonorepoProject(**self._filter_fields(proj, MonorepoProject))
                            )
                config.monorepo = MonorepoConfig(
                    **self._filter_fields(
                        {k: v for k, v in monorepo_data.items() if k != "projects"}, MonorepoConfig
                    ),
                    projects=parsed_projects,
                )

        return config

    def _filter_fields(self, data: dict[str, Any], dataclass_type: type) -> dict[str, Any]:
        """Filter dictionary to only include fields from a dataclass.

        Args:
            data: Dictionary to filter.
            dataclass_type: Dataclass type to extract field names from.

        Returns:
            Filtered dictionary.
        """
        if not is_dataclass(dataclass_type):
            return data

        # Get field names from dataclass
        field_names = {f.name for f in dataclass_type.__dataclass_fields__.values()}  # type: ignore

        return {k: v for k, v in data.items() if k in field_names}

    def _merge_configs(self, base: Config, override: Config) -> Config:  # noqa: E712
        """Merge two Config objects, with override taking precedence.

        Args:
            base: Base configuration.
            override: Override configuration.

        Returns:
            Merged configuration.
        """
        merged = Config()

        # Merge coverage
        merged.coverage = CoverageConfig(
            enabled=override.coverage.enabled
            if override.coverage.enabled != True
            else base.coverage.enabled,
            minimum=override.coverage.minimum
            if override.coverage.minimum != 80
            else base.coverage.minimum,
            branches=override.coverage.branches
            if override.coverage.branches != True
            else base.coverage.branches,
            exclude=override.coverage.exclude
            if override.coverage.exclude
            else base.coverage.exclude,
        )

        # Merge gaps and detection
        merged.gaps.detection = GapDetectionConfig(
            untested_functions=(
                override.gaps.detection.untested_functions
                if override.gaps.detection.untested_functions != True
                else base.gaps.detection.untested_functions
            ),
            uncovered_branches=(
                override.gaps.detection.uncovered_branches
                if override.gaps.detection.uncovered_branches != True
                else base.gaps.detection.uncovered_branches
            ),
            missing_exceptions=(
                override.gaps.detection.missing_exceptions
                if override.gaps.detection.missing_exceptions != True
                else base.gaps.detection.missing_exceptions
            ),
            state_transitions=(
                override.gaps.detection.state_transitions
                if override.gaps.detection.state_transitions != True
                else base.gaps.detection.state_transitions
            ),
            edge_cases=(
                override.gaps.detection.edge_cases
                if override.gaps.detection.edge_cases != True
                else base.gaps.detection.edge_cases
            ),
        )

        merged.gaps = GapsConfig(
            enabled=override.gaps.enabled if override.gaps.enabled != True else base.gaps.enabled,
            detection=merged.gaps.detection,
            minimum_coverage=(
                override.gaps.minimum_coverage
                if override.gaps.minimum_coverage != 85
                else base.gaps.minimum_coverage
            ),
            suggest_tests=(
                override.gaps.suggest_tests
                if override.gaps.suggest_tests != True
                else base.gaps.suggest_tests
            ),
        )

        # Merge rules
        merged.rules._rules = {**base.rules._rules, **override.rules._rules}

        # Merge ignore
        merged.ignore = IgnoreConfig(
            rules=override.ignore.rules if override.ignore.rules else base.ignore.rules,
            files=override.ignore.files if override.ignore.files else base.ignore.files,
        )

        # Merge scoring
        merged.scoring.weights = ScoringWeights(
            coverage=(
                override.scoring.weights.coverage
                if override.scoring.weights.coverage != 1.0
                else base.scoring.weights.coverage
            ),
            quality=(
                override.scoring.weights.quality
                if override.scoring.weights.quality != 0.8
                else base.scoring.weights.quality
            ),
            gaps=(
                override.scoring.weights.gaps
                if override.scoring.weights.gaps != 1.2
                else base.scoring.weights.gaps
            ),
        )

        merged.scoring.penalties = ScoringPenalties(
            error=(
                override.scoring.penalties.error
                if override.scoring.penalties.error != 5.0
                else base.scoring.penalties.error
            ),
            warning=(
                override.scoring.penalties.warning
                if override.scoring.penalties.warning != 2.0
                else base.scoring.penalties.warning
            ),
            info=(
                override.scoring.penalties.info
                if override.scoring.penalties.info != 0.5
                else base.scoring.penalties.info
            ),
        )

        merged.scoring.gap_penalties = GapPenalties(
            untested_function=(
                override.scoring.gap_penalties.untested_function
                if override.scoring.gap_penalties.untested_function != 5.0
                else base.scoring.gap_penalties.untested_function
            ),
            uncovered_branch=(
                override.scoring.gap_penalties.uncovered_branch
                if override.scoring.gap_penalties.uncovered_branch != 3.0
                else base.scoring.gap_penalties.uncovered_branch
            ),
            missing_exception=(
                override.scoring.gap_penalties.missing_exception
                if override.scoring.gap_penalties.missing_exception != 4.0
                else base.scoring.gap_penalties.missing_exception
            ),
            missing_edge_case=(
                override.scoring.gap_penalties.missing_edge_case
                if override.scoring.gap_penalties.missing_edge_case != 1.0
                else base.scoring.gap_penalties.missing_edge_case
            ),
        )

        merged.scoring.minimum_score = (
            override.scoring.minimum_score
            if override.scoring.minimum_score != 75
            else base.scoring.minimum_score
        )

        # Merge output
        merged.output = OutputConfig(
            format=override.output.format
            if override.output.format != "text"
            else base.output.format,
            colors=override.output.colors if override.output.colors != True else base.output.colors,
            verbose=override.output.verbose
            if override.output.verbose != False
            else base.output.verbose,
            show_metadata=(
                override.output.show_metadata
                if override.output.show_metadata != True
                else base.output.show_metadata
            ),
            max_diagnostics=(
                override.output.max_diagnostics
                if override.output.max_diagnostics != 50
                else base.output.max_diagnostics
            ),
        )

        # Merge github
        merged.github = GitHubConfig(
            post_comment=(
                override.github.post_comment
                if override.github.post_comment != True
                else base.github.post_comment
            ),
            fail_on_score=(
                override.github.fail_on_score
                if override.github.fail_on_score != 75
                else base.github.fail_on_score
            ),
            fail_on_gaps=(
                override.github.fail_on_gaps
                if override.github.fail_on_gaps != True
                else base.github.fail_on_gaps
            ),
            fail_on_errors=(
                override.github.fail_on_errors
                if override.github.fail_on_errors != True
                else base.github.fail_on_errors
            ),
        )

        # Merge monorepo
        merged.monorepo = MonorepoConfig(
            enabled=override.monorepo.enabled
            if override.monorepo.enabled != False
            else base.monorepo.enabled,
            projects=override.monorepo.projects
            if override.monorepo.projects
            else base.monorepo.projects,
        )

        return merged

    def _validate_config(self, config: Config) -> None:
        """Validate configuration values.

        Args:
            config: Configuration to validate.

        Raises:
            ConfigError: If configuration is invalid.
        """
        # Validate coverage minimum
        if not 0 <= config.coverage.minimum <= 100:
            raise ConfigError(f"coverage.minimum must be 0-100, got {config.coverage.minimum}")

        # Validate gaps minimum coverage
        if not 0 <= config.gaps.minimum_coverage <= 100:
            raise ConfigError(
                f"gaps.minimum_coverage must be 0-100, got {config.gaps.minimum_coverage}"
            )

        # Validate output format
        if config.output.format not in ("text", "json", "html"):
            raise ConfigError(
                f"output.format must be 'text', 'json', or 'html', got '{config.output.format}'"
            )

        # Validate severity levels
        valid_severities = ("error", "warning", "info")
        for rule_name, rule_config in config.rules.items():
            if rule_config.severity not in valid_severities:
                raise ConfigError(
                    f"rules.{rule_name}.severity must be one of {valid_severities}, "
                    f"got '{rule_config.severity}'"
                )

        # Validate scoring minimum
        if not 0 <= config.scoring.minimum_score <= 100:
            raise ConfigError(
                f"scoring.minimum_score must be 0-100, got {config.scoring.minimum_score}"
            )

        # Validate GitHub settings
        if not 0 <= config.github.fail_on_score <= 100:
            raise ConfigError(
                f"github.fail_on_score must be 0-100, got {config.github.fail_on_score}"
            )


__all__ = [
    "Config",
    "ConfigLoader",
    "ConfigError",
    "CoverageConfig",
    "GapsConfig",
    "RulesConfig",
    "RuleConfig",
    "IgnoreConfig",
    "ScoringConfig",
    "OutputConfig",
    "GitHubConfig",
    "MonorepoConfig",
]
