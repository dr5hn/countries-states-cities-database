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

from migrations import MigrationError, load_pr_commits, read_jsonl, resolve

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


def load_source_meta(path):
    """Validate source metadata before either export or CI adds its generated data_version."""
    meta = json.loads(Path(path).read_text(encoding='utf-8'))
    if not (isinstance(meta, dict) and isinstance(meta.get('contract_version'), str)
            and re.fullmatch(r'[1-9]\d*', meta['contract_version']) and 'data_version' not in meta):
        raise ReleaseError('migrations/release_meta.json needs a whole-number contract_version and no '
                           'data_version (the run fills it in)')
    return meta


def merge_parents(repo, sha):
    """The parents of a commit in the local clone; ReleaseError when the commit is not there."""
    out = subprocess.run(['git', '-C', str(repo), 'rev-list', '--parents', '-n', '1', sha],
                         capture_output=True, text=True, timeout=60)
    if out.returncode:
        raise ReleaseError(f'commit {sha[:12]} is not in this clone; fetch the full history')
    return out.stdout.split()[1:]


def github_pr_commits(repo, ledger, saved, pending_pr=None, preview=None):
    """Fetch authoritative merge SHAs for PR-only keys; a saved association must agree with GitHub.
    The returned JSONL is kept with export artifacts for offline generator replay. No subject is proof."""
    known = load_pr_commits(saved) if Path(saved).exists() else {}
    numbers = {e['event_pr'] for _, e in read_jsonl(ledger, 'ledger')
               if isinstance(e, dict) and 'event_commit' not in e and type(e.get('event_pr')) is int
               and e['event_pr'] > 0}
    if pending_pr is not None:
        numbers.add(pending_pr)
    proofs = []
    for number in sorted(numbers):
        result = subprocess.run(['gh', 'api', f'repos/{{owner}}/{{repo}}/pulls/{number}'],
                                cwd=repo, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise ReleaseError(f'could not verify PR {number}: {result.stderr.strip()}')
        pr = json.loads(result.stdout)
        if not isinstance(pr, dict):
            raise ReleaseError(f'PR {number}: invalid GitHub response')
        if pr.get('number') != number:
            raise ReleaseError(f'PR {number}: invalid GitHub response')
        if number == pending_pr:
            # The checked commit is the run's merge preview (github.sha). GitHub's live merge_commit_sha moves whenever
            # the base advances and is empty while the PR conflicts, so it is not compared; what must hold is that the
            # PR is open and unsaved and that the preview merges the PR's current head.
            head = (pr.get('head') or {}).get('sha') if isinstance(pr.get('head'), dict) else None
            if pr.get('merged') is not False or number in known:
                raise ReleaseError(f'pending PR {number}: already merged or already saved')
            parents = merge_parents(repo, preview)
            if len(parents) != 2 or not isinstance(head, str) or parents[1] != head:
                raise ReleaseError(f'pending PR {number}: the checked commit is not a merge preview of the current PR '
                                   'head; rerun the check on the latest push')
            continue
        sha = pr.get('merge_commit_sha')
        if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ReleaseError(f'PR {number}: missing GitHub merge_commit_sha association')
        if pr.get('merged') is not True or (number in known and known[number] != sha):
            raise ReleaseError(f'PR {number}: unmerged or saved association disagrees with GitHub')
        proofs.append(json.dumps({'event_pr': number, 'merge_commit_sha': sha}, sort_keys=True) + '\n')
    return ''.join(proofs)


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
        meta = load_source_meta(repo / 'migrations/release_meta.json')
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
        ledger_tip = resolve(repo, 'HEAD')
        proof_path = out / 'MIGRATIONS_PR_COMMITS.jsonl'
        proof_path.write_text(github_pr_commits(repo, repo / 'migrations/events.jsonl',
                                                repo / 'migrations/pr_commits.jsonl'), encoding='utf-8')
        sums = []
        for tag, sha in froms.items():
            print(f'[INFO] generating {tag} ({sha[:12]}) to {args.to[:12]}', flush=True)
            run = subprocess.run([sys.executable, str(repo / 'bin/scripts/release/migrations.py'), '--repo', str(repo),
                                  '--from', sha, '--to', args.to, '--ledger', str(repo / 'migrations/events.jsonl'),
                                  '--reserved', str(repo / 'migrations/reserved_ids.jsonl'), '--meta', str(meta_path),
                                  '--pr-commits', str(proof_path), '--ledger-tip', ledger_tip,
                                  '--out', str(out / f'migrations-from-{tag}')], timeout=GENERATOR_TIMEOUT)
            if run.returncode:
                raise ReleaseError(f'the generator refused {tag} to {args.to[:12]} (see its messages above)')
            target = out / f'migrations-from-{tag}.tar.gz'
            (out / f'migrations-from-{tag}' / 'pr_commits.jsonl').write_bytes(proof_path.read_bytes())
            pack(out / f'migrations-from-{tag}', target)
            sums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}\n')
        (out / 'MIGRATIONS_SHA256SUMS').write_text(''.join(sums), encoding='utf-8')
        (out / 'MIGRATIONS_SOURCE').write_text(f'source {args.to}\n', encoding='utf-8')
        print(f'[INFO] wrote {len(sums)} migration archive(s) to {out}')
        return 0
    except (ReleaseError, MigrationError, OSError, ValueError, subprocess.TimeoutExpired) as e:
        print(f'[ERROR] {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
