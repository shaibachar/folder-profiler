"""
Tests for recommendation engine.
"""

from pathlib import Path
from datetime import datetime, timedelta

import pytest

from folder_profiler.analyzer.recommendations import (
    RecommendationEngine,
    RecommendationType,
    Priority,
)
from folder_profiler.scanner.models import FileInfo, FolderNode
from folder_profiler.analyzer.analyzer import FolderAnalyzer


@pytest.fixture
def recommendation_engine():
    """Create recommendation engine instance."""
    return RecommendationEngine()


@pytest.fixture
def sample_analysis_with_duplicates():
    """Sample analysis results with duplicates."""
    return {
        "statistics": {
            "summary": {
                "total_files": 100,
                "total_folders": 10,
                "total_size": 10 * 1024 * 1024,  # 10 MB
                "average_file_size": 100 * 1024,
                "median_file_size": 50 * 1024,
                "largest_file_size": 1 * 1024 * 1024,
            },
            "depth_analysis": {"max_depth": 5},
            "largest_files": [],
        },
        "duplicates": {
            "duplicate_groups": [],
            "statistics": {
                "total_duplicate_sets": 5,
                "total_duplicate_files": 20,
                "wasted_space": 50 * 1024 * 1024,  # 50 MB - should trigger HIGH priority
            },
        },
        "patterns": {
            "temp_files": [],
            "build_artifacts": [],
            "version_patterns": [],
            "duplicate_names": {},
        },
    }


@pytest.fixture
def sample_analysis_with_temp_files():
    """Sample analysis results with temp files."""
    return {
        "statistics": {
            "summary": {
                "total_files": 150,
                "total_folders": 10,
                "total_size": 5 * 1024 * 1024,
                "average_file_size": 34 * 1024,
                "median_file_size": 20 * 1024,
                "largest_file_size": 500 * 1024,
            },
            "depth_analysis": {"max_depth": 3},
            "largest_files": [],
        },
        "duplicates": {
            "duplicate_groups": [],
            "statistics": {
                "total_duplicate_sets": 0,
                "total_duplicate_files": 0,
                "wasted_space": 0,
            },
        },
        "patterns": {
            "temp_files": [f"temp{i}.tmp" for i in range(50)],  # 50 temp files
            "build_artifacts": [],
            "version_patterns": [],
            "duplicate_names": {},
        },
    }


