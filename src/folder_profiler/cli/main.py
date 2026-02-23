"""
Main CLI entry point using Click.
"""

import click
from pathlib import Path
from rich.console import Console

from folder_profiler import __version__

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
    type=click.Choice(["json", "html", "pdf"], case_sensitive=False),
    default="html",
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
def analyze(path, output, format, max_depth, include, exclude):
    """
    Analyze a folder and generate a report.

    PATH is the folder to analyze.
    """
    console.print(f"[bold blue]Analyzing:[/bold blue] {path}")
    console.print(f"[dim]Output format: {format}[/dim]")

    # Implementation will be added in CLI-001
    console.print("[yellow]Implementation pending (CLI-001)[/yellow]")


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
    # Implementation will be added in CLI-002
    console.print("[yellow]Implementation pending (CLI-002)[/yellow]")


def main():
    """Main entry point."""
    return cli(obj={})


if __name__ == "__main__":
    main()
