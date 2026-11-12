"""Builds data.js, the snapshot as the film reads it, from data/freshness.tsv and figures.json.

One row per corpus: path, level (0 national, 1 sub-national), status (0 current, 1 stale, 2 unverified,
3 pending-change), number of acts, pinned commit, newest commit, commits in the 24 hours before the snapshot, and days
from `last_verified` to the snapshot day (-1 when the corpus has never been checked).

  python build_data.py 2026-11-11
"""
import csv
import datetime as dt
import json
import sys

snap = dt.date.fromisoformat(sys.argv[1])
fig = json.load(open('figures.json', encoding='utf-8'))
status = {'current': 0, 'stale': 1, 'unverified': 2, 'pending-change': 3}
rows = []
for x in csv.DictReader(open('data/freshness.tsv', encoding='utf-8'), delimiter='\t'):
    since = (snap - dt.date.fromisoformat(x['last_verified'])).days if x['last_verified'] else -1
    rows.append([x['path'], 0 if x['level'] == 'national' else 1, status[x['status']], int(x['acts'] or 0),
                 x['pinned'][:7], x['newest'][:7], fig['per_corpus'][x['path']][1], since])
keep = ('snapshot', 'total_commits', 'commits_in_window', 'corpora_with_commits_in_window')
with open('data.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write('window.CORPORA=' + json.dumps(rows, separators=(',', ':')) + ';\n')
    f.write('window.FIGURES=' + json.dumps({k: fig[k] for k in keep}) + ';\n')
