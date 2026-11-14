#!/usr/bin/env python3
"""classify9.py - attribute each findings disagreement (citing, cited) of a differential run to the rows of
expect.tsv with that (by/text owner, target) pair, by the row's zone flavour (`what` column of expect.tsv:
r8ok|r8fail [/nopower] /zok|/zfail|/nozone).  python classify9.py FAILDIR...  (FAILDIR/<u>/{diff.tsv,expect.tsv})"""
import os
import sys
from collections import Counter, defaultdict


def rows(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8', errors='replace') as f:
        return [l.rstrip('\n').split('\t') for l in f if l.strip()]


def main():
    cnt = Counter()
    ex = {}
    for root in sys.argv[1:]:
        for u in sorted(os.listdir(root)):
            d = os.path.join(root, u)
            pair = defaultdict(set)
            for r in rows(os.path.join(d, 'expect.tsv')):
                if len(r) >= 7:
                    pair[(r[6], r[5])].add(r[3])
            for r in rows(os.path.join(d, 'diff.tsv')):
                if r[0] != 'findings':
                    k = (r[0], r[1], '-')
                else:
                    p = r[3].split(' ')
                    k = (r[0], r[1] + ':' + r[2], '|'.join(sorted(pair.get((p[1], p[2]), {'nopair'}))) if len(p) >= 3
                         else '?')
                cnt[k] += 1
                ex.setdefault(k, '%s %s' % (u, r[3]))
    for k, n in sorted(cnt.items()):
        print('%-9s %-45s %-40s %4d  e.g. %s' % (k + (n, ex[k])))


if __name__ == '__main__':
    main()
