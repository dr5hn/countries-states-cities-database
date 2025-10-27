"""
Archiver - Manages changelog retention and archiving.

Applies retention policy to keep recent changes in main files.
Archives old changes by year for historical reference.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

try:
    from . import utils
except ImportError:
    import utils


class Archiver:
    """Manages changelog retention and archiving."""

    def __init__(self, retention_months: int = 24):
        """
        Initialize archiver.

        Args:
            retention_months: Number of months to retain in main changelog
        """
        self.retention_months = retention_months
        self.output_dir = utils.get_output_dir()
        self.archive_dir = self.output_dir / 'archive'

    def apply_retention(self, changes: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Split changes into retained and archived based on retention policy.

        Args:
            changes: List of all changes

        Returns:
            Tuple of (retained_changes, archived_changes)
        """
        if self.retention_months <= 0:
            # No archiving - retain all
            return changes, []

        cutoff_date = datetime.now() - timedelta(days=self.retention_months * 30)

        retained = []
        archived = []

        for change in changes:
            timestamp_str = change.get('timestamp', '')
            if not timestamp_str:
                # No timestamp - keep in retained
                retained.append(change)
                continue

            try:
                change_date = utils.parse_timestamp(timestamp_str)

                if change_date >= cutoff_date:
                    retained.append(change)
                else:
                    archived.append(change)

            except ValueError:
                # Invalid timestamp - keep in retained
                retained.append(change)

        return retained, archived

    def archive_old_changes(self, changes: List[Dict]) -> Dict[str, int]:
        """
        Archive old changes by year.

        Args:
            changes: List of changes to archive

        Returns:
            Statistics dictionary (years_archived, changes_archived)
        """
        if not changes:
            return {'years_archived': 0, 'changes_archived': 0}

        # Ensure archive directory exists
        utils.ensure_dir(self.archive_dir)

        # Group changes by year
        by_year = self._group_by_year(changes)

        stats = {
            'years_archived': 0,
            'changes_archived': 0
        }

        # Write archive files by year
        for year, year_changes in by_year.items():
            file_path = self.archive_dir / f'{year}.json'

            archive_data = {
                'year': year,
                'change_count': len(year_changes),
                'archived_at': utils.format_timestamp(datetime.now()),
                'changes': year_changes
            }

            utils.write_json(archive_data, file_path, minify=True)

            stats['years_archived'] += 1
            stats['changes_archived'] += len(year_changes)

        return stats

    def _group_by_year(self, changes: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Group changes by year.

        Args:
            changes: List of change dictionaries

        Returns:
            Dictionary mapping year to change lists
        """
        by_year = defaultdict(list)

        for change in changes:
            timestamp_str = change.get('timestamp', '')
            if not timestamp_str:
                # No timestamp - skip
                continue

            try:
                change_date = utils.parse_timestamp(timestamp_str)
                year = change_date.year
                by_year[year].append(change)

            except ValueError:
                # Invalid timestamp - skip
                continue

        return dict(by_year)

    def get_archive_summary(self) -> Dict:
        """
        Get summary of archived files.

        Returns:
            Summary dictionary with archive info
        """
        summary = {
            'archive_dir': str(self.archive_dir),
            'archive_files': 0,
            'total_size': 0,
            'years': []
        }

        if not self.archive_dir.exists():
            return summary

        for file_path in sorted(self.archive_dir.glob('*.json')):
            size = utils.get_file_size(file_path)
            summary['archive_files'] += 1
            summary['total_size'] += size

            # Try to read change count from file
            data = utils.read_json(file_path)
            change_count = data.get('change_count', 0) if data else 0

            summary['years'].append({
                'year': file_path.stem,
                'file': file_path.name,
                'size': utils.format_file_size(size),
                'changes': change_count
            })

        summary['total_size_formatted'] = utils.format_file_size(summary['total_size'])

        return summary

    def clean_archives(self) -> int:
        """
        Remove all archive files.

        Returns:
            Number of files removed
        """
        if not self.archive_dir.exists():
            return 0

        return utils.clean_directory(self.archive_dir, '*.json')
