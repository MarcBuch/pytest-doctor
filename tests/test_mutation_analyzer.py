"""Tests for the mutation analyzer."""

import pytest

from pytest_doctor.models import IssueSource, Severity, Mutation
from pytest_doctor.mutation_analyzer import MutationAnalyzer
from tests.fixtures.sample_mutations import (
    create_sample_mutations,
    create_single_survived_mutation,
    create_single_killed_mutation,
    create_empty_mutations,
)


class TestMutationAnalyzerInit:
    """Test MutationAnalyzer initialization."""

    def test_mutation_analyzer_init(self) -> None:
        """Test basic initialization."""
        analyzer = MutationAnalyzer()
        assert analyzer is not None


class TestMutationAnalyzerAnalyzeMutations:
    """Test analyze_mutations method."""

    def test_analyze_mutations_empty(self) -> None:
        """Test analyzing empty mutation list."""
        analyzer = MutationAnalyzer()
        issues = analyzer.analyze_mutations(create_empty_mutations())
        assert len(issues) == 0

    def test_analyze_mutations_all_killed(self) -> None:
        """Test analyzing only killed mutations."""
        analyzer = MutationAnalyzer()
        mutations = create_single_killed_mutation()
        issues = analyzer.analyze_mutations(mutations)
        assert len(issues) == 0

    def test_analyze_mutations_all_survived(self) -> None:
        """Test analyzing only survived mutations."""
        analyzer = MutationAnalyzer()
        mutations = create_single_survived_mutation()
        issues = analyzer.analyze_mutations(mutations)
        assert len(issues) == 1

    def test_analyze_mutations_mixed(self) -> None:
        """Test analyzing mixed mutations (some survived, some killed)."""
        analyzer = MutationAnalyzer()
        mutations = create_sample_mutations()
        issues = analyzer.analyze_mutations(mutations)
        # Should have 3 survived mutations (ids 1, 2, 3)
        assert len(issues) == 3

    def test_analyze_mutations_issue_details(self) -> None:
        """Test that issues have correct details."""
        analyzer = MutationAnalyzer()
        mutations = create_single_survived_mutation()
        issues = analyzer.analyze_mutations(mutations)

        assert len(issues) == 1
        issue = issues[0]

        assert issue.file_path == "test.py"
        assert issue.line_number == 5
        assert issue.rule_id == "weak-assertion"
        assert issue.rule_name == "Weak Assertion - Mutation Survived"
        assert "< changed to <=" in issue.message
        assert issue.severity == Severity.WARNING
        assert issue.source == IssueSource.MUTATION_TESTING
        assert "< changed to <=" in issue.recommendation

    def test_analyze_mutations_multiple_issues(self) -> None:
        """Test analyzing multiple survived mutations."""
        analyzer = MutationAnalyzer()
        mutations = [
            Mutation(
                id="1",
                source_location="file1.py:10",
                mutation_type="< changed to <=",
                killed=False,
                failing_tests=[],
            ),
            Mutation(
                id="2",
                source_location="file2.py:20",
                mutation_type="== changed to !=",
                killed=False,
                failing_tests=[],
            ),
        ]
        issues = analyzer.analyze_mutations(mutations)

        assert len(issues) == 2
        assert issues[0].file_path == "file1.py"
        assert issues[0].line_number == 10
        assert issues[1].file_path == "file2.py"
        assert issues[1].line_number == 20


class TestMutationAnalyzerCalculateStats:
    """Test calculate_mutation_stats method."""

    def test_calculate_stats_empty(self) -> None:
        """Test calculating stats with empty mutations."""
        analyzer = MutationAnalyzer()
        stats = analyzer.calculate_mutation_stats(create_empty_mutations())

        assert stats.total_mutations == 0
        assert stats.killed_count == 0
        assert stats.survival_rate == 0.0
        assert stats.time_ms == 0

    def test_calculate_stats_all_killed(self) -> None:
        """Test calculating stats with all killed mutations."""
        analyzer = MutationAnalyzer()
        mutations = [
            Mutation(
                id="1",
                source_location="test.py:5",
                mutation_type="mutation1",
                killed=True,
                failing_tests=["test1"],
            ),
            Mutation(
                id="2",
                source_location="test.py:10",
                mutation_type="mutation2",
                killed=True,
                failing_tests=["test2"],
            ),
        ]
        stats = analyzer.calculate_mutation_stats(mutations)

        assert stats.total_mutations == 2
        assert stats.killed_count == 2
        assert stats.survival_rate == 0.0

    def test_calculate_stats_all_survived(self) -> None:
        """Test calculating stats with all survived mutations."""
        analyzer = MutationAnalyzer()
        mutations = [
            Mutation(
                id="1",
                source_location="test.py:5",
                mutation_type="mutation1",
                killed=False,
                failing_tests=[],
            ),
            Mutation(
                id="2",
                source_location="test.py:10",
                mutation_type="mutation2",
                killed=False,
                failing_tests=[],
            ),
        ]
        stats = analyzer.calculate_mutation_stats(mutations)

        assert stats.total_mutations == 2
        assert stats.killed_count == 0
        assert stats.survival_rate == 1.0

    def test_calculate_stats_mixed(self) -> None:
        """Test calculating stats with mixed mutations."""
        analyzer = MutationAnalyzer()
        mutations = create_sample_mutations()  # 3 survived, 2 killed
        stats = analyzer.calculate_mutation_stats(mutations)

        assert stats.total_mutations == 5
        assert stats.killed_count == 2
        assert stats.survival_rate == 0.6


class TestMutationAnalyzerSourceLocationParsing:
    """Test source location parsing."""

    def test_parse_source_location_with_line(self) -> None:
        """Test parsing source location with line number."""
        analyzer = MutationAnalyzer()
        mutation = Mutation(
            id="1",
            source_location="src/module.py:42",
            mutation_type="test",
            killed=False,
            failing_tests=[],
        )
        issues = analyzer.analyze_mutations([mutation])

        assert len(issues) == 1
        assert issues[0].file_path == "src/module.py"
        assert issues[0].line_number == 42

    def test_parse_source_location_without_line(self) -> None:
        """Test parsing source location without line number."""
        analyzer = MutationAnalyzer()
        mutation = Mutation(
            id="1",
            source_location="src/module.py",
            mutation_type="test",
            killed=False,
            failing_tests=[],
        )
        issues = analyzer.analyze_mutations([mutation])

        assert len(issues) == 1
        assert issues[0].file_path == "src/module.py"
        assert issues[0].line_number == 0

    def test_parse_source_location_invalid_line(self) -> None:
        """Test parsing source location with invalid line number."""
        analyzer = MutationAnalyzer()
        mutation = Mutation(
            id="1",
            source_location="src/module.py:invalid",
            mutation_type="test",
            killed=False,
            failing_tests=[],
        )
        issues = analyzer.analyze_mutations([mutation])

        assert len(issues) == 1
        assert issues[0].file_path == "src/module.py"
        assert issues[0].line_number == 0

    def test_parse_source_location_multiple_colons(self) -> None:
        """Test parsing source location with multiple colons (e.g., Windows paths)."""
        analyzer = MutationAnalyzer()
        mutation = Mutation(
            id="1",
            source_location="C:\\Users\\test\\src\\module.py:42",
            mutation_type="test",
            killed=False,
            failing_tests=[],
        )
        issues = analyzer.analyze_mutations([mutation])

        assert len(issues) == 1
        # Should split from the rightmost colon
        assert "module.py" in issues[0].file_path
        assert issues[0].line_number == 42
