# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Action execution (delete, move, rename files)
- Incremental analysis with SQLite caching
- Near-duplicate detection (text/image similarity)
- PDF report generation
- Deep content analysis
- Web UI dashboard

## [1.0.0] - 2026-02-23

### Added
- **File System Scanner**
  - Recursive directory traversal with configurable depth limits
  - Cross-platform path handling (Windows, macOS, Linux)
  - Symbolic link and junction point detection
  - Support for .gitignore-style ignore patterns
  - Custom include/exclude patterns via CLI
  - Graceful permission error handling

- **Statistics & Analysis**
  - Comprehensive file and folder statistics
  - File type and extension distribution analysis
  - Age distribution analysis
  - Depth analysis (files per directory level)
  - Largest files and folders detection
  - Pattern detection (naming conventions, versioning, temp files, build artifacts)

- **Duplicate Detection**
  - Exact duplicate detection using SHA-256 hashing
  - Streaming hash calculation for memory efficiency
  - Wasted space calculation
  - Duplicate groups ranked by impact

- **Smart Recommendations**
  - AI-powered recommendation engine with 5 types and 5 priority levels
  - Actionable suggestions for folder optimization
  - Impact estimation (space savings, affected files)
  - Duplicate file cleanup recommendations
  - Temporary file detection and cleanup suggestions
  - Build artifact cleanup recommendations
  - Deep folder nesting warnings
  - Version pattern detection (suggest Git instead of manual versioning)

- **Folder Health Scoring**
  - 0-100 health score based on folder quality
  - Weighted scoring across multiple dimensions
  - Health summary (Excellent, Good, Fair, Poor, Critical)

- **Reporting Formats**
  - Console: Rich-formatted terminal output with colored tables
  - JSON: Machine-readable format with complete analysis data
  - HTML: Styled web reports with health scores and recommendations

- **Command-Line Interface**
  - `analyze` command with comprehensive options
  - Progress indicators during scanning and analysis
  - Format selection, output file specification, depth control
  - Include/exclude pattern support

- **Testing & Quality**
  - 106 test cases with 87% overall coverage
  - CI/CD pipeline with multi-OS testing (Ubuntu, Windows, macOS)
  - Multi-Python version testing (3.9, 3.10, 3.11, 3.12)
  - Code formatting (Black, isort), linting (Ruff), type checking (mypy)

### Fixed
- Windows short path (8.3 format) handling in tests
- Circular symlink detection on Windows
- Type annotation issues for cross-platform compatibility
- Import errors for optional dependencies (beautifulsoup4)

## [0.1.0] - 2026-02-23

### Added
- Project initialization
- Basic package structure
- Core module scaffolding

[Unreleased]: https://github.com/folder-profiler/folder-profiler/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/folder-profiler/folder-profiler/releases/tag/v1.0.0
[0.1.0]: https://github.com/folder-profiler/folder-profiler/releases/tag/v0.1.0
