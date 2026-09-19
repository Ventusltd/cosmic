#!/usr/bin/env python3
"""tools/clusters.py - the estate as a hierarchy, measured at every level.

A flat disc of 37.9 billion identical points is white, because 37.9 billion over a million pixels
is forty thousand lines per pixel. The night sky is not white. What makes a sky is CLUSTERING:
things are bound to other things, and the black between them is as real as the light.

The estate was never a flat list. It is already a hierarchy:

    estate  ->  repository  ->  commit  ->  line

So the telescope draws the level the field can resolve, and no deeper. At full field it draws the
repositories. Enter one and its commits resolve. Enter a commit and its lines resolve. The 37.9
billion are only drawn inside a sector small enough to hold them, which is what a telescope does:
it does not resolve the whole sky at once, and it never pretended to.

Writes:
  belt.tsv           repo  entry_lines  entries  commits  head_lines  first_commit_unix
  commits/NN.tsv     unix  entry_lines  entries  sha12    one file per repository, fetched only
                                                          when that sector is entered, exactly as
                                                          GridAtlas fetches a project on demand
  belt-meta.json     the totals, and whether they match what was published

Sharding the commits by repository is the point: the whole hierarchy is never downloaded, because
nobody looks at two sectors at once.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

PUBLISHED_ENTRY_LINES = 37796045093
PUBLISHED_ENTRIES = 14998313


def git(d, args):
    return subprocess.run(['git'] + args, cwd=d, capture_output=True, text=True,
                          encoding='utf-8', errors='replace').stdout


def lines_of(body, size):
    """-1 means binary. Otherwise newlines, plus one if the file does not end in a newline."""
    if b'\x00' in body[:8000]:
        return -1
    return body.count(b'\n') + (1 if size and not body.endswith(b'\n') else 0)


def batch_count(d, shas):
    """One git cat-file --batch pass. Returns {sha: lines, or -1 for binary}."""
    if not shas:
        return {}
    p = subprocess.run(['git', 'cat-file', '--batch'], cwd=d,
                       input=('\n'.join(shas) + '\n').encode(), capture_output=True)
    out, i, res = p.stdout, 0, {}
    for sha in shas:
        nl = out.find(b'\n', i)
        if nl < 0:
            break
        h = out[i:nl].split()
        if len(h) < 3:
            break
        size = int(h[2])
        res[sha] = lines_of(out[nl + 1:nl + 1 + size], size)
        i = nl + 1 + size + 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--roots', default='C:/Users/vikra/Documents/GitHub')
    ap.add_argument('--out', default='.')
    a = ap.parse_args()

    repos = []
    for root in a.roots.split(','):
        if not os.path.isdir(root):
            continue
        for n in sorted(os.listdir(root)):
            d = os.path.join(root, n)
            if os.path.isdir(os.path.join(d, '.git')):
                repos.append((n, d))
    if not repos:
        print('FAIL: zero repositories. A check that examines nothing refuses.')
        return 1

    os.makedirs(os.path.join(a.out, 'commits'), exist_ok=True)
    cache, rows, t0 = {}, [], time.time()

    for name, d in repos:
        times = {}
        for line in git(d, ['log', '--all', '--format=%H %ct']).splitlines():
            p = line.split()
            if len(p) == 2:
                times[p[0]] = int(p[1])
        crows, entries, lines = [], 0, 0
        for c in git(d, ['rev-list', '--all']).split():
            ce = cl = 0
            need, have = [], []
            for line in git(d, ['ls-tree', '-r', c]).splitlines():
                p = line.split(None, 3)
                if len(p) < 4 or p[1] != 'blob':
                    continue
                have.append(p[2])
                if p[2] not in cache:
                    cache[p[2]] = None
                    need.append(p[2])
            if need:
                cache.update(batch_count(d, need))
            for sha in have:
                ce += 1
                v = cache.get(sha)
                if v and v > 0:
                    cl += v
            crows.append((times.get(c, 0), cl, ce, c[:12]))
            entries += ce
            lines += cl
        head, seen = 0, set()
        for line in git(d, ['ls-tree', '-r', '-l', 'HEAD']).splitlines():
            p = line.split(None, 4)
            if len(p) < 5 or p[1] != 'blob' or p[2] in seen:
                continue
            seen.add(p[2])
            v = cache.get(p[2])
            if v is None:
                v = batch_count(d, [p[2]]).get(p[2])
                cache[p[2]] = v
            if v and v > 0:
                head += v
        first = min([r[0] for r in crows if r[0]], default=0)
        rows.append({'repo': name, 'lines': lines, 'entries': entries, 'commits': len(crows),
                     'head': head, 'first': first, 'crows': crows})
        print('  %-34s %16s lines %10s entries %5s commits %6.1f s'
              % (name, format(lines, ','), format(entries, ','), len(crows), time.time() - t0),
              file=sys.stderr, flush=True)

    # the belt's own order: newest repository at the centre, oldest at the rim, because distance
    # is time. This is the same ordering the estate already uses, not a new one.
    rows.sort(key=lambda r: (-r['first'], r['repo']))
    total = sum(r['lines'] for r in rows)
    tot_e = sum(r['entries'] for r in rows)

    with open(os.path.join(a.out, 'belt.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# repo\tentry_lines\tentries\tcommits\thead_lines\tfirst_commit_unix\n')
        for r in rows:
            f.write('%s\t%d\t%d\t%d\t%d\t%d\n'
                    % (r['repo'], r['lines'], r['entries'], r['commits'], r['head'], r['first']))

    for i, r in enumerate(rows):
        with open(os.path.join(a.out, 'commits', '%02d.tsv' % i), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write('# %s\tunix\tentry_lines\tentries\tsha12\n' % r['repo'])
            for t, cl, ce, sha in sorted(r['crows'], key=lambda x: -x[0]):
                f.write('%d\t%d\t%d\t%s\n' % (t, cl, ce, sha))

    meta = {'asof': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'),
            'repositories': len(rows), 'entry_lines': total, 'entries': tot_e,
            'commits': sum(r['commits'] for r in rows),
            'published_entry_lines': PUBLISHED_ENTRY_LINES,
            'published_entries': PUBLISHED_ENTRIES,
            'matches_published_lines': total == PUBLISHED_ENTRY_LINES,
            'matches_published_entries': tot_e == PUBLISHED_ENTRIES,
            'delta_lines': total - PUBLISHED_ENTRY_LINES,
            'seconds': round(time.time() - t0, 1),
            'command': 'python tools/clusters.py ' + ' '.join(sys.argv[1:])}
    with open(os.path.join(a.out, 'belt-meta.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    print(json.dumps(meta, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
