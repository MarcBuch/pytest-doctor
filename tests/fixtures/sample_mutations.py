"""Sample mutations for testing assertion quality analysis."""

from __future__ import annotations

from pytest_doctor.models import Mutation


def create_sample_mutations() -> list[Mutation]:
    """
    Create sample mutations for testing.

    Returns:
        List of Mutation objects for testing
    """
    return [
        # Survived mutations (weak assertions)
        Mutation(
            id="1",
            source_location="src/math.py:10",
            mutation_type="< changed to <=",
            killed=False,
            failing_tests=[],
        ),
        Mutation(
            id="2",
            source_location="src/math.py:15",
            mutation_type="== changed to !=",
            killed=False,
            failing_tests=[],
        ),
        Mutation(
            id="3",
            source_location="src/utils.py:25",
            mutation_type="True changed to False",
            killed=False,
            failing_tests=[],
        ),
        # Killed mutations (strong assertions)
        Mutation(
            id="4",
            source_location="src/math.py:20",
            mutation_type="> changed to <",
            killed=True,
            failing_tests=["test_math.py::test_greater_than"],
        ),
        Mutation(
            id="5",
            source_location="src/utils.py:30",
            mutation_type="len() removed",
            killed=True,
            failing_tests=["test_utils.py::test_list_length"],
        ),
    ]


def create_single_survived_mutation() -> list[Mutation]:
    """
    Create a single survived mutation for testing.

    Returns:
        List with one Mutation that survived
    """
    return [
        Mutation(
            id="1",
            source_location="test.py:5",
            mutation_type="< changed to <=",
            killed=False,
            failing_tests=[],
        ),
    ]


def create_single_killed_mutation() -> list[Mutation]:
    """
    Create a single killed mutation for testing.

    Returns:
        List with one Mutation that was killed
    """
    return [
        Mutation(
            id="1",
            source_location="test.py:5",
            mutation_type="< changed to <=",
            killed=True,
            failing_tests=["test_example.py::test_comparison"],
        ),
    ]


def create_empty_mutations() -> list[Mutation]:
    """
    Create an empty list of mutations.

    Returns:
        Empty list
    """
    return []
