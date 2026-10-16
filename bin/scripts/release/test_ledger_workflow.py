"""Exercise the workflow's actual path filter on full Git diffs, without Actions or network access."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class RequiredCheck(unittest.TestCase):
    """The required job reports on every PR and only its expensive walk is conditional."""

    def test_triggers_and_path_filter(self):
        """Data, docs, generated-only and a large file list all reach the expected branch."""
        workflow = Path(__file__).resolve().parents[3] / '.github/workflows/ledger-migrations.yml'
        text = workflow.read_text()
        self.assertIn('on:\n  pull_request:\n\npermissions:', text)
        self.assertNotIn('    paths:', text)
        self.assertNotIn('    if:', text.split('    steps:')[0])
        self.assertIn("if: steps.paths.outputs.relevant == 'true'", text)
        script = text.split("python3 - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
        script = '\n'.join(line[10:] for line in script.splitlines())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git = lambda *args: subprocess.run(['git', '-C', d, *args], check=True, capture_output=True)
            git('init', '-q')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'test')
            (root / 'README.md').write_text('base')
            git('add', '.')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD').stdout.decode().strip()
            for paths, expected in ((['README.md'], False), (['json/cities.json'], False),
                                    (['contributions/cities/XX.json'], True),
                                    (['migrations/release_meta.json'], True),
                                    (['bin/scripts/release/migrations.py'], True),
                                    (['.github/workflows/ledger-migrations.yml'], True),
                                    ([f'generated/{i}.txt' for i in range(310)] + ['migrations/events.jsonl'], True)):
                with self.subTest(paths=paths[-1]):
                    git('reset', '--hard', base)
                    git('clean', '-fdq')
                    for name in paths:
                        p = root / name
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text('changed')
                    git('add', '.')
                    git('commit', '-qm', 'candidate')
                    output = root / 'output'
                    subprocess.run(['python3', '-c', script], cwd=d, check=True, capture_output=True,
                                   env={**os.environ, 'GITHUB_OUTPUT': str(output)})
                    self.assertEqual(output.read_text(), f'relevant={str(expected).lower()}\n')
