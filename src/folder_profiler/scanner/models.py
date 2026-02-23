"""
Data models for file system scanning.
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


@dataclass
class FileInfo:
    """
    Metadata for a single file.
    """

    path: Path
    name: str
    size: int
    created: datetime
    modified: datetime
    accessed: datetime
    extension: str
    mime_type: Optional[str] = None
    is_hidden: bool = False
    is_symlink: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": str(self.path),
            "name": self.name,
            "size": self.size,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "accessed": self.accessed.isoformat(),
            "extension": self.extension,
            "mime_type": self.mime_type,
            "is_hidden": self.is_hidden,
            "is_symlink": self.is_symlink,
        }


@dataclass
class FolderNode:
    """
    Represents a folder in the file tree.
    """

    path: Path
    name: str
    depth: int
    files: List[FileInfo] = field(default_factory=list)
    subfolders: List["FolderNode"] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        """Calculate total size of all files in this folder and subfolders."""
        file_size = sum(f.size for f in self.files)
        subfolder_size = sum(sf.total_size for sf in self.subfolders)
        return file_size + subfolder_size

    @property
    def total_files(self) -> int:
        """Count total files in this folder and subfolders."""
        return len(self.files) + sum(sf.total_files for sf in self.subfolders)

    @property
    def total_folders(self) -> int:
        """Count total subfolders (including nested)."""
        return len(self.subfolders) + sum(sf.total_folders for sf in self.subfolders)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": str(self.path),
            "name": self.name,
            "depth": self.depth,
            "files": [f.to_dict() for f in self.files],
            "subfolders": [sf.to_dict() for sf in self.subfolders],
            "total_size": self.total_size,
            "total_files": self.total_files,
            "total_folders": self.total_folders,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
