"""
Console/Terminal report generation with Rich formatting.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn


class ConsoleReporter:
    """
    Generates formatted console output using Rich.
    """
    
    def __init__(self, console: Console = None):
        """
        Initialize console reporter.
        
        Args:
            console: Rich Console instance (creates new one if not provided)
        """
        self.console = console or Console()
    
    def generate(self, analysis_results: Dict[str, Any]) -> None:
        """
        Print analysis results to console.
        
        Args:
            analysis_results: Analysis results to display
        """
        stats = analysis_results.get("statistics", {})
        duplicates = analysis_results.get("duplicates", {})
        patterns = analysis_results.get("patterns", {})
        
        # Print summary
        self._print_summary(stats.get("summary", {}))
        
        # Print largest files
        self.console.print("\n")
        self._print_largest_files(stats.get("largest_files", []))
        
        # Print duplicates
        self.console.print("\n")
        self._print_duplicates(duplicates)
        
        # Print file extensions
        self.console.print("\n")
        self._print_extensions(stats.get("extensions", {}))
        
        # Print patterns
        self.console.print("\n")
        self._print_patterns(patterns)
    
    def _print_summary(self, summary: dict) -> None:
        """Print summary statistics."""
        table = Table(title="📊 Summary Statistics", show_header=False, box=None)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green bold")
        
        table.add_row("Total Files", f"{summary.get('total_files', 0):,}")
        table.add_row("Total Folders", f"{summary.get('total_folders', 0):,}")
        table.add_row("Total Size", self._format_size(summary.get('total_size', 0)))
        table.add_row("Average File Size", self._format_size(int(summary.get('average_file_size', 0))))
        table.add_row("Median File Size", self._format_size(int(summary.get('median_file_size', 0))))
        table.add_row("Largest File", self._format_size(summary.get('largest_file_size', 0)))
        
        self.console.print(table)
    
    def _print_largest_files(self, files: list) -> None:
        """Print largest files table."""
        if not files:
            return
        
        table = Table(title="📁 Top 10 Largest Files", box=None)
        table.add_column("File Name", style="cyan", no_wrap=False)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Extension", style="magenta")
        
        for file in files[:10]:
            table.add_row(
                file.get('name', ''),
                self._format_size(file.get('size', 0)),
                file.get('extension', '')
            )
        
        self.console.print(table)
    
    def _print_duplicates(self, duplicates: dict) -> None:
        """Print duplicates summary."""
        stats = duplicates.get('statistics', {})
        
        table = Table(title="🔄 Duplicate Files", show_header=False, box=None)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="yellow bold")
        
        table.add_row("Duplicate Sets", f"{stats.get('total_duplicate_sets', 0):,}")
        table.add_row("Duplicate Files", f"{stats.get('total_duplicate_files', 0):,}")
        table.add_row("Wasted Space", self._format_size(stats.get('wasted_space', 0)))
        
        self.console.print(table)
        
        # Show top duplicate groups
        groups = duplicates.get('duplicate_groups', [])
        if groups:
            self.console.print("\n[bold]Top Duplicate Groups:[/bold]")
            for i, group in enumerate(groups[:5], 1):
                self.console.print(
                    f"  {i}. [cyan]{group.get('count', 0)} files[/cyan] × "
                    f"[green]{self._format_size(group.get('size', 0))}[/green] = "
                    f"[yellow]{self._format_size(group.get('size', 0) * (group.get('count', 0) - 1))}[/yellow] wasted"
                )
    
    def _print_extensions(self, extensions: dict) -> None:
        """Print file extensions table."""
        if not extensions:
            return
        
        table = Table(title="📄 File Extensions", box=None)
        table.add_column("Extension", style="cyan")
        table.add_column("Count", style="green", justify="right")
        table.add_column("Total Size", style="blue", justify="right")
        
        for ext, data in list(extensions.items())[:15]:
            table.add_row(
                ext,
                f"{data.get('count', 0):,}",
                self._format_size(data.get('total_size', 0))
            )
        
        self.console.print(table)
    
    def _print_patterns(self, patterns: dict) -> None:
        """Print detected patterns."""
        temp_files = patterns.get('temp_files', [])
        build_artifacts = patterns.get('build_artifacts', [])
        version_patterns = patterns.get('version_patterns', [])
        
        table = Table(title="🔍 Detected Patterns", show_header=False, box=None)
        table.add_column("Pattern Type", style="cyan", width=25)
        table.add_column("Count", style="yellow bold")
        
        table.add_row("Temporary Files", str(len(temp_files)))
        table.add_row("Build Artifacts", str(len(build_artifacts)))
        table.add_row("Version Patterns", str(len(version_patterns)))
        
        self.console.print(table)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
