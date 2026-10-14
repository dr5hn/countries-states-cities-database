#!/usr/bin/env python3
"""Generate the migration files an export release carries (see migrations/README.md), as the export workflow does.

The two --from snapshots are picked from the repository's published GitHub releases (drafts and prereleases skipped):
- cumulative: the newest feature release (vX.Y or vX.Y.Z) of a major below the contract_version in
  migrations/release_meta.json, e.g. v4.0 for v5 data;
- step: the newest export release of that same major (v<feature>-export.N), e.g. v5.0.0-export.1 for the next v5
  export. An earlier major's export is not used: its tag may hold rows whose ids the export assigned and synced back
  later (v4.0-export.51 has 10,851), and the generator needs every id at --from. v5.0.0's own first export carries
  only the cumulative file: users of a later v4.0 export use it to remap the ids they store (its added ids and
  changed fields are relative to v4.0) and load the v5 data fresh.
migrations.py runs from each to --to; each output folder is packed as migrations-from-<tag>.tar.gz, and
MIGRATIONS_SHA256SUMS and MIGRATIONS_SOURCE are written next to them. data_version is the newest published feature
release of the contract's major, the base the publish job names the export after; before that release is cut (a
candidate run) it is "<major>-candidate", and --production refuses.

Usage, from a full clone with `gh` signed in (GH_TOKEN in Actions):
    python3 bin/scripts/release/release_migrations.py --to <sha> --out <new folder> [--production]
Exits 1 with a message naming the problem; the generator's own output says what to fix in the ledger.
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

FEATURE = re.compile(r'^v?(\d+)\.(\d+)(?:\.(\d+))?$')
EXPORT = re.compile(r'^v?(\d+)\.(\d+)(?:\.(\d+))?-export\.(\d+)$')
GENERATOR_TIMEOUT = 45 * 60   # seconds per run; a full v4.0 run takes about 75 s on a laptop


class ReleaseError(Exception):
    """A precondition failed; the message says what to fix."""


def pick(tags, major):
    """(cumulative tag or None, step tag or None, data_version or None, newest feature major or None) from published
    release tags, for data whose contract major is `major`."""
    features = [(tuple(int(x or 0) for x in m.groups()), t) for t in tags if (m := FEATURE.match(t))]
    exports = [(tuple(int(x or 0) for x in m.groups()), t) for t in tags
               if (m := EXPORT.match(t)) and int(m[1]) == major]
    earlier = [f for f in features if f[0][0] < major]
    current = [f for f in features if f[0][0] == major]
    return (max(earlier)[1] if earlier else None,
            max(exports)[1] if exports else None,
            max(current)[1].lstrip('v') if current else None,
            max(features)[0][0] if features else None)


def published_tags(repo):
    """Tag names of the repository's published releases (not drafts, not prereleases)."""
    out = subprocess.run(['gh', 'api', '--paginate', 'repos/{owner}/{repo}/releases', '--jq',
                          '.[] | select((.draft or .prerelease) | not) | .tag_name'],
                         cwd=repo, capture_output=True, text=True, timeout=300)
    if out.returncode:
        raise ReleaseError(f'could not list releases with gh: {out.stderr.strip()}')
    return out.stdout.split()


def commit_of(repo, tag):
    """The commit a tag points at; the clone must hold the tag (a full clone does)."""
    out = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', '--quiet', f'refs/tags/{tag}^{{commit}}'],
                         capture_output=True, text=True)
    if out.returncode:
        raise ReleaseError(f'tag {tag} is not in this clone; fetch the full history with its tags')
    return out.stdout.strip()


def pack(folder, target):
    """Write folder as a gzipped tar with fixed times and owners, so the same files always give the same bytes."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(p for p in folder.rglob('*') if p.is_file()):
            info = tarfile.TarInfo(f'{folder.name}/{path.relative_to(folder).as_posix()}')
            info.size, info.mode, info.mtime = path.stat().st_size, 0o644, 0
            with open(path, 'rb') as f:
                tar.addfile(info, f)
    with open(target, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
        gz.write(buf.getvalue())


def main():
    """Pick the intervals, run the generator for each and pack the results; returns the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--to', required=True, help='the release candidate commit (a full SHA)')
    ap.add_argument('--out', required=True, help='a folder that does not exist yet')
    ap.add_argument('--production', action='store_true', help='refuse unless the contract major has a feature release')
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[3]
    out = Path(args.out)
    try:
        if not re.fullmatch(r'[0-9a-f]{40}', args.to):
            raise ReleaseError(f'--to must be a full commit SHA, got {args.to!r}')
        if out.exists():
            raise ReleaseError(f'{out} exists; pass a new folder')
        meta = json.loads((repo / 'migrations' / 'release_meta.json').read_text(encoding='utf-8'))
        if not re.fullmatch(r'[1-9]\d*', str(meta.get('contract_version', ''))) or 'data_version' in meta:
            raise ReleaseError('migrations/release_meta.json needs a whole-number contract_version and no '
                               'data_version (the run fills it in)')
        major = int(meta['contract_version'])
        cumulative, step, data_version, newest = pick(published_tags(repo), major)
        print(f'[INFO] contract {major}: cumulative from {cumulative}, step from {step}, data_version {data_version}')
        if args.production and (data_version is None or newest != major):
            raise ReleaseError(f'the newest published feature release is major {newest}, not {major}: cut '
                               f'v{major}.0.0 (or the right feature release) before a production export')
        froms = {}
        for tag in (cumulative, step):
            if tag and commit_of(repo, tag) not in froms.values():
                froms[tag] = commit_of(repo, tag)
        if not froms:
            raise ReleaseError('no published feature or export release to compare with')
        out.mkdir(parents=True)
        meta_path = out / 'release_meta.json'
        meta_path.write_text(json.dumps({**meta, 'data_version': data_version or f'{major}-candidate'}), encoding='utf-8')
        sums = []
        for tag, sha in froms.items():
            print(f'[INFO] generating {tag} ({sha[:12]}) to {args.to[:12]}', flush=True)
            run = subprocess.run([sys.executable, str(repo / 'bin/scripts/release/migrations.py'), '--repo', str(repo),
                                  '--from', sha, '--to', args.to, '--ledger', str(repo / 'migrations/events.jsonl'),
                                  '--reserved', str(repo / 'migrations/reserved_ids.jsonl'), '--meta', str(meta_path),
                                  '--out', str(out / f'migrations-from-{tag}')], timeout=GENERATOR_TIMEOUT)
            if run.returncode:
                raise ReleaseError(f'the generator refused {tag} to {args.to[:12]} (see its messages above)')
            target = out / f'migrations-from-{tag}.tar.gz'
            pack(out / f'migrations-from-{tag}', target)
            sums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}\n')
        (out / 'MIGRATIONS_SHA256SUMS').write_text(''.join(sums), encoding='utf-8')
        (out / 'MIGRATIONS_SOURCE').write_text(f'source {args.to}\n', encoding='utf-8')
        print(f'[INFO] wrote {len(sums)} migration archive(s) to {out}')
        return 0
    except (ReleaseError, OSError, ValueError, subprocess.TimeoutExpired) as e:
        print(f'[ERROR] {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
