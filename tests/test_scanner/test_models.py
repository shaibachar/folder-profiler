"""
Unit tests for scanner models.
"""

import json
from datetime import datetime
from pathlib import Path

from folder_profiler.scanner.models import FileInfo, FolderNode


class TestFileInfo:
    """Test FileInfo model."""

    def test_create_file_info(self):
        """Test creating a FileInfo instance."""
        fi = FileInfo(
            path=Path("/test/file.txt"),
            name="file.txt",
            size=100,
            created=datetime(2024, 1, 1),
            modified=datetime(2024, 1, 2),
            accessed=datetime(2024, 1, 3),
            extension=".txt",
        )

        assert fi.name == "file.txt"
        assert fi.size == 100
        assert fi.extension == ".txt"
        assert not fi.is_hidden
        assert not fi.is_symlink

    def test_file_info_to_dict(self, sample_file_info):
        """Test FileInfo dictionary serialization."""
        data = sample_file_info.to_dict()

        assert data["name"] == "sample.txt"
        assert data["size"] == 1024
        assert data["extension"] == ".txt"
        assert data["mime_type"] == "text/plain"
        assert "created" in data
        assert "modified" in data
        assert "accessed" in data


class TestFolderNode:
    """Test FolderNode model."""

    def test_create_folder_node(self):
        """Test creating a FolderNode instance."""
        node = FolderNode(
            path=Path("/test"),
            name="test",
            depth=0,
        )

        assert node.name == "test"
        assert node.depth == 0
        assert len(node.files) == 0
        assert len(node.subfolders) == 0

    def test_folder_node_total_size(self, sample_file_info):
        """Test total size calculation."""
        node = FolderNode(
            path=Path("/test"),
            name="test",
            depth=0,
            files=[sample_file_info],
        )

        assert node.total_size == 1024

    def test_folder_node_nested_size(self, sample_file_info):
        """Test total size with nested folders."""
        child = FolderNode(
            path=Path("/test/child"),
            name="child",
            depth=1,
            files=[sample_file_info],
        )

        parent = FolderNode(
            path=Path("/test"),
            name="test",
            depth=0,
            files=[sample_file_info],
            subfolders=[child],
        )

        assert parent.total_size == 2048  # 1024 * 2

    def test_folder_node_total_files(self, sample_file_info):
        """Test file count calculation."""
        child = FolderNode(
            path=Path("/test/child"),
            name="child",
            depth=1,
            files=[sample_file_info, sample_file_info],
        )

        parent = FolderNode(
            path=Path("/test"),
            name="test",
            depth=0,
            files=[sample_file_info],
            subfolders=[child],
        )

        assert parent.total_files == 3

    def test_folder_node_total_folders(self):
        """Test folder count calculation."""
        grandchild = FolderNode(
            path=Path("/test/child/grandchild"),
            name="grandchild",
            depth=2,
        )

        child = FolderNode(
            path=Path("/test/child"),
            name="child",
            depth=1,
            subfolders=[grandchild],
        )

        parent = FolderNode(
            path=Path("/test"),
            name="test",
            depth=0,
            subfolders=[child],
        )

        assert parent.total_folders == 2

    def test_folder_node_to_dict(self, sample_folder_node):
        """Test FolderNode dictionary serialization."""
        data = sample_folder_node.to_dict()

        assert data["name"] == "test"
        assert data["depth"] == 0
        assert len(data["files"]) == 1
        assert data["total_size"] == 1024
        assert data["total_files"] == 1
        assert data["total_folders"] == 0

    def test_folder_node_to_json(self, sample_folder_node):
        """Test FolderNode JSON serialization."""
        json_str = sample_folder_node.to_json()
        data = json.loads(json_str)

        assert data["name"] == "test"
        assert isinstance(json_str, str)