class TestRecommendationEngine:
    """Tests for recommendation engine."""

    def test_generate_recommendations_structure(self, recommendation_engine):
        """Test that generate_recommendations returns proper structure."""
        analysis = {
            "statistics": {"summary": {}, "depth_analysis": {}, "largest_files": []},
            "duplicates": {"duplicate_groups": [], "statistics": {}},
            "patterns": {
                "temp_files": [],
                "build_artifacts": [],
                "version_patterns": [],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)

        assert "recommendations" in result
        assert "health_score" in result
        assert "summary" in result
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["health_score"], int)
        assert isinstance(result["summary"], str)

    def test_health_score_perfect(self, recommendation_engine):
        """Test health score for perfect folder."""
        analysis = {
            "statistics": {
                "summary": {
                    "total_files": 10,
                    "total_folders": 3,
                    "total_size": 1024 * 1024,
                    "average_file_size": 100 * 1024,
                    "median_file_size": 100 * 1024,
                    "largest_file_size": 200 * 1024,
                },
                "depth_analysis": {"max_depth": 3},
                "largest_files": [],
            },
            "duplicates": {
                "duplicate_groups": [],
                "statistics": {
                    "total_duplicate_sets": 0,
                    "total_duplicate_files": 0,
                    "wasted_space": 0,
                },
            },
            "patterns": {
                "temp_files": [],
                "build_artifacts": [],
                "version_patterns": [],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)
        assert result["health_score"] >= 90
        assert "Excellent" in result["summary"]

    def test_duplicate_recommendation_high_priority(
        self, recommendation_engine, sample_analysis_with_duplicates
    ):
        """Test that large duplicates trigger HIGH priority recommendation."""
        result = recommendation_engine.generate_recommendations(
            sample_analysis_with_duplicates
        )

        recs = result["recommendations"]
        assert len(recs) > 0

        # Find duplicate recommendation
        dup_rec = next(
            (r for r in recs if r["type"] == RecommendationType.STORAGE), None
        )
        assert dup_rec is not None
        assert dup_rec["priority"] == Priority.HIGH
        assert "Duplicate" in dup_rec["title"]
        assert dup_rec["estimated_savings"] > 0

    def test_temp_files_recommendation(
        self, recommendation_engine, sample_analysis_with_temp_files
    ):
        """Test temp files recommendation."""
        result = recommendation_engine.generate_recommendations(
            sample_analysis_with_temp_files
        )

        recs = result["recommendations"]

        # Find temp files recommendation
        temp_rec = next(
            (r for r in recs if "Temporary" in r["title"]), None
        )
        assert temp_rec is not None
        assert temp_rec["type"] == RecommendationType.CLEANUP
        assert temp_rec["priority"] in [Priority.HIGH, Priority.MEDIUM]
        assert temp_rec["affected_files"] == 50

    def test_build_artifacts_recommendation(self, recommendation_engine):
        """Test build artifacts recommendation."""
        analysis = {
            "statistics": {
                "summary": {"total_files": 100, "total_size": 1024 * 1024},
                "depth_analysis": {"max_depth": 3},
                "largest_files": [],
            },
            "duplicates": {"duplicate_groups": [], "statistics": {"wasted_space": 0}},
            "patterns": {
                "temp_files": [],
                "build_artifacts": [f"file{i}.pyc" for i in range(200)],
                "version_patterns": [],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)
        recs = result["recommendations"]

        # Find build artifacts recommendation
        build_rec = next(
            (r for r in recs if "Build Artifacts" in r["title"]), None
        )
        assert build_rec is not None
        assert build_rec["type"] == RecommendationType.CLEANUP

    def test_deep_nesting_recommendation(self, recommendation_engine):
        """Test deep folder nesting recommendation."""
        analysis = {
            "statistics": {
                "summary": {"total_files": 50, "total_size": 1024 * 1024},
                "depth_analysis": {"max_depth": 15},  # Very deep
                "largest_files": [],
            },
            "duplicates": {"duplicate_groups": [], "statistics": {"wasted_space": 0}},
            "patterns": {
                "temp_files": [],
                "build_artifacts": [],
                "version_patterns": [],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)
        recs = result["recommendations"]

        # Find deep nesting recommendation
        depth_rec = next(
            (r for r in recs if "Deep Folder Nesting" in r["title"]), None
        )
        assert depth_rec is not None
        assert depth_rec["type"] == RecommendationType.ORGANIZATION

    def test_version_patterns_recommendation(self, recommendation_engine):
        """Test version patterns recommendation."""
        analysis = {
            "statistics": {
                "summary": {"total_files": 50, "total_size": 1024 * 1024},
                "depth_analysis": {"max_depth": 3},
                "largest_files": [],
            },
            "duplicates": {"duplicate_groups": [], "statistics": {"wasted_space": 0}},
            "patterns": {
                "temp_files": [],
                "build_artifacts": [],
                "version_patterns": [{"pattern": "semantic", "files": [f"file-v{i}.txt" for i in range(10)]}],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)
        recs = result["recommendations"]

        # Find version patterns recommendation
        version_rec = next(
            (r for r in recs if "Versioned" in r["title"]), None
        )
        assert version_rec is not None
        assert version_rec["type"] == RecommendationType.ORGANIZATION

    def test_recommendations_sorted_by_priority(self, recommendation_engine):
        """Test that recommendations are sorted by priority."""
        # Create analysis with multiple issues
        analysis = {
            "statistics": {
                "summary": {
                    "total_files": 100,
                    "total_folders": 10,
                    "total_size": 100 * 1024 * 1024,
                    "average_file_size": 1024 * 1024,
                    "median_file_size": 500 * 1024,
                    "largest_file_size": 50 * 1024 * 1024,
                },
                "depth_analysis": {"max_depth": 15},
                "largest_files": [],
            },
            "duplicates": {
                "duplicate_groups": [],
                "statistics": {
                    "total_duplicate_sets": 10,
                    "total_duplicate_files": 50,
                    "wasted_space": 200 * 1024 * 1024,  # 200 MB - HIGH
                },
            },
            "patterns": {
                "temp_files": [f"temp{i}.tmp" for i in range(150)],  # HIGH
                "build_artifacts": [f"build{i}.pyc" for i in range(600)],  # MEDIUM
                "version_patterns": [{"pattern": "semantic", "files": [f"v{i}" for i in range(10)]}],
                "duplicate_names": {},
            },
        }

        result = recommendation_engine.generate_recommendations(analysis)
        recs = result["recommendations"]

        # Verify they're sorted (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        priorities = [r["priority"] for r in recs]
        priority_weights = [
            recommendation_engine._priority_weight(Priority(p)) for p in priorities
        ]
        assert priority_weights == sorted(priority_weights)

    def test_health_score_calculation(self, recommendation_engine):
        """Test health score decreases with issues."""
        perfect_analysis = {
            "statistics": {
                "summary": {"total_files": 10, "total_size": 1024 * 1024},
                "depth_analysis": {"max_depth": 3},
                "largest_files": [],
            },
            "duplicates": {"duplicate_groups": [], "statistics": {"wasted_space": 0}},
            "patterns": {
                "temp_files": [],
                "build_artifacts": [],
                "version_patterns": [],
                "duplicate_names": {},
            },
        }

        poor_analysis = {
            "statistics": {
                "summary": {"total_files": 100, "total_size": 10 * 1024 * 1024},
                "depth_analysis": {"max_depth": 20},
                "largest_files": [],
            },
            "duplicates": {
                "duplicate_groups": [],
                "statistics": {"wasted_space": 5 * 1024 * 1024},  # 50% waste
            },
            "patterns": {
                "temp_files": [f"t{i}" for i in range(50)],  # 50% temp
                "build_artifacts": [f"b{i}" for i in range(30)],  # 30% build
                "version_patterns": [{"pattern": "semantic", "files": [f"v{i}" for i in range(20)]}],
                "duplicate_names": {},
            },
        }

        perfect_score = recommendation_engine.generate_recommendations(perfect_analysis)[
            "health_score"
        ]
        poor_score = recommendation_engine.generate_recommendations(poor_analysis)[
            "health_score"
        ]

        assert perfect_score > poor_score
        assert perfect_score >= 90
        assert poor_score < 70


class TestRecommendationsIntegration:
    """Integration tests with full analyzer."""

    def test_analyzer_includes_recommendations(self, tmp_path):
        """Test that analyzer includes recommendations in results."""
        # Create test folder structure
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "temp.tmp").write_text("temp")

        analyzer = FolderAnalyzer()
        from folder_profiler.scanner.scanner import FolderScanner

        scanner = FolderScanner()
        folder_tree = scanner.scan(tmp_path)

        results = analyzer.analyze(folder_tree)

        assert "recommendations" in results
        assert "health_score" in results["recommendations"]
        assert "summary" in results["recommendations"]
        assert "recommendations" in results["recommendations"]
