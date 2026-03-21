"""Ruff linting integration for pytest-doctor."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from pytest_doctor.config import Config
from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity


class RuffAnalyzer:
    """Analyzes Python test files using ruff linter."""

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the Ruff analyzer.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def analyze(self, path: str | Path) -> AnalysisResult:
        """
        Run ruff on the given path and collect linting violations.

        Args:
            path: Directory or file path to analyze

        Returns:
            AnalysisResult containing found issues
        """
        start_time = time.time()
        result = AnalysisResult(engine="ruff")

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result

            # Run ruff with JSON output
            cmd = [
                "ruff",
                "check",
                str(path_obj),
                "--output-format",
                "json",
            ]

            # Add ignore rules if configured
            if self.config.ignore.rules:
                ignore_str = ",".join(self.config.ignore.rules)
                cmd.extend(["--ignore", ignore_str])

            output = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            # Parse JSON output
            if output.stdout:
                violations = json.loads(output.stdout)
                result.issues = self._parse_violations(violations)

        except (subprocess.SubprocessError, json.JSONDecodeError):
            # If ruff fails to run or parse, return empty result
            pass
        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _parse_violations(self, violations: list[dict[str, Any]]) -> list[Issue]:
        """
        Parse ruff JSON violations into Issue objects.

        Args:
            violations: List of violation dicts from ruff JSON output

        Returns:
            List of Issue objects
        """
        issues: list[Issue] = []

        for violation in violations:
            # Filter by configured ignore files
            file_path = str(violation.get("filename", ""))
            if self._should_ignore_file(file_path):
                continue

            # Map ruff severity to our Severity enum
            severity = self._map_severity(str(violation.get("code", "")))

            issue = Issue(
                file_path=file_path,
                line_number=int(violation.get("location", {}).get("row", 0)),
                column_number=int(violation.get("location", {}).get("column", 0)),
                rule_id=str(violation.get("code", "")),
                rule_name=str(violation.get("code", "")),
                message=str(violation.get("message", "")),
                severity=severity,
                source=IssueSource.LINTING,
                recommendation=self._get_recommendation(str(violation.get("code", ""))),
            )
            issues.append(issue)

        return issues

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on config."""
        import pathspec

        if not self.config.ignore.files:
            return False

        spec = pathspec.PathSpec.from_lines("gitignore", self.config.ignore.files)
        return spec.match_file(file_path)

    def _map_severity(self, rule_code: str) -> Severity:
        """Map ruff rule code to severity level."""
        # E/F/W are typically errors, others are warnings
        if rule_code and rule_code[0] in ("E", "F", "W"):
            return Severity.WARNING
        if rule_code and rule_code.startswith("B"):  # flake8-bugbear
            return Severity.WARNING
        return Severity.INFO

    def _get_recommendation(self, rule_code: str) -> str:
        """Get actionable recommendation for a rule."""
        recommendations = {
            "E501": "Consider breaking long lines or increasing the line length limit",
            "F841": "Remove unused variable or use it in the code",
            "W503": "Move binary operator to the next line for better readability",
            "E302": "Add missing blank lines before class/function definitions",
            "E303": "Remove excessive blank lines",
            "E401": "Import multiple items on one line or use 'from X import *'",
            "B008": "Do not use mutable default arguments",
        }
        return recommendations.get(rule_code, f"Fix {rule_code} violation")
