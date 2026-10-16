"""Tests for release_migrations.py: which releases a run compares with, and reproducible archives."""
import gzip
import importlib.util
import tarfile
import tempfile
import unittest
import json
import subprocess
from unittest import mock
from pathlib import Path

# Loaded by path, as test_migrations.py loads migrations.py, so the tests also run from the repository root
_spec = importlib.util.spec_from_file_location('release_migrations_wrapper',
                                               Path(__file__).resolve().with_name('release_migrations.py'))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
pick, pack = _m.pick, _m.pack

TAGS = ['v3.2', 'v4.0', 'v4.0-export.9', 'v4.0-export.51', 'v4.0-export.10', 'export-20250101', 'v2.0']


class Inputs(unittest.TestCase):
    """CI and export share metadata and authoritative PR association validation."""

    def setUp(self):
        """Create minimal source inputs, without network access."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.meta = self.root / 'release_meta.json'
        self.ledger = self.root / 'events.jsonl'
        self.saved = self.root / 'pr_commits.jsonl'
        self.ledger.write_text('{"event_pr": 42}\n')
        self.sha = 'a' * 40

    def test_source_meta_parity(self):
        """Both callers reject bad contract majors and source data_version before filling candidate fields."""
        for meta in ({'contract_version': 'banana'}, {'contract_version': '5', 'data_version': 'wrong'},
                     [], {'contract_version': True}, {'contract_version': '0'}):
            self.meta.write_text(json.dumps(meta))
            with self.subTest(meta=meta), self.assertRaises(_m.ReleaseError):
                _m.load_source_meta(self.meta)
        self.meta.write_text('{"contract_version": "6"}')
        validated = _m.load_source_meta(self.meta)
        self.assertEqual(f"{validated['contract_version']}-candidate", '6-candidate')
        wrapper = Path(_m.__file__).read_text()
        workflow = Path(_m.__file__).resolve().parents[3] / '.github/workflows/ledger-migrations.yml'
        self.assertIn("meta = load_source_meta(repo / 'migrations/release_meta.json')", wrapper)
        self.assertIn("meta = load_source_meta('migrations/release_meta.json')", workflow.read_text())

    def fetch(self, response, pending=None, preview=None, returncode=0):
        """Call the production association helper with a deterministic GitHub response."""
        result = subprocess.CompletedProcess([], returncode, json.dumps(response), 'API unavailable')
        with mock.patch.object(_m.subprocess, 'run', return_value=result) as run:
            value = _m.github_pr_commits(self.root, self.ledger, self.saved, pending, preview)
            run.assert_called_once_with(['gh', 'api', 'repos/{owner}/{repo}/pulls/42'], cwd=self.root,
                                        capture_output=True, text=True, timeout=60)
            return value

    def test_github_association_and_disagreement(self):
        """Only the merged PR's API SHA is saved; missing, unmerged, forged or disagreeing responses fail."""
        response = {'number': 42, 'merged': True, 'merge_commit_sha': self.sha}
        self.assertEqual(json.loads(self.fetch(response)), {'event_pr': 42, 'merge_commit_sha': self.sha})
        self.saved.write_text(json.dumps({'event_pr': 42, 'merge_commit_sha': 'b' * 40}) + '\n')
        with self.assertRaisesRegex(_m.ReleaseError, 'disagrees'):
            self.fetch(response)
        self.saved.unlink()
        for bad in ({**response, 'merged': False}, {**response, 'merge_commit_sha': None},
                    {**response, 'number': 99}, [], {}):
            with self.subTest(response=bad), self.assertRaises(_m.ReleaseError):
                self.fetch(bad)
        with self.assertRaisesRegex(_m.ReleaseError, 'could not verify'):
            self.fetch(response, returncode=1)

    def test_pending_api_preview_parity(self):
        """Pending associations are temporary and require GitHub's current unmerged preview."""
        response = {'number': 42, 'merged': False, 'merge_commit_sha': self.sha}
        self.assertEqual(self.fetch(response, 42, self.sha), '')
        for bad in ({**response, 'merged': True}, {**response, 'merge_commit_sha': 'b' * 40}):
            with self.subTest(response=bad), self.assertRaisesRegex(_m.ReleaseError, 'preview disagrees'):
                self.fetch(bad, 42, self.sha)

    def test_legacy_pr_metadata_needs_no_api(self):
        """The existing SHA-keyed ledger does not acquire an API dependency per event."""
        self.ledger.write_text(json.dumps({'event_pr': 42, 'event_commit': self.sha}) + '\n')
        with mock.patch.object(_m.subprocess, 'run') as run:
            self.assertEqual(_m.github_pr_commits(self.root, self.ledger, self.saved), '')
            run.assert_not_called()


class Pick(unittest.TestCase):
    """pick() names the cumulative and step releases and the data version."""

    def test_before_the_major_is_cut(self):
        """Candidate for v5 while v4.0 is the newest feature release: no data version yet, no v5 export to step from."""
        self.assertEqual(pick(TAGS, 5), ('v4.0', None, None, 4))

    def test_after_the_major_is_cut(self):
        """Once v5.0.0 is published, the cumulative file still starts at v4.0 and exports of v5 come next."""
        self.assertEqual(pick(TAGS + ['v5.0.0'], 5), ('v4.0', None, '5.0.0', 5))
        self.assertEqual(pick(TAGS + ['v5.0.0', 'v5.0.0-export.2', 'v5.0.0-export.12'], 5),
                         ('v4.0', 'v5.0.0-export.12', '5.0.0', 5))

    def test_numbers_compare_as_numbers(self):
        """v4.10 is newer than v4.9, export.51 newer than export.9 (not by string order)."""
        self.assertEqual(pick(['v4.9', 'v4.10', 'v5.0'], 6)[0], 'v5.0')
        self.assertEqual(pick(['v4.9', 'v4.10'], 5)[0], 'v4.10')
        self.assertEqual(pick(['v5.0.0', 'v5.0.0-export.9', 'v5.0.0-export.51'], 5)[1], 'v5.0.0-export.51')

    def test_nothing_published(self):
        """No releases at all gives nothing to compare with."""
        self.assertEqual(pick([], 5), (None, None, None, None))


class Pack(unittest.TestCase):
    """pack() gives the same bytes for the same files."""

    def test_reproducible(self):
        """Two packs of one folder, written at different times, are byte-identical and hold every file."""
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / 'migrations-from-v4.0'
            (folder / 'sub').mkdir(parents=True)
            (folder / 'removed_ids.jsonl').write_text('{"a": 1}\n')
            (folder / 'sub' / 'x.csv').write_text('a,b\n')
            pack(folder, Path(d) / 'one.tar.gz')
            (folder / 'removed_ids.jsonl').touch()
            pack(folder, Path(d) / 'two.tar.gz')
            self.assertEqual((Path(d) / 'one.tar.gz').read_bytes(), (Path(d) / 'two.tar.gz').read_bytes())
            with gzip.open(Path(d) / 'one.tar.gz') as g, tarfile.open(fileobj=g) as t:
                self.assertEqual(t.getnames(), ['migrations-from-v4.0/removed_ids.jsonl',
                                                'migrations-from-v4.0/sub/x.csv'])


if __name__ == '__main__':
    unittest.main()
