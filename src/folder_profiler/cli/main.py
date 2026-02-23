"""
Main CLI entry point using Click.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from folder_profiler import __version__
from folder_profiler.scanner.scanner import FolderScanner
from folder_profiler.analyzer.analyzer import FolderAnalyzer
from folder_profiler.reporter.reporter import ReportGenerator
from folder_profiler.reporter.console_reporter import ConsoleReporter

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="folder-profiler")
@click.pass_context
def cli(ctx):
    """
    Folder Profiler - Intelligent file system analysis tool.

    Analyze folder structures, detect duplicates, and get AI-powered
    recommendations for organization and cleanup.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output report path",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "console"], case_sensitive=False),
    default="console",
    help="Report format",
)
@click.option(
    "--max-depth",
    "-d",
    type=int,
    help="Maximum depth to scan",
)
@click.option(
    "--include",
    "-i",
    multiple=True,
    help="Include patterns (can be specified multiple times)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Exclude patterns (can be specified multiple times)",
)
@click.option(
    "--no-gitignore",
    is_flag=True,
    help="Don't respect .gitignore files",
)
def analyze(path, output, format, max_depth, include, exclude, no_gitignore):
    """
    Analyze a folder and generate a report.

    PATH is the folder to analyze.
    """
    console.print(f"[bold blue]Analyzing:[/bold blue] {path}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Scan the folder
            task = progress.add_task("[cyan]Scanning folder structure...", total=None)
            scanner = FolderScanner(
                max_depth=max_depth,
                include_patterns=list(include) if include else None,
                exclude_patterns=list(exclude) if exclude else None,
                respect_gitignore=not no_gitignore,
            )
            folder_tree = scanner.scan(path)
            progress.update(task, completed=True)
            
            # Analyze the folder
            task = progress.add_task("[cyan]Analyzing files...", total=None)
            analyzer = FolderAnalyzer()
            analysis_results = analyzer.analyze(folder_tree)
            progress.update(task, completed=True)
            
            # Generate report
            if format == "console":
                console.print("\n")
                reporter = ConsoleReporter(console)
                reporter.generate(analysis_results)
            else:
                if not output:
                    output = Path(f"folder-report.{format}")
                
                task = progress.add_task(f"[cyan]Generating {format.upper()} report...", total=None)
                report_gen = ReportGenerator()
                report_path = report_gen.generate(analysis_results, output, format)
                progress.update(task, completed=True)
                
                console.print(f"\n[bold green]✓[/bold green] Report generated: {report_path}")
        
        # Show scan statistics
        console.print(f"\n[dim]Scanned {scanner.files_scanned:,} files, "
                     f"{scanner.folders_scanned:,} folders[/dim]")
                     
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis cancelled by user[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration",
)
def config(show):
    """
    Manage configuration settings.
    """
    if show:
        console.print("[bold]Folder Profiler Configuration[/bold]")
        console.print(f"Version: {__version__}")
        console.print("\n[dim]No saved configuration yet[/dim]")
    else:
        console.print("[yellow]Configuration management coming soon[/yellow]")


def main():
    """Main entry point."""
    return cli(obj={})


if __name__ == "__main__":
    main()
