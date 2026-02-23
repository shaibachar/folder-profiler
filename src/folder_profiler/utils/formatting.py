"""
Formatting utilities for display.
"""

from datetime import datetime
from typing import Union


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_date(dt: Union[datetime, str]) -> str:
    """
    Format datetime in readable format.

    Args:
        dt: Datetime object or ISO string

    Returns:
        Formatted date string
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
