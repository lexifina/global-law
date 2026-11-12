"""Lists the courts inside every case-law corpus: the folders under `decisions/` in each corpus's repository.

A case-law corpus gathers the decisions of several courts, one folder per court. This asks GitHub for the folders of
`decisions/` at the corpus's `newest` commit in data/freshness.tsv and writes one row per corpus and court to
courts.tsv. Folders that are not courts (`undated`) are left out.

  python courts.py data/freshness.tsv data/gitmodules.txt courts.tsv

Needs the GitHub CLI (`gh`) signed in. One request per case-law corpus.
"""
import csv
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

NOT_A_COURT = {'undated'}


def folders(args):
    path, (owner, repo), sha = args
    for attempt in range(4):  # the connection drops now and then
        r = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}/contents/decisions?ref={sha}'], capture_output=True)
        if not r.returncode:
            return path, sorted(e['name'] for e in json.loads(r.stdout) if e['type'] == 'dir' and e['name'] not in NOT_A_COURT)
    return path, None


def main(freshness, gitmodules, out):
    url = {}
    for block in re.findall(r'\[submodule "[^"]+"\]\s*((?:\s+\w+ = .*\n?)+)', open(gitmodules, encoding='utf-8').read()):
        d = dict(re.findall(r'(\w+) = (.*)', block))
        url[d['path']] = re.search(r'github\.com/([^/]+)/(.+?)(?:\.git)?$', d['url']).groups()
    rows = [r for r in csv.DictReader(open(freshness, encoding='utf-8'), delimiter='\t') if r['path'].endswith('/caselaw')]
    with ThreadPoolExecutor(8) as pool:
        got = dict(pool.map(folders, [(r['path'], url[r['path']], r['newest']) for r in rows]))
    missing = sorted(p for p, v in got.items() if v is None)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('corpus\tcourt\n')
        for p in sorted(got):
            for c in got[p] or []:
                f.write(f'{p}\t{c}\n')
    pairs = [(p, c) for p in got for c in got[p] or []]
    # the same court can sit in several corpora of one country (a court's decisions split by years): count it once
    courts = {(p.split('/')[0], c) for p, c in pairs}
    print(len(rows), 'case-law corpora;', len(pairs), 'corpus and court rows;', len(courts), 'different courts; could not list:', missing)


if __name__ == '__main__':
    main(*sys.argv[1:4])
