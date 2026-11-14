"""counts.tsv for round12/data_orders: per year, every parsed Journal entry by class, the node-class entries by the
lower court named, and nodes in nodes.tsv by provenance (round 11 / round-12 r11-rule append / r12:longlist).

python -I counts12.py <entries.jsonl> <nodes.tsv> <n_round11_rows> <out counts.tsv>
"""
import sys, json, re, collections

NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')
CLASSES = ['gvr', 'vacated', 'order_vacated', 'granted_remanded', 'reversed', 'affirmed', 'cert_denied', 'dismissed',
           'opinion', 'other']


def court_kind(ct):
    return ('federal_circuit' if re.search(r'Court of Appeals for the|Court of Appeals for Veterans|Armed Forces', ct) else
            'federal_district' if re.search(r'District Court', ct) else
            'state' if ct != '-' else 'none')


def main():
    ent, nodes, n11, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    c = collections.Counter()
    courts = collections.Counter()
    journals = collections.defaultdict(set)
    for l in open(ent, encoding='utf-8'):
        r = json.loads(l)
        y = r['date'][:4] if r['date'] else '-'
        c[(y, r['cls'])] += 1
        journals[y].add(r['journal'].rsplit('_', 1)[-1])
        if r['cls'] in NODE_CLASSES:
            courts[(y, court_kind(r['court']))] += 1
    lines = [l.rstrip('\n').split('\t') for l in open(nodes, encoding='utf-8')][1:]
    nc = collections.Counter()
    for i, f in enumerate(lines):
        src = f[7] if len(f) > 7 else '-'
        grp = 'r11' if i < n11 else ('longlist' if src == 'r12:longlist' else 'r12_append')
        nc[(f[2][:4], grp)] += 1
    years = sorted(set(y for y, _ in c))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('year\tjournals\t' + '\t'.join(CLASSES) + '\tall_entries\tnode_class_entries\t'
                'node_class_court_federal_circuit\tnode_class_court_federal_district\tnode_class_court_state\t'
                'node_class_court_none\tnodes_round11\tnodes_r12_append\tnodes_r12_longlist\tnodes_total\n')
        tot = collections.Counter()
        for y in years:
            v = [c[(y, k)] for k in CLASSES]
            ncls = sum(c[(y, k)] for k in NODE_CLASSES)
            ck = [courts[(y, k)] for k in ('federal_circuit', 'federal_district', 'state', 'none')]
            nn = [nc[(y, g)] for g in ('r11', 'r12_append', 'longlist')]
            row = v + [sum(v), ncls] + ck + nn + [sum(nn)]
            for i, x in enumerate(row):
                tot[i] += x
            f.write('\t'.join([y, ','.join(sorted(journals[y]))] + [str(x) for x in row]) + '\n')
        f.write('\t'.join(['all', '-'] + [str(tot[i]) for i in range(len(tot))]) + '\n')
    print(open(out, encoding='utf-8').read())


if __name__ == '__main__':
    main()
