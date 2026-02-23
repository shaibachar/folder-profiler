"""
Pattern detection in file naming and organization.
"""

import re
from collections import defaultdict
from typing import Any, cast

from folder_profiler.scanner.models import FileInfo, FolderNode


class PatternDetector:
    """
    Detects patterns in file naming and organization.
    """

    def detect_patterns(self, folder_tree: FolderNode) -> dict[str, Any]:
        """
        Detect various patterns in file naming.

        Args:
            folder_tree: Root folder node to analyze

        Returns:
            Dictionary of detected patterns
        """
        all_files = self._collect_all_files(folder_tree)

        return {
            "version_patterns": self.detect_version_patterns(all_files),
            "temp_files": self._format_file_list(self.detect_temp_files(all_files)),
            "build_artifacts": self._format_file_list(
                self.detect_build_artifacts(all_files)
            ),
            "naming_conventions": self.detect_naming_conventions(all_files),
            "duplicate_names": self.detect_duplicate_names(all_files),
        }

    def detect_version_patterns(self, files: list[FileInfo]) -> list[dict[str, Any]]:
        """
        Detect version numbering patterns.

        Args:
            files: List of files to analyze

        Returns:
            List of detected version patterns
        """
        # Common version patterns
        version_patterns = [
            (
                r"(.+?)[-_\.]v?(\d+)\.(\d+)\.(\d+)",
                "semantic",
            ),  # file-v1.2.3 or file_1.2.3
            (r"(.+?)[-_\.]v?(\d+)\.(\d+)", "major_minor"),  # file-v1.2 or file_1.2
            (r"(.+?)[-_\.]v?(\d+)", "simple"),  # file-v1 or file_1
            (r"(.+?)\((\d+)\)", "increment"),  # file(1), file(2)
        ]

        version_groups = defaultdict(list)

        for file in files:
            name_without_ext = (
                file.name.rsplit(".", 1)[0] if "." in file.name else file.name
            )

            for pattern, version_type in version_patterns:
                match = re.match(pattern, name_without_ext)
                if match:
                    base_name = match.group(1)
                    version_groups[base_name].append(
                        {
                            "file": file.name,
                            "type": version_type,
                            "version": match.groups()[1:],
                        }
                    )
                    break

        # Filter to only groups with multiple versions
        result = []
        for base_name, versions in version_groups.items():
            if len(versions) > 1:
                result.append(
                    {
                        "base_name": base_name,
                        "count": len(versions),
                        "versions": versions,
                    }
                )

        return result

    def detect_temp_files(self, files: list[FileInfo]) -> list[FileInfo]:
        """
        Detect temporary and backup files.

        Args:
            files: List of files to analyze

        Returns:
            List of temporary/backup files
        """
        temp_extensions = {".tmp", ".bak", ".temp", ".swp", ".swo", ".~", ".cache"}
        temp_prefixes = {"~$", ".~"}
        temp_patterns = [
            r".*\.tmp$",
            r".*\.bak$",
            r".*~$",
            r"^\#.*\#$",  # Emacs auto-save files
        ]

        temp_files = []
        for file_info in files:
            # Check extension
            if file_info.extension and file_info.extension.lower() in temp_extensions:
                temp_files.append(file_info)
                continue

            # Check prefix
            if any(file_info.name.startswith(prefix) for prefix in temp_prefixes):
                temp_files.append(file_info)
                continue

            # Check patterns
            for pattern in temp_patterns:
                if re.match(pattern, file_info.name, re.IGNORECASE):
                    temp_files.append(file_info)
                    break

        return temp_files

    def detect_build_artifacts(self, files: list[FileInfo]) -> list[FileInfo]:
        """
        Detect build artifacts and generated files.

        Args:
            files: List of files to analyze

        Returns:
            List of build artifact files
        """
        artifact_extensions = {
            ".pyc",
            ".pyo",
            ".class",
            ".o",
            ".obj",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".jar",
            ".war",
            ".ear",
            ".whl",
            ".egg",
        }

        artifact_patterns = [
            r".*\.min\.js$",
            r".*\.min\.css$",
            r".*\.map$",
        ]

        artifacts = []
        for file_info in files:
            # Check extension
            if (
                file_info.extension
                and file_info.extension.lower() in artifact_extensions
            ):
                artifacts.append(file_info)
                continue

            # Check patterns
            for pattern in artifact_patterns:
                if re.match(pattern, file_info.name, re.IGNORECASE):
                    artifacts.append(file_info)
                    break

        return artifacts

    def detect_naming_conventions(self, files: list[FileInfo]) -> dict[str, int]:
        """
        Detect file naming conventions.

        Args:
            files: List of files to analyze

        Returns:
            Dictionary with counts of different naming conventions
        """
        conventions = {
            "snake_case": 0,
            "kebab-case": 0,
            "camelCase": 0,
            "PascalCase": 0,
            "UPPERCASE": 0,
            "lowercase": 0,
            "mixed": 0,
        }

        for file in files:
            name_without_ext = (
                file.name.rsplit(".", 1)[0] if "." in file.name else file.name
            )

            if re.match(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$", name_without_ext):
                conventions["snake_case"] += 1
            elif re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$", name_without_ext):
                conventions["kebab-case"] += 1
            elif re.match(r"^[a-z][a-zA-Z0-9]*$", name_without_ext) and any(
                c.isupper() for c in name_without_ext
            ):
                conventions["camelCase"] += 1
            elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name_without_ext):
                conventions["PascalCase"] += 1
            elif name_without_ext.isupper():
                conventions["UPPERCASE"] += 1
            elif name_without_ext.islower():
                conventions["lowercase"] += 1
            else:
                conventions["mixed"] += 1

        return conventions

    def detect_duplicate_names(self, files: list[FileInfo]) -> list[dict[str, Any]]:
        """
        Detect files with the same name in different locations.

        Args:
            files: List of files to analyze

        Returns:
            List of duplicate name groups
        """
        name_groups = defaultdict(list)

        for file in files:
            name_groups[file.name].append(file)

        # Filter to only duplicates
        duplicates = []
        for name, file_list in name_groups.items():
            if len(file_list) > 1:
                duplicates.append(
                    {
                        "name": name,
                        "count": len(file_list),
                        "locations": [str(f.path.parent) for f in file_list],
                    }
                )

        # Sort by count descending
        duplicates.sort(key=lambda x: cast(int, x["count"]), reverse=True)

        return duplicates

    def _collect_all_files(self, folder_tree: FolderNode) -> list[FileInfo]:
        """Recursively collect all files from the folder tree."""
        all_files = []

        def collect(node: FolderNode) -> None:
            all_files.extend(node.files)
            for subfolder in node.subfolders:
                collect(subfolder)

        collect(folder_tree)
        return all_files

    def _format_file_list(
        self, files: list[FileInfo], limit: int = 50
    ) -> list[dict[str, Any]]:
        """Format file list for output."""
        return [
            {
                "path": str(f.path),
                "name": f.name,
                "size": f.size,
            }
            for f in files[:limit]
        ]
