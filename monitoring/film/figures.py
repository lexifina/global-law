"""Counts the commit figures shown in the monitoring short.

For every corpus in global-law's data/freshness.tsv it asks GitHub for the history of that corpus's repository at the
commit in the `newest` column (the newest commit the pipeline had published when the snapshot was taken):

  total   commits reachable from that commit
  window  of those, the commits whose committer date falls in the 24 hours before the snapshot

global-law's own commits (the ones that move the pins) are not counted in either figure.

  python figures.py <freshness.tsv> <gitmodules file> <snapshot time, e.g. 2026-11-11T20:11:55Z> <out.json>

Needs the GitHub CLI (`gh`) signed in. About 25 GraphQL requests.
"""
import csv
import datetime as dt
import json
import re
import subprocess
import sys


def main(freshness, gitmodules, snapshot, out):
    until = dt.datetime.strptime(snapshot, '%Y-%m-%dT%H:%M:%SZ')
    since = until - dt.timedelta(hours=24)
    iso = lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')
    text = open(gitmodules, encoding='utf-8').read()
    url = {}
    for block in re.findall(r'\[submodule "[^"]+"\]\s*((?:\s+\w+ = .*\n?)+)', text):
        d = dict(re.findall(r'(\w+) = (.*)', block))
        url[d['path']] = re.search(r'github\.com/([^/]+)/(.+?)(?:\.git)?$', d['url']).groups()
    rows = [r for r in csv.DictReader(open(freshness, encoding='utf-8'), delimiter='\t') if r['path'] in url]
    counts, missing = {}, []
    for k in range(0, len(rows), 40):
        chunk = rows[k:k + 40]
        q = 'query{' + ''.join(
            f'r{i}:repository(owner:"{url[r["path"]][0]}",name:"{url[r["path"]][1]}"){{object(oid:"{r["newest"]}"){{... on Commit{{'
            f'all:history{{totalCount}} day:history(since:"{iso(since)}",until:"{iso(until)}"){{totalCount}}}}}}}}'
            for i, r in enumerate(chunk)) + '}'
        res = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + q], capture_output=True, text=True, encoding='utf-8')
        data = (json.loads(res.stdout) if res.stdout else {}).get('data') or {}
        for i, r in enumerate(chunk):
            obj = (data.get(f'r{i}') or {}).get('object')
            if obj:
                counts[r['path']] = [obj['all']['totalCount'], obj['day']['totalCount']]
            else:
                missing.append(r['path'])
    result = {
        'snapshot': snapshot, 'window': [iso(since), iso(until)], 'corpora': len(rows),
        'total_commits': sum(v[0] for v in counts.values()),
        'commits_in_window': sum(v[1] for v in counts.values()),
        'corpora_with_commits_in_window': sum(1 for v in counts.values() if v[1]),
        'missing': missing, 'per_corpus': counts,
    }
    json.dump(result, open(out, 'w', encoding='utf-8', newline='\n'), indent=0)
    print({k: v for k, v in result.items() if k != 'per_corpus'})
    print(sorted(((v[1], p) for p, v in counts.items() if v[1]), reverse=True)[:15])


if __name__ == '__main__':
    main(*sys.argv[1:5])
