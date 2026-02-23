"""
Tests for utility functions.
"""

import pytest
from datetime import datetime

from folder_profiler.utils.formatting import format_size, format_date


class TestFormatSize:
    """Test format_size function."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        assert format_size(100) == "100.00 B"

    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(1536) == "1.50 KB"

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1048576) == "1.00 MB"
        assert format_size(1572864) == "1.50 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1073741824) == "1.00 GB"

    def test_format_zero(self):
        """Test formatting zero bytes."""
        assert format_size(0) == "0.00 B"


class TestFormatDate:
    """Test format_date function."""

    def test_format_datetime_object(self):
        """Test formatting datetime object."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        assert format_date(dt) == "2024-01-15 14:30:45"

    def test_format_iso_string(self):
        """Test formatting ISO date string."""
        iso_str = "2024-01-15T14:30:45"
        assert format_date(iso_str) == "2024-01-15 14:30:45"
