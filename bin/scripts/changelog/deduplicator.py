"""
Deduplicator - Prevents duplicate changelog entries.

Uses SHA-256 hashing to detect and filter duplicate changes across commits.
Maintains a seen set to track processed changes.
"""

import hashlib
import json
from typing import Dict, Set, List


class Deduplicator:
    """Deduplicates changelog entries using content hashing."""

    def __init__(self):
        """Initialize deduplicator with empty seen set."""
        self.seen_hashes: Set[str] = set()

    def is_duplicate(self, change: Dict) -> bool:
        """
        Check if a change has been seen before.

        Args:
            change: Change dictionary to check

        Returns:
            True if duplicate, False if unique
        """
        change_hash = self._hash_change(change)

        if change_hash in self.seen_hashes:
            return True

        self.seen_hashes.add(change_hash)
        return False

    def filter_duplicates(self, changes: List[Dict]) -> List[Dict]:
        """
        Filter duplicate changes from a list.

        Args:
            changes: List of change dictionaries

        Returns:
            List with duplicates removed
        """
        unique_changes = []

        for change in changes:
            if not self.is_duplicate(change):
                unique_changes.append(change)

        return unique_changes

    def _hash_change(self, change: Dict) -> str:
        """
        Generate hash for a change.

        Hashes key attributes: action, entity_type, entity ID/name, and specific change details.

        Args:
            change: Change dictionary

        Returns:
            SHA-256 hash string
        """
        # Build a canonical representation for hashing
        hash_data = {
            'action': change.get('action'),
            'entity_type': change.get('entity_type'),
            'country_code': change.get('country_code'),
        }

        # Include entity identifier (ID or name)
        entity = change.get('entity', {})
        if 'id' in entity:
            hash_data['entity_id'] = entity['id']
        elif 'name' in entity:
            hash_data['entity_name'] = entity['name']

        # Include change-specific data
        changes_data = change.get('changes', {})

        if change['action'] == 'add':
            # For additions, hash the added fields
            hash_data['added'] = changes_data.get('added', {})

        elif change['action'] == 'update':
            # For updates, hash the updated fields (new values)
            updated = changes_data.get('updated', {})
            hash_data['updated'] = {k: v.get('new') for k, v in updated.items()}

        elif change['action'] == 'delete':
            # For deletions, hash the deleted fields
            hash_data['deleted'] = changes_data.get('deleted', {})

        # Convert to JSON string (sorted keys for consistency)
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)

        # Generate SHA-256 hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def get_stats(self) -> Dict[str, int]:
        """
        Get deduplication statistics.

        Returns:
            Dictionary with stats (unique_count)
        """
        return {
            'unique_count': len(self.seen_hashes)
        }

    def reset(self) -> None:
        """Clear seen hashes (useful for testing or reprocessing)."""
        self.seen_hashes.clear()
