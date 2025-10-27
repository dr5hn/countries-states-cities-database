"""
JSON Diff Analyzer - Analyzes JSON changes from git diffs.

Detects additions, updates, and deletions in JSON files from contributions/ folder.
Matches objects by ID and name to distinguish updates from add/delete pairs.
"""

import json
import re
from typing import List, Dict, Optional


class JSONAnalyzer:
    """Analyzes JSON diffs from git to detect database changes."""

    def __init__(self):
        """Initialize the JSON analyzer."""
        self.entity_types = {
            'cities': 'city',
            'states': 'state',
            'countries': 'country'
        }

    def analyze_diff(self, diff_text: str, file_path: str) -> List[Dict]:
        """
        Analyze a git diff for JSON changes.

        Args:
            diff_text: Git diff output
            file_path: Path to the file being analyzed

        Returns:
            List of change dictionaries with action, entity_type, country_code, entity data
        """
        changes = []

        # Extract country code and entity type from path
        country_code = self._extract_country_code(file_path)
        entity_type = self._extract_entity_type(file_path)

        if not entity_type:
            return changes

        # Extract added and removed JSON objects from diff
        added_objects = self._extract_json_objects(diff_text, '+')
        removed_objects = self._extract_json_objects(diff_text, '-')

        # Track which removed objects have been matched (for updates)
        matched_removed = set()

        # Process added objects - check if they're updates or new additions
        for obj in added_objects:
            matching_removed = self._find_matching_object(obj, removed_objects)

            if matching_removed:
                # This is an update
                matched_removed.add(id(matching_removed))
                change = self._create_update_change(obj, matching_removed, entity_type, country_code)
                changes.append(change)
            else:
                # This is a new addition
                change = self._create_add_change(obj, entity_type, country_code)
                changes.append(change)

        # Process removed objects that weren't matched - these are deletions
        for obj in removed_objects:
            if id(obj) not in matched_removed:
                change = self._create_delete_change(obj, entity_type, country_code)
                changes.append(change)

        return changes

    def _extract_country_code(self, file_path: str) -> Optional[str]:
        """Extract country code from file path."""
        # For cities: contributions/cities/US.json -> US
        match = re.search(r'contributions/cities/([A-Z]{2})\.json', file_path)
        if match:
            return match.group(1)

        # For states/countries: use 'global'
        if 'states' in file_path or 'countries' in file_path:
            return 'global'

        return None

    def _extract_entity_type(self, file_path: str) -> Optional[str]:
        """Determine entity type from file path."""
        if 'cities' in file_path:
            return 'city'
        elif 'states' in file_path:
            return 'state'
        elif 'countries' in file_path:
            return 'country'
        return None

    def _extract_json_objects(self, diff_text: str, prefix: str) -> List[Dict]:
        """
        Extract JSON objects from diff lines starting with prefix (+/-).

        Args:
            diff_text: Git diff output
            prefix: '+' for added lines, '-' for removed lines

        Returns:
            List of parsed JSON objects
        """
        objects = []

        # Find lines starting with prefix that contain JSON objects
        # Look for complete object patterns: {"id": ..., "name": ..., ...}
        lines = diff_text.split('\n')
        current_obj = ""
        in_object = False
        brace_count = 0

        for line in lines:
            # Skip diff headers
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue

            # Check if line starts with our prefix
            if line.startswith(prefix):
                content = line[1:].strip()  # Remove prefix and whitespace

                # Track braces to detect complete objects
                for char in content:
                    if char == '{':
                        if brace_count == 0:
                            in_object = True
                            current_obj = ""
                        brace_count += 1

                    if in_object:
                        current_obj += char

                    if char == '}':
                        brace_count -= 1
                        if brace_count == 0 and in_object:
                            # Complete object found
                            try:
                                obj = json.loads(current_obj)
                                objects.append(obj)
                            except json.JSONDecodeError:
                                pass  # Skip malformed JSON
                            in_object = False
                            current_obj = ""

        return objects

    def _find_matching_object(self, obj: Dict, candidates: List[Dict]) -> Optional[Dict]:
        """
        Find matching object in candidates list for update detection.

        Matches by ID (primary) or name (fallback).

        Args:
            obj: Object to match
            candidates: List of candidate objects

        Returns:
            Matching object or None
        """
        obj_id = obj.get('id')
        obj_name = obj.get('name')

        for candidate in candidates:
            # Match by ID (most reliable)
            if obj_id and candidate.get('id') == obj_id:
                return candidate

            # Match by name (fallback for objects without IDs)
            if obj_name and candidate.get('name') == obj_name:
                return candidate

        return None

    def _create_add_change(self, obj: Dict, entity_type: str, country_code: str) -> Dict:
        """Create a change record for an addition."""
        return {
            'action': 'add',
            'entity_type': entity_type,
            'country_code': country_code,
            'entity': obj,
            'changes': {
                'added': self._extract_essential_fields(obj)
            }
        }

    def _create_update_change(self, new_obj: Dict, old_obj: Dict, entity_type: str, country_code: str) -> Dict:
        """Create a change record for an update."""
        # Detect what fields changed
        changed_fields = {}
        for key in new_obj:
            if key in old_obj:
                if new_obj[key] != old_obj[key]:
                    changed_fields[key] = {
                        'old': old_obj[key],
                        'new': new_obj[key]
                    }
            else:
                # New field added
                changed_fields[key] = {
                    'old': None,
                    'new': new_obj[key]
                }

        return {
            'action': 'update',
            'entity_type': entity_type,
            'country_code': country_code,
            'entity': new_obj,
            'changes': {
                'updated': changed_fields
            }
        }

    def _create_delete_change(self, obj: Dict, entity_type: str, country_code: str) -> Dict:
        """Create a change record for a deletion."""
        return {
            'action': 'delete',
            'entity_type': entity_type,
            'country_code': country_code,
            'entity': obj,
            'changes': {
                'deleted': self._extract_essential_fields(obj)
            }
        }

    def _extract_essential_fields(self, obj: Dict) -> Dict:
        """Extract essential fields for changelog (id, name, code fields)."""
        essential = {}

        # Always include these if present
        key_fields = ['id', 'name', 'code', 'iso2', 'iso3', 'state_code', 'country_code']

        for field in key_fields:
            if field in obj:
                essential[field] = obj[field]

        return essential
