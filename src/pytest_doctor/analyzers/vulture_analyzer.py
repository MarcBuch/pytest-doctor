"""Vulture dead code detection integration for pytest-doctor."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import vulture

from pytest_doctor.config import Config
from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity


class VultureAnalyzer:
    """Analyzes Python test files for dead code using vulture."""

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the Vulture analyzer.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def analyze(self, path: str | Path) -> AnalysisResult:
        """
        Run vulture on the given path and collect dead code findings.

        Args:
            path: Directory or file path to analyze

        Returns:
            AnalysisResult containing found dead code issues
        """
        start_time = time.time()
        result = AnalysisResult(engine="vulture")

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result

            # Get Python files to analyze
            if path_obj.is_file():
                files = [str(path_obj)]
            else:
                # Only analyze test files
                files = [str(f) for f in path_obj.rglob("test_*.py")] + [
                    str(f) for f in path_obj.rglob("*_test.py")
                ]

            if not files:
                return result

            # Filter by configured ignore files
            files = [f for f in files if not self._should_ignore_file(f)]

            if not files:
                return result

            # Create vulture instance and analyze
            v = vulture.Vulture(verbose=False)
            for file_path in files:
                v.scavenge([file_path], [])

            # Convert unused definitions to issues
            result.issues = self._convert_findings(v)

        except Exception:
            # If vulture fails, return empty result
            pass
        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _convert_findings(self, v: vulture.Vulture) -> list[Issue]:
        """
        Convert vulture findings to Issue objects.

        Args:
            v: Vulture instance with scavenged results

        Returns:
            List of Issue objects
        """
        issues: list[Issue] = []

        # Combine all unused definitions
        unused = v.get_unused_code(min_confidence=60)

        for item in unused:
            # Get line number (some items might not have lineno)
            line_number = getattr(item, "lineno", 0)

            # Determine severity based on type and confidence
            severity = self._map_severity(item)

            # Generate recommendation
            recommendation = self._get_recommendation(item)

            issue = Issue(
                file_path=str(getattr(item, "filename", "")),
                line_number=line_number,
                column_number=0,
                rule_id="dead-code",
                rule_name=f"Unused {getattr(item, 'type', 'code')}",
                message=f"{getattr(item, 'name', 'item')} is unused {getattr(item, 'type', 'code')}",
                severity=severity,
                source=IssueSource.DEAD_CODE,
                recommendation=recommendation,
            )
            issues.append(issue)

        return issues

    def _map_severity(self, item: Any) -> Severity:
        """Map vulture findings to severity level based on confidence."""
        confidence = getattr(item, "confidence", 0)

        # Higher confidence means more likely to be dead code
        if confidence >= 80:
            return Severity.WARNING
        return Severity.INFO

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on config."""
        import pathspec

        if not self.config.ignore.files:
            return False

        spec = pathspec.PathSpec.from_lines("gitignore", self.config.ignore.files)
        return spec.match_file(file_path)

    def _get_recommendation(self, item: Any) -> str:
        """Get actionable recommendation for dead code finding."""
        item_type = getattr(item, "type", "code").lower()
        item_name = getattr(item, "name", "item")

        recommendations = {
            "function": f"Remove unused function '{item_name}' or add test coverage that uses it",
            "variable": f"Remove unused variable '{item_name}' or assign it a value that's actually used",
            "attribute": f"Remove unused attribute '{item_name}' from class or use it in methods",
            "class": f"Remove unused class '{item_name}' or add test coverage that uses it",
            "import": f"Remove unused import '{item_name}' or use it in the code",
        }

        return recommendations.get(item_type, f"Remove or use the unused {item_type} '{item_name}'")
