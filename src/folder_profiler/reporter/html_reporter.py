"""
HTML report generation.
"""

from pathlib import Path
from typing import Dict, Any


class HTMLReporter:
    """
    Generates HTML format reports.
    """

    def generate(self, analysis_results: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate HTML report.

        Args:
            analysis_results: Analysis results
            output_path: Output file path

        Returns:
            Path to generated report
        """
        # Implementation will be added in REPORT-002 and REPORT-003
        raise NotImplementedError("HTML reporter implementation pending")
