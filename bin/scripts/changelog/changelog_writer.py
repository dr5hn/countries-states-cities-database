"""
Changelog Writer - Generates JSON changelog files.

Creates per-country changelog files and global changelog with statistics.
Supports minified JSON output for size optimization.
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

try:
    from . import utils
except ImportError:
    import utils


class ChangelogWriter:
    """Writes changelog data to JSON files."""

    def __init__(self, minify: bool = True):
        """
        Initialize changelog writer.

        Args:
            minify: If True, write minified JSON
        """
        self.minify = minify
        self.output_dir = utils.get_output_dir()

    def write_changelogs(self, changes_by_country: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Write per-country changelog files.

        Args:
            changes_by_country: Dictionary mapping country codes to change lists

        Returns:
            Statistics dictionary (files_written, total_changes)
        """
        stats = {
            'files_written': 0,
            'total_changes': 0
        }

        # Ensure output directories exist
        countries_dir = self.output_dir / 'countries'
        utils.ensure_dir(countries_dir)

        # Write per-country files
        for country_code, changes in changes_by_country.items():
            if not changes:
                continue

            file_path = countries_dir / f'{country_code}.json'

            changelog_data = {
                'country_code': country_code,
                'change_count': len(changes),
                'changes': changes
            }

            utils.write_json(changelog_data, file_path, minify=self.minify)

            stats['files_written'] += 1
            stats['total_changes'] += len(changes)

        return stats

    def write_global_changelog(self, all_changes: List[Dict], metadata: Dict = None) -> Path:
        """
        Write global changelog file with all changes.

        Args:
            all_changes: List of all changes
            metadata: Optional metadata to include

        Returns:
            Path to written file
        """
        file_path = utils.get_global_changelog_path()

        # Build statistics
        stats = self._calculate_statistics(all_changes)

        changelog_data = {
            'generated_at': utils.format_timestamp(datetime.now()),
            'total_changes': len(all_changes),
            'statistics': stats,
            'changes': all_changes
        }

        if metadata:
            changelog_data['metadata'] = metadata

        utils.write_json(changelog_data, file_path, minify=self.minify)

        return file_path

    def write_statistics(self, all_changes: List[Dict], metadata: Dict = None) -> Path:
        """
        Write statistics summary file.

        Args:
            all_changes: List of all changes
            metadata: Optional metadata to include

        Returns:
            Path to written file
        """
        file_path = utils.get_stats_path()

        stats = self._calculate_statistics(all_changes)

        stats_data = {
            'generated_at': utils.format_timestamp(datetime.now()),
            'total_changes': len(all_changes),
            'statistics': stats
        }

        if metadata:
            stats_data['metadata'] = metadata

        utils.write_json(stats_data, file_path, minify=False)  # Never minify stats

        return file_path

    def _calculate_statistics(self, changes: List[Dict]) -> Dict:
        """
        Calculate statistics from changes.

        Args:
            changes: List of change dictionaries

        Returns:
            Statistics dictionary
        """
        stats = {
            'by_action': defaultdict(int),
            'by_entity': defaultdict(int),
            'by_country': defaultdict(int),
            'by_date': defaultdict(int)
        }

        for change in changes:
            # Count by action
            action = change.get('action', 'unknown')
            stats['by_action'][action] += 1

            # Count by entity type
            entity_type = change.get('entity_type', 'unknown')
            stats['by_entity'][entity_type] += 1

            # Count by country
            country_code = change.get('country_code', 'unknown')
            stats['by_country'][country_code] += 1

            # Count by date (YYYY-MM-DD)
            timestamp = change.get('timestamp', '')
            if timestamp:
                date = timestamp.split('T')[0]  # Extract YYYY-MM-DD
                stats['by_date'][date] += 1

        # Convert defaultdicts to regular dicts for JSON serialization
        return {
            'by_action': dict(stats['by_action']),
            'by_entity': dict(stats['by_entity']),
            'by_country': dict(stats['by_country']),
            'by_date': dict(sorted(stats['by_date'].items()))  # Sort by date
        }

    def group_changes_by_country(self, changes: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group changes by country code.

        Args:
            changes: List of change dictionaries

        Returns:
            Dictionary mapping country codes to change lists
        """
        by_country = defaultdict(list)

        for change in changes:
            country_code = change.get('country_code', 'unknown')
            by_country[country_code].append(change)

        return dict(by_country)

    def get_output_summary(self) -> Dict:
        """
        Get summary of output files and sizes.

        Returns:
            Summary dictionary with file counts and sizes
        """
        summary = {
            'countries_dir': str(self.output_dir / 'countries'),
            'country_files': 0,
            'total_size': 0,
            'files': []
        }

        # Check countries directory
        countries_dir = self.output_dir / 'countries'
        if countries_dir.exists():
            for file_path in sorted(countries_dir.glob('*.json')):
                size = utils.get_file_size(file_path)
                summary['country_files'] += 1
                summary['total_size'] += size
                summary['files'].append({
                    'name': file_path.name,
                    'size': size,
                    'size_formatted': utils.format_file_size(size)
                })

        # Check global files
        for file_path in [utils.get_global_changelog_path(), utils.get_stats_path()]:
            if file_path.exists():
                size = utils.get_file_size(file_path)
                summary['total_size'] += size
                summary['files'].append({
                    'name': file_path.name,
                    'size': size,
                    'size_formatted': utils.format_file_size(size)
                })

        summary['total_size_formatted'] = utils.format_file_size(summary['total_size'])

        return summary
