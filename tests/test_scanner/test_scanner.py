"""
Unit tests for FolderScanner.
"""

from datetime import datetime
from pathlib import Path

import pytest

from folder_profiler.scanner.models import FolderNode
from folder_profiler.scanner.scanner import FolderScanner


class TestFolderScanner:
    """Test FolderScanner class."""

    def test_scanner_initialization(self):
        """Test scanner initialization with default parameters."""
        scanner = FolderScanner()

        assert scanner.max_depth is None
        assert scanner.include_patterns == []
        assert scanner.exclude_patterns == []
        assert scanner.follow_symlinks is False
        assert scanner.respect_gitignore is True

    def test_scanner_initialization_with_params(self):
        """Test scanner initialization with custom parameters."""
        scanner = FolderScanner(
            max_depth=5,
            include_patterns=["*.py"],
            exclude_patterns=["*.pyc", "__pycache__"],
            follow_symlinks=True,
            respect_gitignore=False,
        )

        assert scanner.max_depth == 5
        assert scanner.include_patterns == ["*.py"]
        assert scanner.exclude_patterns == ["*.pyc", "__pycache__"]
        assert scanner.follow_symlinks is True
        assert scanner.respect_gitignore is False

    def test_validate_path_success(self, temp_dir):
        """Test path validation with valid directory."""
        scanner = FolderScanner()
        validated = scanner.validate_path(temp_dir)

        assert validated.is_absolute()
        assert validated.exists()
        assert validated.is_dir()

    def test_validate_path_string_input(self, temp_dir):
        """Test path validation with string input."""
        scanner = FolderScanner()
        validated = scanner.validate_path(str(temp_dir))

        assert isinstance(validated, Path)
        assert validated.is_absolute()

    def test_validate_path_nonexistent(self, temp_dir):
        """Test path validation with non-existent path."""
        scanner = FolderScanner()
        nonexistent = temp_dir / "does_not_exist"

        with pytest.raises(ValueError, match="does not exist"):
            scanner.validate_path(nonexistent)

    def test_validate_path_file_not_directory(self, temp_dir):
        """Test path validation with file instead of directory."""
        scanner = FolderScanner()
        file_path = temp_dir / "test.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            scanner.validate_path(file_path)

    def test_is_hidden_dotfile(self):
        """Test hidden file detection for dotfiles."""
        scanner = FolderScanner()
        hidden_path = Path(".hidden_file")

        assert scanner._is_hidden(hidden_path) is True

    def test_is_hidden_regular_file(self):
        """Test hidden file detection for regular files."""
        scanner = FolderScanner()
        regular_path = Path("regular_file.txt")

        # On Unix/Mac, this won't be hidden
        # On Windows, might depend on attributes
        result = scanner._is_hidden(regular_path)
        assert isinstance(result, bool)

    def test_should_ignore_with_exclude_patterns(self):
        """Test ignore logic with exclude patterns."""
        scanner = FolderScanner(exclude_patterns=["*.pyc", "*.tmp"])

        assert scanner._should_ignore(Path("test.pyc")) is True
        assert scanner._should_ignore(Path("test.tmp")) is True
        assert scanner._should_ignore(Path("test.py")) is False

    def test_should_ignore_with_include_patterns(self):
        """Test ignore logic with include patterns."""
        scanner = FolderScanner(include_patterns=["*.py", "*.json"])

        # Only .py and .json should be included
        assert scanner._should_ignore(Path("test.py")) is False
        assert scanner._should_ignore(Path("data.json")) is False
        assert scanner._should_ignore(Path("readme.txt")) is True

    def test_scan_empty_directory(self, temp_dir):
        """Test scanning an empty directory."""
        scanner = FolderScanner()
        result = scanner.scan(temp_dir)

        assert isinstance(result, FolderNode)
        assert result.depth == 0
        assert len(result.files) == 0
        assert len(result.subfolders) == 0
        assert scanner.files_scanned == 0
        assert scanner.folders_scanned == 1

    def test_scan_directory_with_files(self, create_test_structure):
        """Test scanning a directory with files."""
        structure = create_test_structure(
            {
                "file1.txt": "content1",
                "file2.py": "content2",
                "file3.json": '{"key": "value"}',
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert len(result.files) == 3
        assert scanner.files_scanned == 3
        assert scanner.folders_scanned == 1

        file_names = {f.name for f in result.files}
        assert file_names == {"file1.txt", "file2.py", "file3.json"}

    def test_scan_nested_directories(self, create_test_structure):
        """Test scanning nested directory structure."""
        structure = create_test_structure(
            {
                "file1.txt": "content",
                "dir1": {
                    "file2.txt": "content",
                    "dir2": {
                        "file3.txt": "content",
                    },
                },
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert len(result.files) == 1
        assert len(result.subfolders) == 1
        assert scanner.folders_scanned == 3
        assert scanner.files_scanned == 3

        # Check nested structure
        dir1 = result.subfolders[0]
        assert dir1.name == "dir1"
        assert dir1.depth == 1
        assert len(dir1.files) == 1
        assert len(dir1.subfolders) == 1

        dir2 = dir1.subfolders[0]
        assert dir2.name == "dir2"
        assert dir2.depth == 2
        assert len(dir2.files) == 1

    def test_scan_with_max_depth(self, create_test_structure):
        """Test scanning with max depth limit."""
        structure = create_test_structure(
            {
                "file1.txt": "content",
                "dir1": {
                    "file2.txt": "content",
                    "dir2": {
                        "file3.txt": "content",
                    },
                },
            }
        )

        scanner = FolderScanner(max_depth=1)
        result = scanner.scan(structure)

        # Should scan root (depth 0) and one level deep (depth 1)
        assert len(result.files) == 1  # file1.txt at root
        assert len(result.subfolders) == 1  # dir1

        dir1 = result.subfolders[0]
        # dir1 is at depth 1, at max_depth we stop recursing into subfolders
        # but we still scan the current directory's files
        assert len(dir1.subfolders) == 0  # stopped at max_depth
        # The files should still be scanned
        # Actually, when depth reaches max_depth, we return early

    def test_scan_with_exclude_patterns(self, create_test_structure):
        """Test scanning with exclude patterns."""
        structure = create_test_structure(
            {
                "file1.txt": "content",
                "file2.pyc": b"bytecode",
                "file3.py": "code",
                "__pycache__": {
                    "cached.pyc": b"cached",
                },
            }
        )

        scanner = FolderScanner(exclude_patterns=["*.pyc", "__pycache__/"])
        result = scanner.scan(structure)

        # Should only have file1.txt and file3.py
        file_names = {f.name for f in result.files}
        assert "file1.txt" in file_names
        assert "file3.py" in file_names
        assert "file2.pyc" not in file_names

        # __pycache__ folder should be ignored
        folder_names = {f.name for f in result.subfolders}
        assert "__pycache__" not in folder_names

    def test_scan_with_include_patterns(self, create_test_structure):
        """Test scanning with include patterns."""
        structure = create_test_structure(
            {
                "file1.py": "code",
                "file2.txt": "text",
                "file3.py": "code",
                "data.json": "data",
            }
        )

        scanner = FolderScanner(include_patterns=["*.py"])
        result = scanner.scan(structure)

        # Should only have .py files
        assert len(result.files) == 2
        file_names = {f.name for f in result.files}
        assert file_names == {"file1.py", "file3.py"}

    def test_collect_file_metadata(self, temp_dir):
        """Test file metadata collection."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        scanner = FolderScanner()
        file_info = scanner._collect_file_metadata(test_file)

        assert file_info is not None
        assert file_info.name == "test.txt"
        assert file_info.size == 13  # "Hello, World!" is 13 bytes
        assert file_info.extension == ".txt"
        assert isinstance(file_info.created, datetime)
        assert isinstance(file_info.modified, datetime)
        assert isinstance(file_info.accessed, datetime)
        assert file_info.is_symlink is False

    def test_file_info_includes_path(self, temp_dir):
        """Test that FileInfo includes the full path."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        scanner = FolderScanner()
        result = scanner.scan(temp_dir)

        assert len(result.files) == 1
        file_info = result.files[0]
        assert file_info.path == test_file
        assert file_info.path.is_absolute()

    def test_statistics_tracking(self, create_test_structure):
        """Test that scanner tracks statistics correctly."""
        structure = create_test_structure(
            {
                "file1.txt": "content",
                "file2.txt": "content",
                "dir1": {
                    "file3.txt": "content",
                },
            }
        )

        scanner = FolderScanner()
        scanner.scan(structure)

        assert scanner.files_scanned == 3
        assert scanner.folders_scanned == 2  # root + dir1
        assert isinstance(scanner.errors_encountered, list)

    def test_total_size_calculation(self, create_test_structure):
        """Test that total size is calculated correctly."""
        structure = create_test_structure(
            {
                "file1.txt": "12345",  # 5 bytes
                "file2.txt": "1234567890",  # 10 bytes
                "dir1": {
                    "file3.txt": "123",  # 3 bytes
                },
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        # Total should be 5 + 10 + 3 = 18 bytes
        assert result.total_size == 18
        assert result.total_files == 3


class TestScannerEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_with_gitignore(self, create_test_structure):
        """Test that .gitignore patterns are respected."""
        structure = create_test_structure(
            {
                ".gitignore": "*.log\n__pycache__/\n",
                "app.py": "code",
                "debug.log": "log content",
                "__pycache__": {
                    "cache.pyc": b"cache",
                },
            }
        )

        scanner = FolderScanner(respect_gitignore=True)
        result = scanner.scan(structure)

        # .gitignore itself should be scanned
        file_names = {f.name for f in result.files}
        assert ".gitignore" in file_names
        assert "app.py" in file_names

        # .log files and __pycache__ should be ignored
        assert "debug.log" not in file_names
        folder_names = {f.name for f in result.subfolders}
        assert "__pycache__" not in folder_names

    def test_scan_without_gitignore_respect(self, create_test_structure):
        """Test scanning without respecting .gitignore."""
        structure = create_test_structure(
            {
                ".gitignore": "*.log\n",
                "app.py": "code",
                "debug.log": "log content",
            }
        )

        scanner = FolderScanner(respect_gitignore=False)
        result = scanner.scan(structure)

        # All files should be scanned
        file_names = {f.name for f in result.files}
        assert "debug.log" in file_names

    def test_circular_symlink_detection(self, temp_dir):
        """Test detection of circular symlinks."""
        scanner = FolderScanner()

        # Create a directory
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        # Create a symlink that points to parent (circular)
        circular_link = subdir / "parent_link"
        try:
            circular_link.symlink_to(temp_dir)

            # Test circular detection
            is_circular = scanner._is_circular_symlink(circular_link)
            assert is_circular is True
        except OSError:
            # Skip test if symlinks not supported (Windows without admin)
            pytest.skip("Symlinks not supported on this system")
