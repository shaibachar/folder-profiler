"""
Statistics calculation for file systems.
"""

from folder_profiler.scanner.models import FolderNode, FileInfo
from typing import Dict, Any, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
import statistics


class StatisticsCalculator:
    """
    Calculates various statistics about folder structures.
    """

    def calculate(self, folder_tree: FolderNode) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics.

        Args:
            folder_tree: Root folder node

        Returns:
            Dictionary of statistics including:
            - File counts and sizes
            - File type distribution
            - Age distributions
            - Depth analysis
            - Folder sizes
            - Extension diversity
        """
        stats = {
            "summary": self._calculate_summary(folder_tree),
            "file_types": self._calculate_file_types(folder_tree),
            "extensions": self._calculate_extensions(folder_tree),
            "age_distribution": self._calculate_age_distribution(folder_tree),
            "size_distribution": self._calculate_size_distribution(folder_tree),
            "depth_analysis": self._calculate_depth_analysis(folder_tree),
            "largest_files": self._find_largest_files(folder_tree),
            "largest_folders": self._find_largest_folders(folder_tree),
            "oldest_files": self._find_oldest_files(folder_tree),
            "newest_files": self._find_newest_files(folder_tree),
        }
        return stats

    def _calculate_summary(self, folder_tree: FolderNode) -> Dict[str, Any]:
        """Calculate basic summary statistics."""
        all_files = self._collect_all_files(folder_tree)
        
        sizes = [f.size for f in all_files if f.size > 0]
        
        return {
            "total_files": folder_tree.total_files,
            "total_folders": folder_tree.total_folders,
            "total_size": folder_tree.total_size,
            "average_file_size": statistics.mean(sizes) if sizes else 0,
            "median_file_size": statistics.median(sizes) if sizes else 0,
            "largest_file_size": max(sizes) if sizes else 0,
            "smallest_file_size": min(sizes) if sizes else 0,
        }

    def _calculate_file_types(self, folder_tree: FolderNode) -> Dict[str, Dict[str, Any]]:
        """Calculate file type distribution by MIME type."""
        all_files = self._collect_all_files(folder_tree)
        
        type_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
        
        for file in all_files:
            mime_type = file.mime_type or "unknown"
            # Group by primary MIME type (e.g., "text", "image", "application")
            primary_type = mime_type.split("/")[0] if "/" in mime_type else mime_type
            
            type_stats[primary_type]["count"] += 1
            type_stats[primary_type]["total_size"] += file.size
        
        return dict(type_stats)

    def _calculate_extensions(self, folder_tree: FolderNode) -> Dict[str, Dict[str, Any]]:
        """Calculate file extension distribution."""
        all_files = self._collect_all_files(folder_tree)
        
        ext_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
        
        for file in all_files:
            ext = file.extension or "no_extension"
            ext_stats[ext]["count"] += 1
            ext_stats[ext]["total_size"] += file.size
        
        # Sort by count descending
        sorted_stats = dict(sorted(ext_stats.items(), key=lambda x: x[1]["count"], reverse=True))
        
        return sorted_stats

    def _calculate_age_distribution(self, folder_tree: FolderNode) -> Dict[str, int]:
        """Calculate file age distribution."""
        all_files = self._collect_all_files(folder_tree)
        now = datetime.now()
        
        age_buckets = {
            "last_24h": 0,
            "last_week": 0,
            "last_month": 0,
            "last_3_months": 0,
            "last_6_months": 0,
            "last_year": 0,
            "older_than_year": 0,
        }
        
        for file in all_files:
            if not file.modified:
                continue
                
            age = now - file.modified
            
            if age <= timedelta(days=1):
                age_buckets["last_24h"] += 1
            elif age <= timedelta(weeks=1):
                age_buckets["last_week"] += 1
            elif age <= timedelta(days=30):
                age_buckets["last_month"] += 1
            elif age <= timedelta(days=90):
                age_buckets["last_3_months"] += 1
            elif age <= timedelta(days=180):
                age_buckets["last_6_months"] += 1
            elif age <= timedelta(days=365):
                age_buckets["last_year"] += 1
            else:
                age_buckets["older_than_year"] += 1
        
        return age_buckets

    def _calculate_size_distribution(self, folder_tree: FolderNode) -> Dict[str, int]:
        """Calculate file size distribution."""
        all_files = self._collect_all_files(folder_tree)
        
        size_buckets = {
            "empty": 0,
            "tiny_1kb": 0,          # < 1 KB
            "small_10kb": 0,        # 1 KB - 10 KB
            "medium_100kb": 0,      # 10 KB - 100 KB
            "large_1mb": 0,         # 100 KB - 1 MB
            "xlarge_10mb": 0,       # 1 MB - 10 MB
            "xxlarge_100mb": 0,     # 10 MB - 100 MB
            "huge_1gb": 0,          # 100 MB - 1 GB
            "gigantic": 0,          # > 1 GB
        }
        
        for file in all_files:
            size = file.size
            
            if size == 0:
                size_buckets["empty"] += 1
            elif size < 1024:
                size_buckets["tiny_1kb"] += 1
            elif size < 10 * 1024:
                size_buckets["small_10kb"] += 1
            elif size < 100 * 1024:
                size_buckets["medium_100kb"] += 1
            elif size < 1024 * 1024:
                size_buckets["large_1mb"] += 1
            elif size < 10 * 1024 * 1024:
                size_buckets["xlarge_10mb"] += 1
            elif size < 100 * 1024 * 1024:
                size_buckets["xxlarge_100mb"] += 1
            elif size < 1024 * 1024 * 1024:
                size_buckets["huge_1gb"] += 1
            else:
                size_buckets["gigantic"] += 1
        
        return size_buckets

    def _calculate_depth_analysis(self, folder_tree: FolderNode) -> Dict[str, Any]:
        """Analyze folder depth distribution."""
        depth_files = defaultdict(int)
        depth_folders = defaultdict(int)
        depth_sizes = defaultdict(int)
        
        def analyze_depth(node: FolderNode, depth: int = 0):
            depth_folders[depth] += 1
            
            for file in node.files:
                depth_files[depth] += 1
                depth_sizes[depth] += file.size
            
            for subfolder in node.subfolders:
                analyze_depth(subfolder, depth + 1)
        
        analyze_depth(folder_tree)
        
        max_depth = max(depth_folders.keys()) if depth_folders else 0
        
        return {
            "max_depth": max_depth,
            "files_by_depth": dict(depth_files),
            "folders_by_depth": dict(depth_folders),
            "size_by_depth": dict(depth_sizes),
        }

    def _find_largest_files(self, folder_tree: FolderNode, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the largest files."""
        all_files = self._collect_all_files(folder_tree)
        
        sorted_files = sorted(all_files, key=lambda f: f.size, reverse=True)[:limit]
        
        return [
            {
                "path": str(f.path),
                "name": f.name,
                "size": f.size,
                "extension": f.extension,
            }
            for f in sorted_files
        ]

    def _find_largest_folders(self, folder_tree: FolderNode, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the largest folders."""
        all_folders = []
        
        def collect_folders(node: FolderNode):
            all_folders.append(node)
            for subfolder in node.subfolders:
                collect_folders(subfolder)
        
        collect_folders(folder_tree)
        
        sorted_folders = sorted(all_folders, key=lambda f: f.total_size, reverse=True)[:limit]
        
        return [
            {
                "path": str(f.path),
                "name": f.name,
                "size": f.total_size,
                "file_count": f.total_files,
                "folder_count": f.total_folders,
            }
            for f in sorted_folders
        ]

    def _find_oldest_files(self, folder_tree: FolderNode, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the oldest files by modification time."""
        all_files = self._collect_all_files(folder_tree)
        
        # Filter files with modification time
        files_with_time = [f for f in all_files if f.modified]
        
        sorted_files = sorted(files_with_time, key=lambda f: f.modified)[:limit]
        
        return [
            {
                "path": str(f.path),
                "name": f.name,
                "size": f.size,
                "modified": f.modified.isoformat() if f.modified else None,
            }
            for f in sorted_files
        ]

    def _find_newest_files(self, folder_tree: FolderNode, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the newest files by modification time."""
        all_files = self._collect_all_files(folder_tree)
        
        # Filter files with modification time
        files_with_time = [f for f in all_files if f.modified]
        
        sorted_files = sorted(files_with_time, key=lambda f: f.modified, reverse=True)[:limit]
        
        return [
            {
                "path": str(f.path),
                "name": f.name,
                "size": f.size,
                "modified": f.modified.isoformat() if f.modified else None,
            }
            for f in sorted_files
        ]

    def _collect_all_files(self, folder_tree: FolderNode) -> List[FileInfo]:
        """Recursively collect all files from the folder tree."""
        all_files = []
        
        def collect(node: FolderNode):
            all_files.extend(node.files)
            for subfolder in node.subfolders:
                collect(subfolder)
        
        collect(folder_tree)
        return all_files
