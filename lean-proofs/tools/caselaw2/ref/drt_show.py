#!/usr/bin/env python3
"""drt_show.py - print everything about one node of a differential-testing universe, for triage.

  python drt_show.py UNIVERSE_DIR NODE [NODE ...]

Shows the node's decisions2 row and court epochs, every treatment / history / supersession row that names it (as
target or by), its holdings, and both sides' status rows and findings mentioning it.
"""
import os
import sys


def rows(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return [l.rstrip('\n').split('\t') for l in f if l.strip()]


def main():
    d = sys.argv[1]
    nodes = set(sys.argv[2:])
    D = lambda f: rows(os.path.join(d, 'data', f))
    dec = {r[0]: r for r in D('decisions2.tsv')}
    courts = D('courts2.tsv')
    want = set(nodes)
    for r in D('treatments.tsv'):
        if r[1] in nodes or r[2] in nodes:
            want.update((r[1], r[2]))
    for r in D('history.tsv'):
        if r[1] in nodes or r[2] in nodes:
            want.add(r[1])
            if r[2] != '-1':
                want.add(r[2])
    print('== decisions')
    for n in sorted(want, key=int):
        r = dec.get(n)
        if r:
            ep = [c for c in courts if c[0] == r[1] and int(c[1]) <= int(r[2]) <= int(c[2])]
            print('  ', '\t'.join(r[:7]), '|', ep[0][3] if ep else '?', ep[0][5] if ep else '')
    print('== system_rules')
    for r in D('system_rules.tsv'):
        print('  ', '\t'.join(r[:5]), r[6])
    print('== treatments')
    for r in D('treatments.tsv'):
        if r[1] in nodes or r[2] in nodes:
            print('  ', '\t'.join(r[:8]), '| part', r[13], '| q', r[11][:70], '| ev', r[12])
    print('== history')
    for r in D('history.tsv'):
        if r[1] in nodes or r[2] in nodes:
            print('  ', '\t'.join(r[:6]), '| q', r[9][:60], '| ev', r[10])
    print('== supersessions / lawchanges')
    for r in D('supersessions.tsv'):
        if r[1] in nodes:
            print('  ', '\t'.join(r))
    for r in D('lawchanges.tsv'):
        print('  ', '\t'.join(r))
    print('== holdings')
    for r in D('holdings.tsv'):
        if r[1] in nodes:
            print('  ', '\t'.join(r[:6]))
    for side in ('lean', 'ref'):
        print('== %s status' % side)
        for r in rows(os.path.join(d, side, 'status.tsv')):
            if r[0] in nodes:
                print('  ', '\t'.join(r))
        print('== %s certs (rows on these nodes)' % side)
        ids = {r[0] for r in D('treatments.tsv') + D('history.tsv') if r[1] in nodes or r[2] in nodes}
        for r in rows(os.path.join(d, side, 'certs.tsv')):
            if r[1] in ids:
                print('  ', '\t'.join(r))
        print('== %s findings' % side)
        for r in rows(os.path.join(d, side, 'findings.tsv')):
            if r[1] in nodes or r[2] in nodes:
                print('  ', '\t'.join(r))


if __name__ == '__main__':
    main()
