"""Unit tests for core data models."""

import json

from pytest_doctor.models import (
    CoverageStats,
    Diagnostic,
    DiagnosticType,
    EdgeCase,
    EdgeCaseCategory,
    Gap,
    GapCategory,
    Location,
    ProjectInfo,
    Results,
    Score,
    ScoreLabel,
    Severity,
    SuggestedTest,
)


class TestLocation:
    """Tests for Location model."""

    def test_location_creation(self):
        """Test basic location creation."""
        loc = Location(file="test.py", line=42, column=10)
        assert loc.file == "test.py"
        assert loc.line == 42
        assert loc.column == 10

    def test_location_default_column(self):
        """Test location with default column value."""
        loc = Location(file="test.py", line=42)
        assert loc.column == 0

    def test_location_to_dict(self):
        """Test location serialization to dict."""
        loc = Location(file="test.py", line=42, column=10)
        d = loc.to_dict()
        assert d == {"file": "test.py", "line": 42, "column": 10}


class TestDiagnostic:
    """Tests for Diagnostic model."""

    def test_diagnostic_creation(self):
        """Test basic diagnostic creation."""
        diag = Diagnostic(
            type=DiagnosticType.QUALITY,
            category="assertions/missing-messages",
            file="test_app.py",
            line=15,
            column=5,
            severity=Severity.WARNING,
            message="Missing assertion message",
            help="Assertions should include descriptive messages",
            suggestion="Add a message parameter to assert",
        )
        assert diag.type == DiagnosticType.QUALITY
        assert diag.category == "assertions/missing-messages"
        assert diag.severity == Severity.WARNING
        assert diag.suggestion is not None

    def test_diagnostic_without_suggestion(self):
        """Test diagnostic without optional suggestion."""
        diag = Diagnostic(
            type=DiagnosticType.GAP,
            category="gap/untested-functions",
            file="app.py",
            line=10,
            column=0,
            severity=Severity.ERROR,
            message="Function not tested",
            help="This function has no test coverage",
        )
        assert diag.suggestion is None

    def test_diagnostic_to_dict(self):
        """Test diagnostic serialization to dict."""
        diag = Diagnostic(
            type=DiagnosticType.QUALITY,
            category="assertions/missing-messages",
            file="test.py",
            line=5,
            column=0,
            severity=Severity.ERROR,
            message="Test message",
            help="Test help",
            suggestion="Test suggestion",
        )
        d = diag.to_dict()
        assert d["type"] == "quality"
        assert d["severity"] == "error"
        assert d["file"] == "test.py"
        assert d["suggestion"] == "Test suggestion"

    def test_diagnostic_to_json(self):
        """Test diagnostic serialization to JSON."""
        diag = Diagnostic(
            type=DiagnosticType.QUALITY,
            category="test-category",
            file="test.py",
            line=5,
            column=0,
            severity=Severity.WARNING,
            message="Test",
            help="Help",
        )
        json_str = diag.to_json()
        parsed = json.loads(json_str)
        assert parsed["type"] == "quality"
        assert parsed["severity"] == "warning"


class TestSuggestedTest:
    """Tests for SuggestedTest model."""

    def test_suggestion_creation(self):
        """Test basic test suggestion creation."""
        suggestion = SuggestedTest(
            description="Test with empty list",
            test_inputs={"items": []},
            expected_behavior="Should handle empty input gracefully",
        )
        assert suggestion.description == "Test with empty list"
        assert suggestion.test_inputs == {"items": []}

    def test_suggestion_to_dict(self):
        """Test suggestion serialization to dict."""
        suggestion = SuggestedTest(
            description="Test edge case",
            test_inputs={"value": 0},
            expected_behavior="Return None",
        )
        d = suggestion.to_dict()
        assert d["description"] == "Test edge case"
        assert d["test_inputs"] == {"value": 0}
        assert d["expected_behavior"] == "Return None"


