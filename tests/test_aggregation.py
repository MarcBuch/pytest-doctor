"""Tests for the aggregation module."""

from pytest_doctor.aggregation import AggregatedIssues, ResultsAggregator
from pytest_doctor.models import (
    AnalysisResult,
    Issue,
    IssueSource,
    Severity,
    MutationStats,
)


def _make_issue(
    file_path: str = "test.py",
    line_number: int = 1,
    rule_id: str = "E501",
    severity: Severity = Severity.WARNING,
    source: IssueSource = IssueSource.LINTING,
    message: str = "Test message",
    column_number: int = 5,
) -> Issue:
    """Helper to create an issue with default values."""
    return Issue(
        file_path=file_path,
        line_number=line_number,
        column_number=column_number,
        rule_id=rule_id,
        message=message,
        severity=severity,
        source=source,
    )


class TestAggregatedIssues:
    """Tests for AggregatedIssues dataclass."""

    def test_aggregated_issues_defaults(self) -> None:
        """Test AggregatedIssues default initialization."""
        agg = AggregatedIssues()
        assert agg.by_file == {}
        assert agg.all_issues == []
        assert agg.summary == {"critical": 0, "warning": 0, "info": 0}

    def test_aggregated_issues_to_dict(self) -> None:
        """Test converting AggregatedIssues to dictionary."""
        issue = Issue(
            file_path="test_example.py",
            line_number=10,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        agg = AggregatedIssues(
            by_file={"test_example.py": [issue]},
            all_issues=[issue],
            summary={"critical": 0, "warning": 1, "info": 0},
        )
        result_dict = agg.to_dict()
        assert result_dict["summary"] == {"critical": 0, "warning": 1, "info": 0}
        assert result_dict["total_issues"] == 1
        assert "by_file" in result_dict
        assert "all_issues" in result_dict


class TestResultsAggregator:
    """Tests for ResultsAggregator."""

    def test_aggregator_init(self) -> None:
        """Test ResultsAggregator initialization."""
        aggregator = ResultsAggregator()
        assert aggregator is not None

    def test_aggregate_empty_results(self) -> None:
        """Test aggregating empty results."""
        aggregator = ResultsAggregator()
        result = aggregator.aggregate([])
        assert result.all_issues == []
        assert result.by_file == {}
        assert result.summary == {"critical": 0, "warning": 0, "info": 0}

    def test_aggregate_single_engine(self) -> None:
        """Test aggregating results from single engine."""
        aggregator = ResultsAggregator()
        issue = Issue(
            file_path="test_example.py",
            line_number=10,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        analysis_result = AnalysisResult(engine="ruff", issues=[issue])
        result = aggregator.aggregate([analysis_result])
        assert len(result.all_issues) == 1
        assert result.all_issues[0] == issue
        assert "test_example.py" in result.by_file
        assert result.summary["warning"] == 1

    def test_aggregate_multiple_engines(
        self, analysis_result_with_warning, analysis_result_with_info
    ) -> None:
        """Test aggregating results from multiple engines."""
        aggregator = ResultsAggregator()
        aggregated = aggregator.aggregate([analysis_result_with_warning, analysis_result_with_info])
        assert len(aggregated.all_issues) == 2
        assert aggregated.summary["warning"] == 1
        assert aggregated.summary["info"] == 1

    def test_deduplicate_identical_issues(self) -> None:
        """Test deduplication of identical issues."""
        aggregator = ResultsAggregator()
        issue = Issue(
            file_path="test_example.py",
            line_number=10,
            column_number=5,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        # Same issue reported twice
        result1 = AnalysisResult(engine="ruff", issues=[issue])
        result2 = AnalysisResult(engine="ruff", issues=[issue])
        aggregated = aggregator.aggregate([result1, result2])
        # Should deduplicate to single issue
        assert len(aggregated.all_issues) == 1
        assert aggregated.summary["warning"] == 1

    def test_sort_by_severity(self, issue_info, issue_warning, issue_critical) -> None:
        """Test issues are sorted by severity."""
        aggregator = ResultsAggregator()
        result = AnalysisResult(
            engine="ruff",
            issues=[issue_info, issue_warning, issue_critical],
        )
        aggregated = aggregator.aggregate([result])
        # Check that critical comes first, then warning, then info
        assert aggregated.all_issues[0].severity == Severity.CRITICAL
        assert aggregated.all_issues[1].severity == Severity.WARNING
        assert aggregated.all_issues[2].severity == Severity.INFO

    def test_group_by_file(self) -> None:
        """Test issues are grouped by file."""
        aggregator = ResultsAggregator()
        issue1 = _make_issue(file_path="test_a.py", line_number=10)
        issue2 = _make_issue(file_path="test_a.py", line_number=20, rule_id="E502")
        issue3 = _make_issue(file_path="test_b.py", line_number=30)
        result = AnalysisResult(engine="ruff", issues=[issue1, issue2, issue3])
        aggregated = aggregator.aggregate([result])
        assert len(aggregated.by_file) == 2
        assert len(aggregated.by_file["test_a.py"]) == 2
        assert len(aggregated.by_file["test_b.py"]) == 1

    def test_calculate_summary(self) -> None:
        """Test summary calculation."""
        aggregator = ResultsAggregator()
        issues = [
            _make_issue(line_number=1, rule_id="C1", severity=Severity.CRITICAL),
            _make_issue(line_number=2, rule_id="C2", severity=Severity.CRITICAL),
            _make_issue(line_number=3, rule_id="W1", severity=Severity.WARNING),
            _make_issue(line_number=4, rule_id="I1", severity=Severity.INFO),
        ]
        result = AnalysisResult(engine="ruff", issues=issues)
        aggregated = aggregator.aggregate([result])
        assert aggregated.summary["critical"] == 2
        assert aggregated.summary["warning"] == 1
        assert aggregated.summary["info"] == 1

    def test_collect_all_issues(self) -> None:
        """Test collecting issues from multiple results."""
        aggregator = ResultsAggregator()
        issue1 = _make_issue(line_number=1, rule_id="R1", source=IssueSource.LINTING)
        issue2 = _make_issue(line_number=2, rule_id="R2", source=IssueSource.DEAD_CODE)
        issue3 = _make_issue(line_number=3, rule_id="R3", source=IssueSource.TEST_QUALITY)
        results = [
            AnalysisResult(engine="ruff", issues=[issue1]),
            AnalysisResult(engine="vulture", issues=[issue2]),
            AnalysisResult(engine="quality", issues=[issue3]),
        ]
        all_issues = aggregator._collect_all_issues(results)
        assert len(all_issues) == 3
        assert issue1 in all_issues
        assert issue2 in all_issues
        assert issue3 in all_issues

    def test_deduplicate_keeps_first_occurrence(self) -> None:
        """Test deduplication keeps first occurrence."""
        aggregator = ResultsAggregator()
        issue1 = _make_issue(line_number=10, message="First message")
        issue2 = _make_issue(line_number=10, message="Second message")
        issues = [issue1, issue2]
        deduplicated = aggregator._deduplicate_issues(issues)
        assert len(deduplicated) == 1
        assert deduplicated[0].message == "First message"

    def test_filter_by_files(self) -> None:
        """Test filtering issues by changed files."""
        aggregator = ResultsAggregator()
        issue_a = _make_issue(file_path="test_a.py", line_number=10)
        issue_b = _make_issue(file_path="test_b.py", line_number=20, rule_id="E502")
        issue_c = _make_issue(file_path="test_c.py", line_number=30, rule_id="E503")
        aggregated = AggregatedIssues(
            by_file={
                "test_a.py": [issue_a],
                "test_b.py": [issue_b],
                "test_c.py": [issue_c],
            },
            all_issues=[issue_a, issue_b, issue_c],
            summary={"critical": 0, "warning": 3, "info": 0},
        )

        # Filter to only test_a.py and test_c.py
        filtered = aggregator.filter_by_files(aggregated, {"test_a.py", "test_c.py"})

        assert len(filtered.all_issues) == 2
        assert issue_a in filtered.all_issues
        assert issue_c in filtered.all_issues
        assert issue_b not in filtered.all_issues
        assert filtered.summary["warning"] == 2
        assert len(filtered.by_file) == 2

    def test_filter_by_files_empty_result(self) -> None:
        """Test filtering when no files match."""
        aggregator = ResultsAggregator()
        issue = _make_issue(file_path="test.py")
        aggregated = AggregatedIssues(
            by_file={"test.py": [issue]},
            all_issues=[issue],
            summary={"critical": 0, "warning": 1, "info": 0},
        )

        # Filter with no matching files
        filtered = aggregator.filter_by_files(aggregated, set())

        assert len(filtered.all_issues) == 0
        assert filtered.summary["warning"] == 0
        assert len(filtered.by_file) == 0

    def test_aggregate_with_mutation_results(self) -> None:
        """Test aggregating results that include mutation results."""
        aggregator = ResultsAggregator()

        # Create weak assertion issues (from mutations)
        weak_assertion_issue = Issue(
            file_path="src/math.py",
            line_number=10,
            rule_id="weak-assertion",
            severity=Severity.WARNING,
            source=IssueSource.MUTATION_TESTING,
            message="Mutation '< changed to <=' survived",
            recommendation="Strengthen assertion",
        )

        # Create mutation analysis result with metadata
        mutation_stats = MutationStats(
            total_mutations=5,
            killed_count=3,
            survival_rate=0.4,
            time_ms=1000,
        )
        mutation_result = AnalysisResult(
            engine="assertion_quality",
            issues=[weak_assertion_issue],
            metadata={"mutation_stats": mutation_stats},
        )

        # Create regular lint result
        lint_issue = Issue(
            file_path="src/math.py",
            line_number=5,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            message="Line too long",
        )
        lint_result = AnalysisResult(engine="ruff", issues=[lint_issue])

        # Aggregate both results
        aggregated = aggregator.aggregate([lint_result, mutation_result])

        # Verify mutation issues are included
        assert len(aggregated.all_issues) == 2
        assert any(issue.source == IssueSource.MUTATION_TESTING for issue in aggregated.all_issues)
        assert any(issue.source == IssueSource.LINTING for issue in aggregated.all_issues)
        assert aggregated.summary["warning"] == 2

    def test_aggregate_with_mutation_stats_metadata(self) -> None:
        """Test that mutation stats are preserved in aggregation."""
        aggregator = ResultsAggregator()

        mutation_stats = MutationStats(
            total_mutations=10,
            killed_count=7,
            survival_rate=0.3,
            time_ms=5000,
        )

        mutation_result = AnalysisResult(
            engine="assertion_quality",
            issues=[],
            metadata={"mutation_stats": mutation_stats},
        )

        aggregated = aggregator.aggregate([mutation_result])

        # Metadata should be preserved in results
        assert len(aggregated.all_issues) == 0
        assert aggregated.summary["warning"] == 0

    def test_aggregate_backward_compatibility_no_mutations(self) -> None:
        """Test that aggregation works without mutation results."""
        aggregator = ResultsAggregator()

        # Only regular results
        issues = [
            _make_issue(line_number=1, rule_id="E501"),
            _make_issue(line_number=2, rule_id="E502"),
        ]
        result = AnalysisResult(engine="ruff", issues=issues)
        aggregated = aggregator.aggregate([result])

        # Should work as before
        assert len(aggregated.all_issues) == 2
        assert aggregated.summary["warning"] == 2
