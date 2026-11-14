"""Compare an unrepaired and a glyph-aware Journal text: same lines, and every difference is an 'f' that became a
ligature character (U+FB00-FB04). python -I cmp_lig.py <old.txt> <new.txt>"""
import sys
a = open(sys.argv[1], encoding='utf-8').read().split('\n')
b = open(sys.argv[2], encoding='utf-8').read().split('\n')
if len(a) != len(b):
    print('LINES DIFFER', len(a), len(b))
    sys.exit(1)
ch = bad = subs = 0
for x, y in zip(a, b):
    if x == y:
        continue
    ch += 1
    if len(x) != len(y):
        bad += 1
        continue
    for p, q in zip(x, y):
        if p != q:
            if p == 'f' and 'ﬀ' <= q <= 'ﬄ':
                subs += 1
            else:
                bad += 1
print(sys.argv[2].rsplit('/', 1)[-1], 'lines', len(a), 'changed', ch, 'f->ligature', subs, 'other differences', bad)
