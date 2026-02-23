"""
Ignore pattern handling (.gitignore-style patterns).
"""

import fnmatch
from pathlib import Path


class IgnorePatternMatcher:
    """
    Handles .gitignore-style ignore patterns.
    """

    def __init__(self, patterns: list[str]):
        """
        Initialize with a list of ignore patterns.

        Args:
            patterns: List of glob-style patterns
        """
        self.patterns = patterns

    def should_ignore(self, path: Path, is_dir: bool = False) -> bool:
        """
        Check if a path should be ignored.

        Args:
            path: Path to check
            is_dir: Whether the path is a directory

        Returns:
            True if the path should be ignored
        """
        path_str = str(path)
        name = path.name

        for pattern in self.patterns:
            # Directory-specific pattern
            if pattern.endswith("/"):
                if is_dir and fnmatch.fnmatch(name, pattern.rstrip("/")):
                    return True
            # General pattern
            elif fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path_str, pattern):
                return True

        return False

    @staticmethod
    def from_file(ignore_file: Path) -> "IgnorePatternMatcher":
        """
        Load ignore patterns from a file.

        Args:
            ignore_file: Path to ignore file (.gitignore, etc.)

        Returns:
            IgnorePatternMatcher instance
        """
        patterns = []
        if ignore_file.exists():
            with open(ignore_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return IgnorePatternMatcher(patterns)
