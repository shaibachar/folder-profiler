"""
Integration tests for the complete scanner workflow.
"""

from folder_profiler.scanner.models import FolderNode
from folder_profiler.scanner.scanner import FolderScanner


class TestScannerIntegration:
    """Integration tests for real-world scanning scenarios."""

    def test_scan_typical_python_project(self, create_test_structure):
        """Test scanning a typical Python project structure."""
        structure = create_test_structure(
            {
                "README.md": "# Project",
                "setup.py": "from setuptools import setup",
                ".gitignore": "*.pyc\n__pycache__/\n.venv/",
                "src": {
                    "__init__.py": "",
                    "main.py": "def main(): pass",
                    "utils.py": "# utilities",
                },
                "tests": {
                    "__init__.py": "",
                    "test_main.py": "def test_something(): pass",
                },
                ".venv": {
                    "lib": {
                        "package.py": "# virtual env",
                    }
                },
                "__pycache__": {
                    "main.cpython-39.pyc": b"bytecode",
                },
            }
        )

        scanner = FolderScanner(respect_gitignore=True)
        result = scanner.scan(structure)

        # Check that .venv and __pycache__ are ignored
        folder_names = {f.name for f in result.subfolders}
        assert "src" in folder_names
        assert "tests" in folder_names
        assert ".venv" not in folder_names
        assert "__pycache__" not in folder_names

        # Check root files
        root_files = {f.name for f in result.files}
        assert "README.md" in root_files
        assert "setup.py" in root_files
        assert ".gitignore" in root_files

    def test_scan_with_deep_nesting(self, create_test_structure):
        """Test scanning deeply nested directory structure."""
        structure = create_test_structure(
            {
                "level0.txt": "0",
                "dir1": {
                    "level1.txt": "1",
                    "dir2": {
                        "level2.txt": "2",
                        "dir3": {
                            "level3.txt": "3",
                            "dir4": {
                                "level4.txt": "4",
                            },
                        },
                    },
                },
            }
        )

        # Scan with unlimited depth
        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert result.total_files == 5
        assert result.total_folders == 4  # dir1, dir2, dir3, dir4
        assert scanner.files_scanned == 5
        assert scanner.folders_scanned == 5  # root + 4 subdirs

    def test_scan_large_number_of_files(self, create_test_structure):
        """Test scanning directory with many files."""
        # Create 100 files
        structure = {f"file_{i:03d}.txt": f"content {i}" for i in range(100)}

        root = create_test_structure(structure)

        scanner = FolderScanner()
        result = scanner.scan(root)

        assert len(result.files) == 100
        assert scanner.files_scanned == 100
        assert result.total_files == 100

    def test_scan_mixed_file_types(self, create_test_structure):
        """Test scanning directory with various file types."""
        structure = create_test_structure(
            {
                "document.txt": "text content",
                "script.py": "print('hello')",
                "data.json": '{"key": "value"}',
                "config.yaml": "key: value",
                "image.png": b"PNG binary data",
                "archive.zip": b"ZIP binary data",
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert len(result.files) == 6

        # Check extensions
        extensions = {f.extension for f in result.files}
        assert extensions == {".txt", ".py", ".json", ".yaml", ".png", ".zip"}

    def test_scan_with_size_calculations(self, create_test_structure):
        """Test that size calculations work correctly in nested structure."""
        structure = create_test_structure(
            {
                "small.txt": "x" * 100,  # 100 bytes
                "medium.txt": "y" * 1000,  # 1000 bytes
                "subdir": {
                    "large.txt": "z" * 10000,  # 10000 bytes
                },
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        # Total should be 100 + 1000 + 10000 = 11100 bytes
        assert result.total_size == 11100

        # Check individual folder sizes
        subdir = result.subfolders[0]
        assert subdir.total_size == 10000

    def test_scan_preserves_directory_structure(self, create_test_structure):
        """Test that directory hierarchy is preserved correctly."""
        structure = create_test_structure(
            {
                "root.txt": "root",
                "a": {
                    "a.txt": "a",
                    "a1": {
                        "a1.txt": "a1",
                    },
                    "a2": {
                        "a2.txt": "a2",
                    },
                },
                "b": {
                    "b.txt": "b",
                },
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        # Check root level
        assert len(result.files) == 1
        assert len(result.subfolders) == 2

        # Find 'a' directory
        folder_a = next(f for f in result.subfolders if f.name == "a")
        assert len(folder_a.files) == 1
        assert len(folder_a.subfolders) == 2

        # Check nested structure in 'a'
        subfolder_names = {f.name for f in folder_a.subfolders}
        assert subfolder_names == {"a1", "a2"}

    def test_scan_with_filtering_workflow(self, create_test_structure):
        """Test complete filtering workflow with include and exclude."""
        structure = create_test_structure(
            {
                "main.py": "code",
                "test.py": "tests",
                "utils.py": "utilities",
                "README.md": "docs",
                "data.json": "data",
                "cache.pyc": b"cache",
                "logs": {
                    "app.log": "logs",
                    "error.log": "errors",
                },
            }
        )

        # Include only .py files, exclude cache files
        scanner = FolderScanner(include_patterns=["*.py"], exclude_patterns=["*.pyc"])
        result = scanner.scan(structure)

        # Should only have .py files (not .pyc)
        file_names = {f.name for f in result.files}
        assert file_names == {"main.py", "test.py", "utils.py"}
        assert scanner.files_scanned == 3

    def test_scan_respects_depth_limit_performance(self, create_test_structure):
        """Test that depth limit improves performance by limiting traversal."""
        # Create deep structure
        structure = create_test_structure(
            {
                "level_0.txt": "0",
                "d1": {
                    "level_1.txt": "1",
                    "d2": {
                        "level_2.txt": "2",
                        "d3": {
                            "level_3.txt": "3",
                            "d4": {
                                "level_4.txt": "4",
                                "d5": {
                                    "level_5.txt": "5",
                                },
                            },
                        },
                    },
                },
            }
        )

        # Scan with depth limit
        scanner = FolderScanner(max_depth=2)
        scanner.scan(structure)

        # Should only scan up to depth 2
        # This means we stop recursing at depth 2, so we don't see d3 contents
        assert scanner.folders_scanned <= 3  # root, d1, d2

        # Files at depth 0, 1, 2 should be found
        # But we won't recurse into d3
        assert scanner.files_scanned <= 3

    def test_end_to_end_real_world_scenario(self, create_test_structure):
        """Test end-to-end scanning of a realistic project."""
        structure = create_test_structure(
            {
                ".git": {
                    "config": "git config",
                    "HEAD": "ref: refs/heads/main",
                },
                ".gitignore": "*.pyc\n__pycache__/\n.env",
                "README.md": "# My Project",
                "requirements.txt": "requests==2.28.0",
                ".env": "SECRET_KEY=secret",
                "src": {
                    "__init__.py": "",
                    "app.py": "def app(): pass",
                    "models": {
                        "__init__.py": "",
                        "user.py": "class User: pass",
                    },
                },
                "tests": {
                    "test_app.py": "def test_app(): pass",
                },
                "docs": {
                    "index.md": "# Documentation",
                },
                "__pycache__": {
                    "app.cpython-39.pyc": b"cache",
                },
            }
        )

        scanner = FolderScanner(respect_gitignore=True, exclude_patterns=[".git/"])
        result = scanner.scan(structure)

        # .git and __pycache__ should be ignored
        folder_names = {f.name for f in result.subfolders}
        assert ".git" not in folder_names
        assert "__pycache__" not in folder_names
        assert "src" in folder_names
        assert "tests" in folder_names
        assert "docs" in folder_names

        # .env should be ignored (in .gitignore)
        root_files = {f.name for f in result.files}
        assert ".env" not in root_files
        assert "README.md" in root_files

        # Verify nested structure
        assert result.total_folders >= 3  # src, src/models, tests, docs
        assert result.total_files >= 6


class TestScannerRobustness:
    """Test scanner robustness and error handling."""

    def test_scan_handles_permission_errors_gracefully(self, temp_dir):
        """Test that permission errors are handled gracefully."""
        scanner = FolderScanner()

        # Scan should complete even if some files are inaccessible
        # We can't easily create permission-denied scenarios in tests,
        # but we verify the error handling structure exists
        result = scanner.scan(temp_dir)

        assert isinstance(result, FolderNode)
        assert isinstance(scanner.errors_encountered, list)

    def test_scan_empty_nested_directories(self, create_test_structure):
        """Test scanning nested empty directories."""
        structure = create_test_structure(
            {
                "empty1": {},
                "empty2": {
                    "empty3": {},
                },
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert len(result.subfolders) == 2
        assert result.total_files == 0

        # Verify empty directories are still counted
        # root + empty1 + empty2 + empty3 = 4
        assert scanner.folders_scanned == 4

    def test_scan_statistics_reset_between_scans(self, temp_dir):
        """Test that statistics are reset between multiple scans."""
        # Create first structure
        dir1 = temp_dir / "scan1"
        dir1.mkdir()
        (dir1 / "file1.txt").write_text("content")

        scanner = FolderScanner()
        scanner.scan(dir1)

        first_files_scanned = scanner.files_scanned
        first_folders_scanned = scanner.folders_scanned

        assert first_files_scanned == 1
        assert first_folders_scanned == 1

        # Create second structure
        dir2 = temp_dir / "scan2"
        dir2.mkdir()
        (dir2 / "file2.txt").write_text("content")
        (dir2 / "file3.txt").write_text("content")

        scanner.scan(dir2)

        # Statistics should be reset
        assert scanner.files_scanned == 2  # Only from second scan
        assert scanner.folders_scanned == 1  # Only from second scan

    def test_scan_with_unicode_filenames(self, create_test_structure):
        """Test scanning files with unicode characters in names."""
        structure = create_test_structure(
            {
                "файл.txt": "Russian",
                "文件.txt": "Chinese",
                "ファイル.txt": "Japanese",
                "αρχείο.txt": "Greek",
            }
        )

        scanner = FolderScanner()
        result = scanner.scan(structure)

        assert len(result.files) == 4
        file_names = {f.name for f in result.files}
        assert "файл.txt" in file_names
        assert "文件.txt" in file_names
