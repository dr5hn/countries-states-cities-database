"""Tests for release_migrations.py: which releases a run compares with, and reproducible archives."""
import gzip
import importlib.util
import tarfile
import tempfile
import unittest
from pathlib import Path

# Loaded by path, as test_migrations.py loads migrations.py, so the tests also run from the repository root
_spec = importlib.util.spec_from_file_location('release_migrations_wrapper',
                                               Path(__file__).resolve().with_name('release_migrations.py'))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
pick, pack = _m.pick, _m.pack

TAGS = ['v3.2', 'v4.0', 'v4.0-export.9', 'v4.0-export.51', 'v4.0-export.10', 'export-20250101', 'v2.0']


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
