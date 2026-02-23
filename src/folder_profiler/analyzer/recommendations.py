"""
Smart recommendations based on folder analysis.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class RecommendationType(str, Enum):
    """Types of recommendations."""

    CLEANUP = "cleanup"
    ORGANIZATION = "organization"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STORAGE = "storage"


class Priority(str, Enum):
    """Recommendation priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Recommendation:
    """A single recommendation."""

    type: RecommendationType
    priority: Priority
    title: str
    description: str
    action: str
    estimated_savings: int = 0  # In bytes
    affected_files: int = 0


class RecommendationEngine:
    """Generate smart recommendations based on analysis results."""

    def __init__(self):
        """Initialize recommendation engine."""
        self.recommendations: List[Recommendation] = []

    def generate_recommendations(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on analysis results.

        Args:
            analysis_results: Analysis results from FolderAnalyzer

        Returns:
            Dictionary containing recommendations and health score
        """
        self.recommendations = []

        # Extract data
        statistics = analysis_results.get("statistics", {})
        duplicates = analysis_results.get("duplicates", {})
        patterns = analysis_results.get("patterns", {})

        # Generate various recommendations
        self._analyze_duplicates(duplicates)
        self._analyze_temp_files(patterns)
        self._analyze_build_artifacts(patterns)
        self._analyze_storage(statistics)
        self._analyze_organization(statistics, patterns)

        # Calculate health score
        health_score = self._calculate_health_score(
            statistics, duplicates, patterns
        )

        return {
            "recommendations": [
                {
                    "type": rec.type,
                    "priority": rec.priority,
                    "title": rec.title,
                    "description": rec.description,
                    "action": rec.action,
                    "estimated_savings": rec.estimated_savings,
                    "affected_files": rec.affected_files,
                }
                for rec in sorted(
                    self.recommendations, key=lambda x: self._priority_weight(x.priority)
                )
            ],
            "health_score": health_score,
            "summary": self._generate_summary(health_score),
        }

    def _analyze_duplicates(self, duplicates: Dict[str, Any]) -> None:
        """Analyze duplicate files and generate recommendations."""
        dup_stats = duplicates.get("statistics", {})
        wasted_space = dup_stats.get("wasted_space", 0)
        duplicate_files = dup_stats.get("total_duplicate_files", 0)

        if wasted_space > 20 * 1024 * 1024:  # > 20 MB
            priority = Priority.HIGH
        elif wasted_space > 5 * 1024 * 1024:  # > 5 MB
            priority = Priority.MEDIUM
        elif wasted_space > 0:
            priority = Priority.LOW
        else:
            return

        self.recommendations.append(
            Recommendation(
                type=RecommendationType.STORAGE,
                priority=priority,
                title="Duplicate Files Detected",
                description=f"Found {duplicate_files} duplicate files wasting space",
                action="Review and delete duplicate files to free up space",
                estimated_savings=wasted_space,
                affected_files=duplicate_files,
            )
        )

    def _analyze_temp_files(self, patterns: Dict[str, Any]) -> None:
        """Analyze temporary files and generate recommendations."""
        temp_files = patterns.get("temp_files", [])
        temp_count = len(temp_files)

        if temp_count == 0:
            return

        # Estimate size (assume average temp file is 50KB)
        estimated_size = temp_count * 50 * 1024

        if temp_count > 100:
            priority = Priority.HIGH
        elif temp_count > 10:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW

        self.recommendations.append(
            Recommendation(
                type=RecommendationType.CLEANUP,
                priority=priority,
                title="Temporary Files Found",
                description=f"Found {temp_count} temporary files that can be safely removed",
                action="Delete temporary files (.tmp, .bak, .swp, etc.)",
                estimated_savings=estimated_size,
                affected_files=temp_count,
            )
        )

    def _analyze_build_artifacts(self, patterns: Dict[str, Any]) -> None:
        """Analyze build artifacts and generate recommendations."""
        build_files = patterns.get("build_artifacts", [])
        build_count = len(build_files)

        if build_count == 0:
            return

        # Estimate size (assume average build artifact is 20KB)
        estimated_size = build_count * 20 * 1024

        if build_count > 500:
            priority = Priority.MEDIUM
        elif build_count > 100:
            priority = Priority.LOW
        else:
            priority = Priority.INFO

        self.recommendations.append(
            Recommendation(
                type=RecommendationType.CLEANUP,
                priority=priority,
                title="Build Artifacts Detected",
                description=f"Found {build_count} build artifacts that could be regenerated",
                action="Consider adding build artifacts to .gitignore and cleaning them periodically",
                estimated_savings=estimated_size,
                affected_files=build_count,
            )
        )

    def _analyze_storage(self, statistics: Dict[str, Any]) -> None:
        """Analyze storage usage and generate recommendations."""
        summary = statistics.get("summary", {})
        total_size = summary.get("total_size", 0)

        # Check largest files
        largest_files = statistics.get("largest_files", [])
        if largest_files and len(largest_files) > 0:
            top_file = largest_files[0]
            file_size = top_file.get("size", 0)

            # If top file is > 50% of total size
            if total_size > 0 and file_size > total_size * 0.5:
                self.recommendations.append(
                    Recommendation(
                        type=RecommendationType.STORAGE,
                        priority=Priority.MEDIUM,
                        title="Large File Dominates Storage",
                        description=f"Single file accounts for >50% of total storage",
                        action=f"Review large file: {top_file.get('path', 'unknown')}",
                        estimated_savings=0,
                        affected_files=1,
                    )
                )

        # Check if many small files
        total_files = summary.get("total_files", 0)
        avg_size = summary.get("average_file_size", 0)

        if total_files > 1000 and avg_size < 10 * 1024:  # < 10KB average
            self.recommendations.append(
                Recommendation(
                    type=RecommendationType.ORGANIZATION,
                    priority=Priority.LOW,
                    title="Many Small Files",
                    description=f"{total_files} files with average size {avg_size} bytes",
                    action="Consider archiving or consolidating small files",
                    estimated_savings=0,
                    affected_files=total_files,
                )
            )

    def _analyze_organization(
        self, statistics: Dict[str, Any], patterns: Dict[str, Any]
    ) -> None:
        """Analyze folder organization and generate recommendations."""
        # Check depth analysis
        depth_analysis = statistics.get("depth_analysis", {})
        if depth_analysis:
            max_depth = depth_analysis.get("max_depth", 0)
            if max_depth > 10:
                self.recommendations.append(
                    Recommendation(
                        type=RecommendationType.ORGANIZATION,
                        priority=Priority.LOW,
                        title="Deep Folder Nesting",
                        description=f"Folders nested up to {max_depth} levels deep",
                        action="Consider flattening folder structure for better accessibility",
                        estimated_savings=0,
                        affected_files=0,
                    )
                )

        # Check version patterns
        version_patterns = patterns.get("version_patterns", [])
        # Count total files across all version patterns
        total_versioned_files = sum(
            len(p.get("files", [])) for p in version_patterns
        ) if isinstance(version_patterns, list) else 0
        
        if total_versioned_files > 5:
            self.recommendations.append(
                Recommendation(
                    type=RecommendationType.ORGANIZATION,
                    priority=Priority.MEDIUM,
                    title="Multiple Versioned Files",
                    description=f"Found {total_versioned_files} file versioning patterns",
                    action="Consider using version control (Git) instead of file naming",
                    estimated_savings=0,
                    affected_files=total_versioned_files,
                )
            )

        # Check duplicate names in different folders
        duplicate_names = patterns.get("duplicate_names", {})
        if duplicate_names and len(duplicate_names) > 10:
            self.recommendations.append(
                Recommendation(
                    type=RecommendationType.ORGANIZATION,
                    priority=Priority.INFO,
                    title="Duplicate File Names",
                    description=f"{len(duplicate_names)} file names appear in multiple locations",
                    action="Review naming strategy for better clarity",
                    estimated_savings=0,
                    affected_files=0,
                )
            )

    def _calculate_health_score(
        self,
        statistics: Dict[str, Any],
        duplicates: Dict[str, Any],
        patterns: Dict[str, Any],
    ) -> int:
        """
        Calculate folder health score (0-100).

        Args:
            statistics: Statistics from analysis
            duplicates: Duplicate file information
            patterns: Pattern detection results

        Returns:
            Health score from 0 (poor) to 100 (excellent)
        """
        score = 100

        # Deduct for duplicates
        dup_stats = duplicates.get("statistics", {})
        wasted_space = dup_stats.get("wasted_space", 0)
        summary = statistics.get("summary", {})
        total_size = summary.get("total_size", 1)  # Avoid division by zero

        wasted_percentage = (wasted_space / total_size) * 100 if total_size > 0 else 0
        score -= min(wasted_percentage * 2, 20)  # Max -20 points

        # Deduct for temp files
        temp_files = patterns.get("temp_files", [])
        temp_count = len(temp_files)
        total_files = summary.get("total_files", 1)
        temp_percentage = (temp_count / total_files) * 100 if total_files > 0 else 0
        score -= min(temp_percentage * 3, 15)  # Max -15 points

        # Deduct for build artifacts
        build_files = patterns.get("build_artifacts", [])
        build_count = len(build_files)
        build_percentage = (build_count / total_files) * 100 if total_files > 0 else 0
        score -= min(build_percentage * 2, 15)  # Max -15 points

        # Deduct for deep nesting
        depth_analysis = statistics.get("depth_analysis", {})
        max_depth = depth_analysis.get("max_depth", 0) if depth_analysis else 0
        if max_depth > 10:
            score -= min((max_depth - 10) * 2, 10)  # Max -10 points

        # Deduct for version patterns
        version_patterns = patterns.get("version_patterns", [])
        if len(version_patterns) > 5:
            score -= min((len(version_patterns) - 5), 10)  # Max -10 points

        return max(0, min(100, int(score)))

    def _generate_summary(self, health_score: int) -> str:
        """Generate summary based on health score."""
        if health_score >= 90:
            return "Excellent: Folder is well-organized and optimized"
        elif health_score >= 75:
            return "Good: Folder is in good shape with minor improvements possible"
        elif health_score >= 60:
            return "Fair: Several areas could be improved"
        elif health_score >= 40:
            return "Poor: Significant cleanup and organization needed"
        else:
            return "Critical: Immediate attention required"

    @staticmethod
    def _priority_weight(priority: Priority) -> int:
        """Get numeric weight for priority (lower = higher priority)."""
        weights = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
            Priority.INFO: 4,
        }
        return weights.get(priority, 5)
