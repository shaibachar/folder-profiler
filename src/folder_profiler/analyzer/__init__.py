"""
File system analysis module.

Handles statistics generation, duplicate detection, and pattern analysis.
"""

from folder_profiler.analyzer.analyzer import FolderAnalyzer
from folder_profiler.analyzer.duplicates import DuplicateDetector
from folder_profiler.analyzer.statistics import StatisticsCalculator

__all__ = ["FolderAnalyzer", "StatisticsCalculator", "DuplicateDetector"]