class TestGap:
    """Tests for Gap model."""

    def test_gap_creation(self):
        """Test basic gap creation."""
        loc = Location(file="app.py", line=20)
        gap = Gap(
            category=GapCategory.UNTESTED_FUNCTIONS,
            location=loc,
            description="Function calculate_total is not tested",
            severity=Severity.ERROR,
        )
        assert gap.category == GapCategory.UNTESTED_FUNCTIONS
        assert gap.location.file == "app.py"
        assert gap.severity == Severity.ERROR

    def test_gap_with_test_suggestion(self):
        """Test gap with test suggestion."""
        loc = Location(file="app.py", line=20)
        suggestion = SuggestedTest(
            description="Test the function",
            test_inputs={"value": 1},
        )
        gap = Gap(
            category=GapCategory.UNCOVERED_BRANCHES,
            location=loc,
            description="Uncovered else branch",
            severity=Severity.WARNING,
            test_suggestion=suggestion,
        )
        assert gap.test_suggestion is not None
        assert gap.test_suggestion.description == "Test the function"

    def test_gap_to_dict(self):
        """Test gap serialization to dict."""
        loc = Location(file="app.py", line=20, column=5)
        gap = Gap(
            category=GapCategory.MISSING_EXCEPTION_TESTS,
            location=loc,
            description="Missing exception test",
            severity=Severity.ERROR,
        )
        d = gap.to_dict()
        assert d["category"] == "missing-exception-tests"
        assert d["location"]["file"] == "app.py"
        assert d["severity"] == "error"

    def test_gap_to_json(self):
        """Test gap serialization to JSON."""
        loc = Location(file="app.py", line=20)
        gap = Gap(
            category=GapCategory.UNTESTED_FUNCTIONS,
            location=loc,
            description="Test gap",
            severity=Severity.WARNING,
        )
        json_str = gap.to_json()
        parsed = json.loads(json_str)
        assert parsed["category"] == "untested-functions"
        assert parsed["location"]["line"] == 20


class TestEdgeCase:
    """Tests for EdgeCase model."""

    def test_edge_case_creation(self):
        """Test basic edge case creation."""
        edge_case = EdgeCase(
            category=EdgeCaseCategory.BOUNDARY_VALUE,
            description="Test with maximum integer value",
            function_name="process_number",
            function_file="utils.py",
            test_inputs={"num": 2**31 - 1},
            expected_behavior="Should handle max int without overflow",
        )
        assert edge_case.category == EdgeCaseCategory.BOUNDARY_VALUE
        assert edge_case.function_name == "process_number"

    def test_edge_case_empty_inputs(self):
        """Test edge case with default empty inputs."""
        edge_case = EdgeCase(
            category=EdgeCaseCategory.EMPTY_INPUT,
            description="Test with empty list",
            function_name="filter_items",
            function_file="utils.py",
        )
        assert edge_case.test_inputs == {}

    def test_edge_case_to_dict(self):
        """Test edge case serialization to dict."""
        edge_case = EdgeCase(
            category=EdgeCaseCategory.SPECIAL_CHARACTERS,
            description="Test with unicode",
            function_name="process_string",
            function_file="utils.py",
            test_inputs={"text": "café"},
        )
        d = edge_case.to_dict()
        assert d["category"] == "special-characters"
        assert d["function_name"] == "process_string"
        assert d["function_file"] == "utils.py"

    def test_edge_case_to_json(self):
        """Test edge case serialization to JSON."""
        edge_case = EdgeCase(
            category=EdgeCaseCategory.RESOURCE_LIMITS,
            description="Test with large input",
            function_name="parse_data",
            function_file="parser.py",
        )
        json_str = edge_case.to_json()
        parsed = json.loads(json_str)
        assert parsed["category"] == "resource-limits"


class TestCoverageStats:
    """Tests for CoverageStats model."""

    def test_coverage_stats_creation(self):
        """Test basic coverage stats creation."""
        stats = CoverageStats(
            total_lines=100,
            covered_lines=85,
            total_branches=40,
            covered_branches=30,
        )
        assert stats.total_lines == 100
        assert stats.covered_lines == 85

    def test_coverage_line_coverage_percent(self):
        """Test line coverage percentage calculation."""
        stats = CoverageStats(total_lines=100, covered_lines=85)
        assert stats.line_coverage_percent == 85.0

    def test_coverage_branch_coverage_percent(self):
        """Test branch coverage percentage calculation."""
        stats = CoverageStats(total_branches=40, covered_branches=30)
        assert stats.branch_coverage_percent == 75.0

    def test_coverage_zero_lines(self):
        """Test coverage with zero total lines."""
        stats = CoverageStats(total_lines=0, covered_lines=0)
        assert stats.line_coverage_percent == 0.0

    def test_coverage_to_dict(self):
        """Test coverage stats serialization to dict."""
        stats = CoverageStats(
            total_lines=100,
            covered_lines=90,
            total_branches=20,
            covered_branches=18,
        )
        d = stats.to_dict()
        assert d["total_lines"] == 100
        assert d["covered_lines"] == 90
        assert d["line_coverage_percent"] == 90.0
        assert d["branch_coverage_percent"] == 90.0


