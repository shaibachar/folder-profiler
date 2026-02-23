"""
File system scanner module.

Handles folder traversal, metadata collection, and ignore pattern processing.
"""

from folder_profiler.scanner.models import FileInfo, FolderNode
from folder_profiler.scanner.scanner import FolderScanner

__all__ = ["FolderScanner", "FileInfo", "FolderNode"]
