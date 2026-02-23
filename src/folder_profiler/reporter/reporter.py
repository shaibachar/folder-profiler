"""
Main report generation orchestrator.
"""

from pathlib import Path
from typing import Dict, Any, Literal
from folder_profiler.reporter.json_reporter import JSONReporter
from folder_profiler.reporter.html_reporter import HTMLReporter

ReportFormat = Literal["json", "html", "pdf"]


class ReportGenerator:
    """
    Generates reports in various formats.
    """

    def __init__(self):
        """Initialize the report generator."""
        self.json_reporter = JSONReporter()
        self.html_reporter = HTMLReporter()

    def generate(
        self,
        analysis_results: Dict[str, Any],
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
        # Implementation will be added in REPORT-001, REPORT-002, REPORT-003
        raise NotImplementedError("Report generator implementation pending")
