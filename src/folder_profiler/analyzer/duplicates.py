"""
Duplicate file detection.
"""

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from folder_profiler.scanner.models import FileInfo, FolderNode


class DuplicateDetector:
    """
    Detects exact and near-duplicate files.
    """

    def __init__(self, hash_algorithm: str = "sha256"):
        """
        Initialize duplicate detector.

        Args:
            hash_algorithm: Hash algorithm to use (sha256, md5, etc.)
        """
        self.hash_algorithm = hash_algorithm

    def find_duplicates(self, folder_tree: FolderNode) -> dict[str, Any]:
        """
        Find exact duplicate files.

        Args:
            folder_tree: Root folder node to analyze

        Returns:
            Dictionary with duplicate groups and statistics
        """
        all_files = self._collect_all_files(folder_tree)

        # Group files by size first (quick filter)
        size_groups = defaultdict(list)
        for file in all_files:
            if file.size > 0:  # Skip empty files
                size_groups[file.size].append(file)

        # Find duplicates by hashing files with same size
        hash_groups = defaultdict(list)
        duplicate_count = 0
        wasted_space = 0

        for _size, files in size_groups.items():
            if len(files) < 2:
                continue  # No potential duplicates

            # Hash all files of this size
            for file in files:
                try:
                    file_hash = self.hash_file(file.path)
                    hash_groups[file_hash].append(file)
                except OSError:
                    # Skip files we can't read
                    continue

        # Filter to only groups with duplicates
        duplicate_groups = {
            h: files for h, files in hash_groups.items() if len(files) > 1
        }

        # Calculate statistics
        for files in duplicate_groups.values():
            duplicate_count += len(files) - 1  # All but one are duplicates
            wasted_space += files[0].size * (len(files) - 1)

        return {
            "duplicate_groups": self._format_duplicate_groups(duplicate_groups),
            "statistics": {
                "total_duplicate_sets": len(duplicate_groups),
                "total_duplicate_files": duplicate_count,
                "wasted_space": wasted_space,
            },
        }

    def hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read (default 8KB)

        Returns:
            Hex digest of file hash
        """
        hasher = hashlib.new(self.hash_algorithm)

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _collect_all_files(self, folder_tree: FolderNode) -> list[FileInfo]:
        """Recursively collect all files from the folder tree."""
        all_files = []

        def collect(node: FolderNode) -> None:
            all_files.extend(node.files)
            for subfolder in node.subfolders:
                collect(subfolder)

        collect(folder_tree)
        return all_files

    def _format_duplicate_groups(
        self, duplicate_groups: dict[str, list[FileInfo]]
    ) -> list[dict[str, Any]]:
        """Format duplicate groups for output."""
        formatted = []

        for file_hash, files in duplicate_groups.items():
            formatted.append(
                {
                    "hash": file_hash,
                    "size": files[0].size,
                    "count": len(files),
                    "files": [
                        {
                            "path": str(f.path),
                            "name": f.name,
                        }
                        for f in files
                    ],
                }
            )

        # Sort by wasted space (size * (count - 1))
        formatted.sort(
            key=lambda x: cast(int, x["size"]) * (cast(int, x["count"]) - 1),
            reverse=True,
        )

        return formatted
