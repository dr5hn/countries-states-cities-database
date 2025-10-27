"""
Changelog System - Automated changelog generation from git history.

This package provides tools to track changes in the contributions/ folder
and generate per-country changelog files.

Main Components:
- changelog_generator: Main CLI entry point
- json_analyzer: Analyzes JSON diffs from contributions/
- git_parser: Extracts git commit history
- changelog_writer: Generates JSON changelog files
- deduplicator: Prevents duplicate entries
- archiver: Manages retention and archiving
- utils: Shared helper functions
"""

__version__ = '1.0.0'
