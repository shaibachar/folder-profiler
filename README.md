# Folder Profiler

[![PyPI version](https://badge.fury.io/py/folder-profiler.svg)](https://badge.fury.io/py/folder-profiler)
[![Python Support](https://img.shields.io/pypi/pyversions/folder-profiler.svg)](https://pypi.org/project/folder-profiler/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intelligent file system analysis tool with AI-powered recommendations for organization and cleanup.

## Overview

Folder Profiler is a Python-based CLI application that provides deep insights into folder structures, identifies optimization opportunities, detects duplicate content, and generates AI-powered recommendations for organization and cleanup.

### Key Features

- 📊 **Comprehensive File System Analysis** - Deep scanning with detailed statistics
- 🔍 **Duplicate Detection** - Find exact and near-duplicate files
- 🤖 **AI-Powered Recommendations** - Intelligent suggestions for organization
- 📈 **Detailed Reporting** - Generate reports in JSON, HTML, and PDF formats
- ⚡ **High Performance** - Efficiently handles large directory structures
- 🎨 **Beautiful CLI** - Rich terminal UI with progress indicators
- 🔧 **Flexible Configuration** - Customizable ignore patterns and analysis depth

## Installation

### From PyPI (Recommended)

```bash
pip install folder-profiler
```

### From Source

```bash
git clone https://github.com/folder-profiler/folder-profiler.git
cd folder-profiler
pip install -e .
```

### Optional Dependencies

```bash
# For ML-based features
pip install folder-profiler[ml]

# For enhanced reports
pip install folder-profiler[reports]

# Install everything
pip install folder-profiler[all]
```

## Quick Start

### Basic Analysis

```bash
# Analyze a folder and generate an HTML report
folder-profiler analyze /path/to/folder

# Specify output format
folder-profiler analyze /path/to/folder --format json -o report.json

# Limit scan depth
folder-profiler analyze /path/to/folder --max-depth 3
```

### Advanced Usage

```bash
# Exclude patterns
folder-profiler analyze /path/to/folder --exclude "*.tmp" --exclude "node_modules"

# Include only specific patterns
folder-profiler analyze /path/to/folder --include "*.py" --include "*.js"

# Combine options
folder-profiler analyze ~/projects \
  --format html \
  --output analysis.html \
  --max-depth 5 \
  --exclude "venv" \
  --exclude ".git"
```

## Features in Detail

### File System Scanning

- Recursive directory traversal with depth control
- Cross-platform path handling (Windows, macOS, Linux)
- Symbolic link and junction point detection
- Respect for `.gitignore` and custom ignore patterns
- Graceful handling of permission errors

### Analysis Capabilities

- **Basic Statistics**: File/folder counts, size distributions, type breakdowns
- **Advanced Metrics**: Age distributions, depth analysis, growth rates
- **Pattern Detection**: Naming conventions, version schemes, temporary files
- **Duplicate Detection**: Exact matches via hashing, near-duplicates via ML
- **Content Analysis**: MIME type detection, file classification

### Reporting

- **JSON**: Machine-readable format for integration
- **HTML**: Interactive reports with charts and visualizations
- **PDF**: Professional reports for sharing (requires `reports` extras)

### AI Recommendations (v1.5+)

- Organization suggestions based on content analysis
- Security insights (sensitive data detection)
- Storage optimization recommendations
- Cleanup action lists with safety checks

## Configuration

Create a `.folder_profiler_ignore` file in your project root:

```gitignore
# Version control
.git/
.svn/

# Dependencies
node_modules/
venv/

# Build outputs
build/
dist/
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/folder-profiler/folder-profiler.git
cd folder-profiler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=folder_profiler --cov-report=html

# Run specific test
pytest tests/test_scanner/test_models.py

# Run only unit tests
pytest -m unit
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

## Project Status

**Current Version:** 0.1.0 (Alpha)

### Roadmap

- ✅ **v1.0** (MVP) - Core scanning, analysis, and reporting
- 🚧 **v1.5** - Advanced content analysis and AI recommendations
- 📅 **v2.0** - Web UI, real-time monitoring, plugin system

See [`.speckit/plan.md`](.speckit/plan.md) for detailed implementation plan.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Terminal UI powered by [Rich](https://rich.readthedocs.io/)
- ML features using [scikit-learn](https://scikit-learn.org/)

## Support

- **Documentation**: [https://folder-profiler.readthedocs.io](https://folder-profiler.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/folder-profiler/folder-profiler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/folder-profiler/folder-profiler/discussions)

---

**Made with ❤️ by the Folder Profiler Team**

