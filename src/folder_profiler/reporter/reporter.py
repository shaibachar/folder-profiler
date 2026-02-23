"""
Main report generation orchestrator.
"""

from pathlib import Path
from typing import Any, Literal

from folder_profiler.reporter.html_reporter import HTMLReporter
from folder_profiler.reporter.json_reporter import JSONReporter

ReportFormat = Literal["json", "html", "pdf"]


class ReportGenerator:
    """
    Generates reports in various formats.
    """

    def __init__(self) -> None:
        """Initialize the report generator."""
        self.json_reporter = JSONReporter()
        self.html_reporter = HTMLReporter()

    def generate(
        self,
        analysis_results: dict[str, Any],
        output_path: Path,
        format: ReportFormat = "html",
    ) -> Path:
        """
        Generate a report in the specified format.

        Args:
            analysis_results: Analysis results to report
            output_path: Path to write report to
            format: Report format (json, html, pdf)

        Returns:
            Path to generated report

        Raises:
            ValueError: If format is unsupported
        """
        if format == "json":
            return self.json_reporter.generate(analysis_results, output_path)
        elif format == "html":
            return self.html_reporter.generate(analysis_results, output_path)
        elif format == "pdf":
            raise NotImplementedError("PDF format not yet supported")
        else:
            raise ValueError(f"Unsupported format: {format}")
