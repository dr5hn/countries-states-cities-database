"""
SQL Analyzer (DEPRECATED - For Reference Only)

This module was used in the old setup to track changes from world.sql.
The new setup uses json_analyzer.py to track changes from contributions/ folder.

Kept for historical reference only.
"""

import re
from typing import List, Dict, Optional


class SQLAnalyzer:
    """
    DEPRECATED: Analyzes SQL diffs from git.

    This analyzer was designed to parse INSERT/UPDATE/DELETE statements
    from world.sql diffs. It has been replaced by JSONAnalyzer which
    parses JSON diffs from contributions/ folder.

    Historical Context:
    - Old setup tracked sql/world.sql (auto-generated export file)
    - New setup tracks contributions/cities/*.json, contributions/states/states.json, etc.
    - JSON tracking provides better granularity and accuracy
    """

    def __init__(self):
        """Initialize SQL analyzer (deprecated)."""
        pass

    def analyze_diff(self, diff_text: str) -> List[Dict]:
        """
        Analyze SQL diff (deprecated).

        This method is no longer used. See JSONAnalyzer.analyze_diff() instead.

        Args:
            diff_text: Git diff output

        Returns:
            Empty list (deprecated)
        """
        print("⚠️  WARNING: SQLAnalyzer is deprecated. Use JSONAnalyzer instead.")
        return []
