"""
Main CLI entry point using Click.
"""

from pathlib import Path
from typing import cast

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from folder_profiler import __version__
from folder_profiler.analyzer.analyzer import FolderAnalyzer
from folder_profiler.reporter.console_reporter import ConsoleReporter
from folder_profiler.reporter.reporter import ReportFormat, ReportGenerator
from folder_profiler.scanner.scanner import FolderScanner

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="folder-profiler")
@click.pass_context
def cli(ctx: click.Context) -> None:
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
def analyze(
    path: str,
    output: str,
    format: str,
    max_depth: int,
    include: tuple[str, ...],
    exclude: tuple[str, ...],
    no_gitignore: bool,
) -> None:
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
            folder_tree = scanner.scan(Path(path))
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
                output_path: Path
                if not output:
                    output_path = Path(f"folder-report.{format}")
                else:
                    output_path = Path(output)

                task = progress.add_task(
                    f"[cyan]Generating {format.upper()} report...", total=None
                )
                report_gen = ReportGenerator()
                output_path = report_gen.generate(
                    analysis_results, output_path, cast(ReportFormat, format)
                )
                progress.update(task, completed=True)

                console.print(
                    f"\n[bold green]✓[/bold green] Report generated: {output_path}"
                )

        # Show scan statistics
        console.print(
            f"\n[dim]Scanned {scanner.files_scanned:,} files, "
            f"{scanner.folders_scanned:,} folders[/dim]"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis cancelled by user[/yellow]")
        raise click.Abort() from None
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise click.Abort() from e


@cli.command()
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration",
)
def config(show: bool) -> None:
    """
    Manage configuration settings.
    """
    if show:
        console.print("[bold]Folder Profiler Configuration[/bold]")
        console.print(f"Version: {__version__}")
        console.print("\n[dim]No saved configuration yet[/dim]")
    else:
        console.print("[yellow]Configuration management coming soon[/yellow]")


def main() -> int:
    """Main entry point."""
    try:
        cli(obj={})
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    main()
