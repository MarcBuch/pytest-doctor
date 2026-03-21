"""Tests for the aggregation module."""

from pytest_doctor.aggregation import AggregatedIssues, ResultsAggregator
from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity


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

    def test_aggregate_multiple_engines(self) -> None:
        """Test aggregating results from multiple engines."""
        aggregator = ResultsAggregator()
        issue1 = Issue(
            file_path="test_example.py",
            line_number=10,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue2 = Issue(
            file_path="test_example.py",
            line_number=15,
            rule_id="unused_fixture",
            severity=Severity.INFO,
            source=IssueSource.DEAD_CODE,
        )
        result1 = AnalysisResult(engine="ruff", issues=[issue1])
        result2 = AnalysisResult(engine="vulture", issues=[issue2])
        aggregated = aggregator.aggregate([result1, result2])
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

    def test_sort_by_severity(self) -> None:
        """Test issues are sorted by severity."""
        aggregator = ResultsAggregator()
        issue_info = Issue(
            file_path="test_a.py",
            line_number=10,
            rule_id="info",
            severity=Severity.INFO,
            source=IssueSource.LINTING,
        )
        issue_warning = Issue(
            file_path="test_b.py",
            line_number=20,
            rule_id="warning",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue_critical = Issue(
            file_path="test_c.py",
            line_number=30,
            rule_id="critical",
            severity=Severity.CRITICAL,
            source=IssueSource.LINTING,
        )
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
        issue1 = Issue(
            file_path="test_a.py",
            line_number=10,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue2 = Issue(
            file_path="test_a.py",
            line_number=20,
            rule_id="E502",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue3 = Issue(
            file_path="test_b.py",
            line_number=30,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        result = AnalysisResult(engine="ruff", issues=[issue1, issue2, issue3])
        aggregated = aggregator.aggregate([result])
        assert len(aggregated.by_file) == 2
        assert len(aggregated.by_file["test_a.py"]) == 2
        assert len(aggregated.by_file["test_b.py"]) == 1

    def test_calculate_summary(self) -> None:
        """Test summary calculation."""
        aggregator = ResultsAggregator()
        issues = [
            Issue(
                file_path="test.py",
                line_number=1,
                rule_id="C1",
                severity=Severity.CRITICAL,
                source=IssueSource.LINTING,
            ),
            Issue(
                file_path="test.py",
                line_number=2,
                rule_id="C2",
                severity=Severity.CRITICAL,
                source=IssueSource.LINTING,
            ),
            Issue(
                file_path="test.py",
                line_number=3,
                rule_id="W1",
                severity=Severity.WARNING,
                source=IssueSource.LINTING,
            ),
            Issue(
                file_path="test.py",
                line_number=4,
                rule_id="I1",
                severity=Severity.INFO,
                source=IssueSource.LINTING,
            ),
        ]
        result = AnalysisResult(engine="ruff", issues=issues)
        aggregated = aggregator.aggregate([result])
        assert aggregated.summary["critical"] == 2
        assert aggregated.summary["warning"] == 1
        assert aggregated.summary["info"] == 1

    def test_collect_all_issues(self) -> None:
        """Test collecting issues from multiple results."""
        aggregator = ResultsAggregator()
        issue1 = Issue(
            file_path="test.py",
            line_number=1,
            rule_id="R1",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue2 = Issue(
            file_path="test.py",
            line_number=2,
            rule_id="R2",
            severity=Severity.WARNING,
            source=IssueSource.DEAD_CODE,
        )
        issue3 = Issue(
            file_path="test.py",
            line_number=3,
            rule_id="R3",
            severity=Severity.WARNING,
            source=IssueSource.TEST_QUALITY,
        )
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
        issue1 = Issue(
            file_path="test.py",
            line_number=10,
            column_number=5,
            rule_id="E501",
            message="First message",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issue2 = Issue(
            file_path="test.py",
            line_number=10,
            column_number=5,
            rule_id="E501",
            message="Second message",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        )
        issues = [issue1, issue2]
        deduplicated = aggregator._deduplicate_issues(issues)
        assert len(deduplicated) == 1
        assert deduplicated[0].message == "First message"