class TestScore:
    """Tests for Score model."""

    def test_score_creation(self):
        """Test basic score creation."""
        score = Score(
            value=85.5,
            label=ScoreLabel.EXCELLENT,
            breakdown={"coverage": 5, "quality": 8, "gaps": 1.5},
        )
        assert score.value == 85.5
        assert score.label == ScoreLabel.EXCELLENT

    def test_score_auto_label_excellent(self):
        """Test automatic label assignment for excellent score."""
        score = Score(
            value=80.0,
            label=ScoreLabel.EXCELLENT,
            breakdown={},
        )
        assert score.label == ScoreLabel.EXCELLENT

    def test_score_capping_max(self):
        """Test score capping at maximum 100."""
        score = Score(
            value=150.0,
            label=ScoreLabel.EXCELLENT,
        )
        assert score.value == 100.0

    def test_score_capping_min(self):
        """Test score capping at minimum 0."""
        score = Score(
            value=-50.0,
            label=ScoreLabel.CRITICAL,
        )
        assert score.value == 0.0

    def test_score_to_dict(self):
        """Test score serialization to dict."""
        score = Score(
            value=72.3,
            label=ScoreLabel.NEEDS_WORK,
            breakdown={"coverage": 10.5, "quality": 12.2, "gaps": 5.0},
        )
        d = score.to_dict()
        assert d["value"] == 72.3
        assert d["label"] == "Needs Work"
        assert "coverage" in d["breakdown"]

    def test_score_to_json(self):
        """Test score serialization to JSON."""
        score = Score(
            value=95.0,
            label=ScoreLabel.EXCELLENT,
            breakdown={"coverage": 0, "quality": 4, "gaps": 1},
        )
        json_str = score.to_json()
        parsed = json.loads(json_str)
        assert parsed["value"] == 95.0
        assert parsed["label"] == "Excellent"


class TestProjectInfo:
    """Tests for ProjectInfo model."""

    def test_project_info_creation(self):
        """Test basic project info creation."""
        info = ProjectInfo(
            name="my-project",
            root_path="/home/user/my-project",
            python_version="3.9.0",
            total_files=42,
            total_tests=150,
            analysis_time_seconds=2.456,
        )
        assert info.name == "my-project"
        assert info.total_files == 42

    def test_project_info_to_dict(self):
        """Test project info serialization to dict."""
        info = ProjectInfo(
            name="test-project",
            root_path="/root",
            python_version="3.8",
            total_files=10,
            total_tests=25,
            analysis_time_seconds=1.234567,
        )
        d = info.to_dict()
        assert d["name"] == "test-project"
        assert d["analysis_time_seconds"] == 1.23  # Rounded to 2 decimals


