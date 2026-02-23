"""
Unit tests for ignore pattern matching.
"""

from pathlib import Path

from folder_profiler.scanner.ignore_patterns import IgnorePatternMatcher


class TestIgnorePatternMatcher:
    """Test IgnorePatternMatcher class."""

    def test_simple_pattern_match(self):
        """Test simple pattern matching."""
        matcher = IgnorePatternMatcher(["*.pyc", "*.tmp"])

        assert matcher.should_ignore(Path("test.pyc"))
        assert matcher.should_ignore(Path("test.tmp"))
        assert not matcher.should_ignore(Path("test.py"))

    def test_directory_pattern_match(self):
        """Test directory-specific patterns."""
        matcher = IgnorePatternMatcher(["__pycache__/", "node_modules/"])

        assert matcher.should_ignore(Path("__pycache__"), is_dir=True)
        assert matcher.should_ignore(Path("node_modules"), is_dir=True)
        assert not matcher.should_ignore(Path("__pycache__"), is_dir=False)

    def test_wildcard_patterns(self):
        """Test wildcard patterns."""
        matcher = IgnorePatternMatcher(["test_*"])

        assert matcher.should_ignore(Path("test_file.txt"))
        assert matcher.should_ignore(Path("test_data.json"))
        assert not matcher.should_ignore(Path("file_test.txt"))

    def test_empty_patterns(self):
        """Test with no patterns."""
        matcher = IgnorePatternMatcher([])

        assert not matcher.should_ignore(Path("anything.txt"))

    def test_from_file_nonexistent(self, temp_dir):
        """Test loading from non-existent file."""
        matcher = IgnorePatternMatcher.from_file(temp_dir / ".gitignore")

        assert len(matcher.patterns) == 0

    def test_from_file_with_content(self, temp_dir):
        """Test loading from file with patterns."""
        ignore_file = temp_dir / ".gitignore"
        ignore_file.write_text("*.pyc\n__pycache__/\n# comment\n\n*.tmp")

        matcher = IgnorePatternMatcher.from_file(ignore_file)

        assert len(matcher.patterns) == 3
        assert "*.pyc" in matcher.patterns
        assert "__pycache__/" in matcher.patterns
        assert "*.tmp" in matcher.patterns
        assert "# comment" not in matcher.patterns
