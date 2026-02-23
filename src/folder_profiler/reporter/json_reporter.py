"""
JSON report generation.
"""

from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class JSONReporter:
    """
    Generates JSON format reports.
    """

    def generate(self, analysis_results: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate JSON report.

        Args:
            analysis_results: Analysis results
            output_path: Output file path

        Returns:
            Path to generated report
        """
        # Add metadata
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "folder-profiler",
                "version": "0.1.0",
            },
            "analysis": analysis_results,
        }
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with pretty printing
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
