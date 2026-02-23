"""
Main folder analysis orchestrator.
"""

from folder_profiler.scanner.models import FolderNode
from folder_profiler.analyzer.statistics import StatisticsCalculator
from folder_profiler.analyzer.duplicates import DuplicateDetector
from folder_profiler.analyzer.patterns import PatternDetector
from folder_profiler.analyzer.recommendations import RecommendationEngine
from typing import Dict, Any


class FolderAnalyzer:
    """
    Analyzes folder structures and generates insights.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.stats_calculator = StatisticsCalculator()
        self.duplicate_detector = DuplicateDetector()
        self.pattern_detector = PatternDetector()
        self.recommendation_engine = RecommendationEngine()

    def analyze(self, folder_tree: FolderNode) -> Dict[str, Any]:
        """
        Perform complete analysis on a folder tree.

        Args:
            folder_tree: Root folder node to analyze

        Returns:
            Dictionary containing all analysis results
        """
        analysis = {
            "statistics": self.stats_calculator.calculate(folder_tree),
            "duplicates": self.duplicate_detector.find_duplicates(folder_tree),
            "patterns": self.pattern_detector.detect_patterns(folder_tree),
        }
        
        # Generate smart recommendations
        analysis["recommendations"] = self.recommendation_engine.generate_recommendations(
            analysis
        )
        
        return analysis
