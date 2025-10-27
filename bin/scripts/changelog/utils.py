"""
Utilities - Shared helper functions for changelog system.

Provides configuration loading, date formatting, JSON operations, and file I/O.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def load_config() -> Dict[str, Any]:
    """
    Load changelog configuration from bin/config/changelog.json.

    Returns:
        Configuration dictionary
    """
    # Determine config path relative to this script
    script_dir = Path(__file__).parent
    config_path = script_dir.parent.parent / 'config' / 'changelog.json'

    if not config_path.exists():
        # Fallback to old location for backward compatibility
        config_path = Path('config/changelog.json')

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        return json.load(f)


def get_repo_root() -> Path:
    """
    Get repository root directory.

    Returns:
        Path to repository root
    """
    # Start from this script's directory and find .git
    current = Path(__file__).parent
    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent

    # Fallback to current working directory
    return Path.cwd()


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime for changelog display.

    Args:
        dt: Datetime object

    Returns:
        ISO 8601 formatted string
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime.

    Args:
        timestamp_str: ISO 8601 timestamp string

    Returns:
        Datetime object (timezone-naive)
    """
    # Handle various timestamp formats
    formats = [
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d'
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            # Ensure timezone-naive for comparison
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    raise ValueError(f"Could not parse timestamp: {timestamp_str}")


def write_json(data: Any, file_path: Path, minify: bool = False) -> None:
    """
    Write data to JSON file.

    Args:
        data: Data to write
        file_path: Output file path
        minify: If True, write minified JSON
    """
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        if minify:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(file_path: Path) -> Any:
    """
    Read JSON file.

    Args:
        file_path: Input file path

    Returns:
        Parsed JSON data
    """
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dir(dir_path: Path) -> None:
    """
    Ensure directory exists.

    Args:
        dir_path: Directory path to create
    """
    dir_path.mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: File path

    Returns:
        Size in bytes
    """
    if not file_path.exists():
        return 0
    return file_path.stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size for human reading.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_output_dir() -> Path:
    """
    Get changelogs output directory.

    Returns:
        Path to changelogs/ directory
    """
    return get_repo_root() / 'changelogs'


def clean_directory(dir_path: Path, pattern: str = "*") -> int:
    """
    Remove files matching pattern in directory.

    Args:
        dir_path: Directory to clean
        pattern: Glob pattern for files to remove

    Returns:
        Number of files removed
    """
    if not dir_path.exists():
        return 0

    count = 0
    for file_path in dir_path.glob(pattern):
        if file_path.is_file():
            file_path.unlink()
            count += 1

    return count


def get_changelog_path(country_code: str) -> Path:
    """
    Get path to country-specific changelog file.

    Args:
        country_code: ISO country code

    Returns:
        Path to changelog JSON file
    """
    output_dir = get_output_dir()
    return output_dir / 'countries' / f'{country_code}.json'


def get_global_changelog_path() -> Path:
    """
    Get path to global changelog file.

    Returns:
        Path to global changelog JSON file
    """
    return get_output_dir() / 'changelog.json'


def get_stats_path() -> Path:
    """
    Get path to statistics file.

    Returns:
        Path to stats JSON file
    """
    return get_output_dir() / 'stats.json'
