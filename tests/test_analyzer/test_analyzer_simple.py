"""Simple tests for analyzer components."""
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from folder_profiler.analyzer.analyzer import FolderAnalyzer
from folder_profiler.analyzer.statistics import StatisticsCalculator
from folder_profiler.analyzer.duplicates import DuplicateDetector
from folder_profiler.analyzer.patterns import PatternDetector
from folder_profiler.scanner.models import FileInfo, FolderNode


def test_statistics_calculator_basic():
    """Test basic statistics calculation."""
    calc = StatisticsCalculator()
    
    # Create simple folder with one file
    file1 = FileInfo(
        path=Path("/test/file1.txt"),
        name="file1.txt",
        size=100,
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".txt",
        mime_type="text/plain",
    )
    
    folder = FolderNode(
        path=Path("/test"),
        name="test",
        depth=0,
        files=[file1],
        subfolders=[],
    )
    
    stats = calc.calculate(folder)
    
    assert "summary" in stats
    assert stats["summary"]["total_files"] == 1
    assert stats["summary"]["total_size"] == 100


def test_duplicate_detector_basic(tmp_path):
    """Test basic duplicate detection."""
    detector = DuplicateDetector()
    
    # Create two identical files
    content = "Hello World"
    (tmp_path / "file1.txt").write_text(content)
    (tmp_path / "file2.txt").write_text(content)
    
    file1 = FileInfo(
        path=tmp_path / "file1.txt",
        name="file1.txt",
        size=len(content),
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".txt",
        mime_type="text/plain",
    )
    
    file2 = FileInfo(
        path=tmp_path / "file2.txt",
        name="file2.txt",
        size=len(content),
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".txt",
        mime_type="text/plain",
    )
    
    folder = FolderNode(
        path=tmp_path,
        name=tmp_path.name,
        depth=0,
        files=[file1, file2],
        subfolders=[],
    )
    
    result = detector.find_duplicates(folder)
    
    assert "statistics" in result
    assert result["statistics"]["total_duplicate_files"] >= 1


def test_pattern_detector_temp_files():
    """Test temp file detection."""
    detector = PatternDetector()
    
    temp_file = FileInfo(
        path=Path("/test/file.tmp"),
        name="file.tmp",
        size=100,
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".tmp",
        mime_type="application/octet-stream",
    )
    
    normal_file = FileInfo(
        path=Path("/test/file.txt"),
        name="file.txt",
        size=100,
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".txt",
        mime_type="text/plain",
    )
    
    temp_files = detector.detect_temp_files([temp_file, normal_file])
    
    assert len(temp_files) == 1
    assert temp_files[0].name == "file.tmp"


def test_folder_analyzer_integration():
    """Test full analyzer integration."""
    analyzer = FolderAnalyzer()
    
    file1 = FileInfo(
        path=Path("/test/file1.txt"),
        name="file1.txt",
        size=100,
        created=datetime.now(),
        modified=datetime.now(),
        accessed=datetime.now(),
        extension=".txt",
        mime_type="text/plain",
    )
    
    folder = FolderNode(
        path=Path("/test"),
        name="test",
        depth=0,
        files=[file1],
        subfolders=[],
    )
    
    result = analyzer.analyze(folder)
    
    assert "statistics" in result
    assert "duplicates" in result
    assert "patterns" in result
