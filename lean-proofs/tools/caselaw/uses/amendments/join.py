"""Join Lean outputs with ops.tsv -> results table."""
import csv, sys, collections, glob
csv.field_size_limit(10**9)
opsp, outs, dst = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
res, geq = {}, {}
for p in outs:
    for l in open(p, encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[1] == 'G': geq[f[0]] = f[2]; continue
        res[(f[0], f[1])] = f[2:]
w = open(dst, 'w', encoding='utf-8', newline='\n')
rd = csv.reader(open(opsp, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)
hdr = next(rd)
w.write('\t'.join(hdr[:11] + ['outcome', 'places', 'record_shows', 'record_cand', 'cands_differ', 'group_replay_equal', 'args', 'wording']) + '\n')
for r in rd:
    gid, oid, status = r[0], r[1], r[8]
    if status == 'section_not_in_record': o = ['section_not_in_record', '', '', '', '']
    elif status == 'chapter_level': o = ['chapter_level', '', '', '', '']
    else: o = res.get((gid, oid), ['missing', '', '', '', ''])
    w.write('\t'.join(r[:11] + o + [geq.get(gid, '')] + r[11:13]) + '\n')
