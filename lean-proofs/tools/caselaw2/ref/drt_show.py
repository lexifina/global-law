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
    # round 4 / round 5: a witness row also shows when the node is its witness W; with its witness and class lines
    wit = {r[0]: r for r in D('treatment_witness.tsv') if len(r) >= 3}
    cls = {}
    for r in D('treatment_class.tsv'):
        cls.setdefault(r[0], []).append(r)
    for r in D('treatments.tsv'):
        w = wit.get(r[0])
        if r[1] in nodes or r[2] in nodes or (w and w[1] in nodes):
            print('  ', '\t'.join(r[:8]), '| part', r[13], '| q', r[11][:90], '| ev', r[12])
            if w:
                print('       witness W', w[1], '| by-ev', w[2])
            for c in cls.get(r[0], ()):
                print('       class row', '\t'.join(c))
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
        ids |= {k for k, w in wit.items() if w[1] in nodes}
        for r in rows(os.path.join(d, side, 'certs.tsv')):
            if r[1] in ids:
                print('  ', '\t'.join(r))
        if os.path.exists(os.path.join(d, side, 'classes.tsv')):
            print('== %s classes (rows on these nodes)' % side)
            for r in rows(os.path.join(d, side, 'classes.tsv')):
                if r[0] in ids:
                    print('  ', '\t'.join(r))
        print('== %s findings' % side)
        for r in rows(os.path.join(d, side, 'findings.tsv')):
            if r[1] in nodes or r[2] in nodes:
                print('  ', '\t'.join(r))


if __name__ == '__main__':
    main()
