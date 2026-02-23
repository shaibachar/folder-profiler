"""
End-to-end CLI integration tests.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from folder_profiler.cli.main import cli


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_folder(tmp_path):
    """Create a test folder structure."""
    # Create some test files
    (tmp_path / "file1.txt").write_text("Hello World")
    (tmp_path / "file2.txt").write_text("Test content")
    (tmp_path / "data.json").write_text('{"key": "value"}')
    
    # Create subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("Nested file")
    (subdir / "duplicate.txt").write_text("Hello World")  # Duplicate of file1.txt
    
    return tmp_path


class TestCLIAnalyze:
    """Tests for the analyze command."""

    def test_analyze_with_console_output(self, cli_runner, test_folder):
        """Test analyze command with console output (default)."""
        result = cli_runner.invoke(cli, ["analyze", str(test_folder)])
        
        assert result.exit_code == 0
        assert "Analyzing:" in result.output
        assert "Summary Statistics" in result.output or "Scanned" in result.output

    def test_analyze_with_json_output(self, cli_runner, test_folder, tmp_path):
        """Test analyze command with JSON output."""
        output_file = tmp_path / "output" / "report.json"
        result = cli_runner.invoke(
            cli, ["analyze", str(test_folder), "--format", "json", "--output", str(output_file)]
        )
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        assert "analysis" in data
        assert "metadata" in data

    def test_analyze_with_html_output(self, cli_runner, test_folder, tmp_path):
        """Test analyze command with HTML output."""
        output_file = tmp_path / "output" / "report.html"
        result = cli_runner.invoke(
            cli, ["analyze", str(test_folder), "--format", "html", "--output", str(output_file)]
        )
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify HTML is generated
        html_content = output_file.read_text()
        assert "<html" in html_content or "<!DOCTYPE html>" in html_content

    def test_analyze_with_max_depth(self, cli_runner, test_folder):
        """Test analyze command with max depth option."""
        result = cli_runner.invoke(cli, ["analyze", str(test_folder), "--max-depth", "1"])
        
        assert result.exit_code == 0
        assert "Analyzing:" in result.output

    def test_analyze_with_include_pattern(self, cli_runner, test_folder):
        """Test analyze command with include patterns."""
        result = cli_runner.invoke(
            cli, ["analyze", str(test_folder), "--include", "*.txt"]
        )
        
        assert result.exit_code == 0

    def test_analyze_with_exclude_pattern(self, cli_runner, test_folder):
        """Test analyze command with exclude patterns."""
        result = cli_runner.invoke(
            cli, ["analyze", str(test_folder), "--exclude", "*.json"]
        )
        
        assert result.exit_code == 0

    def test_analyze_nonexistent_path(self, cli_runner):
        """Test analyze command with nonexistent path."""
        result = cli_runner.invoke(cli, ["analyze", "nonexistent_path"])
        
        # Should fail because path doesn't exist
        assert result.exit_code != 0

    def test_analyze_creates_output_directory(self, cli_runner, test_folder, tmp_path):
        """Test that analyze creates output directory if it doesn't exist."""
        output_file = tmp_path / "deep" / "nested" / "path" / "report.json"
        result = cli_runner.invoke(
            cli, ["analyze", str(test_folder), "--format", "json", "--output", str(output_file)]
        )
        
        assert result.exit_code == 0
        assert output_file.exists()

    def test_analyze_default_json_filename(self, cli_runner, test_folder):
        """Test that JSON format uses default filename if not specified."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(
                cli, ["analyze", str(test_folder), "--format", "json"]
            )
            
            assert result.exit_code == 0
            assert Path("folder-report.json").exists()

    def test_analyze_default_html_filename(self, cli_runner, test_folder):
        """Test that HTML format uses default filename if not specified."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(
                cli, ["analyze", str(test_folder), "--format", "html"]
            )
            
            assert result.exit_code == 0
            assert Path("folder-report.html").exists()


class TestCLIConfig:
    """Tests for the config command."""

    def test_config_show(self, cli_runner):
        """Test config --show command."""
        result = cli_runner.invoke(cli, ["config", "--show"])
        
        assert result.exit_code == 0
        assert "Configuration" in result.output or "Version" in result.output

    def test_config_default(self, cli_runner):
        """Test config command without options."""
        result = cli_runner.invoke(cli, ["config"])
        
        assert result.exit_code == 0


class TestCLIVersion:
    """Tests for version option."""

    def test_version_option(self, cli_runner):
        """Test --version option."""
        result = cli_runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "folder-profiler" in result.output


class TestCLIIntegration:
    """End-to-end integration tests."""

    def test_full_workflow_json(self, cli_runner, test_folder, tmp_path):
        """Test full workflow: scan, analyze, and generate JSON report."""
        output_file = tmp_path / "report.json"
        
        result = cli_runner.invoke(
            cli,
            [
                "analyze",
                str(test_folder),
                "--format",
                "json",
                "--output",
                str(output_file),
                "--max-depth",
                "10",
            ],
        )
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify the report contains expected data
        with open(output_file) as f:
            data = json.load(f)
        
        assert "analysis" in data
        assert "statistics" in data["analysis"]
        assert "duplicates" in data["analysis"]
        assert "patterns" in data["analysis"]
        
        # Verify metadata
        assert "metadata" in data
        assert "generated_at" in data["metadata"]
        assert data["metadata"]["generator"] == "folder-profiler"

    def test_full_workflow_html(self, cli_runner, test_folder, tmp_path):
        """Test full workflow: scan, analyze, and generate HTML report."""
        output_file = tmp_path / "report.html"
        
        result = cli_runner.invoke(
            cli,
            [
                "analyze",
                str(test_folder),
                "--format",
                "html",
                "--output",
                str(output_file),
            ],
        )
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify HTML contains expected content
        html_content = output_file.read_text()
        assert "Folder Analysis Report" in html_content
        assert "<html" in html_content or "<!DOCTYPE" in html_content

    def test_workflow_with_filters(self, cli_runner, test_folder, tmp_path):
        """Test workflow with include/exclude patterns."""
        output_file = tmp_path / "report.json"
        
        result = cli_runner.invoke(
            cli,
            [
                "analyze",
                str(test_folder),
                "--format",
                "json",
                "--output",
                str(output_file),
                "--include",
                "*.txt",
                "--exclude",
                "duplicate.txt",
            ],
        )
        
        assert result.exit_code == 0
        assert output_file.exists()
