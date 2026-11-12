"""Builds data.js, the snapshot as the film reads it, from data/freshness.tsv and figures.json.

SOURCES is the list shown in the last scene: up to two `official_source` names per country, taken in path order, where the
name is 12 to 44 characters, fits the row beside its path and uses only characters in the film's fonts; each name is
listed once, and mirrors and private collections are left out. Fourteen courts of the United States from courts.tsv
are mixed in, named from their folders. SOURCE_COUNT is the number of different `official_source` names in the file
plus the number of different courts in courts.tsv (a court that sits in several corpora of one country counts once;
folders named by year are not courts).

One row per corpus: path, level (0 national, 1 sub-national), status (0 current, 1 stale, 2 unverified,
3 pending-change), number of acts, pinned commit, newest commit, commits in the 24 hours before the snapshot, and days
from `last_verified` to the snapshot day (-1 when the corpus has never been checked).

  python build_data.py 2026-11-11
"""
import csv
import re
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
import zlib  # noqa: E402

table = list(csv.DictReader(open('data/freshness.tsv', encoding='utf-8'), delimiter='\t'))
names = {x['official_source'] for x in table if x['official_source']}
# rows whose source is a mirror or a private collection are left out of the list (they still count in SOURCE_COUNT)
NOT_A_PUBLISHER = ('Wiki', 'Veritas', 'unofficial', 'Bar Association')
seen, used, sources = {}, set(), []
for x in sorted(table, key=lambda x: (x['level'] != 'national', x['path'])):
    n, country = x['official_source'], x['path'].split('/')[0]
    if any(w in n for w in NOT_A_PUBLISHER) or n in used or len(n) + len(x['path']) > 60:
        continue
    if n and seen.get(country, 0) < 2 and 12 <= len(n) <= 44 and all(ord(ch) < 256 for ch in n):
        seen[country] = seen.get(country, 0) + 1
        used.add(n)
        sources.append([n, x['path']])
sources = sorted(sources, key=lambda r: zlib.crc32(r[1].encode()))[:56]
court_rows = [r for r in csv.DictReader(open('courts.tsv', encoding='utf-8'), delimiter='\t')
              if not re.fullmatch(r'[\d_-]+', r['court'])]
courts = {(r['corpus'].split('/')[0], r['court']) for r in court_rows}
SMALL = {'of', 'the', 'for', 'and', 'in'}
us = sorted((r for r in court_rows if r['corpus'].startswith('united-states/') and 'court' in r['court'] and 14 <= len(r['court']) <= 40
             and len(r['court']) + len(r['corpus']) <= 76), key=lambda r: zlib.crc32(r['court'].encode()))
seen_court = set()
for r in us:
    if r['court'] in seen_court or len(seen_court) == 14:
        continue
    seen_court.add(r['court'])
    words = r['court'].split('-')
    sources.append([' '.join(w if w in SMALL and i else w.capitalize() for i, w in enumerate(words)), r['corpus']])
sources.sort(key=lambda r: zlib.crc32(r[1].encode() + r[0].encode()))  # a fixed shuffle, so neighbours are from different places
keep = ('snapshot', 'total_commits', 'commits_in_window', 'corpora_with_commits_in_window')
with open('data.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write('window.CORPORA=' + json.dumps(rows, separators=(',', ':')) + ';\n')
    f.write('window.FIGURES=' + json.dumps({k: fig[k] for k in keep}) + ';\n')
    f.write('window.SOURCES=' + json.dumps(sources, ensure_ascii=False, separators=(',', ':')) + ';\n')
    f.write('window.SOURCE_COUNT=' + str(len(names) + len(courts)) + ';\n')
print(len(names), 'publishers +', len(courts), 'courts =', len(names) + len(courts), '| list rows', len(sources))
