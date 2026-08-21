# Contributing to enumplus

Thank you for your interest in contributing to enumplus! This document describes the process for contributing to the project.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/enumpy.git
   cd enumpy
   ```
3. Create a virtual environment and install dev dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

> **Note:** The git repository is named `enumpy`, while the package name is `enumplus`. This is expected — the repository name predates the package rename.

## Development Workflow

1. Create a branch for your feature or bugfix:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes, keeping code style consistent with the existing codebase.
3. Run the checks before committing:
   ```bash
   ruff check enumplus/ tests/
   mypy --strict enumplus/ tests/
   pytest --tb=short
   ```
4. Commit using [conventional commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in X"
   ```
5. Push to your fork and open a Pull Request.

## Code Style

- Follow PEP 8 and PEP 257.
- Use type hints for all public APIs.
- Line length: 100 characters (enforced by ruff).
- Target Python 3.11+.

## Testing

- All new features must include tests.
- Place tests in the `tests/` directory.
- Run the full suite with `pytest`.
- Do not weaken or delete existing tests without explicit justification.

## Cross-Version Testing

CI tests Python 3.11, 3.12, 3.13, and 3.14. To test locally against multiple Python versions, use the Python launcher (Windows) or `pyenv` (macOS/Linux):

```bash
py -3.11 -m pip install -e ".[dev]"
py -3.11 -m pytest --tb=short
py -3.11 -m mypy --strict enumplus/ tests/
```

## Pull Request Guidelines

- Keep PRs focused and small.
- Reference any related issues (e.g., `Closes #123`).
- Ensure all CI checks pass before requesting review.
- Update documentation (`README.md`) if your change affects the public API.
- Add a `CHANGELOG.md` entry under the `[Unreleased]` section.

## Reporting Issues

- Use [GitHub Issues](https://github.com/MathiasPaulenko/enumpy/issues) to report bugs or request features.
- Use the provided issue templates for consistency.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
