# pytest-doctor

Intelligent test analysis and reporting for pytest-based projects.

## Development

This project uses `uv` for dependency and environment management.

### Getting Started

```bash
# Install dependencies and set up the virtual environment
uv sync

# Run tests
uv run pytest

# Run linting and type checking
uv run ruff check .
uv run mypy src
```

### Project Structure

```
src/pytest_doctor/
├── analyzers/        # Test and code analysis modules
├── scoring/          # Metrics calculation and scoring
├── reporter/         # Output formatting and reporting
├── cli/              # Command-line interface
└── __init__.py       # Package initialization
tests/                # Test suite
```
