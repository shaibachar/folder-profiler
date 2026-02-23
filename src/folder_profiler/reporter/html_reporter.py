"""
HTML report generation.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import html


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
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML content
        html_content = self._generate_html(analysis_results)
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML content from analysis results."""
        stats = analysis.get("statistics", {})
        summary = stats.get("summary", {})
        duplicates = analysis.get("duplicates", {})
        patterns = analysis.get("patterns", {})
        recommendations = analysis.get("recommendations", {})
        
        # Build recommendations section if available
        recommendations_html = ""
        if recommendations and recommendations.get("recommendations"):
            recommendations_html = f"""
    <h2>Smart Recommendations</h2>
    {self._generate_health_score_card(recommendations)}
    {self._generate_recommendations_table(recommendations.get('recommendations', []))}
            """
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Folder Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .health-score {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .health-score .score {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .priority-critical {{ color: #d32f2f; font-weight: bold; }}
        .priority-high {{ color: #f57c00; font-weight: bold; }}
        .priority-medium {{ color: #fbc02d; font-weight: bold; }}
        .priority-low {{ color: #1976d2; }}
        .priority-info {{ color: #757575; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>Folder Analysis Report</h1>
    <p>Generated: {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
    
    {recommendations_html}
    
    <h2>Summary</h2>
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Total Files</h3>
            <div class="value">{summary.get('total_files', 0):,}</div>
        </div>
        <div class="summary-card">
            <h3>Total Folders</h3>
            <div class="value">{summary.get('total_folders', 0):,}</div>
        </div>
        <div class="summary-card">
            <h3>Total Size</h3>
            <div class="value">{self._format_size(summary.get('total_size', 0))}</div>
        </div>
        <div class="summary-card">
            <h3>Average File Size</h3>
            <div class="value">{self._format_size(int(summary.get('average_file_size', 0)))}</div>
        </div>
    </div>
    
    <h2>Largest Files</h2>
    {self._generate_largest_files_table(stats.get('largest_files', []))}
    
    <h2>Duplicates</h2>
    {self._generate_duplicates_section(duplicates)}
    
    <h2>File Extensions</h2>
    {self._generate_extensions_table(stats.get('extensions', {}))}
    
    <div class="footer">
        Generated by folder-profiler v0.1.0
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _generate_largest_files_table(self, files: list) -> str:
        """Generate HTML table for largest files."""
        if not files:
            return "<p>No files found.</p>"
        
        rows = ""
        for file in files[:10]:
            rows += f"""
        <tr>
            <td>{html.escape(file.get('name', ''))}</td>
            <td>{self._format_size(file.get('size', 0))}</td>
            <td>{html.escape(file.get('extension', ''))}</td>
        </tr>
            """
        
        return f"""
        <table>
            <tr>
                <th>File Name</th>
                <th>Size</th>
                <th>Extension</th>
            </tr>
            {rows}
        </table>
        """
    
    def _generate_duplicates_section(self, duplicates: dict) -> str:
        """Generate duplicates section."""
        stats = duplicates.get('statistics', {})
        
        return f"""
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Duplicate Sets</h3>
                <div class="value">{stats.get('total_duplicate_sets', 0):,}</div>
            </div>
            <div class="summary-card">
                <h3>Duplicate Files</h3>
                <div class="value">{stats.get('total_duplicate_files', 0):,}</div>
            </div>
            <div class="summary-card">
                <h3>Wasted Space</h3>
                <div class="value">{self._format_size(stats.get('wasted_space', 0))}</div>
            </div>
        </div>
        """
    
    def _generate_extensions_table(self, extensions: dict) -> str:
        """Generate HTML table for file extensions."""
        if not extensions:
            return "<p>No extensions found.</p>"
        
        rows = ""
        for ext, data in list(extensions.items())[:15]:
            rows += f"""
        <tr>
            <td>{html.escape(ext)}</td>
            <td>{data.get('count', 0):,}</td>
            <td>{self._format_size(data.get('total_size', 0))}</td>
        </tr>
            """
        
        return f"""
        <table>
            <tr>
                <th>Extension</th>
                <th>Count</th>
                <th>Total Size</th>
            </tr>
            {rows}
        </table>
        """
    
    def _generate_health_score_card(self, recommendations: dict) -> str:
        """Generate health score card."""
        health_score = recommendations.get("health_score", 0)
        summary = recommendations.get("summary", "")
        
        # Determine color based on score
        if health_score >= 90:
            color = "#4CAF50"  # Green
        elif health_score >= 75:
            color = "#2196F3"  # Blue
        elif health_score >= 60:
            color = "#FFC107"  # Amber
        elif health_score >= 40:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red
        
        return f"""
        <div class="health-score">
            <h3>Folder Health Score</h3>
            <div class="score" style="color: {color};">{health_score}/100</div>
            <p>{html.escape(summary)}</p>
        </div>
        """
    
    def _generate_recommendations_table(self, recommendations: list) -> str:
        """Generate recommendations table."""
        if not recommendations:
            return "<p>No recommendations available.</p>"
        
        rows = ""
        for rec in recommendations[:10]:  # Top 10
            priority = rec.get("priority", "info")
            priority_class = f"priority-{priority}"
            
            savings = rec.get("estimated_savings", 0)
            impact = self._format_size(savings) if savings > 0 else "-"
            
            rows += f"""
        <tr>
            <td class="{priority_class}">{priority.upper()}</td>
            <td>{html.escape(rec.get('title', ''))}</td>
            <td>{html.escape(rec.get('action', ''))}</td>
            <td>{impact}</td>
        </tr>
            """
        
        return f"""
        <table>
            <tr>
                <th>Priority</th>
                <th>Title</th>
                <th>Action</th>
                <th>Estimated Savings</th>
            </tr>
            {rows}
        </table>
        """