class TestResults:
    """Tests for Results model."""

    def test_results_creation(self):
        """Test basic results creation."""
        score = Score(value=75.0, label=ScoreLabel.EXCELLENT)
        results = Results(score=score)
        assert results.score.value == 75.0
        assert len(results.diagnostics) == 0
        assert len(results.gaps) == 0

    def test_results_with_diagnostics(self):
        """Test results with diagnostics."""
        score = Score(value=60.0, label=ScoreLabel.NEEDS_WORK)
        diag = Diagnostic(
            type=DiagnosticType.QUALITY,
            category="test-category",
            file="test.py",
            line=10,
            column=0,
            severity=Severity.WARNING,
            message="Test warning",
            help="Test help",
        )
        results = Results(score=score, diagnostics=[diag])
        assert len(results.diagnostics) == 1
        assert results.diagnostics[0].message == "Test warning"

    def test_results_with_gaps(self):
        """Test results with gaps."""
        score = Score(value=50.0, label=ScoreLabel.CRITICAL)
        loc = Location(file="app.py", line=15)
        gap = Gap(
            category=GapCategory.UNTESTED_FUNCTIONS,
            location=loc,
            description="Test gap",
            severity=Severity.ERROR,
        )
        results = Results(score=score, gaps=[gap])
        assert len(results.gaps) == 1
        assert results.gaps[0].category == GapCategory.UNTESTED_FUNCTIONS

    def test_results_with_coverage(self):
        """Test results with coverage stats."""
        score = Score(value=80.0, label=ScoreLabel.EXCELLENT)
        coverage = CoverageStats(
            total_lines=100,
            covered_lines=80,
        )
        results = Results(score=score, coverage=coverage)
        assert results.coverage.line_coverage_percent == 80.0

    def test_results_to_dict(self):
        """Test results serialization to dict."""
        score = Score(value=72.0, label=ScoreLabel.NEEDS_WORK)
        diag = Diagnostic(
            type=DiagnosticType.GAP,
            category="gap/test",
            file="test.py",
            line=5,
            column=0,
            severity=Severity.ERROR,
            message="Gap found",
            help="Help text",
        )
        coverage = CoverageStats(total_lines=50, covered_lines=40)
        results = Results(
            score=score,
            diagnostics=[diag],
            coverage=coverage,
        )
        d = results.to_dict()
        assert "score" in d
        assert "diagnostics" in d
        assert "coverage" in d
        assert len(d["diagnostics"]) == 1

    def test_results_to_json(self):
        """Test results serialization to JSON."""
        score = Score(value=85.0, label=ScoreLabel.EXCELLENT)
        results = Results(score=score)
        json_str = results.to_json()
        parsed = json.loads(json_str)
        assert parsed["score"]["value"] == 85.0
        assert isinstance(parsed["diagnostics"], list)
        assert isinstance(parsed["coverage"], dict)

    def test_results_full_scenario(self):
        """Test results with all components populated."""
        score = Score(
            value=65.0,
            label=ScoreLabel.NEEDS_WORK,
            breakdown={"coverage": 15, "quality": 15, "gaps": 5},
        )
        diag = Diagnostic(
            type=DiagnosticType.QUALITY,
            category="assertions/missing",
            file="test_app.py",
            line=20,
            column=5,
            severity=Severity.WARNING,
            message="Missing assertion",
            help="Add assertion to verify behavior",
            suggestion="assert result == expected_value",
        )
        loc = Location(file="app.py", line=30)
        suggestion = SuggestedTest(
            description="Test error path",
            test_inputs={"value": -1},
        )
        gap = Gap(
            category=GapCategory.UNCOVERED_BRANCHES,
            location=loc,
            description="Error handling not tested",
            severity=Severity.ERROR,
            test_suggestion=suggestion,
        )
        edge_case = EdgeCase(
            category=EdgeCaseCategory.BOUNDARY_VALUE,
            description="Test with zero value",
            function_name="divide",
            function_file="math.py",
            test_inputs={"denominator": 0},
        )
        coverage = CoverageStats(
            total_lines=200,
            covered_lines=130,
            total_branches=50,
            covered_branches=35,
        )
        project = ProjectInfo(
            name="test-project",
            root_path="/home/user/project",
            python_version="3.9",
            total_files=25,
            total_tests=75,
            analysis_time_seconds=3.5,
        )
        results = Results(
            score=score,
            diagnostics=[diag],
            gaps=[gap],
            edge_cases=[edge_case],
            coverage=coverage,
            project_info=project,
            metadata={"custom_field": "custom_value"},
        )
        # Verify structure
        assert results.score.value == 65.0
        assert len(results.diagnostics) == 1
        assert len(results.gaps) == 1
        assert len(results.edge_cases) == 1
        assert results.coverage.line_coverage_percent == 65.0
        assert results.project_info.name == "test-project"

        # Verify JSON serialization works
        json_str = results.to_json()
        parsed = json.loads(json_str)
        assert parsed["score"]["value"] == 65.0
        assert len(parsed["diagnostics"]) == 1
        assert len(parsed["gaps"]) == 1
        assert len(parsed["edge_cases"]) == 1


class TestEnums:
    """Tests for enum values."""

    def test_severity_values(self):
        """Test all severity values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

    def test_diagnostic_type_values(self):
        """Test all diagnostic type values."""
        assert DiagnosticType.GAP.value == "gap"
        assert DiagnosticType.QUALITY.value == "quality"
        assert DiagnosticType.COVERAGE.value == "coverage"

    def test_gap_category_values(self):
        """Test all gap category values."""
        assert GapCategory.UNTESTED_FUNCTIONS.value == "untested-functions"
        assert GapCategory.UNCOVERED_BRANCHES.value == "uncovered-branches"
        assert GapCategory.MISSING_EXCEPTION_TESTS.value == "missing-exception-tests"
        assert GapCategory.STATE_TRANSITION_GAPS.value == "state-transition-gaps"
        assert GapCategory.DEAD_TEST_CODE.value == "dead-test-code"

    def test_edge_case_category_values(self):
        """Test all edge case category values."""
        assert EdgeCaseCategory.BOUNDARY_VALUE.value == "boundary-value"
        assert EdgeCaseCategory.EMPTY_INPUT.value == "empty-input"
        assert EdgeCaseCategory.SPECIAL_CHARACTERS.value == "special-characters"
        assert EdgeCaseCategory.RESOURCE_LIMITS.value == "resource-limits"
        assert EdgeCaseCategory.STATE_TRANSITIONS.value == "state-transitions"
        assert EdgeCaseCategory.TYPE_COERCION.value == "type-coercion"

    def test_score_label_values(self):
        """Test all score label values."""
        assert ScoreLabel.EXCELLENT.value == "Excellent"
        assert ScoreLabel.NEEDS_WORK.value == "Needs Work"
        assert ScoreLabel.CRITICAL.value == "Critical"
