"""
Core folder scanning implementation.
"""

import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional

from folder_profiler.scanner.ignore_patterns import IgnorePatternMatcher
from folder_profiler.scanner.models import FileInfo, FolderNode

try:
    import magic
except ImportError:
    magic = None


class FolderScanner:
    """
    Scans folder structures and collects file metadata.
    """

    def __init__(
        self,
        max_depth: Optional[int] = None,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        follow_symlinks: bool = False,
        respect_gitignore: bool = True,
    ):
        """
        Initialize the folder scanner.

        Args:
            max_depth: Maximum depth to scan (None for unlimited)
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            follow_symlinks: Whether to follow symbolic links
            respect_gitignore: Whether to respect .gitignore files
        """
        self.max_depth = max_depth
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.follow_symlinks = follow_symlinks
        self.respect_gitignore = respect_gitignore

        # Initialize ignore pattern matcher
        self._ignore_matcher = IgnorePatternMatcher(self.exclude_patterns)

        # Statistics
        self.files_scanned = 0
        self.folders_scanned = 0
        self.errors_encountered: list[str] = []

    def validate_path(self, path: Path) -> Path:
        """
        Validate and normalize a path.

        Args:
            path: Path to validate

        Returns:
            Normalized absolute Path

        Raises:
            ValueError: If path is invalid or doesn't exist
            PermissionError: If path is not accessible
        """
        # Convert to Path object if string
        if isinstance(path, str):
            path = Path(path)

        # Resolve to absolute path
        try:
            path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {e}") from e

        # Check if path exists
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        # Check if it's a directory
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Check if we have read permissions
        if not os.access(path, os.R_OK):
            raise PermissionError(f"No read permission for path: {path}")

        return path

    def scan(self, path: Path) -> FolderNode:
        """
        Scan a folder and return the folder tree.

        Args:
            path: Path to scan

        Returns:
            Root FolderNode containing the complete tree

        Raises:
            ValueError: If path is invalid
            PermissionError: If path is not accessible
        """
        # Validate path (SCAN-001)
        validated_path = self.validate_path(path)

        # Reset statistics
        self.files_scanned = 0
        self.folders_scanned = 0
        self.errors_encountered = []

        # Load .gitignore if requested
        if self.respect_gitignore:
            self._load_gitignore(validated_path)

        # Scan the tree (SCAN-002, SCAN-004, SCAN-005)
        root_node = self._scan_directory(validated_path, depth=0)

        return root_node

    def _load_gitignore(self, root_path: Path) -> None:
        """
        Load .gitignore patterns from the root directory.

        Args:
            root_path: Root directory to check for .gitignore
        """
        gitignore_file = root_path / ".gitignore"
        if gitignore_file.exists():
            gitignore_matcher = IgnorePatternMatcher.from_file(gitignore_file)
            # Merge with existing patterns
            self._ignore_matcher.patterns.extend(gitignore_matcher.patterns)

        # Also check for .folder_profiler_ignore
        custom_ignore = root_path / ".folder_profiler_ignore"
        if custom_ignore.exists():
            custom_matcher = IgnorePatternMatcher.from_file(custom_ignore)
            self._ignore_matcher.patterns.extend(custom_matcher.patterns)

    def _scan_directory(self, dir_path: Path, depth: int) -> FolderNode:
        """
        Recursively scan a directory and build folder tree.

        Args:
            dir_path: Directory to scan
            depth: Current depth in the tree

        Returns:
            FolderNode for this directory
        """
        self.folders_scanned += 1

        # Create folder node
        node = FolderNode(
            path=dir_path,
            name=dir_path.name or str(dir_path),
            depth=depth,
        )

        try:
            # Iterate through directory contents
            for entry in dir_path.iterdir():
                try:
                    # Check if should be ignored
                    if self._should_ignore(entry):
                        continue

                    # Handle symbolic links
                    if entry.is_symlink():
                        if not self.follow_symlinks:
                            continue
                        # Detect circular symlinks
                        if self._is_circular_symlink(entry):
                            continue

                    # Process based on type
                    if entry.is_file():
                        file_info = self._collect_file_metadata(entry)
                        if file_info:
                            node.files.append(file_info)
                            self.files_scanned += 1

                    elif entry.is_dir():
                        # Check depth limit before recursing
                        if self.max_depth is not None and depth >= self.max_depth:
                            # At max depth, don't recurse into subdirectories
                            continue
                        # Recursively scan subdirectory
                        subfolder = self._scan_directory(entry, depth + 1)
                        node.subfolders.append(subfolder)

                except PermissionError:
                    self.errors_encountered.append(f"Permission denied: {entry}")
                except OSError as e:
                    self.errors_encountered.append(f"OS error scanning {entry}: {e}")

        except PermissionError:
            self.errors_encountered.append(f"Permission denied: {dir_path}")
        except OSError as e:
            self.errors_encountered.append(f"OS error scanning {dir_path}: {e}")

        return node

    def _should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on patterns.

        Args:
            path: Path to check

        Returns:
            True if path should be ignored
        """
        is_dir = path.is_dir()

        # Check against ignore patterns
        if self._ignore_matcher.should_ignore(path, is_dir):
            return True

        # If include patterns specified, check if path matches
        if self.include_patterns:
            matches_include = False
            for pattern in self.include_patterns:
                if path.match(pattern):
                    matches_include = True
                    break
            if not matches_include:
                return True

        return False

    def _is_circular_symlink(self, path: Path) -> bool:
        """
        Check if a symlink creates a circular reference.

        Args:
            path: Symlink path to check

        Returns:
            True if symlink is circular
        """
        try:
            resolved = path.resolve()
            current = path.parent

            while current != current.parent:
                if resolved == current:
                    return True
                current = current.parent

            return False
        except (OSError, RuntimeError):
            return True

    def _collect_file_metadata(self, file_path: Path) -> Optional[FileInfo]:
        """
        Collect metadata for a single file.

        Args:
            file_path: Path to file

        Returns:
            FileInfo object with metadata, or None if file cannot be accessed
        """
        try:
            stat = file_path.stat()

            # Get timestamps
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)
            accessed = datetime.fromtimestamp(stat.st_atime)

            # Get extension
            extension = file_path.suffix.lower()

            # Get MIME type if magic is available
            mime_type = None
            if magic is not None:
                try:
                    mime_type = magic.from_file(str(file_path), mime=True)
                except Exception:
                    pass

            # Check if hidden
            is_hidden = self._is_hidden(file_path)

            # Create FileInfo
            file_info = FileInfo(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                created=created,
                modified=modified,
                accessed=accessed,
                extension=extension,
                mime_type=mime_type,
                is_hidden=is_hidden,
                is_symlink=file_path.is_symlink(),
            )

            return file_info

        except (PermissionError, OSError) as e:
            self.errors_encountered.append(
                f"Cannot read file metadata: {file_path} - {e}"
            )
            return None

    def _is_hidden(self, path: Path) -> bool:
        """
        Check if a file or directory is hidden.

        Args:
            path: Path to check

        Returns:
            True if hidden
        """
        # Unix/Linux/Mac: starts with dot
        if path.name.startswith("."):
            return True

        # Windows: check hidden attribute
        if platform.system() == "Windows":
            try:
                import ctypes

                FILE_ATTRIBUTE_HIDDEN = 0x02
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
            except Exception:
                pass

        return False
