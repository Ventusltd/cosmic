#!/usr/bin/env python3
"""tools/belt_split.py - split the estate's line count by repository, exactly.

The telescope draws 37,796,045,093 particles from a single integer. To draw the BELT it needs to
know which repository each ordinal belongs to, and that needs one number per repository, measured
the same way the total was measured: every path in every commit's tree, copies counted each time.

    python tools/belt_split.py --roots C:/Users/vikra/Documents/GitHub --out belt.tsv

Writes  repo <TAB> entry_lines <TAB> entries <TAB> commits <TAB> head_lines <TAB> first_commit_unix

Sixty-six numbers, not 37.8 billion. The placement law stays computed; only the band boundaries
are shipped, and they sum to the published total or the script says so and exits non-zero.
"""
import argparse, json, os, subprocess, sys, time
from datetime import datetime, timezone

PUBLISHED_ENTRY_LINES = 37796045093
PUBLISHED_ENTRIES     = 14998313

def git(d, args, binary=False):
    r = subprocess.run(['git'] + args, cwd=d, capture_output=True,
                       text=not binary, encoding=None if binary else 'utf-8',
                       errors=None if binary else 'replace')
    return r.stdout

def lines_of(body, size):
    if b'\x00' in body[:8000]:
        return -1
    return body.count(b'\n') + (1 if size and not body.endswith(b'\n') else 0)

def batch_count(d, shas):
    if not shas: return {}
    p = subprocess.run(['git','cat-file','--batch'], cwd=d,
                       input=('\n'.join(shas)+'\n').encode(), capture_output=True)
    out, i, res = p.stdout, 0, {}
    for sha in shas:
        nl = out.find(b'\n', i)
        if nl < 0: break
        hdr = out[i:nl].split()
        if len(hdr) < 3: break
        size = int(hdr[2])
        res[sha] = lines_of(out[nl+1:nl+1+size], size)
        i = nl + 1 + size + 1
    return res

def find_repos(root):
    out = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if os.path.isdir(os.path.join(d, '.git')):
            out.append((name, d))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--roots', default='C:/Users/vikra/Documents/GitHub')
    ap.add_argument('--out', default='belt.tsv')
    a = ap.parse_args()

    repos = []
    for root in a.roots.split(','):
        if os.path.isdir(root):
            repos += find_repos(root)
    if not repos:
        print('FAIL: zero repositories. A check that examines nothing refuses.'); return 1

    cache = {}          # blob sha -> lines (-1 binary). shared across repos: content is content.
    rows = []
    t0 = time.time()
    for name, d in repos:
        entries = lines = 0
        commits = git(d, ['rev-list','--all']).split()
        for c in commits:
            need, have = [], []
            for line in git(d, ['ls-tree','-r',c]).splitlines():
                p = line.split(None, 3)
                if len(p) < 4 or p[1] != 'blob': continue
                have.append(p[2])
                if p[2] not in cache:
                    cache[p[2]] = None
                    need.append(p[2])
            if need: cache.update(batch_count(d, need))
            for sha in have:
                entries += 1
                v = cache.get(sha)
                if v and v > 0: lines += v
        head_lines = 0
        seen_head = set()
        for line in git(d, ['ls-tree','-r','-l','HEAD']).splitlines():
            p = line.split(None, 4)
            if len(p) < 5 or p[1] != 'blob' or p[2] in seen_head: continue
            seen_head.add(p[2])
            v = cache.get(p[2])
            if v is None:
                v = batch_count(d, [p[2]]).get(p[2]); cache[p[2]] = v
            if v and v > 0: head_lines += v
        first = git(d, ['log','--reverse','--all','--format=%ct']).split('\n')[0].strip() or '0'
        rows.append((name, lines, entries, len(commits), head_lines, int(first or 0)))
        print('  %-36s %16s lines  %10s entries  %5s commits  %6.1f s'
              % (name, format(lines,','), format(entries,','), len(commits), time.time()-t0),
              file=sys.stderr, flush=True)

    total_lines   = sum(r[1] for r in rows)
    total_entries = sum(r[2] for r in rows)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# repo\tentry_lines\tentries\tcommits\thead_lines\tfirst_commit_unix\n')
        for r in sorted(rows, key=lambda r: (r[5], r[0])):
            f.write('%s\t%d\t%d\t%d\t%d\t%d\n' % r)

    meta = {'asof': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'),
            'repositories': len(rows),
            'entry_lines': total_lines, 'entries': total_entries,
            'published_entry_lines': PUBLISHED_ENTRY_LINES,
            'published_entries': PUBLISHED_ENTRIES,
            'matches_published_lines': total_lines == PUBLISHED_ENTRY_LINES,
            'matches_published_entries': total_entries == PUBLISHED_ENTRIES,
            'seconds': round(time.time()-t0, 1),
            'command': 'python tools/belt_split.py ' + ' '.join(sys.argv[1:])}
    with open(os.path.splitext(a.out)[0] + '-meta.json','w',encoding='utf-8',newline='\n') as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    print(json.dumps(meta, indent=1, sort_keys=True))
    if total_lines != PUBLISHED_ENTRY_LINES:
        print('MISMATCH: the bands do not sum to the published total. The belt must not be drawn '
              'from these numbers until this is explained.', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
