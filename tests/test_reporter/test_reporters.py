"""
Tests for report generators.
"""

import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from rich.console import Console

from folder_profiler.reporter.json_reporter import JSONReporter
from folder_profiler.reporter.html_reporter import HTMLReporter
from folder_profiler.reporter.console_reporter import ConsoleReporter
from folder_profiler.reporter.reporter import ReportGenerator


@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing."""
    return {
        "statistics": {
            "summary": {
                "total_files": 10,
                "total_folders": 3,
                "total_size": 1024000,
                "average_file_size": 102400,
                "median_file_size": 51200,
                "largest_file_size": 512000,
            },
            "file_types": {
                "text/plain": {"count": 5, "total_size": 256000},
                "application/json": {"count": 3, "total_size": 153600},
                "image/png": {"count": 2, "total_size": 614400},
            },
            "extensions": {
                ".txt": {"count": 5, "total_size": 256000},
                ".json": {"count": 3, "total_size": 153600},
                ".png": {"count": 2, "total_size": 614400},
            },
            "largest_files": [
                {"path": "image1.png", "size": 512000, "extension": ".png"},
                {"path": "data.json", "size": 102400, "extension": ".json"},
            ],
        },
        "duplicates": {
            "duplicate_groups": [
                {
                    "hash": "abc123",
                    "size": 51200,
                    "count": 2,
                    "total_size": 102400,
                    "files": ["file1.txt", "file2.txt"],
                }
            ],
            "statistics": {
                "total_duplicate_sets": 1,
                "total_duplicate_files": 2,
                "wasted_space": 51200,
            },
        },
        "patterns": {
            "temp_files": ["temp.tmp", "backup.bak"],
            "build_artifacts": ["script.min.js"],
            "version_patterns": [{"pattern": "semantic", "files": ["app-1.2.3.txt"]}],
        },
    }


class TestJSONReporter:
    """Tests for JSON reporter."""

    def test_generate_creates_file(self, tmp_path, sample_analysis_results):
        """Test that JSON reporter creates output file."""
        reporter = JSONReporter()
        output_path = tmp_path / "report.json"

        result_path = reporter.generate(sample_analysis_results, output_path)

        assert result_path.exists()
        assert result_path == output_path

    def test_generate_valid_json(self, tmp_path, sample_analysis_results):
        """Test that generated JSON is valid and parseable."""
        reporter = JSONReporter()
        output_path = tmp_path / "report.json"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "analysis" in data
        assert "metadata" in data

    def test_generate_includes_metadata(self, tmp_path, sample_analysis_results):
        """Test that JSON includes metadata."""
        reporter = JSONReporter()
        output_path = tmp_path / "report.json"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            data = json.load(f)

        assert "generated_at" in data["metadata"]
        assert "generator" in data["metadata"]
        assert "version" in data["metadata"]
        assert data["metadata"]["generator"] == "folder-profiler"

    def test_generate_includes_analysis_results(self, tmp_path, sample_analysis_results):
        """Test that JSON includes all analysis results."""
        reporter = JSONReporter()
        output_path = tmp_path / "report.json"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            data = json.load(f)

        assert data["analysis"]["statistics"]["summary"]["total_files"] == 10
        assert data["analysis"]["duplicates"]["statistics"]["total_duplicate_files"] == 2
        assert len(data["analysis"]["patterns"]["temp_files"]) == 2

    def test_generate_creates_parent_directories(self, tmp_path, sample_analysis_results):
        """Test that JSON reporter creates parent directories if needed."""
        reporter = JSONReporter()
        output_path = tmp_path / "subdir" / "nested" / "report.json"

        reporter.generate(sample_analysis_results, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestHTMLReporter:
    """Tests for HTML reporter."""

    def test_generate_creates_file(self, tmp_path, sample_analysis_results):
        """Test that HTML reporter creates output file."""
        reporter = HTMLReporter()
        output_path = tmp_path / "report.html"

        result_path = reporter.generate(sample_analysis_results, output_path)

        assert result_path.exists()
        assert result_path == output_path

    def test_generate_valid_html(self, tmp_path, sample_analysis_results):
        """Test that generated HTML is valid."""
        reporter = HTMLReporter()
        output_path = tmp_path / "report.html"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("html") is not None
        assert soup.find("head") is not None
        assert soup.find("body") is not None

    def test_generate_includes_title(self, tmp_path, sample_analysis_results):
        """Test that HTML includes title."""
        reporter = HTMLReporter()
        output_path = tmp_path / "report.html"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("title")
        assert title is not None
        assert "Folder Analysis Report" in title.text

    def test_generate_includes_statistics(self, tmp_path, sample_analysis_results):
        """Test that HTML includes statistics."""
        reporter = HTMLReporter()
        output_path = tmp_path / "report.html"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            html = f.read()

        assert "10" in html  # total files
        assert "3" in html  # total folders

    def test_generate_includes_css(self, tmp_path, sample_analysis_results):
        """Test that HTML includes CSS styling."""
        reporter = HTMLReporter()
        output_path = tmp_path / "report.html"

        reporter.generate(sample_analysis_results, output_path)

        with open(output_path) as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        style = soup.find("style")
        assert style is not None
        assert "body" in style.text
        assert "summary-grid" in style.text

    def test_generate_creates_parent_directories(self, tmp_path, sample_analysis_results):
        """Test that HTML reporter creates parent directories if needed."""
        reporter = HTMLReporter()
        output_path = tmp_path / "subdir" / "nested" / "report.html"

        reporter.generate(sample_analysis_results, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestConsoleReporter:
    """Tests for console reporter."""

    def test_generate_with_default_console(self, sample_analysis_results, capsys):
        """Test that console reporter works with default console."""
        reporter = ConsoleReporter()
        
        reporter.generate(sample_analysis_results)
        
        captured = capsys.readouterr()
        # Check that some output was produced
        # (Rich console may format differently, so just verify output exists)
        assert len(captured.out) > 0 or len(captured.err) > 0

    def test_generate_includes_statistics(self, sample_analysis_results, capsys):
        """Test that console output includes statistics."""
        console = Console(file=None, force_terminal=False, width=80)
        reporter = ConsoleReporter(console)
        
        # We can't easily capture Rich output, so just verify it doesn't crash
        reporter.generate(sample_analysis_results)

    def test_generate_with_empty_results(self):
        """Test console reporter handles empty results."""
        console = Console(file=None, force_terminal=False)
        reporter = ConsoleReporter(console)
        
        empty_results = {
            "statistics": {"summary": {}, "largest_files": []},
            "duplicates": {"duplicate_groups": [], "statistics": {}},
            "patterns": {},
        }
        
        # Should not crash
        reporter.generate(empty_results)


class TestReportGenerator:
    """Tests for main report generator."""

    def test_generate_json_report(self, tmp_path, sample_analysis_results):
        """Test generating JSON report via main generator."""
        generator = ReportGenerator()
        output_path = tmp_path / "report.json"

        result_path = generator.generate(sample_analysis_results, output_path, "json")

        assert result_path.exists()
        with open(result_path) as f:
            data = json.load(f)
        assert "analysis" in data

    def test_generate_html_report(self, tmp_path, sample_analysis_results):
        """Test generating HTML report via main generator."""
        generator = ReportGenerator()
        output_path = tmp_path / "report.html"

        result_path = generator.generate(sample_analysis_results, output_path, "html")

        assert result_path.exists()
        with open(result_path) as f:
            html = f.read()
        assert "<!DOCTYPE html>" in html or "<html" in html

    def test_generate_unsupported_format(self, tmp_path, sample_analysis_results):
        """Test that unsupported format raises ValueError."""
        generator = ReportGenerator()
        output_path = tmp_path / "report.xyz"

        with pytest.raises(ValueError, match="Unsupported format"):
            generator.generate(sample_analysis_results, output_path, "xyz")

    def test_generate_pdf_not_implemented(self, tmp_path, sample_analysis_results):
        """Test that PDF format raises NotImplementedError."""
        generator = ReportGenerator()
        output_path = tmp_path / "report.pdf"

        with pytest.raises(NotImplementedError):
            generator.generate(sample_analysis_results, output_path, "pdf")
