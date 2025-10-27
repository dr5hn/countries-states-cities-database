"""
Git Parser - Extracts commit history and diffs from git repository.

Supports tracking changes across multiple paths (e.g., cities/, states.json, countries.json).
Returns file-level diffs for each changed file in each commit.
"""

import git
from datetime import datetime
from typing import List, Dict, Optional


class GitParser:
    """Parses git commits for changes in target paths."""

    def __init__(self, repo_path: str = ".", target_paths: List[str] = None):
        """
        Initialize git parser.

        Args:
            repo_path: Path to git repository
            target_paths: List of paths to track (e.g., ['contributions/cities/', 'contributions/states/states.json'])
        """
        self.repo = git.Repo(repo_path)
        self.target_paths = target_paths or ["contributions/"]

    def get_commits(self, since: Optional[str] = None, until: Optional[str] = None) -> List[Dict]:
        """
        Get commits that modified target paths.

        Args:
            since: Start date (ISO format: YYYY-MM-DD or git format)
            until: End date (ISO format: YYYY-MM-DD or git format)

        Returns:
            List of commit dictionaries with file_diffs
        """
        commits = []

        # Build git log arguments
        log_kwargs = {
            'paths': self.target_paths,
            'reverse': False  # Most recent first
        }

        if since:
            log_kwargs['since'] = since
        if until:
            log_kwargs['until'] = until

        # Iterate through commits
        for commit in self.repo.iter_commits(**log_kwargs):
            commit_data = self._extract_commit_data(commit)
            if commit_data and commit_data.get('file_diffs'):
                commits.append(commit_data)

        return commits

    def _extract_commit_data(self, commit: git.Commit) -> Optional[Dict]:
        """
        Extract commit metadata and file diffs.

        Args:
            commit: GitPython Commit object

        Returns:
            Dictionary with commit data and file_diffs list
        """
        try:
            # Get parent commit for diff comparison
            if not commit.parents:
                # Initial commit - no parent to diff against
                return None

            parent = commit.parents[0]

            # Get diffs for target paths
            diffs = parent.diff(commit, paths=self.target_paths, create_patch=True)

            # Extract diffs for each file
            file_diffs = []
            for diff in diffs:
                if diff.diff:
                    diff_text = diff.diff.decode('utf-8', errors='ignore')
                    file_path = diff.b_path or diff.a_path  # Use new path, fallback to old

                    # Only include files that match our target paths
                    if self._matches_target_paths(file_path):
                        file_diffs.append({
                            'path': file_path,
                            'diff': diff_text
                        })

            # Skip commits with no relevant diffs
            if not file_diffs:
                return None

            # Extract commit metadata
            return {
                'sha': commit.hexsha,
                'author': commit.author.name,
                'email': commit.author.email,
                'date': datetime.fromtimestamp(commit.committed_date),
                'message': commit.message.strip(),
                'file_diffs': file_diffs
            }

        except Exception as e:
            print(f"Error processing commit {commit.hexsha}: {e}")
            return None

    def _matches_target_paths(self, file_path: str) -> bool:
        """
        Check if file path matches any target paths.

        Args:
            file_path: File path to check

        Returns:
            True if path matches target paths
        """
        for target in self.target_paths:
            if target.endswith('/'):
                # Directory - check if file is within
                if file_path.startswith(target):
                    return True
            else:
                # Specific file - exact match
                if file_path == target:
                    return True

        return False

    def get_latest_commit_date(self) -> Optional[datetime]:
        """
        Get date of most recent commit in target paths.

        Returns:
            Datetime of latest commit or None
        """
        try:
            latest = next(self.repo.iter_commits(paths=self.target_paths, max_count=1))
            return datetime.fromtimestamp(latest.committed_date)
        except StopIteration:
            return None

    def get_commit_count(self, since: Optional[str] = None) -> int:
        """
        Get count of commits in target paths.

        Args:
            since: Optional start date

        Returns:
            Number of commits
        """
        log_kwargs = {'paths': self.target_paths}
        if since:
            log_kwargs['since'] = since

        return sum(1 for _ in self.repo.iter_commits(**log_kwargs))
