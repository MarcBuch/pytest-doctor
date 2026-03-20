# pytest-doctor

Intelligent test analysis and reporting for pytest-based projects.

## Development

This project uses `uv` for dependency and environment management.

### Getting Started

```bash
# Install dependencies and set up the virtual environment
uv sync
```

### Standard Developer Commands

The following commands are the primary workflows for development:

```bash
# Run tests
uv run pytest

# Run linting (check code style, imports, and common issues)
uv run ruff check .

# Run type checking
uv run mypy src

# Run coverage analysis
uv run coverage run -m pytest && uv run coverage report

# Format code (auto-fix style issues)
uv run ruff format .
```

### Useful Aliases

You can add these to your shell profile for convenience:
```bash
alias pytest-doctor-lint="uv run ruff check ."
alias pytest-doctor-type="uv run mypy src"
alias pytest-doctor-test="uv run pytest"
alias pytest-doctor-coverage="uv run coverage run -m pytest && uv run coverage report"
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
