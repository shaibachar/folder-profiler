# Contributing to Folder Profiler

Thank you for your interest in contributing to Folder Profiler! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/folder-profiler.git
   cd folder-profiler
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Write your code following our coding standards (see below)
2. Add or update tests for your changes
3. Update documentation as needed
4. Run tests and linters locally

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=folder_profiler

# Run specific test file
pytest tests/test_scanner/test_models.py

# Run tests by marker
pytest -m unit
pytest -m integration
```

### Code Quality Checks

```bash
# Format code (automatically fixes issues)
black src tests

# Sort imports
isort src tests

# Lint code
ruff check src tests

# Type checking
mypy src

# Run all checks
pre-commit run --all-files
```

### Committing Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in scanner"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Pushing and Creating Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- **PEP 8** compliant (enforced by Black and Ruff)
- **Line length**: 88 characters (Black default)
- **Type hints**: Required for all public APIs
- **Docstrings**: Required for all public modules, classes, and functions

### Docstring Format

```python
def analyze_folder(path: Path, max_depth: Optional[int] = None) -> FolderNode:
    """
    Analyze a folder and return the folder tree.

    Args:
        path: Path to the folder to analyze
        max_depth: Maximum depth to scan (None for unlimited)

    Returns:
        Root FolderNode containing the complete tree

    Raises:
        ValueError: If path is invalid
        PermissionError: If path is not accessible
    """
    pass
```

### Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert
- Use fixtures for common test data

```python
def test_folder_node_calculates_total_size_correctly(sample_folder_node):
    """Test that FolderNode correctly calculates total size including subfolders."""
    # Arrange
    child_node = FolderNode(...)
    sample_folder_node.subfolders.append(child_node)

    # Act
    total = sample_folder_node.total_size

    # Assert
    assert total == expected_size
```

## Project Structure

```
folder-profiler/
├── src/
│   └── folder_profiler/
│       ├── scanner/          # File system scanning
│       ├── analyzer/         # Analysis and statistics
│       ├── reporter/         # Report generation
│       ├── cli/              # Command-line interface
│       └── utils/            # Utility functions
├── tests/                    # Test files mirror src/
├── .speckit/                 # Project specification
├── docs/                     # Documentation
└── pyproject.toml           # Project configuration
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add comments for complex logic
- Update CHANGELOG.md (follows Keep a Changelog format)

## Pull Request Process

1. **Update documentation** - Ensure all changes are documented
2. **Add tests** - All new code should have tests
3. **Pass CI checks** - All tests and linters must pass
4. **Update CHANGELOG** - Add entry under "Unreleased"
5. **Request review** - Tag relevant maintainers
6. **Address feedback** - Respond to review comments
7. **Merge** - Maintainers will merge when approved

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Docstrings updated
- [ ] Type hints added
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)
- [ ] No merge conflicts
- [ ] Commits are clean and descriptive

## Issue Reporting

### Bug Reports

Include:
- OS and Python version
- folder-profiler version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Minimal reproducible example

### Feature Requests

Include:
- Clear description of the feature
- Use case/motivation
- Proposed API or usage example
- Potential implementation approach

## Questions?

- Check existing issues and discussions
- Ask in GitHub Discussions
- Tag maintainers if urgent

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
