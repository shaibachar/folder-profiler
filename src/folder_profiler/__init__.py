"""
Folder Profiler - Intelligent file system analysis tool.

An intelligent file system analysis tool that provides deep insights into folder
structures, identifies optimization opportunities, detects duplicate content, and
generates AI-powered recommendations for organization and cleanup.
"""

__version__ = "0.1.0"
__author__ = "Folder Profiler Team"
__license__ = "MIT"

from folder_profiler.scanner import FolderScanner
from folder_profiler.analyzer import FolderAnalyzer
from folder_profiler.reporter import ReportGenerator

__all__ = [
    "FolderScanner",
    "FolderAnalyzer",
    "ReportGenerator",
    "__version__",
]
