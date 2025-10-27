#!/usr/bin/env python3
"""
Changelog Generator - Main CLI entry point.

Orchestrates the entire changelog generation process:
1. Parse git commits from contributions/ folder
2. Analyze JSON diffs for changes
3. Deduplicate changes
4. Apply retention policy
5. Write changelog files

Usage:
    python3 bin/scripts/changelog/changelog_generator.py [OPTIONS]

Options:
    --retention-months N   Retention period (default: 24)
    --since DATE          Process commits since date
    --until DATE          Process commits until date
    --dry-run            Preview without writing files
    --show-sizes         Show file sizes in summary
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from git_parser import GitParser
from json_analyzer import JSONAnalyzer
from deduplicator import Deduplicator
from archiver import Archiver
from changelog_writer import ChangelogWriter
import utils


class ChangelogGenerator:
    """Main changelog generator orchestrator."""

    def __init__(self, config: dict = None, dry_run: bool = False):
        """
        Initialize changelog generator.

        Args:
            config: Configuration dictionary (loads from file if None)
            dry_run: If True, don't write files
        """
        self.config = config or utils.load_config()
        self.dry_run = dry_run

        # Initialize components
        self.git_parser = GitParser(
            repo_path=str(utils.get_repo_root()),
            target_paths=self.config.get('target_paths', ['contributions/'])
        )
        self.json_analyzer = JSONAnalyzer()
        self.deduplicator = Deduplicator()
        self.archiver = Archiver(
            retention_months=self.config.get('retention_months', 24)
        )
        self.writer = ChangelogWriter(
            minify=self.config.get('minify_json', True)
        )

    def generate(self, since: str = None, until: str = None) -> dict:
        """
        Generate changelogs.

        Args:
            since: Start date for commits
            until: End date for commits

        Returns:
            Statistics dictionary
        """
        print("🔍 Fetching git commits...")
        commits = self.git_parser.get_commits(since=since, until=until)
        print(f"   Found {len(commits)} commits")

        if not commits:
            print("⚠️  No commits found")
            return {'status': 'no_commits'}

        print("\n📊 Analyzing changes...")
        all_changes = []

        for i, commit in enumerate(commits, 1):
            if i % 100 == 0:
                print(f"   Processing commit {i}/{len(commits)}...")

            # Process each file diff in the commit
            for file_diff in commit.get('file_diffs', []):
                changes = self.json_analyzer.analyze_diff(
                    file_diff['diff'],
                    file_diff['path']
                )

                # Add commit metadata to each change
                for change in changes:
                    change['timestamp'] = utils.format_timestamp(commit['date'])
                    change['commit'] = {
                        'sha': commit['sha'][:7],
                        'author': commit['author'],
                        'message': commit['message'].split('\n')[0]  # First line only
                    }

                all_changes.extend(changes)

        print(f"   Found {len(all_changes)} raw changes")

        print("\n🔄 Deduplicating...")
        unique_changes = self.deduplicator.filter_duplicates(all_changes)
        print(f"   {len(unique_changes)} unique changes (removed {len(all_changes) - len(unique_changes)} duplicates)")

        print("\n📅 Applying retention policy...")
        retained_changes, archived_changes = self.archiver.apply_retention(unique_changes)
        print(f"   Retaining {len(retained_changes)} recent changes")
        print(f"   Archiving {len(archived_changes)} old changes")

        if self.dry_run:
            print("\n⚠️  DRY RUN - No files written")
            return self._build_stats(retained_changes, archived_changes)

        print("\n📝 Writing changelog files...")

        # Group changes by country
        by_country = self.writer.group_changes_by_country(retained_changes)
        print(f"   Changes span {len(by_country)} countries")

        # Write per-country files
        country_stats = self.writer.write_changelogs(by_country)
        print(f"   ✓ Wrote {country_stats['files_written']} country files")

        # Write global changelog
        global_path = self.writer.write_global_changelog(retained_changes)
        print(f"   ✓ Wrote global changelog: {global_path.name}")

        # Write statistics
        stats_path = self.writer.write_statistics(retained_changes, metadata={
            'retention_months': self.archiver.retention_months,
            'commits_processed': len(commits)
        })
        print(f"   ✓ Wrote statistics: {stats_path.name}")

        # Archive old changes
        if archived_changes:
            archive_stats = self.archiver.archive_old_changes(archived_changes)
            print(f"   ✓ Archived {archive_stats['changes_archived']} changes to {archive_stats['years_archived']} year files")

        return self._build_stats(retained_changes, archived_changes)

    def _build_stats(self, retained: list, archived: list) -> dict:
        """Build statistics dictionary."""
        all_changes = retained + archived

        stats = {
            'total_changes': len(all_changes),
            'retained_changes': len(retained),
            'archived_changes': len(archived),
            'by_action': {},
            'by_entity': {},
            'by_country': {}
        }

        for change in all_changes:
            action = change.get('action', 'unknown')
            entity = change.get('entity_type', 'unknown')
            country = change.get('country_code', 'unknown')

            stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
            stats['by_entity'][entity] = stats['by_entity'].get(entity, 0) + 1
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1

        return stats


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate changelogs from contributions/ folder changes',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--retention-months',
        type=int,
        default=None,
        help='Retention period in months (default: from config)'
    )
    parser.add_argument(
        '--since',
        type=str,
        default=None,
        help='Process commits since date (YYYY-MM-DD or git format)'
    )
    parser.add_argument(
        '--until',
        type=str,
        default=None,
        help='Process commits until date (YYYY-MM-DD or git format)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without writing files'
    )
    parser.add_argument(
        '--show-sizes',
        action='store_true',
        help='Show file sizes in summary'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Changelog Generator")
    print("=" * 60)

    try:
        # Load config and apply CLI overrides
        config = utils.load_config()
        if args.retention_months is not None:
            config['retention_months'] = args.retention_months

        # Generate changelogs
        generator = ChangelogGenerator(config=config, dry_run=args.dry_run)
        stats = generator.generate(since=args.since, until=args.until)

        # Print summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Total changes: {stats.get('total_changes', 0)}")
        print(f"Retained: {stats.get('retained_changes', 0)}")
        print(f"Archived: {stats.get('archived_changes', 0)}")

        print("\nBy action:")
        for action, count in sorted(stats.get('by_action', {}).items()):
            print(f"  {action}: {count}")

        print("\nBy entity:")
        for entity, count in sorted(stats.get('by_entity', {}).items()):
            print(f"  {entity}: {count}")

        print(f"\nBy country: {len(stats.get('by_country', {}))} countries")

        if args.show_sizes and not args.dry_run:
            summary = generator.writer.get_output_summary()
            print(f"\nOutput files: {summary['country_files']} countries")
            print(f"Total size: {summary['total_size_formatted']}")

        print("\n✅ Done!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
