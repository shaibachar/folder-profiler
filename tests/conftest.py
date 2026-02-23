"""
Test configuration and fixtures.
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from folder_profiler.scanner.models import FileInfo, FolderNode


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_file_info():
    """Create a sample FileInfo object for testing."""
    return FileInfo(
        path=Path("/test/sample.txt"),
        name="sample.txt",
        size=1024,
        created=datetime(2024, 1, 1, 12, 0, 0),
        modified=datetime(2024, 1, 2, 12, 0, 0),
        accessed=datetime(2024, 1, 3, 12, 0, 0),
        extension=".txt",
        mime_type="text/plain",
        is_hidden=False,
        is_symlink=False,
    )


@pytest.fixture
def sample_folder_node(sample_file_info):
    """Create a sample FolderNode for testing."""
    return FolderNode(
        path=Path("/test"),
        name="test",
        depth=0,
        files=[sample_file_info],
        subfolders=[],
    )


def make_file_info(path, name, size, extension="", mime_type=None, modified=None):
    """
    Helper function to create FileInfo objects with sensible defaults.

    Args:
        path: File path
        name: File name
        size: File size in bytes
        extension: File extension (default: "")
        mime_type: MIME type (default: None)
        modified: Modified datetime (default: now)

    Returns:
        FileInfo instance
    """
    if modified is None:
        modified = datetime.now()

    return FileInfo(
        path=path,
        name=name,
        size=size,
        created=modified,
        modified=modified,
        accessed=modified,
        extension=extension,
        mime_type=mime_type,
        is_hidden=False,
        is_symlink=False,
    )


@pytest.fixture
def create_test_structure(temp_dir):
    """
    Factory fixture to create test folder structures.

    Usage:
        structure = create_test_structure({
            "file1.txt": "content1",
            "dir1": {
                "file2.txt": "content2",
            }
        })
    """

    def _create_structure(structure, base_path=None):
        if base_path is None:
            base_path = temp_dir

        for name, content in structure.items():
            path = base_path / name

            if isinstance(content, dict):
                # It's a directory
                path.mkdir(parents=True, exist_ok=True)
                _create_structure(content, path)
            else:
                # It's a file
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    path.write_bytes(content)
                else:
                    path.write_text(str(content), encoding="utf-8")

        return base_path

    return _create_structure
